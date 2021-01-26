import zmq

class Zmq:
   def __init__(self, serverurl, ttl=600):
        # if ':' in serverurl:
        #     server, port = serverurl.split(':')
        #     self.zmq = Redis(host=server, port=port)
        # else:
        #     self.zmq = Redis(host=serverurl)
        
        # self.ttl = ttl
         
    def addFrame(self, frameKey):
        pass
    
    def close(self):
        pass
