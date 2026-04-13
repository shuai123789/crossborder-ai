import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
env_path = Path(__file__).parent / ".env"
print(f"加载 .env 文件: {env_path}")
print(f"文件存在: {env_path.exists()}")

load_dotenv(env_path)

api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key: {api_key[:10]}..." if api_key else "API Key: None")

# 测试文案生成
from copywriting_service import get_copywriting_service

service = get_copywriting_service()
print(f"服务 API Key: {service.api_key[:10]}..." if service.api_key else "服务 API Key: None")

result = service.generate(
    product_name="Wireless Bluetooth Headphones",
    key_points=["Active noise cancellation", "30-hour battery life"],
    keywords=["bluetooth headphones", "wireless"],
    platform="amazon",
    language="en",
    tone="professional"
)

print(f"\n生成结果:")
print(f"Title: {result.title}")
print(f"Description: {result.description[:100]}..." if result.description else "Description: (empty)")
print(f"Bullet Points: {result.bullet_points}")
