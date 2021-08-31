from datetime import datetime;

from suntime import Sun, SunTimeException

class NightTime:
    halfDayInSeconds = 12*60*60
    
    # Slovakia
    latitude = 48.414980208990976
    longitude = 18.223144711888395

    now = lambda self: datetime.now().timestamp() 

    def __init__(self):
        self.sun = Sun(self.latitude, self.longitude)
        self.sunset = 0
        self.sunrise = 0

    def isNight(self):
        currentTime = self.now()
        return  self.getSunrise() > currentTime or currentTime > self.getSunset()

    def secondsTillNight(self):
        return self.getSunset() - self.now()

    def getSunrise(self):
        return self.sun.get_sunrise_time().timestamp()

    def getSunset(self):
        return self.sun.get_sunset_time().timestamp()
