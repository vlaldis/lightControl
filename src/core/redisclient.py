import numpy as np

from redis import Redis

class RedisClient:
    formatKey = lambda self, frameKey: '{}:{}'.format(self.session, frameKey)
    IMAGE = "image"
    IMAGEWITHDETECTIONS = "imagewithdetections"

    def __init__(self, serverurl, session='default', ttl=600):
        if ':' in serverurl:
            server, port = serverurl.split(':')
            self.redis = Redis(host=server, port=port)
        else:
            self.redis = Redis(host=serverurl)
        
        self.ttl = ttl
        self.session = session
        self.lastFrameKey = '{}:lastframeid'.format(session)
        self.lastDetectionKey = '{}:lastdetectionid'.format(session)
         
    def addFrame(self, frameId, frame):
        self.addImage(frameId, frame, self.IMAGE, self.lastFrameKey)
        
    def addDetection(self, detectionId, detectedImage):
        self.addImage(detectionId, detectedImage, self.IMAGEWITHDETECTIONS, self.lastDetectionKey)

    def addImage(self, frameId, frame, hKeyName, lastKeyName):
        key = self.formatKey(frameId)
        self.redis.hset(key, hKeyName, frame)
        self.redis.expire(key, self.ttl)
        self.redis.setex(lastKeyName, self.ttl, frameId)

    def getFrame(self, frameId):
        return self.getImage(frameId, self.IMAGE)

    def getDetection(self, detectionId):
        return self.getImage(detectionId, self.IMAGEWITHDETECTIONS)

    def getImage(self, id, hKeyName):
        key = self.formatKey(id)
        imageBytes = self.redis.hget(key, hKeyName)
        return np.frombuffer(imageBytes, dtype=np.int8)
    
    def getLastFrameId(self):
        return self.getLast(self.lastFrameKey)

    def getLastDetectionId(self):
        return self.getLast(self.lastDetectionKey)

    def getLast(self, lastKeyName):
        id = self.redis.get(lastKeyName)
        return int(id) if id else None

    def close(self):
        pass