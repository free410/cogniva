"""测试注册和登录 API"""
import sys
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 测试注册
print("Testing register API...")
resp = client.post('/api/auth/register', json={'username': 'testuser456', 'password': '123456'})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Success! User: {data['user']['username']}")
    print(f"Token received: {data['access_token'][:30]}...")
else:
    print(f"Error: {resp.text}")

# 测试登录
print("\nTesting login API...")
resp = client.post('/api/auth/login', json={'username': 'testuser456', 'password': '123456'})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Success! User: {data['user']['username']}")
else:
    print(f"Error: {resp.text}")
