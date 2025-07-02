import requests
# import pandas as pd
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("时间机器")

# Define the common headers for API requests
AUTH_TOKEN = "Basic YmFpbGlhbl9hcGlfYWxpeXVuOjlyYm10NjUydnlxOXJldm0ycXdleTZpa2UzeGcxbQ=="
headers = {
    'Authorization': AUTH_TOKEN,
    'Content-Type': 'application/json'
}

# 1. 根据输入的船舶 MMSI 和时间，查询到船舶的位置和时间
@mcp.tool()
def get_vessel_position(mmsi: int, postime: str) -> dict:
    """根据输入的船舶 MMSI 和时间，查询到船舶的位置和时间"""
    url = 'http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location/slice'
    data = {"mmsi": mmsi, "postime": postime}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return {"error": f"Error: {response.status_code} - {response.text}"}

# 2. 根据传入的时间和坐标，获取区域内的船舶列表信息
@mcp.tool()
def get_vessels_in_area(scan_range: dict, slice_time: str, before_after_slice_minutes: int) -> dict:
    """根据传入的时间和坐标，获取区域内的船舶列表信息"""
    url = 'http://voc.uat.myvessel.cn/sdc/v1/vessels/status/nearby/slice'
    data = {
        "scanRange": scan_range,
        "sliceTime": slice_time,
        "beforeAfterSliceMinutes": before_after_slice_minutes
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return {"error": [f"Error: {response.status_code} - {response.text}"]}

# 3. 可以根据传入的 MMSI list，返回船舶当前船舶列表的表格
@mcp.tool()
def get_vessels_by_mmsi_list(mmsi_list: list) -> dict:
    """可以根据传入的 MMSI list，返回船舶当前船舶列表的表格"""
    url = 'http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location'
    data = {"mmsiList": mmsi_list, "withSpeedOverWater": False}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return {"error": [f"Error: {response.status_code} - {response.text}"]}

# 4. 根据传入的 MMSI list 和时间查询这些船舶的轨迹，并根据 get_cross_png.py 中的内容生成图片，输出图片地址，同时返回网页地址
@mcp.tool()
def get_vessel_trajectory(mmsi_list: list, start_postime: str, end_postime: str, unit_type: int) -> dict:
    """根据传入的 MMSI list 和时间查询这些船舶的轨迹，并根据 get_cross_png.py 中的内容生成图片，输出图片地址，同时返回网页地址"""
    url = 'http://voc.uat.myvessel.cn/sdc/v1/routes/route/cross'
    data = {
        "mmsiList": mmsi_list,
        "startPostime": start_postime,
        "endPostime": end_postime,
        "unitType": unit_type
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        # 假设这里调用 get_cross_png.py 来生成图片并返回图片地址
        # 实际实现中需要集成 get_cross_png.py 的功能
        image_url = "http://voc.uat.myvessel.cn/microapps/vesseltimemachine/#/"
        return {
            "image_url": image_url,
            "web_url": "http://voc.uat.myvessel.cn/microapps/vesseltimemachine/#/"
        }
    else:
        return {"error": f"Error: {response.status_code} - {response.text}"}

# 5. 根据输入的 MMSI 和时间，查询船舶周围的情况
@mcp.tool()
def get_vessel_surroundings(mmsi: int, postime: str, radius:int=10, before_after_slice_minutes: int=30) -> dict:
    """根据输入的 MMSI 和时间，查询船舶周围的情况 默认扫描范围为半径 radius 海里"""
    # 首先获取船舶的位置
    vessel_position = get_vessel_position(mmsi, postime)
    if "error" in vessel_position:
        return vessel_position
    # return vessel_position
    # 提取船舶的经纬度
    latitude = vessel_position.get('lat')
    longitude = vessel_position.get('lon')
    print(f"latitude:{latitude},longitude:{longitude}")
    # 如果没有获取到位置信息，返回错误
    if not latitude or not longitude:
        return {"error": "无法获取船舶的位置信息"}

    # 构造扫描范围
    scan_range = {
        "center": {"lat": latitude, "lon": longitude},
        "radius": radius  # 单位为海里
    }
    

    # 获取周围船舶列表
    vessels_in_area = get_vessels_in_area(scan_range, postime, before_after_slice_minutes)

    # 如果获取周围船舶失败，返回错误
    if "error" in vessels_in_area:
        return vessels_in_area

    # 返回结果
    return {
        "vessel_position": vessel_position,
        "vessels_in_area": vessels_in_area
    }



if __name__ == "__main__":
    # Start the MCP server
    # mcp.run(transport='streamable-http')
    mcp.run(transport='sse')
