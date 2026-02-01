import { Activity, CheckCircle, AlertCircle, Clock, Loader } from 'lucide-react'

const agentIcons = {
  email: '📧',
  calendar: '📅',
  document: '📄',
  task: '✅',
  context: '🧠',
  meeting: '🎤'
}

const agentColors = {
  email: 'text-blue-600',
  calendar: 'text-purple-600',
  document: 'text-green-600',
  task: 'text-orange-600',
  context: 'text-pink-600',
  meeting: 'text-indigo-600'
}

function AgentActivity({ actions }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'in_progress':
        return <Loader className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Agent Activity</h2>
        {actions.length > 0 && (
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Processing...</span>
          </div>
        )}
      </div>

      {/* Activity Feed */}
      <div className="card">
        {actions.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No agent activity yet</p>
            <p className="text-sm text-gray-400 mt-1">Start a workflow to see agents in action</p>
          </div>
        ) : (
          <div className="space-y-4">
            {actions.map((action, index) => (
              <div
                key={index}
                className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-200 transition-all hover:shadow-md"
              >
                <div className="flex-shrink-0 mt-0.5">
                  <span className="text-2xl">{agentIcons[action.agent_type] || '🤖'}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className={`font-medium ${agentColors[action.agent_type] || 'text-gray-700'}`}>
                      {action.agent_type?.toUpperCase() || 'AGENT'}
                    </p>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(action.status)}
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(action.timestamp)}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">
                    {action.action?.replace(/_/g, ' ')}
                  </p>
                  {action.result && (
                    <p className="text-xs text-gray-500 mt-1 bg-white px-2 py-1 rounded">
                      {action.result}
                    </p>
                  )}
                  {action.error && (
                    <p className="text-xs text-red-600 mt-1 bg-red-50 px-2 py-1 rounded">
                      Error: {action.error}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Agent Status Summary */}
      {actions.length > 0 && (
        <div className="card bg-primary-50 border border-primary-200">
          <h3 className="font-semibold text-gray-900 mb-3">Summary</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-gray-600">Total Actions</p>
              <p className="text-2xl font-bold text-gray-900">{actions.length}</p>
            </div>
            <div>
              <p className="text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-green-600">
                {actions.filter(a => a.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentActivity
