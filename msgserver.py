import sys
try:
    from urlparse import urlparse, parse_qsl
except:
    from urllib.parse import urlparse, parse_qsl
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        app_name = parsed_url.path[1:]
        kwargs = dict(parse_qsl(parsed_url.query))
        print(app_name, kwargs)
        result = ''
        for func in globals()['apps']:
            if app_name == func.__name__:
                result = func(**kwargs)
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        if result:
            self.wfile.write(bytes(result, encoding = "utf-16"))
            
        
    def do_POST(self):
        parsed_url = urlparse(self.path)
        app_name = parsed_url.path[1:]
        kwargs = dict(parse_qsl(parsed_url.query))
        print(app_name, kwargs)
        post = self.rfile.read(int(self.headers['content-length']))
        kwargs.update(dict(parse_qsl(post))) 
        for func in globals()['apps']:
            if app_name == func.__name__:
                func(**kwargs)

if __name__ == '__main__':
    import json, requests
    import ctypes
    
    def translator(content='', src='auto', dst='zh'):
        if content=='': return None
        GOOGLE_API="http://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl={src}&tl={dst}&q={content}"
        try:    
            url = GOOGLE_API.format(content=content, src=src, dst=dst)
            decoder = json.JSONDecoder()
            html = requests.get(url, timeout=3).text
            result = decoder.decode(html)
            result = result['sentences'][0]['trans']

            user = ctypes.windll.LoadLibrary('user32.dll')
            user.MessageBoxW(None, result, 'translator', 0)

            return result
        except Exception as e:
            print(e, str(e))
            return None
        

    apps = [translator, ]
    address = ('localhost', 8088)
    server = HTTPServer(address, RequestHandler)
    server.serve_forever()
