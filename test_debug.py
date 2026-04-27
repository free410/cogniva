import requests

# Login
resp = requests.post('http://127.0.0.1:8000/api/auth/login', json={
    'username': 'testuser123',
    'password': 'password123'
})
token = resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Create conversation
resp = requests.post('http://127.0.0.1:8000/api/conversations', 
    headers=headers, json={'title': 'Debug Test'})
conv_id = resp.json().get('id')

# Send message
resp = requests.post(
    f'http://127.0.0.1:8000/api/conversations/{conv_id}/messages',
    headers=headers,
    json={'content': 'What is Python?', 'provider': 'deepseek', 'use_rag': False}
)

print(f'Status: {resp.status_code}')
print(f'Headers: {dict(resp.headers)}')
print(f'Content-Type: {resp.headers.get("content-type")}')

# Try different encodings
print('\n--- Raw response ---')
print(f'Raw bytes (first 100): {resp.content[:100]}')

# Try decoding with different encodings
for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
    try:
        text = resp.text
        print(f'\n{encoding} decoded: {text[:300]}')
    except Exception as e:
        print(f'{encoding} error: {e}')

# Check what we actually received
print('\n--- JSON response ---')
import json
try:
    data = resp.json()
    print(f'Keys: {list(data.keys())}')
    for key, value in data.items():
        if isinstance(value, str):
            print(f'{key}: {repr(value)[:200]}')
        else:
            print(f'{key}: {value}')
except Exception as e:
    print(f'JSON parse error: {e}')
    print(f'Response text: {resp.text[:500]}')
