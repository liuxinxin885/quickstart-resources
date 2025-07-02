from fastmcp import FastMCP
import requests

class VesselAPI:
    def __init__(self):
        self.AUTH_TOKEN = "Basic Ybailian_api_alixiuN:lybm652vyq9revm2qwl e6ik e3xg1m"
        self.headers = {
            'Authorization': self.AUTH_TOKEN,
            'Content-Type': 'application/json'
        }

    def get_vessel_location(self, mmsi, postime):
        url = 'http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location/slice'
        data = {"mmsi": mmsi, "postime": postime}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_vessels_in_area(self, scan_range, slice_time, before_after_slice_minutes):
        url = 'http://voc.uat.myvessel.cn/sdc/v1/vessels/status/nearby/slice'
        data = {
            "scanRange": scan_range,
            "sliceTime": slice_time,
            "beforeAfterSliceMinutes": before_after_slice_minutes
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_vessel_details(self, mmsi_list, with_speed_over_water):
        url = 'http://voc.uat.myvessel.cn/sdc/v1/vessels/status/location'
        data = {
            "mmsiList": mmsi_list,
            "withSpeedOverWater": with_speed_over_water
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def get_vessel_trajectory(self, mmsi_list, start_postime, end_postime, unit_type):
        url = 'http://voc.uat.myvessel.cn/sdc/v1/routes/route/cross'
        data = {
            "mmsiList": mmsi_list,
            "startPostime": start_postime,
            "endPostime": end_postime,
            "unitType": unit_type
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

# 创建MCP服务器实例
server = FastMCP()

# 注册VesselAPI类的方法为MCP服务
server.register(VesselAPI())

# 启动MCP服务器
server.start()
