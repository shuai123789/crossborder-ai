"""
AI文案生成服务 - 多语言商品描述生成
"""

import os
import requests
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CopywritingResult:
    """文案生成结果"""
    title: str
    description: str
    bullet_points: List[str]
    hashtags: List[str]
    seo_keywords: List[str]
    platform: str
    language: str


class CopywritingService:
    """文案生成服务"""

    # 平台风格提示词
    PLATFORM_PROMPTS = {
        "amazon": {
            "style": "亚马逊风格：专业、详细、SEO优化，突出产品功能和卖点",
            "max_title": 200,
            "max_desc": 2000,
            "bullet_count": 5
        },
        "tiktok": {
            "style": "TikTok风格：简短、有趣、有冲击力，适合短视频带货",
            "max_title": 100,
            "max_desc": 300,
            "bullet_count": 3
        },
        "shopify": {
            "style": "独立站风格：品牌故事感、情感共鸣、转化率优化",
            "max_title": 150,
            "max_desc": 1500,
            "bullet_count": 4
        }
    }

    # 语言映射
    LANGUAGE_MAP = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "zh": "Chinese"
    }

    # 语气风格
    TONE_PROMPTS = {
        "professional": "专业正式，适合商务场景",
        "casual": "轻松随意，像朋友推荐",
        "hype": "促销感强，制造紧迫感",
        "story": "讲故事风格，情感共鸣"
    }

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def generate(
            self,
            product_name: str,
            key_points: List[str],
            keywords: List[str],
            platform: str = "amazon",
            language: str = "en",
            tone: str = "professional"
    ) -> CopywritingResult:
        """
        生成商品文案

        Args:
            product_name: 商品名称
            key_points: 产品卖点列表
            keywords: SEO关键词列表
            platform: 平台类型 (amazon/tiktok/shopify)
            language: 语言代码 (en/es/fr/de/it/zh)
            tone: 语气风格 (professional/casual/hype/story)
        """

        platform_config = self.PLATFORM_PROMPTS.get(platform, self.PLATFORM_PROMPTS["amazon"])
        lang_name = self.LANGUAGE_MAP.get(language, "English")
        tone_desc = self.TONE_PROMPTS.get(tone, self.TONE_PROMPTS["professional"])

        # 构建提示词
        prompt = self._build_prompt(
            product_name=product_name,
            key_points=key_points,
            keywords=keywords,
            platform_config=platform_config,
            lang_name=lang_name,
            tone_desc=tone_desc
        )

        # 调用 DeepSeek API
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a professional e-commerce copywriter. Write in {lang_name}."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000
                },
                timeout=60
            )

            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']

            # 解析返回结果
            return self._parse_response(content, platform, language)

        except Exception as e:
            # 返回错误信息包装的结果
            return CopywritingResult(
                title=f"Error: {str(e)}",
                description="",
                bullet_points=[],
                hashtags=[],
                seo_keywords=keywords,
                platform=platform,
                language=language
            )

    def _build_prompt(
            self,
            product_name: str,
            key_points: List[str],
            keywords: List[str],
            platform_config: Dict,
            lang_name: str,
            tone_desc: str
    ) -> str:
        """构建生成提示词"""

        key_points_text = "\n".join([f"- {p}" for p in key_points])
        keywords_text = ", ".join(keywords)

        prompt = f"""请为以下商品生成{lang_name}文案：

【商品名称】{product_name}

【产品卖点】
{key_points_text}

【SEO关键词】{keywords_text}

【平台要求】{platform_config['style']}
【语气风格】{tone_desc}

请按以下格式返回（使用{lang_name}）：

TITLE: [商品标题，不超过{platform_config['max_title']}字符]

DESCRIPTION: [商品描述，不超过{platform_config['max_desc']}字符]

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
        return prompt

    def _parse_response(self, content: str, platform: str, language: str) -> CopywritingResult:
        """解析 API 返回的文本"""

        lines = content.strip().split('\n')

        title = ""
        description = ""
        bullet_points = []
        hashtags = []
        seo_keywords = []

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别各个部分
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                current_section = "title"
            elif line.startswith("DESCRIPTION:"):
                # DESCRIPTION: 可能在同一行，也可能在下一行
                desc_content = line.replace("DESCRIPTION:", "").strip()
                if desc_content:
                    description = desc_content
                current_section = "description"
            elif line.startswith("BULLET_POINTS:"):
                current_section = "bullet"
            elif line.startswith("HASHTAGS:"):
                current_section = "hashtags"
            elif line.startswith("SEO_KEYWORDS:"):
                seo_keywords = [k.strip() for k in line.replace("SEO_KEYWORDS:", "").split(",") if k.strip()]
                current_section = "seo"
            elif current_section == "description":
                # 描述内容（多行）
                if description:
                    description += " " + line
                else:
                    description = line
            elif line.startswith("- ") and current_section == "bullet":
                bullet_points.append(line[2:].strip())
            elif line.startswith("#") and current_section == "hashtags":
                # 提取 hashtags
                tags = [t.strip() for t in line.split() if t.startswith("#")]
                hashtags.extend(tags)

        return CopywritingResult(
            title=title,
            description=description.strip(),
            bullet_points=bullet_points,
            hashtags=hashtags,
            seo_keywords=seo_keywords,
            platform=platform,
            language=language
        )


# 单例模式
_copywriting_service = None


def get_copywriting_service() -> CopywritingService:
    """获取文案生成服务实例"""
    global _copywriting_service
    if _copywriting_service is None:
        _copywriting_service = CopywritingService()
    return _copywriting_service


# 快速测试
if __name__ == "__main__":
    service = CopywritingService()
    result = service.generate(
        product_name="Wireless Bluetooth Headphones",
        key_points=[
            "Active noise cancellation",
            "30-hour battery life",
            "Comfortable over-ear design",
            "Hi-res audio quality"
        ],
        keywords=["bluetooth headphones", "wireless", "noise cancelling", "over ear"],
        platform="amazon",
        language="en",
        tone="professional"
    )

    print(f"Title: {result.title}")
    print(f"\nDescription: {result.description}")
    print(f"\nBullet Points: {result.bullet_points}")
    print(f"\nHashtags: {result.hashtags}")