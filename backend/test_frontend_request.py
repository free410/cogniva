"""模拟前端请求测试"""
import requests

# 测试与前端完全相同的请求格式
url = 'http://127.0.0.1:8000/api/auth/login'
data = {'username': 'testuser', 'password': '123456'}

print('Sending request like frontend...')
resp = requests.post(
    url,
    json=data,
    headers={'Content-Type': 'application/json'},
    timeout=10
)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text}')

# 测试注册
print('\nTesting register...')
register_url = 'http://127.0.0.1:8000/api/auth/register'
new_user = {'username': 'newuser999', 'password': '123456'}
resp = requests.post(register_url, json=new_user, timeout=10)
print(f'Register Status: {resp.status_code}')
print(f'Response: {resp.text}')
