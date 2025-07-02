import requests
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
# 圆心"lat":31.608933,"lon":123.424562 半径 30 海里

def plot_ship_tracks(data, center_lat=31.608933, center_lon=123.424562, radius_nm=30):
    # 绘制船舶轨迹
    plt.figure(figsize=(10, 8))
    
    for mmsi in data.json()['data']['aisRecords']:
        # 假设每个mmsi的轨迹点存储在'mmsi'键下
        # 这里需要根据实际数据结构进行调整
        track_points = [(point['lon'], point['lat']) for point in data.json()['data']['aisRecords'][mmsi]]
        # print(f"mmsi: {mmsi}, track points: {track_points}")
        plt.plot([p[0] for p in track_points], [p[1] for p in track_points], label=f'MMSI {mmsi}', marker='o')
    
    # 绘制圆形区域
    circle = plt.Circle((center_lon, center_lat), radius_nm * 1852 / 111319, color='red', fill=True, alpha=0.2)
    plt.gca().add_patch(circle)
    
    # 设置图表标题和标签
    plt.title('船舶轨迹和圆形区域')
    plt.xlabel('经度')
    plt.ylabel('纬度')
    plt.legend()
    plt.grid(True)
    
    # 保存图表为PNG文件
    plt.savefig("cross.png")
    print("地图已保存为 cross.png")

# 调用函数绘制船舶轨迹
plot_ship_tracks(data)
