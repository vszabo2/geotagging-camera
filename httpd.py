#!/usr/bin/python

from BaseHTTPServer import HTTPServer, test
import cgi
import os
import posixpath
import shutil
import signal
from SimpleHTTPServer import SimpleHTTPRequestHandler
import sys
import urllib
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def dirEntries(dir_name):
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile): fileList.append(dirfile)
        elif os.path.isdir(dirfile): fileList.extend(dirEntries(dirfile))
    return fileList

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            {"/home/pi/app/path": self.pathMgr,
             "/home/pi/app/updatePath": self.updatePath, 
             "/home/pi/app/zip": self.zip}[self.translate_path(self.path)]()
        except KeyError:
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
#       # abandon query parameters
        try:
            path, self.querystring = path.split('?',1) #changed
        except ValueError:
            pass
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul><br>\n<a href=/zip?%s>Zip directory</a>\n"
                    % self.path)
        f.write("<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def pathMgr(self):
        with open("path") as f:
            path = f.read().strip()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("cache-control", "private, max-age=0, no-cache")
        self.end_headers()
        self.wfile.write("""<html>
<head><script type="text/javascript">
function update() {
  path = document.getElementById("path").value;
  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    document.getElementById("result").innerText = "New path (very likely) set"; };
  xmlhttp.open("GET", "updatePath?" + path, true);
  xmlhttp.send()
}
</script></head>
<body>Save location (don't forget trailing slash!): <br>
<input type="text" value="%s" id="path"/><br>
<input type="button" value="Update" onclick="update()"/><br>
<div id="result"/></body>
</html>""" % path)

    def updatePath(self):
        with open("path", "w") as f:
            f.write(self.querystring + "\n")
        os.kill(os.getppid(), signal.SIGUSR1)

    def zip(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        os.remove("last.zip")
        zip = zipfile.ZipFile("../last.zip", "w")
        for file in dirEntries("." + self.querystring):
            print "zipping", file
            zip.write(file)
        zip.close()
        print "done zipping"
        shutil.move("../last.zip", "last.zip")
        os.chown("last.zip", 1000, 1000)
        self.wfile.write("<html><body><a href=/last.zip>Download</a></body></html>")

test(MyHTTPRequestHandler, HTTPServer)
