import { useState, useEffect } from 'react';
import axios from 'axios';

interface CopywritingResult {
  title: string;
  description: string;
  bullet_points: string[];
  hashtags: string[];
  seo_keywords: string[];
  platform: string;
  language: string;
}

interface HistoryItem {
  id: string;
  timestamp: number;
  productName: string;
  platform: string;
  language: string;
  result: CopywritingResult;
}

export default function CopywritingGenerator() {
  const [productName, setProductName] = useState('');
  const [keyPoints, setKeyPoints] = useState(['', '', '', '']);
  const [keywords, setKeywords] = useState('');
  const [platform, setPlatform] = useState('amazon');
  const [language, setLanguage] = useState('zh');
  const [tone, setTone] = useState('professional');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CopywritingResult | null>(null);
  const [copied, setCopied] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // 加载历史记录
  useEffect(() => {
    const saved = localStorage.getItem('copywriting_history');
    if (saved) {
      try {
        setHistory(JSON.parse(saved));
      } catch {
        console.error('Failed to parse history');
      }
    }
  }, []);

  // 保存历史记录
  const saveToHistory = (newResult: CopywritingResult) => {
    const newItem: HistoryItem = {
      id: Date.now().toString(),
      timestamp: Date.now(),
      productName,
      platform,
      language,
      result: newResult
    };
    const updated = [newItem, ...history].slice(0, 50); // 最多保存50条
    setHistory(updated);
    localStorage.setItem('copywriting_history', JSON.stringify(updated));
  };

  // 删除单条历史
  const deleteHistoryItem = (id: string) => {
    const updated = history.filter(item => item.id !== id);
    setHistory(updated);
    localStorage.setItem('copywriting_history', JSON.stringify(updated));
  };

  // 清空历史
  const clearHistory = () => {
    if (confirm('确定要清空所有历史记录吗？')) {
      setHistory([]);
      localStorage.removeItem('copywriting_history');
    }
  };

  // 加载历史记录到当前
  const loadHistoryItem = (item: HistoryItem) => {
    setProductName(item.productName);
    setPlatform(item.platform);
    setLanguage(item.language);
    setResult(item.result);
    setShowHistory(false);
  };

  const platforms = [
    { value: 'amazon', label: '亚马逊 Amazon', icon: '🛒' },
    { value: 'tiktok', label: 'TikTok Shop', icon: '📱' },
    { value: 'shopify', label: '独立站 Shopify', icon: '🏪' },
  ];

  const languages = [
    { value: 'en', label: 'English 英语' },
    { value: 'es', label: 'Español 西班牙语' },
    { value: 'fr', label: 'Français 法语' },
    { value: 'de', label: 'Deutsch 德语' },
    { value: 'it', label: 'Italiano 意大利语' },
    { value: 'zh', label: '中文' },
  ];

  const tones = [
    { value: 'professional', label: '专业正式', desc: '适合商务场景' },
    { value: 'casual', label: '轻松随意', desc: '像朋友推荐' },
    { value: 'hype', label: '促销 hype', desc: '制造紧迫感' },
    { value: 'story', label: '讲故事', desc: '情感共鸣' },
  ];

  const addKeyPoint = () => {
    setKeyPoints([...keyPoints, '']);
  };

  const removeKeyPoint = (index: number) => {
    setKeyPoints(keyPoints.filter((_, i) => i !== index));
  };

  const updateKeyPoint = (index: number, value: string) => {
    const newKeyPoints = [...keyPoints];
    newKeyPoints[index] = value;
    setKeyPoints(newKeyPoints);
  };

  const generateCopywriting = async () => {
    const filteredKeyPoints = keyPoints.filter(kp => kp.trim() !== '');
    if (!productName || filteredKeyPoints.length === 0) {
      alert('请填写商品名称和至少一个卖点');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('https://crossborder-ai.onrender.com/api/copywriting', {
        product_name: productName,
        key_points: filteredKeyPoints,
        keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
        platform,
        language,
        tone,
      });
      setResult(res.data);
      saveToHistory(res.data); // 保存到历史记录
    } catch (err: any) {
      alert('生成失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopied(field);
    setTimeout(() => setCopied(''), 2000);
  };

  const copyAll = () => {
    if (!result) return;
    const allText = `【标题】\n${result.title}\n\n【描述】\n${result.description}\n\n【卖点】\n${result.bullet_points.map(bp => '• ' + bp).join('\n')}\n\n【标签】\n${result.hashtags.join(' ')}\n\n【SEO关键词】\n${result.seo_keywords.join(', ')}`;
    copyToClipboard(allText, 'all');
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-2">
        <h1 className="text-3xl font-bold text-blue-600">✍️ AI商品文案工厂</h1>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm"
        >
          📜 历史记录 ({history.length})
        </button>
      </div>
      <p className="text-gray-500 mb-8">一键生成多平台、多语言、高质量商品文案</p>

      {/* 历史记录面板 */}
      {showHistory && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">历史记录</h2>
            {history.length > 0 && (
              <button
                onClick={clearHistory}
                className="text-red-500 text-sm hover:underline"
              >
                清空全部
              </button>
            )}
          </div>
          {history.length === 0 ? (
            <p className="text-gray-400 text-center py-4">暂无历史记录</p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded hover:bg-gray-100"
                >
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => loadHistoryItem(item)}
                  >
                    <div className="font-medium">{item.productName}</div>
                    <div className="text-xs text-gray-500">
                      {platforms.find(p => p.value === item.platform)?.label} · 
                      {languages.find(l => l.value === item.language)?.label} · 
                      {formatTime(item.timestamp)}
                    </div>
                  </div>
                  <button
                    onClick={() => deleteHistoryItem(item.id)}
                    className="text-red-400 hover:text-red-600 px-2"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 左侧：输入区域 */}
        <div className="space-y-6">
          {/* 平台选择 */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium mb-3">选择平台</label>
            <div className="grid grid-cols-3 gap-3">
              {platforms.map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPlatform(p.value)}
                  className={`p-3 rounded-lg border-2 text-center transition-all ${
                    platform === p.value
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{p.icon}</div>
                  <div className="text-sm font-medium">{p.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 语言和语气 */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">语言</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {languages.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">语气风格</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {tones.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {tones.find(t => t.value === tone)?.desc}
            </p>
          </div>

          {/* 商品信息 */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium mb-2">商品名称</label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="例如：无线蓝牙耳机"
              className="w-full border rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500"
            />

            <label className="block text-sm font-medium mb-2">产品卖点</label>
            <div className="space-y-2">
              {keyPoints.map((kp, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    value={kp}
                    onChange={(e) => updateKeyPoint(index, e.target.value)}
                    placeholder={`卖点 ${index + 1}`}
                    className="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  />
                  {keyPoints.length > 1 && (
                    <button
                      onClick={() => removeKeyPoint(index)}
                      className="px-3 py-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              onClick={addKeyPoint}
              className="mt-2 text-blue-600 text-sm hover:underline"
            >
              + 添加卖点
            </button>

            <label className="block text-sm font-medium mb-2 mt-4">SEO关键词（用逗号分隔）</label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="例如：蓝牙耳机, 无线, 降噪"
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* 生成按钮 */}
          <button
            onClick={generateCopywriting}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                生成中...
              </span>
            ) : (
              '🚀 生成文案'
            )}
          </button>
        </div>

        {/* 右侧：结果展示 */}
        <div>
          {result ? (
            <div className="bg-white rounded-lg shadow p-6 space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">生成结果</h2>
                <button
                  onClick={copyAll}
                  className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded transition-colors"
                >
                  {copied === 'all' ? '✅ 已复制' : '📋 复制全部'}
                </button>
              </div>

              {/* 标题 */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm font-medium text-gray-500">标题</label>
                  <button
                    onClick={() => copyToClipboard(result.title, 'title')}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {copied === 'title' ? '已复制' : '复制'}
                  </button>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-sm">{result.title}</div>
              </div>

              {/* 描述 */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm font-medium text-gray-500">描述</label>
                  <button
                    onClick={() => copyToClipboard(result.description, 'desc')}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {copied === 'desc' ? '已复制' : '复制'}
                  </button>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-sm whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {result.description}
                </div>
              </div>

              {/* 卖点 */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm font-medium text-gray-500">卖点</label>
                  <button
                    onClick={() => copyToClipboard(result.bullet_points.join('\n'), 'bullets')}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {copied === 'bullets' ? '已复制' : '复制'}
                  </button>
                </div>
                <ul className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                  {result.bullet_points.map((bp, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-blue-500">•</span>
                      <span>{bp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 标签 */}
              {result.hashtags.length > 0 && (
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-sm font-medium text-gray-500">标签</label>
                    <button
                      onClick={() => copyToClipboard(result.hashtags.join(' '), 'hashtags')}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      {copied === 'hashtags' ? '已复制' : '复制'}
                    </button>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3 text-sm">
                    {result.hashtags.map((tag, i) => (
                      <span key={i} className="inline-block bg-blue-100 text-blue-700 px-2 py-1 rounded mr-2 mb-2">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* SEO关键词 */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm font-medium text-gray-500">SEO关键词</label>
                  <button
                    onClick={() => copyToClipboard(result.seo_keywords.join(', '), 'seo')}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {copied === 'seo' ? '已复制' : '复制'}
                  </button>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
                  {result.seo_keywords.join(', ')}
                </div>
              </div>

              {/* 元信息 */}
              <div className="pt-4 border-t text-xs text-gray-400 flex gap-4">
                <span>平台: {platforms.find(p => p.value === result.platform)?.label}</span>
                <span>语言: {languages.find(l => l.value === result.language)?.label}</span>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg shadow p-12 text-center text-gray-400">
              <div className="text-6xl mb-4">✍️</div>
              <p>填写左侧信息，点击生成文案</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
