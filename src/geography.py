import numpy as np

from utils import any_none

def haversine_vec(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def ddm_to_dd(ddm_str, hemisphere):
    if any_none([ddm_str, hemisphere]):
        return

    val = float(ddm_str)
    degrees = int(val // 100)
    minutes = val % 100
    
    decimal = degrees + (minutes / 60)
    
    if hemisphere in ['S', 'W']:
        decimal *= -1
        
    return decimal