import numpy as np
import json

from redis import Redis

class RedisClient:
    formatKey = lambda self, frameKey: '{}:{}'.format(self.session, frameKey)
    FRAME = "image"
    DETECTIONS = "detections"

    def __init__(self, serverUrl, session='default', ttl=600):
        if ':' in serverUrl:
            server, port = serverUrl.split(':')
            self.redis = Redis(host=server, port=port)
        else:
            self.redis = Redis(host=serverUrl)
        
        self.ttl = ttl
        self.session = session
        self.lastFrameKey = '{}:lastframeid'.format(session)
        self.lastDetectionKey = '{}:lastdetectionid'.format(session)
         
    def addFrame(self, frameId, frame):
        self.addData(frameId, frame, self.FRAME, self.lastFrameKey)
        
    def addDetections(self, frameId, detections):
        jsonDetections = json.dumps(detections)
        self.addData(frameId, jsonDetections, self.DETECTIONS, self.lastDetectionKey)

    def addData(self, frameId, data, hKeyName, lastKeyName):
        key = self.formatKey(frameId)
        self.redis.hset(key, hKeyName, data)
        self.redis.expire(key, self.ttl)
        self.redis.setex(lastKeyName, self.ttl, frameId)

    def getFrame(self, frameId):
        imageBytes = self.getData(frameId, self.FRAME)
        return np.frombuffer(imageBytes, dtype=np.int8)

    def getDetections(self, frameId):
        return self.getFrame(frameId), json.loads(self.getData(frameId, self.DETECTIONS))

    def getData(self, frameId, hKeyName):
        key = self.formatKey(frameId)
        data = self.redis.hget(key, hKeyName)
        return data
    
    def getLastFrameId(self):
        return self.getLast(self.lastFrameKey)

    def getLastDetectionId(self):
        return self.getLast(self.lastDetectionKey)

    def getLast(self, lastKeyName):
        id = self.redis.get(lastKeyName)
        return int(id) if id else None
