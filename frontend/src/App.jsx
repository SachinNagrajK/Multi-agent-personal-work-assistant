import { useState, useEffect } from 'react'
import axios from 'axios'
import Dashboard from './components/Dashboard'
import AgentActivity from './components/AgentActivity'
import WorkflowPanel from './components/WorkflowPanel'
import { Bot, Mail, Calendar, CheckSquare, FileText } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

function App() {
  const [dashboardData, setDashboardData] = useState(null)
  const [agentActions, setAgentActions] = useState([])
  const [loading, setLoading] = useState(true)
  const [ws, setWs] = useState(null)

  useEffect(() => {
    loadDashboard()
    connectWebSocket()
    
    return () => {
      if (ws) ws.close()
    }
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API_BASE}/dashboard`)
      setDashboardData(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      setLoading(false)
    }
  }

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    
    const websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'workflow_progress') {
        setAgentActions(data.agent_actions || [])
      }
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000)
    }
    
    setWs(websocket)
  }

  const handleWorkflowExecute = async (workflowType, parameters = {}) => {
    try {
      setAgentActions([])
      const response = await axios.post(`${API_BASE}/workflow/execute`, {
        workflow_type: workflowType,
        parameters
      })
      
      console.log('Workflow result:', response.data)
      
      // Reload dashboard after workflow
      setTimeout(loadDashboard, 1000)
      
      return response.data
    } catch (error) {
      console.error('Error executing workflow:', error)
      throw error
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Bot className="w-16 h-16 text-primary-600 animate-pulse mx-auto mb-4" />
          <p className="text-gray-600">Loading Workspace Assistant...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bot className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Workspace Assistant</h1>
                <p className="text-sm text-gray-500">AI-Powered Productivity System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Agents Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Workflows */}
          <div className="lg:col-span-1">
            <WorkflowPanel onExecuteWorkflow={handleWorkflowExecute} />
          </div>

          {/* Middle Column - Dashboard */}
          <div className="lg:col-span-1">
            <Dashboard data={dashboardData} />
          </div>

          {/* Right Column - Agent Activity */}
          <div className="lg:col-span-1">
            <AgentActivity actions={agentActions} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>Powered by LangGraph, OpenAI, and Pinecone</p>
            <div className="flex items-center space-x-4">
              <span>Multi-Agent Orchestration</span>
              <span>•</span>
              <span>Human-in-Loop</span>
              <span>•</span>
              <span>Guardrails</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
