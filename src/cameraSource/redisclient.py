from redis import Redis

class RedisClient:
    formatKey = lambda self, frameKey: '{}:{}'.format(self.session, frameKey)

    def __init__(self, serverurl, session='default', ttl=600):
        if ':' in serverurl:
            server, port = serverurl.split(':')
            self.redis = Redis(host=server, port=port)
        else:
            self.redis = Redis(host=serverurl)
        
        self.ttl = ttl
        self.session = session
        self.lastFrameKey = '{}:lastframeid'.format(session)
         
    def addFrame(self, frameId, frame):
        key = self.formatKey(frameId)
        self.redis.setex(key, self.ttl, frame)
        self.redis.setex(self.lastFrameKey, self.ttl, frameId)
        
    def get(self, frameId):
        key = self.formatKey(frameId)
        return self.redis.get(key)

    def getLastFrameId(self):
        key = self.redis.get(self.lastFrameKey)
        return self.get(key) if key else 0


    def close(self):
        pass