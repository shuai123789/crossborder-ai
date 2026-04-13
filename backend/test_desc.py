import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("DEEPSEEK_API_KEY")

prompt = """请为以下商品生成Chinese文案：

【商品名称】无线蓝牙耳机

【产品卖点】
- 主动降噪
- 30小时续航

【SEO关键词】耳机

【平台要求】亚马逊风格：专业、详细、SEO优化，突出产品功能和卖点
【语气风格】专业正式，适合商务场景

请按以下格式返回（使用Chinese）：

TITLE: [商品标题，不超过200字符]

DESCRIPTION: [商品描述，不超过2000字符]

BULLET_POINTS:
- [卖点1]
- [卖点2]
- [卖点3]
...

HASHTAGS:
#[标签1] #[标签2] ...

SEO_KEYWORDS:
[关键词1], [关键词2], ...
"""

response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional e-commerce copywriter. Write in Chinese."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }
)

content = response.json()['choices'][0]['message']['content']
print("=== AI 原始返回 ===")
print(content)
print("\n=== 检查 DESCRIPTION 行 ===")
for i, line in enumerate(content.split('\n')):
    if 'DESCRIPTION' in line or (i > 0 and 'DESCRIPTION' in content.split('\n')[i-1]):
        print(f"Line {i}: {repr(line)}")
