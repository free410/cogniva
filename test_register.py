import requests

# Try to register a new user
print("Trying to register...")
resp = requests.post('http://127.0.0.1:8000/api/auth/register', json={
    'username': 'testuser123',
    'email': 'testuser123@example.com',
    'password': 'password123'
})
print(f'Register status: {resp.status_code}')
print(f'Register response: {resp.text}')

# Check if there's a user creation endpoint
print("\nTrying to check users...")
resp = requests.get('http://127.0.0.1:8000/api/users')
print(f'Users status: {resp.status_code}')
print(f'Users response: {resp.text[:200] if resp.text else "empty"}')
