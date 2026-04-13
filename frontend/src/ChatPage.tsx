import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface KnowledgeFile {
  name: string
  size: number
  modified: number
}

export default function ChatPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<{role: string, content: string}[]>([])
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState<KnowledgeFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [buildingIndex, setBuildingIndex] = useState(false)
  const [showKnowledge, setShowKnowledge] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 加载文件列表
  const loadFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/knowledge/files`)
      if (res.data.success) {
        setFiles(res.data.files)
      }
    } catch (err) {
      console.error('加载文件列表失败', err)
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  // 处理文件上传
  const handleFile = async (file: File) => {
    // 只接受 txt 文件
    if (!file.name.endsWith('.txt')) {
      alert('请上传 .txt 文本文件')
      return
    }

    // 检查文件大小（最大 10MB）
    if (file.size > 10 * 1024 * 1024) {
      alert('文件大小不能超过 10MB')
      return
    }

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post(`${API_BASE}/api/knowledge/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (res.data.success) {
        alert('上传成功！')
        loadFiles()
      } else {
        alert('上传失败: ' + res.data.error)
      }
    } catch (err: any) {
      alert('上传失败: ' + (err.response?.data?.error || err.message))
    } finally {
      setUploading(false)
      setDragActive(false)
    }
  }

  // 点击上传
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await handleFile(file)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // 拖拽事件
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const file = e.dataTransfer.files?.[0]
    if (file) {
      await handleFile(file)
    }
  }, [])

  // 删除文件
  const deleteFile = async (filename: string) => {
    if (!confirm(`确定删除 ${filename} 吗？`)) return

    try {
      const res = await axios.delete(`${API_BASE}/api/knowledge/files/${encodeURIComponent(filename)}`)
      if (res.data.success) {
        loadFiles()
      } else {
        alert('删除失败: ' + res.data.error)
      }
    } catch (err: any) {
      alert('删除失败: ' + (err.response?.data?.error || err.message))
    }
  }

  // 构建索引
  const buildIndex = async () => {
    if (files.length === 0) {
      alert('请先上传知识库文件')
      return
    }

    setBuildingIndex(true)
    try {
      const res = await axios.post(`${API_BASE}/api/knowledge/build-index`)
      if (res.data.success) {
        alert('知识库索引构建成功！现在可以提问了')
      } else {
        alert('构建失败: ' + res.data.error)
      }
    } catch (err: any) {
      alert('构建失败: ' + (err.response?.data?.error || err.message))
    } finally {
      setBuildingIndex(false)
    }
  }

  // 发送消息
  const sendMessage = async () => {
    if (!question.trim()) return
    
    const currentQuestion = question
    setQuestion('')
    setLoading(true)
    
    setMessages(prev => [...prev, {role: 'user', content: currentQuestion}])
    
    try {
      const res = await axios.post(`${API_BASE}/api/chat`, {
        question: currentQuestion
      })
      setMessages(prev => [...prev, {role: 'assistant', content: res.data.answer}])
    } catch {
      setMessages(prev => [...prev, {role: 'assistant', content: '请求失败，请检查后端是否运行'}])
    }
    
    setLoading(false)
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/" className="text-gray-500 hover:text-gray-700">← 返回首页</Link>
              <h1 className="text-xl font-bold">🤖 RAG智能客服</h1>
            </div>
            <button
              onClick={() => setShowKnowledge(!showKnowledge)}
              className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-lg hover:bg-purple-200"
            >
              📚 知识库 ({files.length})
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：知识库管理 */}
          {showKnowledge && (
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold mb-4">知识库管理</h2>
                
                {/* 拖拽上传区域 */}
                <div 
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-lg p-6 text-center mb-4 cursor-pointer transition-all ${
                    dragActive 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleUpload}
                    accept=".txt"
                    className="hidden"
                  />
                  <div className="text-3xl mb-2">{uploading ? '⏳' : dragActive ? '📁' : '📄'}</div>
                  <p className="text-purple-600 font-medium">
                    {uploading ? '上传中...' : dragActive ? '松开以上传' : '点击或拖拽上传 .txt 文档'}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">支持 FAQ、售后政策等文本 · 最大 10MB</p>
                </div>

                {/* 文件列表 */}
                <div className="space-y-2 mb-4 max-h-64 overflow-y-auto">
                  {files.length === 0 ? (
                    <p className="text-gray-400 text-sm text-center py-4">暂无文档</p>
                  ) : (
                    files.map((file) => (
                      <div key={file.name} className="flex justify-between items-center p-3 bg-gray-50 rounded text-sm">
                        <div className="truncate flex-1">
                          <div className="font-medium truncate">{file.name}</div>
                          <div className="text-xs text-gray-400">
                            {formatSize(file.size)} · {formatTime(file.modified)}
                          </div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            deleteFile(file.name)
                          }}
                          className="text-red-400 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50"
                        >
                          ✕
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* 构建索引按钮 */}
                <button
                  onClick={buildIndex}
                  disabled={buildingIndex || files.length === 0}
                  className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {buildingIndex ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      构建中...
                    </span>
                  ) : (
                    '🔍 构建知识库索引'
                  )}
                </button>

                <p className="text-xs text-gray-400 mt-2">
                  上传文档后，点击构建索引即可开始智能问答
                </p>
              </div>
            </div>
          )}

          {/* 右侧：对话区域 */}
          <div className={showKnowledge ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <div className="bg-white rounded-xl shadow p-6">
              {/* 消息列表 */}
              <div className="h-96 overflow-y-auto border rounded-lg p-4 mb-4 bg-gray-50">
                {messages.length === 0 && (
                  <div className="text-center py-20 text-gray-400">
                    <div className="text-4xl mb-2">🤖</div>
                    <p>上传知识库文档，构建索引后开始对话</p>
                    <p className="text-sm mt-2">或点击右上角 📚 知识库 管理文档</p>
                  </div>
                )}
                {messages.map((m, i) => (
                  <div key={i} className={`mb-4 ${m.role === 'user' ? 'text-right' : ''}`}>
                    <span className={`inline-block p-3 rounded-lg max-w-[80%] ${
                      m.role === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-white border border-gray-200'
                    }`}>
                      {m.content}
                    </span>
                  </div>
                ))}
              </div>
              
              {/* 输入框 */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="输入问题，如：运费多少钱？"
                  className="flex-1 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={loading}
                  className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
                >
                  {loading ? '发送中...' : '发送'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
