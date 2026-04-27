import requests
import json

# 登录获取 token
login_resp = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
print('Login:', login_resp.status_code, login_resp.text[:300])

if login_resp.ok:
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 创建对话
    conv_resp = requests.post('http://127.0.0.1:8000/api/conversations', json={'title': 'Test'}, headers=headers)
    print('Create conv:', conv_resp.status_code, conv_resp.text[:300])
    
    if conv_resp.ok:
        conv_id = conv_resp.json()['id']
        
        # 测试流式消息
        print('Testing stream...')
        stream_resp = requests.post(
            f'http://127.0.0.1:8000/api/conversations/{conv_id}/messages/stream',
            json={'content': '你好', 'provider': 'deepseek'},
            headers={**headers, 'Accept': 'text/event-stream'},
            stream=True
        )
        
        full_content = ''
        citations = None
        evidence = None
        
        for line in stream_resp.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    data_str = line[5:].strip()
                    if data_str and data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            print('Chunk type:', data.get('type'), '| content:', str(data.get('content', ''))[:80])
                            if data.get('type') == 'chunk':
                                full_content += data.get('content', '')
                            elif data.get('type') == 'done':
                                citations = data.get('citations')
                                evidence = data.get('evidence')
                        except Exception as e:
                            print('Parse error:', e, 'data:', data_str[:100])
        
        print('\n=== FINAL ===')
        print('Full content:', full_content[:500] if full_content else '(empty)')
        print('Citations:', citations)
        print('Evidence:', evidence)
