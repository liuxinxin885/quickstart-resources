from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/mcp', methods=['POST'])
def mcp():
    data = request.json
    message = data.get('message', '')
    # 简单回显
    return jsonify({'reply': f'服务端收到: {message}'})

if __name__ == '__main__':
    app.run(port=5000)
