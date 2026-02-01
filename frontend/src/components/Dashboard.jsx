import { Mail, Calendar, CheckSquare, AlertCircle } from 'lucide-react'

function Dashboard({ data }) {
  if (!data) return null

  const getPriorityBadge = (priority) => {
    const badges = {
      urgent: 'badge-urgent',
      high: 'badge-high',
      medium: 'badge-medium',
      low: 'badge-low'
    }
    return badges[priority] || 'badge-medium'
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Today's Overview</h2>

      {/* Urgent Emails */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Mail className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900">Priority Emails</h3>
          </div>
          <span className="badge badge-urgent">{data.urgent_emails?.length || 0}</span>
        </div>
        <div className="space-y-3">
          {data.urgent_emails?.slice(0, 3).map((email) => (
            <div key={email.id} className="border-l-4 border-red-500 pl-3 py-2">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900 text-sm">{email.subject}</p>
                  <p className="text-xs text-gray-600 mt-1">From: {email.sender}</p>
                </div>
                <span className={`badge ${getPriorityBadge(email.priority)} ml-2`}>
                  {email.priority}
                </span>
              </div>
            </div>
          ))}
          {(!data.urgent_emails || data.urgent_emails.length === 0) && (
            <p className="text-sm text-gray-500 text-center py-4">No urgent emails</p>
          )}
        </div>
      </div>

      {/* Today's Meetings */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900">Today's Meetings</h3>
          </div>
          <span className="badge bg-blue-100 text-blue-800">
            {data.today_meetings?.length || 0}
          </span>
        </div>
        <div className="space-y-3">
          {data.today_meetings?.map((meeting) => (
            <div key={meeting.id} className="border-l-4 border-blue-500 pl-3 py-2">
              <p className="font-medium text-gray-900 text-sm">{meeting.title}</p>
              <div className="flex items-center justify-between mt-1">
                <p className="text-xs text-gray-600">
                  {formatTime(meeting.start_time)} - {formatTime(meeting.end_time)}
                </p>
                <p className="text-xs text-gray-500">{meeting.attendees?.length || 0} attendees</p>
              </div>
            </div>
          ))}
          {(!data.today_meetings || data.today_meetings.length === 0) && (
            <p className="text-sm text-gray-500 text-center py-4">No meetings today</p>
          )}
        </div>
      </div>

      {/* High Priority Tasks */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <CheckSquare className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900">Priority Tasks</h3>
          </div>
          <span className="badge badge-high">{data.high_priority_tasks?.length || 0}</span>
        </div>
        <div className="space-y-3">
          {data.high_priority_tasks?.map((task) => (
            <div key={task.id} className="border-l-4 border-orange-500 pl-3 py-2">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900 text-sm">{task.title}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`badge ${getPriorityBadge(task.priority)}`}>
                      {task.priority}
                    </span>
                    <span className="text-xs text-gray-600">{task.status}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {(!data.high_priority_tasks || data.high_priority_tasks.length === 0) && (
            <p className="text-sm text-gray-500 text-center py-4">No high priority tasks</p>
          )}
        </div>
      </div>

      {/* Pending Approvals */}
      {data.pending_approvals && data.pending_approvals.length > 0 && (
        <div className="card border-2 border-yellow-300 bg-yellow-50">
          <div className="flex items-center space-x-2 mb-3">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <h3 className="font-semibold text-gray-900">Pending Approvals</h3>
          </div>
          <p className="text-sm text-gray-700">
            {data.pending_approvals.length} items require your approval
          </p>
          <button className="mt-3 btn-primary w-full">
            Review Approvals
          </button>
        </div>
      )}
    </div>
  )
}

export default Dashboard
