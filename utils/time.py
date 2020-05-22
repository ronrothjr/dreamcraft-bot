# t.py
import datetime
import pytz
from config.setup import Setup

SETUP = Setup()
TZ = SETUP.timezone

class T(object):
    @staticmethod
    def now():
        return datetime.datetime.utcnow()

    @staticmethod
    def to(d, user=None):
        if user and user.time_zone:
            user_tz = user.time_zone if user.time_zone else TZ
            tz = pytz.timezone(user_tz)
            my = pytz.utc.localize(d, is_dst=None).astimezone(tz)
            d_str = my.astimezone(tz).strftime('%m/%d %I:%M %p' if 'America' in user_tz else '%m/%d %H:%M')
        else:
            d_str = d.astimezone().strftime('%m/%d %H:%M')
        return d_str

    @staticmethod
    def tz(d, timezone):
        tz = pytz.timezone(timezone)
        d_str = d.astimezone(tz).strftime('%m/%d %I:%M %p' if 'America' in timezone else '%m/%d %H:%M')
        return d_str