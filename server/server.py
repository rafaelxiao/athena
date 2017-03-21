from http.server import HTTPServer, CGIHTTPRequestHandler

port = 7070
httpd = HTTPServer(('', port), CGIHTTPRequestHandler)
print("Starting server on port: " + str(httpd.server_port))
httpd.serve_forever()
