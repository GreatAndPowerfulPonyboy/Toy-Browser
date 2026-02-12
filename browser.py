import socket
import ssl
port = 8080
class URL:
    def __init__(self,url):
        self.scheme, url = url.split("://",1)
        assert self.scheme in ["http","https"]
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/",1)
        self.path = "/" + url
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
    def request(self):
        # Create the socket
        ctx = ssl.create_default_context()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        # Construct HTTP Request
        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
        request += "\r\n"
        s.send(request.encode("utf8"))
        # Reconstruct HTTP Response
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        # Collect response headers
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":",1)
            # We normalize headers to lower case since they're case-insensitive
            response_headers[header.casefold()] = value.strip()
            # Transfer and content encoding not yet implemented
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
        # Collect response
        content = response.read()
        s.close()
        return content
def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
def load(url):
    body = url.request()
    show(body)

if __name__ =="__main__":
    import sys
    load(URL(sys.argv[1]))
    