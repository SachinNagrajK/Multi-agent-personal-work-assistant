import { useState } from 'react'
import { Sunrise, Mail, RefreshCw, Calendar, Play, Loader } from 'lucide-react'

function WorkflowPanel({ onExecuteWorkflow }) {
  const [executing, setExecuting] = useState(null)

  const workflows = [
    {
      id: 'morning_startup',
      name: 'Morning Startup',
      description: 'Triage emails, check calendar, prioritize tasks',
      icon: Sunrise,
      color: 'bg-orange-100 text-orange-600'
    },
    {
      id: 'email_triage',
      name: 'Email Triage',
      description: 'Analyze and draft responses for urgent emails',
      icon: Mail,
      color: 'bg-blue-100 text-blue-600'
    },
    {
      id: 'context_switch',
      name: 'Context Switch',
      description: 'Switch to a different project context',
      icon: RefreshCw,
      color: 'bg-purple-100 text-purple-600'
    },
    {
      id: 'meeting_prep',
      name: 'Meeting Prep',
      description: 'Prepare materials for upcoming meeting',
      icon: Calendar,
      color: 'bg-green-100 text-green-600'
    }
  ]

  const handleExecute = async (workflowType) => {
    setExecuting(workflowType)
    try {
      let parameters = {}
      
      // Get parameters for specific workflows
      if (workflowType === 'context_switch') {
        const projectName = prompt('Enter project name:', 'Project Phoenix')
        if (!projectName) {
          setExecuting(null)
          return
        }
        parameters = { project_name: projectName }
      } else if (workflowType === 'meeting_prep') {
        const meetingId = prompt('Enter meeting ID (leave empty for next meeting):')
        if (meetingId) {
          parameters = { meeting_id: meetingId }
        }
      }
      
      await onExecuteWorkflow(workflowType, parameters)
    } catch (error) {
      console.error('Workflow execution failed:', error)
      alert('Workflow execution failed. Check console for details.')
    } finally {
      setExecuting(null)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>

      {/* Workflow Cards */}
      <div className="space-y-4">
        {workflows.map((workflow) => {
          const Icon = workflow.icon
          const isExecuting = executing === workflow.id
          
          return (
            <div key={workflow.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${workflow.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{workflow.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{workflow.description}</p>
                  <button
                    onClick={() => handleExecute(workflow.id)}
                    disabled={isExecuting || executing !== null}
                    className={`btn-primary w-full flex items-center justify-center space-x-2 ${
                      (isExecuting || executing !== null) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {isExecuting ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        <span>Running...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        <span>Run Workflow</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Info Card */}
      <div className="card bg-gradient-to-br from-primary-50 to-blue-50 border border-primary-200">
        <h3 className="font-semibold text-gray-900 mb-2">How It Works</h3>
        <ul className="text-sm text-gray-700 space-y-2">
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 font-bold">1.</span>
            <span>Select a workflow above</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 font-bold">2.</span>
            <span>Watch agents collaborate in real-time</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 font-bold">3.</span>
            <span>Review and approve suggested actions</span>
          </li>
        </ul>
      </div>

      {/* Features Card */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3 text-sm">Powered By</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-gray-50 p-2 rounded">
            <p className="font-medium text-gray-700">LangGraph</p>
            <p className="text-gray-500">Multi-Agent</p>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <p className="font-medium text-gray-700">OpenAI</p>
            <p className="text-gray-500">GPT-4</p>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <p className="font-medium text-gray-700">Pinecone</p>
            <p className="text-gray-500">Memory</p>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <p className="font-medium text-gray-700">LangSmith</p>
            <p className="text-gray-500">Monitoring</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkflowPanel
