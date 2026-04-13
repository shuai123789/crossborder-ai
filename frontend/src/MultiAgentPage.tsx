import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API_BASE = 'https://crossborder-ai.onrender.com'

interface AgentTask {
  id: string
  description: string
  role: string
  status: string
}

interface AgentResult {
  success: boolean
  plan?: {
    intent: string
    tasks: AgentTask[]
    context: Record<string, any>
  }
  final_report?: string
  execution_time?: number
  error?: string
}

export default function MultiAgentPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AgentResult | null>(null)
  const [activeStep, setActiveStep] = useState(0)

  const agentSteps = [
    { role: 'planner', name: '规划 Agent', icon: '📋', desc: '拆解任务' },
    { role: 'retriever', name: '检索 Agent', icon: '🔍', desc: '获取知识' },
    { role: 'calculator', name: '计算 Agent', icon: '🧮', desc: '分析数据' },
    { role: 'generator', name: '生成 Agent', icon: '✍️', desc: '撰写报告' },
    { role: 'checker', name: '检查 Agent', icon: '✅', desc: '质量验证' },
  ]

  const runAnalysis = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    setResult(null)
    setActiveStep(0)
    
    // 模拟步骤动画
    for (let i = 0; i < agentSteps.length; i++) {
      setActiveStep(i)
      await new Promise(r => setTimeout(r, 800))
    }
    
    try {
      const res = await axios.post(`${API_BASE}/api/multi-agent/analyze`, {
        query: query
      })
      setResult(res.data)
      setActiveStep(agentSteps.length)
    } catch (err: any) {
      setResult({
        success: false,
        error: err.response?.data?.error || err.message
      })
    } finally {
      setLoading(false)
    }
  }

  const examples = [
    '帮我分析一下蓝牙耳机市场，我想定价30美元',
    '分析智能手表竞品，目标价格50美元',
    '评估充电宝市场，定价25美元是否合理',
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-gray-500 hover:text-gray-700">← 返回首页</Link>
            <h1 className="text-xl font-bold">🤖 Multi-Agent 智能分析</h1>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* 介绍 */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-3">
            Multi-Agent 协作定价分析
          </h2>
          <p className="text-gray-500 max-w-2xl mx-auto">
            5个专业 Agent 协作完成定价分析：规划 → 检索 → 计算 → 生成 → 检查
          </p>
        </div>

        {/* Agent 流程展示 */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <div className="flex justify-between items-center">
            {agentSteps.map((step, i) => (
              <div key={step.role} className="flex flex-col items-center flex-1">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl transition-all ${
                  i < activeStep ? 'bg-green-500 text-white' :
                  i === activeStep && loading ? 'bg-blue-500 text-white animate-pulse' :
                  'bg-gray-100 text-gray-400'
                }`}>
                  {i < activeStep ? '✓' : step.icon}
                </div>
                <p className="text-sm font-medium mt-2">{step.name}</p>
                <p className="text-xs text-gray-400">{step.desc}</p>
                {i < agentSteps.length - 1 && (
                  <div className={`absolute right-0 top-6 w-full h-0.5 transform translate-x-1/2 ${
                    i < activeStep ? 'bg-green-500' : 'bg-gray-200'
                  }`} style={{width: '60%', left: '70%'}} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 输入区域 */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <label className="block text-sm font-medium mb-2">输入您的定价分析问题</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="例如：帮我分析一下蓝牙耳机市场，我想定价30美元"
            className="w-full border rounded-lg px-4 py-3 h-24 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex justify-between items-center mt-4">
            <div className="text-sm text-gray-500">
              示例：
              {examples.map((ex, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(ex)}
                  className="ml-2 text-blue-500 hover:underline"
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <button
              onClick={runAnalysis}
              disabled={loading || !query.trim()}
              className="bg-blue-600 text-white px-8 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {loading ? '分析中...' : '开始分析'}
            </button>
          </div>
        </div>

        {/* 执行结果 */}
        {result && (
          <div className="space-y-6">
            {/* 执行信息 */}
            <div className="bg-white rounded-xl shadow p-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">执行结果</h3>
                <div className="flex items-center gap-4">
                  {result.execution_time && (
                    <span className="text-sm text-gray-500">
                      执行时间: {result.execution_time}s
                    </span>
                  )}
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    result.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {result.success ? '成功' : '失败'}
                  </span>
                </div>
              </div>
            </div>

            {/* 任务计划 */}
            {result.plan && (
              <div className="bg-white rounded-xl shadow p-6">
                <h3 className="text-lg font-semibold mb-4">执行计划</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-gray-500">用户意图</span>
                    <p className="font-medium">{result.plan.intent}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">产品类别</span>
                    <p className="font-medium">{result.plan.context?.product_category || '-'}</p>
                  </div>
                </div>
                <div className="mt-4">
                  <span className="text-gray-500">任务列表</span>
                  <div className="mt-2 space-y-2">
                    {result.plan.tasks?.map((task, i) => (
                      <div key={task.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                        <span className="text-blue-500 font-mono">{i + 1}</span>
                        <span className="flex-1">{task.description}</span>
                        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                          {task.role}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* 最终报告 */}
            {result.final_report && (
              <div className="bg-green-50 rounded-xl shadow p-6 border border-green-200">
                <h3 className="text-lg font-semibold mb-4 text-green-800">📊 定价分析报告</h3>
                <div className="prose max-w-none whitespace-pre-wrap text-gray-700">
                  {result.final_report}
                </div>
              </div>
            )}

            {/* 错误信息 */}
            {result.error && (
              <div className="bg-red-50 rounded-xl shadow p-6 border border-red-200">
                <h3 className="text-lg font-semibold mb-2 text-red-800">错误</h3>
                <p className="text-red-600">{result.error}</p>
              </div>
            )}
          </div>
        )}

        {/* 技术说明 */}
        <div className="mt-12 bg-gray-100 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">技术架构</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-2">Agent 设计模式</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• ReAct (Reasoning + Acting)</li>
                <li>• 任务规划与拆解</li>
                <li>• 工具调用 (Function Calling)</li>
                <li>• 多 Agent 消息通信</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">技术栈</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• DeepSeek API (LLM)</li>
                <li>• FastAPI (后端)</li>
                <li>• React + TypeScript (前端)</li>
                <li>• 自定义 Agent 框架</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
