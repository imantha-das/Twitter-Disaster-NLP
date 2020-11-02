import pandas as pd
from geopy import geocoders 
from geopy.exc import GeocoderTimedOut

# Authentication : Replace ??? with your api username 
gn = geocoders.GeoNames(username = "???")

def Lat_Lon_Extractor(df:pd.DataFrame, address_col_name: pd.Series)->pd.DataFrame:
    """Extracts the lat/lon from an address : Max 1000 addresses allowed by geopy api per hour"""

    lat_ls = []
    lon_ls = []

    for addr in df[address_col_name]:
        geo = gn.geocode(addr,timeout = 15)
        if geo is not None:
            lat_ls.append(geo.latitude)
            lon_ls.append(geo.longitude)
        else:
            lat_ls.append(None)
            lon_ls.append(None)

    df["lat"] = lat_ls
    df["lon"] = lon_ls

    return df
        
