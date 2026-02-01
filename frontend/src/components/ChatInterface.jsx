import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Mail, Calendar, Clock, CheckSquare, Zap, TrendingUp, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hi! I\'m your AI workspace assistant. I can help you with:\n\n• 📧 Email management (read, send, search, triage)\n• 📅 Calendar scheduling (view, create, find time slots)\n• ✅ Task organization\n• 📊 Daily briefings and insights\n\nTry asking me things like:\n- "What unread emails do I have?"\n- "Schedule a meeting with Sarah tomorrow at 2pm"\n- "Give me my daily briefing"\n- "Reply to John\'s latest email"',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE}/ai/chat`, {
        message: input
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        stats: response.data.stats
      }

      setMessages(prev => [...prev, assistantMessage])
      
      if (response.data.stats) {
        setStats(response.data.stats)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage = {
        role: 'assistant',
        content: `❌ Sorry, I encountered an error: ${error.response?.data?.detail || error.message}. Please try again.`,
        timestamp: new Date(),
        isError: true
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickActions = [
    {
      icon: <Mail className="w-4 h-4" />,
      label: 'Check Emails',
      prompt: 'What unread emails do I have?'
    },
    {
      icon: <Calendar className="w-4 h-4" />,
      label: 'Today\'s Schedule',
      prompt: 'Show me my schedule for today'
    },
    {
      icon: <TrendingUp className="w-4 h-4" />,
      label: 'Daily Brief',
      prompt: 'Give me my daily briefing'
    },
    {
      icon: <Zap className="w-4 h-4" />,
      label: 'Triage Inbox',
      prompt: 'Triage my emails and tell me what needs attention'
    }
  ]

  const useQuickAction = (prompt) => {
    setInput(prompt)
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Workspace Assistant</h1>
              <p className="text-sm text-gray-500">Powered by LangGraph Multi-Agent System</p>
            </div>
          </div>
          
          {stats && (
            <div className="flex gap-4 text-sm">
              <div className="text-center">
                <div className="text-gray-500">Agents Used</div>
                <div className="font-bold text-blue-600">{stats.agents_used || 0}</div>
              </div>
              <div className="text-center">
                <div className="text-gray-500">Actions</div>
                <div className="font-bold text-green-600">{stats.total_actions || 0}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      {messages.length <= 2 && (
        <div className="max-w-5xl mx-auto w-full px-6 py-4">
          <div className="grid grid-cols-4 gap-3">
            {quickActions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => useQuickAction(action.prompt)}
                className="flex items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all text-left group"
              >
                <div className="text-blue-500 group-hover:text-blue-600">
                  {action.icon}
                </div>
                <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
                  {action.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-5xl mx-auto space-y-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.isError ? 'bg-red-100' : 'bg-gradient-to-br from-blue-500 to-purple-600'
                  }`}>
                    {message.isError ? (
                      <AlertCircle className="w-5 h-5 text-red-600" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>
                </div>
              )}
              
              <div className={`max-w-3xl ${message.role === 'user' ? 'order-first' : ''}`}>
                <div className={`rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                    : message.isError
                    ? 'bg-red-50 text-red-900 border border-red-200'
                    : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
                }`}>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {message.stats && (
                    <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500 flex gap-4">
                      <span>🤖 {message.stats.agents_used} agents</span>
                      <span>⚡ {message.stats.total_actions} actions</span>
                    </div>
                  )}
                </div>
                
                <div className="text-xs text-gray-400 mt-1 px-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
              
              {message.role === 'user' && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <User className="w-5 h-5 text-gray-600" />
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="flex gap-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white animate-pulse" />
                </div>
              </div>
              <div className="bg-white rounded-2xl px-4 py-3 border border-gray-200">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything... (e.g., 'Reply to Sarah's email about the meeting')"
              className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
              rows="3"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2 font-medium"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
          
          <div className="mt-2 text-xs text-gray-500 text-center">
            💡 Tip: Ask me to check emails, schedule meetings, or get your daily briefing
          </div>
        </div>
      </div>
    </div>
  )
}
