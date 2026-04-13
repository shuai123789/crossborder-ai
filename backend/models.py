"""
简化版数据持久化
用 JSON 文件存储商品记录
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class ProductStore:
    """商品数据存储（JSON文件）"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "products.json"
    
    def save(self, product: Dict) -> Dict:
        """保存商品记录"""
        record = {
            "id": self._generate_id(product["url"]),
            "url": product["url"],
            "title": product["title"],
            "price": product["price"],
            "rating": product["rating"],
            "reviews": product["reviews"],
            "platform": product["platform"],
            "created_at": datetime.now().isoformat()
        }
        
        # 读取现有数据
        products = self._load_all()
        
        # 更新或添加
        existing = [p for p in products if p["url"] == record["url"]]
        if existing:
            # 更新价格历史
            existing[0]["price_history"] = existing[0].get("price_history", [])
            existing[0]["price_history"].append({
                "price": record["price"],
                "time": record["created_at"]
            })
            existing[0]["price"] = record["price"]
            existing[0]["updated_at"] = record["created_at"]
        else:
            record["price_history"] = [{"price": record["price"], "time": record["created_at"]}]
            products.append(record)
        
        # 保存
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        return record
    
    def get_all(self) -> List[Dict]:
        """获取所有商品"""
        return self._load_all()
    
    def get_by_url(self, url: str) -> Dict:
        """根据URL获取商品"""
        products = self._load_all()
        for p in products:
            if p["url"] == url:
                return p
        return None
    
    def delete(self, url: str) -> bool:
        """删除商品记录"""
        products = self._load_all()
        products = [p for p in products if p["url"] != url]
        
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        return True
    
    def _load_all(self) -> List[Dict]:
        """加载所有数据"""
        if not self.db_file.exists():
            return []
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    
    def _generate_id(self, url: str) -> str:
        """生成唯一ID"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:8]


# 单例
_store = None

def get_store() -> ProductStore:
    global _store
    if _store is None:
        _store = ProductStore()
    return _store
