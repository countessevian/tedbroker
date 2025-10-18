#!/usr/bin/env python3
import http.server
import socketserver
import os
from urllib.parse import urlparse, unquote

PORT = 8000
DIRECTORY = "public/copytradingbroker.io"

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)

        # Handle root path
        if path == '/' or path == '':
            path = '/index.html'
        # If path doesn't have an extension, try adding .html
        elif not os.path.splitext(path)[1]:
            # Remove trailing slash if present
            if path.endswith('/'):
                path = path[:-1]
            path = path + '.html'

        # Update the path
        self.path = path

        # Call the parent class method to serve the file
        return super().do_GET()

with socketserver.TCPServer(("", PORT), CleanURLHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print(f"Serving files from: {DIRECTORY}")
    print(f"Access the site at: http://localhost:{PORT}/")
    httpd.serve_forever()
