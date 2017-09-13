from __future__ import absolute_import
from datetime import datetime, timedelta

def today_utc_iso():
    
    return datetime.utcnow().strftime('%Y-%m-%d')
    
def today_utc():
    
    return datetime.utcnow().date()
    
def today_iso():
    
    return datetime.now().strftime('%Y-%m-%d')
    
def iso(dt):
    
    if dt.__class__.__name__=='date':
        return dt.strftime('%Y-%m-%d')
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def from_iso(iso):
    
    if len(iso)==19:
        return datetime.strptime(iso,'%Y-%m-%d %H:%M:%S')
    
    if len(iso)==10:
        return datetime.strptime(iso,'%Y-%m-%d').date()

def now_iso():
        
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
    
def now_utc_iso():
    
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')    

def mtime():
    
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')    

def www_format_mtime(time_iso, error_time_diff=None, with_date=True):
    
    dt = from_iso(time_iso)
    
    dt = dt + timedelta(hours=8)
    
    st = datetime.strftime(dt,'%H:%M')

    diff = datetime.now()-dt
    diff = int(diff.total_seconds())
    h = diff // 3600
    m = (diff-h*3600) // 60
    sd = '({0:02d}:{1:02d})'.format(h,m)
    
    if diff > 3600*24:
        if with_date:
            res = datetime.strftime(dt,'%d.%m %H:%M')
        else:
            res = st
    elif diff > 60*30:
        res = st + ' ' + sd
    else:
        res = sd
    
    if error_time_diff:
        if diff/60 > error_time_diff:
            return res, 'ERROR'
        else:
            return res, ''
    else:
        return res

