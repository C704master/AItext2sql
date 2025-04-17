import requests
import json


def test_stream():
    url = "http://localhost:8000/api/chat/stream"
    data = {
        "message": "你好，请介绍一下你自己"
    }
    
    print(f"发送请求到: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
    
    response = requests.post(url, json=data, stream=True)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print("开始接收流式响应...")
    
    try:
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                print(f"收到原始数据: {line}")  # 打印原始数据
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        print("流式响应结束")
                        break
                    try:
                        parsed = json.loads(data)
                        print(f"解析后的数据: {json.dumps(parsed, ensure_ascii=False)}")  # 打印解析后的数据
                        if 'choices' in parsed and parsed['choices']:
                            content = parsed['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                print(f"内容: {content}", end='', flush=True)
                    except json.JSONDecodeError as e:
                        print(f"解析错误: {e}")
                        print(f"原始数据: {data}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    test_stream()
