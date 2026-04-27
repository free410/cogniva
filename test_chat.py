import requests
import time

# Login with the new user
resp = requests.post('http://127.0.0.1:8000/api/auth/login', json={
    'username': 'testuser123',
    'password': 'password123'
})
print(f'Login status: {resp.status_code}')
if resp.status_code != 200:
    print(f'Login error: {resp.text}')
    exit(1)

data = resp.json()
token = data.get('access_token', '')
print(f'Token obtained: {token[:50]}...')

headers = {'Authorization': f'Bearer {token}'}

# Create a conversation
resp = requests.post('http://127.0.0.1:8000/api/conversations', 
    headers=headers, json={'title': 'Test Chat'})
print(f'\nCreate conversation status: {resp.status_code}')
if resp.status_code != 200:
    print(f'Create error: {resp.text}')
    exit(1)

conv_data = resp.json()
conv_id = conv_data.get('id')
print(f'Conversation ID: {conv_id}')

# Send a simple message
print('\nSending message: "What is Python?"')
resp = requests.post(
    f'http://127.0.0.1:8000/api/conversations/{conv_id}/messages',
    headers=headers,
    json={'content': 'What is Python?', 'provider': 'deepseek', 'use_rag': False}
)
print(f'Send message status: {resp.status_code}')

if resp.status_code == 200:
    msg_data = resp.json()
    content = msg_data.get('content', '')
    if content:
        print(f'\n=== SUCCESS! ===')
        print(f'Response: {content[:500]}...')
    else:
        print(f'Response has no content.')
        print(f'Full response: {msg_data}')
else:
    print(f'Error: {resp.text}')

# Test with streaming
print('\n\n--- Testing Stream ---')
print('Creating new conversation...')
resp = requests.post('http://127.0.0.1:8000/api/conversations', 
    headers=headers, json={'title': 'Stream Test'})
conv_id = resp.json().get('id')
print(f'Conversation ID: {conv_id}')

print('Sending streaming message...')
try:
    with requests.post(
        f'http://127.0.0.1:8000/api/conversations/{conv_id}/messages/stream',
        headers=headers,
        json={'content': 'What is JavaScript?', 'provider': 'deepseek', 'use_rag': False},
        stream=True
    ) as resp:
        print(f'Stream status: {resp.status_code}')
        if resp.status_code == 200:
            full_content = ''
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str == '[DONE]':
                            break
                        import json
                        try:
                            data = json.loads(data_str)
                            if data.get('type') == 'chunk':
                                full_content += data.get('content', '')
                        except:
                            pass
            print(f'\n=== STREAM SUCCESS! ===')
            print(f'Response: {full_content[:300]}...')
        else:
            print(f'Error: {resp.text[:200]}')
except Exception as e:
    print(f'Stream error: {e}')
