import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import PricingAssistant from './PricingAssistant'
import CopywritingGenerator from './CopywritingGenerator'
import ChatPage from './ChatPage'
import MultiAgentPage from './MultiAgentPage'

const API_BASE = 'http://localhost:8000'

// ========== 功能卡片组件 ==========
function FeatureCard({ 
  icon, 
  title, 
  desc, 
  features,
  to,
  color 
}: { 
  icon: string
  title: string
  desc: string
  features: string[]
  to: string
  color: string
}) {
  const navigate = useNavigate()
  
  return (
    <div 
      onClick={() => navigate(to)}
      className={`bg-white rounded-xl shadow-lg p-6 cursor-pointer transition-all hover:shadow-xl hover:scale-105 border-l-4 ${color}`}
    >
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-500 text-sm mb-4">{desc}</p>
      <ul className="space-y-1">
        {features.map((f, i) => (
          <li key={i} className="text-xs text-gray-400 flex items-center gap-1">
            <span className="text-green-500">✓</span> {f}
          </li>
        ))}
      </ul>
    </div>
  )
}

// ========== Dashboard 首页 ==========
function Dashboard() {
  const [message, setMessage] = useState('')
  const [health, setHealth] = useState('')

  useEffect(() => {
    axios.get(`${API_BASE}/`)
      .then(res => setMessage(res.data.message))
      .catch(() => setMessage('连接失败'))

    axios.get(`${API_BASE}/health`)
      .then(res => setHealth(res.data.status))
      .catch(() => setHealth('error'))
  }, [])

  const features = [
    {
      icon: '🤖',
      title: 'RAG智能客服',
      desc: '基于知识库的智能问答系统',
      features: ['上传文档', '智能检索', '多轮对话'],
      to: '/chat',
      color: 'border-purple-500'
    },
    {
      icon: '💰',
      title: '竞品定价助手',
      desc: '自动抓取竞品并AI分析定价',
      features: ['亚马逊/京东抓取', 'AI定价建议', '价格追踪'],
      to: '/pricing',
      color: 'border-green-500'
    },
    {
      icon: '✍️',
      title: 'AI文案工厂',
      desc: '一键生成多平台多语言文案',
      features: ['6种语言', '3大平台', '历史记录'],
      to: '/copywriting',
      color: 'border-blue-500'
    },
    {
      icon: '🎯',
      title: 'Multi-Agent分析',
      desc: '多Agent协作智能定价分析',
      features: ['5个Agent协作', '任务规划', '质量检查'],
      to: '/multi-agent',
      color: 'border-orange-500'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">跨境智卖</h1>
              <p className="text-sm text-gray-500">AI跨境电商运营助手</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${health === 'ok' ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span className="text-xs text-gray-500">
                {health === 'ok' ? '服务正常' : '连接异常'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Welcome */}
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-gray-800 mb-3">
            让 AI 帮你做跨境电商
          </h2>
          <p className="text-gray-500 max-w-2xl mx-auto">
            集成智能客服、竞品分析、文案生成、Multi-Agent 分析四大功能，
            帮助卖家提升运营效率，降低人力成本
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {features.map((f, i) => (
            <FeatureCard key={i} {...f} />
          ))}
        </div>

        {/* Stats */}
        <div className="bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold mb-4">项目概况</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">4</div>
              <div className="text-xs text-gray-500">核心功能</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">6</div>
              <div className="text-xs text-gray-500">支持语言</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">3</div>
              <div className="text-xs text-gray-500">电商平台</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">5</div>
              <div className="text-xs text-gray-500">协作Agent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">AI</div>
              <div className="text-xs text-gray-500">DeepSeek驱动</div>
            </div>
          </div>
        </div>


      </main>
    </div>
  )
}

// ========== 定价助手页面 ==========
function PricingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-gray-500 hover:text-gray-700">← 返回首页</Link>
            <h1 className="text-xl font-bold">💰 竞品定价助手</h1>
          </div>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-6">
        <PricingAssistant />
      </main>
    </div>
  )
}

// ========== 文案工厂页面 ==========
function CopywritingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-gray-500 hover:text-gray-700">← 返回首页</Link>
            <h1 className="text-xl font-bold">✍️ AI文案工厂</h1>
          </div>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-6">
        <CopywritingGenerator />
      </main>
    </div>
  )
}

// ========== 主应用 ==========
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/copywriting" element={<CopywritingPage />} />
        <Route path="/multi-agent" element={<MultiAgentPage />} />
      </Routes>
    </Router>
  )
}

export default App
