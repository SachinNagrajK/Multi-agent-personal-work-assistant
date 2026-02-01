function StatsPanel({ contextStats, guardrailsStatus, onRefresh }) {
  return (
    <div className="space-y-4">
      {/* Context Stats */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold">📊 Context Stats</h3>
          <button
            onClick={onRefresh}
            className="text-purple-400 hover:text-purple-300 transition-colors"
          >
            🔄
          </button>
        </div>
        {contextStats ? (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-sm">Total Messages</span>
              <span className="text-white font-semibold">{contextStats.total_messages || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-sm">Context Length</span>
              <span className="text-white font-semibold">{contextStats.context_length || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-sm">Summarized</span>
              <span className={`font-semibold ${contextStats.is_summarized ? 'text-green-400' : 'text-slate-400'}`}>
                {contextStats.is_summarized ? 'Yes' : 'No'}
              </span>
            </div>
            {contextStats.summary_length > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Summary Length</span>
                <span className="text-white font-semibold">{contextStats.summary_length}</span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-slate-400 text-sm">Loading stats...</p>
        )}
      </div>

      {/* Guardrails Status */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-6">
        <h3 className="text-white font-semibold mb-4">🛡️ Safety Guardrails</h3>
        {guardrailsStatus ? (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-sm">Total Actions</span>
              <span className="text-white font-semibold">{guardrailsStatus.total_actions || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-sm">Blocked Actions</span>
              <span className={`font-semibold ${(guardrailsStatus.blocked_actions || 0) > 0 ? 'text-red-400' : 'text-green-400'}`}>
                {guardrailsStatus.blocked_actions || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-sm">Triggered Rules</span>
              <span className="text-white font-semibold">{guardrailsStatus.triggered_guardrails?.length || 0}</span>
            </div>
            
            {/* Rate Limits */}
            {guardrailsStatus.rate_limits && (
              <div className="mt-4 pt-4 border-t border-slate-700">
                <p className="text-slate-400 text-xs mb-2">Rate Limits:</p>
                {Object.entries(guardrailsStatus.rate_limits).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center text-xs mb-1">
                    <span className="text-slate-500">{key}</span>
                    <span className="text-slate-300">{value.used || 0} / {value.limit}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-slate-400 text-sm">Loading status...</p>
        )}
      </div>

      {/* System Info */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-6">
        <h3 className="text-white font-semibold mb-4">ℹ️ System Info</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            <span className="text-slate-300">Backend Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            <span className="text-slate-300">Gmail Connected</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            <span className="text-slate-300">Calendar Connected</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <p className="text-slate-400 text-xs">
              LangGraph • GPT-4 • ReAct Agents
            </p>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-6">
        <h3 className="text-white font-semibold mb-4">✨ Active Features</h3>
        <div className="space-y-2">
          {[
            { icon: '🤖', name: 'Multi-Agent', active: true },
            { icon: '👤', name: 'Human-in-Loop', active: true },
            { icon: '🛡️', name: 'Guardrails', active: true },
            { icon: '📝', name: 'Auto-Summary', active: true },
            { icon: '🔄', name: 'Loop Prevention', active: true },
            { icon: '⏱️', name: 'Rate Limiting', active: true }
          ].map((feature, index) => (
            <div key={index} className="flex items-center justify-between text-sm">
              <span className="text-slate-300">
                {feature.icon} {feature.name}
              </span>
              <span className={`text-xs ${feature.active ? 'text-green-400' : 'text-slate-500'}`}>
                {feature.active ? '✓' : '○'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;
