from datetime import date, datetime
import pytz

def replace_timezone(dt: datetime):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt