from typing import Dict, List
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv(Path(__file__).parent / ".env")


class PricingAgent:
    """
    Agent 定价助手
    分析竞品数据，生成定价建议
    """

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def analyze_competitor(self, product_info: Dict) -> Dict:
        """
        分析单个竞品，生成定价建议

        Args:
            product_info: 竞品信息（标题、价格、评分、评价数）

        Returns:
            定价建议（建议价格、策略、理由）
        """
        # 构建分析提示词
        prompt = self._build_prompt(product_info)

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
                            "content": "你是跨境电商定价专家，擅长竞品分析和定价策略"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7
                },
                timeout=60
            )

            result = response.json()
            analysis = result['choices'][0]['message']['content']

            # 解析 AI 回复，提取结构化数据
            return self._parse_analysis(analysis, product_info)

        except Exception as e:
            return {
                "error": str(e),
                "suggested_price": product_info.get("price", "0"),
                "strategy": "保守定价",
                "reasoning": "分析失败，建议参考竞品价格"
            }

    def _build_prompt(self, product_info: Dict) -> str:
        """构建分析提示词"""
        return f"""请分析以下竞品信息，给出定价建议：

【竞品信息】
- 商品标题: {product_info.get('title', '未知')}
- 当前售价: ${product_info.get('price', '0')}
- 用户评分: {product_info.get('rating', '0')} / 5
- 评价数量: {product_info.get('reviews', '0')}
- 平台: {product_info.get('platform', 'unknown')}

【任务】
1. 判断该商品的市场定位（高端/中端/低端）
2. 分析价格是否合理
3. 给出你的定价建议（具体金额）
4. 说明定价策略和理由

请按以下格式回复：
建议价格: $xx.xx
市场定位: xxxx
定价策略: xxxx
详细理由: xxxx"""

    def _parse_analysis(self, analysis: str, product_info: Dict) -> Dict:
        """解析 AI 分析结果"""
        lines = analysis.strip().split('\n')

        result = {
            "original_price": product_info.get("price", "0"),
            "suggested_price": self._extract_price_from_text(analysis) or product_info.get("price", "0"),
            "market_position": self._extract_line(lines, "市场定位") or "中端",
            "strategy": self._extract_line(lines, "定价策略") or "跟随定价",
            "reasoning": self._extract_line(lines, "详细理由") or analysis[:200],
            "full_analysis": analysis
        }

        return result

    def _extract_price_from_text(self, text: str) -> str:
        """从文本中提取价格"""
        import re
        # 匹配 $xx.xx 或 $x,xxx.xx
        match = re.search(r'\$?([\d,]+\.\d{2})', text)
        if match:
            return match.group(1).replace(',', '')
        return ""

    def _extract_line(self, lines: List[str], keyword: str) -> str:
        """提取包含关键词的行"""
        for line in lines:
            if keyword in line:
                # 提取冒号后的内容
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return ""


# 单例模式
_pricing_agent = None


def get_pricing_agent() -> PricingAgent:
    """获取定价 Agent 单例"""
    global _pricing_agent
    if _pricing_agent is None:
        _pricing_agent = PricingAgent()
    return _pricing_agent


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_product = {
        "title": "Apple 2023 MacBook Pro Laptop M2 Pro",
        "price": "2046.00",
        "rating": "4.7",
        "reviews": "483",
        "platform": "amazon"
    }

    agent = PricingAgent()
    result = agent.analyze_competitor(test_product)

    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))