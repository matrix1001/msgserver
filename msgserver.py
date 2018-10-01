import sys
try:
    from urlparse import urlparse, parse_qsl
    from Queue import Queue
    
except:
    from urllib.parse import urlparse, parse_qsl
    from queue import Queue
from multiprocessing import Process
from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        command = parsed_url.path[1:]
        kwargs = dict(parse_qsl(parsed_url.query))

        encoding = 'utf-8'
        if 'encoding' in kwargs:
            encoding = kwargs['encoding']

        res_code, result = self.server.handlemsg(command, kwargs)

        self.send_response(res_code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        if type(result) == str and result != '':
            self.wfile.write(bytes(result.encode(encoding)))
        elif type(result) == int:
            self.wfile.write(bytes(str(result).encode(encoding)))
            
        
    def do_POST(self):
        parsed_url = urlparse(self.path)
        command = parsed_url.path[1:]
        kwargs = dict(parse_qsl(parsed_url.query))
        post = self.rfile.read(int(self.headers['content-length']))
        kwargs.update(dict(parse_qsl(post))) 
        
        encoding = 'utf-8'
        if 'encoding' in kwargs:
            encoding = kwargs['encoding']

        res_code, result = self.server.handlemsg(command, kwargs)

        self.send_response(res_code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        if type(result) == str and result != '':
            self.wfile.write(bytes(result.encode(encoding)))
        elif type(result) == int:
            self.wfile.write(bytes(str(result).encode(encoding)))


class MsgServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass=RequestHandler, bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandler, bind_and_activate)
        self.commands = {}
        self.server_proc = None

    def start(self):
        self.server_proc = Process(target=self.serve_forever)
        self.server_proc.daemon = True
        self.server_proc.start()
    
    def stop(self):
        self.server_proc.terminate()
        self.server_close()
    
    def handlemsg(self, command_name, kwargs):
        '''200:ok-content   204:ok-nocontent   400:bad req    501:not implemented'''
        if command_name in self.commands:
            command = self.commands[command_name]
            if self._check(kwargs, command):
                result = self._exec(command['func'], kwargs)
                if result:
                    return 200, result
                else:
                    return 204, result
            else:
                return 400, 'Bad Request (Syntax error)'
        else:
            return 501, 'Not Implemented'
        
    def _check(self, kwargs, command):
        required = command['required']
        optional = command['optional']
        for key in required:
            if key not in kwargs:
                return False
            try:
                typ = required[key]
                kwargs[key] = typ(kwargs[key])
            except:
                return False
        for key in optional:
            if key not in kwargs:
                continue
            try:
                typ = optional[key]
                kwargs[key] = typ(kwargs[key])
            except:
                return False
        return True


    def _exec(self, func, kwargs):
        try:
            return func(**kwargs)
        except Exception as e:
            print(e)
            return None
            

        
if __name__ == '__main__':
    import json, requests
    import ctypes
    
    def translator(content='', src='auto', dst='zh', **kwargs):
        if content=='': return None
        GOOGLE_API="http://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl={src}&tl={dst}&q={content}"
        try:    
            url = GOOGLE_API.format(content=content, src=src, dst=dst)
            decoder = json.JSONDecoder()
            html = requests.get(url, timeout=3).text
            result_dict = decoder.decode(html)
            trans = result_dict['sentences'][0]['trans']
            user = ctypes.CDLL('user32.dll')
            title = 'translator: %s' % result_dict['src']
            msg =  '%s -> %s' % (content, trans)
            user.MessageBoxW(None, msg, title, 0)

            return trans
        except Exception as e:
            print(e, str(e))
            return None
        
    def adder(a, b, **kwargs):
        return a+b
    address = ('localhost', 8088)
    server = MsgServer(address)
    server.commands['translator'] = {
        'func':translator,
        'required':{
            'content':str, 
                },
        'optional':{
            'src':str, 
            'dst':str,
            'encoding':str,
                },
        'description':'my translator',
    }
    server.commands['adder'] = {
        'func':adder,
        'required':{
            'a':int,
            'b':int,
        },
        'optional':{},
        'description':'adder',
    }
    server.start()
    input()
    server.stop()
