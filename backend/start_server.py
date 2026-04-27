"""
简单的服务器启动脚本
双击运行此文件启动服务器
"""
import subprocess
import sys
import os

# 确保在正确的目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 启动命令
cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]

print("Starting server...")
print(f"Command: {' '.join(cmd)}")
print("Press Ctrl+C to stop")

try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\nServer stopped.")
