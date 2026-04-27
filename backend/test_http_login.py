"""测试 HTTP 登录"""
import requests

url = 'http://127.0.0.1:8000/api/auth/login'
data = {'username': 'testuser', 'password': '123456'}

print(f'Testing login with: {data}')
try:
    resp = requests.post(url, json=data, timeout=10)
    print(f'Status: {resp.status_code}')
    print(f'Response: {resp.text}')
except Exception as e:
    print(f'Error: {e}')
