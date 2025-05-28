import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

print("CLAUDE_API_KEY:", os.getenv("CLAUDE_API_KEY"))
print("CLAUDE_BASE_URL:", os.getenv("CLAUDE_BASE_URL"))
print("当前工作目录:", os.getcwd())