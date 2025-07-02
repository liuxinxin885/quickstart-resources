import requests
import folium
import matplotlib.pyplot as plt

'''根据船舶和时间查询船舶位置'''
url='http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location/slice'
data={"mmsi":636022692,"postime":"2025-06-30 10:52:32"}
AUTH_TOKEN="Basic YmFpbGlhbl9hcGlfYWxpeXVuOjlyYm10NjUydnlxOXJldm0ycXdleTZpa2UzeGcxbQ=="
headers = {
    'Authorization': AUTH_TOKEN,
    'Content-Type': 'application/json'
}
'''根据船舶mmsi和时间查询船舶轨迹'''
url='http://voc.uat.myvessel.cn/sdc/v1/routes/route/cross'
data={"mmsiList":[636022692,352004603,413259000,477850200,441200000,413288110,477100200,311001693,355534000,413492850],"startPostime":"2025-06-30 09:52:00","endPostime":"2025-06-30 11:52:00","unitType":1}
data=requests.post(url, json=data, headers=headers)
if data.status_code == 200:
    # print(data.json())
    print(f"查询到 {len(data.json()['data']['aisRecords'])} 条船舶轨迹数据")
else:
    print(f"Error: {data.status_code} - {data.text}")
# 圆心"lat":10.708888,"lon":101.673518 半径 30 海里

def plot_ship_tracks(data, center_lat=31.608933, center_lon=123.424562, radius_nm=30):
    # 创建地图
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    # 绘制船舶轨迹
    for mmsi in data.json()['data']['aisRecords']:
        # 假设每个mmsi的轨迹点存储在'mmsi'键下
        # 这里需要根据实际数据结构进行调整
        track_points = [(point['lon'], point['lat']) for point in data.json()['data']['aisRecords'][mmsi]]
        # print(f"mmsi: {mmsi}, track points: {track_points}")
        folium.PolyLine(track_points, color="blue", weight=2.5, opacity=1).add_to(m)
    
    # 绘制圆形区域
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_nm * 1852,  # 海里转米
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.2
    ).add_to(m)
    
    # 保存地图为HTML文件
    m.save("cross.html")
    print("地图已保存为 cross.html")

# 调用函数绘制船舶轨迹
plot_ship_tracks(data)
