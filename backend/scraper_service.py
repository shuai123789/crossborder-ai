from playwright.sync_api import sync_playwright
import json
import re
from typing import Dict


class ScraperService:
    """
    竞品数据采集服务
    支持亚马逊商品信息抓取
    """
    
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    def _init_browser(self):
        """初始化浏览器（带反爬配置）"""
        if not self.browser:
            self.playwright = sync_playwright().start()
            
            # 启动参数，隐藏自动化特征
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
    
    def _close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
    
    def scrape_amazon(self, url: str) -> Dict:
        """
        抓取亚马逊商品信息
        
        Args:
            url: 亚马逊商品链接
            
        Returns:
            商品信息字典
        """
        self._init_browser()
        
        try:
            page = self.browser.new_page()
            
            # 设置更完整的请求头
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            })
            
            # 1. 先访问首页获取 Cookie
            print("访问亚马逊首页...")
            page.goto("https://www.amazon.com", wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            
            # 2. 再访问目标商品页
            print(f"正在访问: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 等待页面加载
            page.wait_for_timeout(3000)  # 基础等待3秒
            
            # 等待价格元素加载（JavaScript动态内容）
            try:
                page.wait_for_selector('.a-price', timeout=10000)
                print("✓ 价格元素已加载")
            except:
                print("✗ 等待价格元素超时")
            
            # 调试：保存截图
            try:
                page.screenshot(path="debug.png")
            except:
                pass
            
            # 提取商品信息
            product_info = {
                'url': url,
                'title': self._extract_title(page),
                'price': self._extract_price(page),
                'rating': self._extract_rating(page),
                'reviews': self._extract_reviews(page),
                'platform': 'amazon'
            }
            
            # 如果价格抓取失败，使用 Mock 数据
            if str(product_info['price']) in ['0', '0.0', '', 'None']:
                print("价格抓取失败，使用 Mock 数据")
                product_info['price'] = '199.00'
                product_info['mock'] = True  # 标记为 Mock 数据
            
            page.close()
            return product_info
            
        except Exception as e:
            print(f"抓取失败: {e}")
            return {'error': str(e), 'url': url}
            
        finally:
            self._close_browser()
    
    def _extract_title(self, page) -> str:
        """提取商品标题"""
        try:
            # 尝试多个选择器
            selectors = [
                '#productTitle',
                '[data-testid="product-title"]',
                'h1.a-size-large'
            ]
            for selector in selectors:
                element = page.query_selector(selector)
                if element:
                    return element.inner_text().strip()
            return "未知标题"
        except:
            return "未知标题"
    
    def _extract_price(self, page) -> str:
        """提取商品价格"""
        print("=== 开始提取价格 ===")  # 调试标记
        
        # 先截图看页面内容
        try:
            page.screenshot(path="price_debug.png")
            print("已保存截图: price_debug.png")
        except Exception as e:
            print(f"截图失败: {e}")
        
        # 打印页面HTML片段，看价格区域
        try:
            html_snippet = page.content()
            # 查找包含 $ 符号的文本
            prices_in_html = re.findall(r'\$[\d,]+\.?\d{0,2}', html_snippet[:50000])
            print(f"HTML中找到的价格文本: {prices_in_html[:5]}")
        except Exception as e:
            print(f"提取HTML失败: {e}")
        
        try:
            selectors = [
                '.a-price .a-offscreen',           # 标准价格
                '.a-price-range .a-offscreen',     # 价格区间
                '.a-price-to-pay .a-offscreen',    # 实际支付价
                '.a-price-buy-box .a-offscreen',   # 购买盒价格
                '[data-a-color="price"] .a-offscreen',  # 价格颜色标记
                '.a-price',                         # 价格容器本身
            ]

            for selector in selectors:
                try:
                    print(f"尝试选择器: {selector}")  # 调试
                    element = page.query_selector(selector)
                    if element:
                        price_text = element.inner_text().strip()
                        print(f"✓ 找到价格 [{selector}]: {price_text}")

                        # 匹配 $xx.xx 或 $x,xxx.xx
                        match = re.search(r'\$?([\d,]+(?:\.\d{2})?)', price_text)
                        if match:
                            price = match.group(1).replace(',', '')
                            if '.' not in price:
                                price += '.00'
                            return price
                    else:
                        print(f"✗ 选择器未找到元素: {selector}")
                except Exception as e:
                    print(f"选择器 {selector} 出错: {e}")
                    continue

            print("所有选择器都未找到价格")
            return "0"
        except Exception as e:
            print(f"提取价格出错: {e}")
            return "0"
    
    def _extract_rating(self, page) -> str:
        """提取评分"""
        try:
            selectors = [
                '[data-hook="average-star-rating"] .a-icon-alt',
                '.a-icon-star .a-icon-alt'
            ]
            for selector in selectors:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text()
                    match = re.search(r'(\d+\.?\d*)', text)
                    if match:
                        return match.group(1)
            return "0"
        except:
            return "0"
    
    def _extract_reviews(self, page) -> str:
        """提取评价数量"""
        try:
            selectors = [
                '[data-hook="total-review-count"]',
                '#acrCustomerReviewText'
            ]
            for selector in selectors:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text()
                    match = re.search(r'([\d,]+)', text)
                    if match:
                        return match.group(1).replace(',', '')
            return "0"
        except:
            return "0"

    # ========== 京东爬虫方法 ==========

    def scrape_jd(self, url: str) -> Dict:
        """
        抓取京东商品信息
        """
        self._init_browser()
        
        try:
            page = self.browser.new_page()
            
            # 设置请求头
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            })
            
            print(f"正在访问: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(5000)
            
            # 提取商品信息
            product_info = {
                'url': url,
                'title': self._extract_jd_title(page),
                'price': self._extract_jd_price(page),
                'rating': self._extract_jd_rating(page),
                'reviews': self._extract_jd_reviews(page),
                'platform': 'jd'
            }
            
            page.close()
            return product_info
            
        except Exception as e:
            print(f"抓取失败: {e}")
            return {'error': str(e), 'url': url}
        finally:
            self._close_browser()

    def _extract_jd_title(self, page) -> str:
        """提取京东商品标题"""
        try:
            selectors = ['#name h1', '.sku-name', 'h1']
            for selector in selectors:
                element = page.query_selector(selector)
                if element:
                    return element.inner_text().strip()
            return "未知标题"
        except:
            return "未知标题"

    def _extract_jd_price(self, page) -> str:
        """提取京东价格"""
        try:
            selectors = [
                '.price-now',
                '#jd-price',
                '.p-price .price',
                '[class*="price"]'
            ]
            for selector in selectors:
                element = page.query_selector(selector)
                if element:
                    price_text = element.inner_text().strip()
                    match = re.search(r'([\d.]+)', price_text)
                    if match:
                        return match.group(1)
            return "0"
        except:
            return "0"

    def _extract_jd_rating(self, page) -> str:
        """提取京东评分"""
        try:
            element = page.query_selector('.comment-score .score-num')
            if element:
                return element.inner_text().strip()
            return "0"
        except:
            return "0"

    def _extract_jd_reviews(self, page) -> str:
        """提取京东评价数"""
        try:
            element = page.query_selector('#comment-count')
            if element:
                text = element.inner_text()
                match = re.search(r'(\d+)', text.replace(',', ''))
                if match:
                    return match.group(1)
            return "0"
        except:
            return "0"


# 单例模式
_scraper_service = None


def get_scraper_service() -> ScraperService:
    """获取爬虫服务单例"""
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService()
    return _scraper_service


# 测试代码
if __name__ == "__main__":
    service = ScraperService()
    # 亚马逊测试链接
    test_url = "https://www.amazon.com/dp/B0CHWRXH8B"
    result = service.scrape_amazon(test_url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
