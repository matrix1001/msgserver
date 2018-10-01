# msgserver
a local server to finish python tasks. check example
# usage
try run this:
```python
from msgserver import MsgServer
if __name__ == '__main__':
    def adder(a, b):
        return a+b
    address = ('localhost', 8088)
    server = MsgServer(address)
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
```
then fire at this url.

`http://localhost:8088/adder?a=1&b=1024`

now you will get this in the response html.

`1025`
