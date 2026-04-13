import { useState } from 'react';
import axios from 'axios';

interface ProductInfo {
  title: string;
  price: string;
  rating: string;
  reviews: string;
  platform: string;
  mock?: boolean;
}

interface PricingAdvice {
  suggested_price: string;
  market_position: string;
  strategy: string;
  reasoning: string;
}

export default function PricingAssistant() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');
  const [result, setResult] = useState<{
    product_info: ProductInfo;
    pricing_advice: PricingAdvice;
  } | null>(null);

  const saveProduct = async () => {
    if (!url) return;
    setSaving(true);
    setSaveMsg('');
    try {
      const res = await axios.post('https://crossborder-ai.onrender.com/api/save', {
        url: url
      });
      if (res.data.success) {
        setSaveMsg('✅ 保存成功');
      } else {
        setSaveMsg('❌ 保存失败: ' + res.data.error);
      }
    } catch (err) {
      setSaveMsg('❌ 网络错误');
    } finally {
      setSaving(false);
    }
  };

  const analyzePricing = async () => {
    if (!url) return;
    setLoading(true);
    try {
      const res = await axios.post('https://crossborder-ai.onrender.com/api/pricing', {
        url: url
      });
      setResult(res.data);
    } catch (err) {
      alert('分析失败: ' + err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6 text-blue-600">Agent定价助手</h1>
      
      {/* 输入区域 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <label className="block text-sm font-medium mb-2">商品链接</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.amazon.com/dp/..."
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            onClick={analyzePricing}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? '分析中...' : '分析定价'}
          </button>
          <button
            onClick={saveProduct}
            disabled={saving || !result}
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
          >
            {saving ? '保存中...' : '保存记录'}
          </button>
        </div>
      </div>

      {/* 保存消息 */}
      {saveMsg && (
        <div className={`p-3 rounded mb-4 ${saveMsg.includes('成功') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {saveMsg}
        </div>
      )}

      {/* 结果展示 */}
      {result && (
        <div className="space-y-6">
          {/* 竞品信息 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">竞品信息</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-gray-500">商品名称</span>
                <p className="font-medium">{result.product_info.title}</p>
                {result.product_info.mock && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Mock数据</span>
                )}
              </div>
              <div>
                <span className="text-gray-500">当前售价</span>
                <p className="text-2xl font-bold text-red-600">${result.product_info.price}</p>
              </div>
              <div>
                <span className="text-gray-500">评分</span>
                <p className="font-medium">⭐ {result.product_info.rating}</p>
              </div>
              <div>
                <span className="text-gray-500">评价数</span>
                <p className="font-medium">{result.product_info.reviews}</p>
              </div>
            </div>
          </div>

          {/* 定价建议 */}
          <div className="bg-green-50 rounded-lg shadow p-6 border border-green-200">
            <h2 className="text-lg font-semibold mb-4 text-green-800">AI定价建议</h2>
            <div className="space-y-3">
              <div>
                <span className="text-gray-600">建议售价</span>
                <p className="text-3xl font-bold text-green-600">${result.pricing_advice.suggested_price}</p>
              </div>
              <div>
                <span className="text-gray-600">市场定位</span>
                <p className="font-medium">{result.pricing_advice.market_position}</p>
              </div>
              <div>
                <span className="text-gray-600">定价策略</span>
                <p className="font-medium">{result.pricing_advice.strategy}</p>
              </div>
              <div>
                <span className="text-gray-600">策略说明</span>
                <p className="text-sm text-gray-700 mt-1">{result.pricing_advice.reasoning}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
