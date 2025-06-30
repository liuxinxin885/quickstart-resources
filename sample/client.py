import requests

url = 'http://127.0.0.1:5000/mcp'
data = {'message': '你好，MCP服务！'}
response = requests.post(url, json=data)
print('服务端回复:', response.json()['reply'])
