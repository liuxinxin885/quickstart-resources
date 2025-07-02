import requests
import pandas as pd
false=False
true=True
'''根据船舶和时间查询船舶位置'''
url='http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location/slice'
data={"mmsi":636022692,"postime":"2025-06-30 10:52:32"}
AUTH_TOKEN="Basic YmFpbGlhbl9hcGlfYWxpeXVuOjlyYm10NjUydnlxOXJldm0ycXdleTZpa2UzeGcxbQ=="
headers = {
    'Authorization': AUTH_TOKEN,
    'Content-Type': 'application/json'
}
data=requests.post(url, json=data, headers=headers)
if data.status_code == 200:
    print(data.json())
    postime=data.json()['data']['postime']
    lon=data.json()['data']['lon']
    lat=data.json()['data']['lat']
else:
    print(f"Error: {data.status_code} - {data.text}")


'''根据位置和时间查询区域内的船'''
url='http://voc.uat.myvessel.cn/sdc/v1/vessels/status/nearby/slice'
data={"scanRange":{"center":{"lat":31.608933,"lon":123.424562},"radius":10},"sliceTime":"2025-06-30 10:52:32","beforeAfterSliceMinutes":30}
data=requests.post(url, json=data, headers=headers)
if data.status_code == 200:
    print(data.json())
    df=pd.DataFrame(data.json()['data'])
else:
    print(f"Error: {data.status_code} - {data.text}")


'''根据船舶mmsi查询最新动态和基本信息'''
url='http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location'
data={"mmsiList":[636022692,352004603,413259000,477850200,441200000,413288110,477100200,311001693,355534000,413492850],"withSpeedOverWater":false}
data=requests.post(url, json=data, headers=headers)
if data.status_code == 200:
    print(data.json())
    df=pd.DataFrame(data.json()['data'])
else:
    print(f"Error: {data.status_code} - {data.text}")



'''根据船舶mmsi和时间查询船舶轨迹'''
url='http://voc.uat.myvessel.cn/sdc/v1/routes/route/cross'
data={"mmsiList":[636022692,352004603,413259000,477850200,441200000,413288110,477100200,311001693,355534000,413492850],"startPostime":"2025-06-30 09:52:00","endPostime":"2025-06-30 11:52:00","unitType":1}
data=requests.post(url, json=data, headers=headers)
if data.status_code == 200:
    print(data.json())
else:
    print(f"Error: {data.status_code} - {data.text}")