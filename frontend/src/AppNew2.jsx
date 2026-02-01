import { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterfaceNew';
import QuickActions from './components/QuickActions';
import EmailPanel from './components/EmailPanel';
import CalendarPanel from './components/CalendarPanel';
import StatsPanel from './components/StatsPanel';

function App() {
  const [activeView, setActiveView] = useState('chat');
  const [contextStats, setContextStats] = useState(null);
  const [guardrailsStatus, setGuardrailsStatus] = useState(null);

  useEffect(() => {
    // Load initial stats
    loadStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const [contextRes, guardrailsRes] = await Promise.all([
        fetch('http://localhost:8000/api/ai/context-summary'),
        fetch('http://localhost:8000/api/ai/guardrails-status')
      ]);
      
      if (contextRes.ok) {
        const contextData = await contextRes.json();
        setContextStats(contextData);
      }
      
      if (guardrailsRes.ok) {
        const guardrailsData = await guardrailsRes.json();
        setGuardrailsStatus(guardrailsData);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-lg border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Workspace Assistant</h1>
                <p className="text-sm text-purple-300">Powered by LangGraph & GPT-4</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* View Switcher */}
              <button
                onClick={() => setActiveView('chat')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeView === 'chat'
                    ? 'bg-purple-500 text-white shadow-lg'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
                }`}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setActiveView('emails')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeView === 'emails'
                    ? 'bg-purple-500 text-white shadow-lg'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
                }`}
              >
                📧 Emails
              </button>
              <button
                onClick={() => setActiveView('calendar')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeView === 'calendar'
                    ? 'bg-purple-500 text-white shadow-lg'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
                }`}
              >
                📅 Calendar
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Panel */}
          <div className="lg:col-span-3">
            {activeView === 'chat' && (
              <div className="space-y-4">
                <ChatInterface onStatsUpdate={loadStats} />
                <QuickActions />
              </div>
            )}
            {activeView === 'emails' && <EmailPanel />}
            {activeView === 'calendar' && <CalendarPanel />}
          </div>

          {/* Stats Sidebar */}
          <div className="lg:col-span-1">
            <StatsPanel 
              contextStats={contextStats} 
              guardrailsStatus={guardrailsStatus}
              onRefresh={loadStats}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 py-4 text-center text-slate-400 text-sm">
        <p>HP IQ Demo • January 31, 2026 • Multi-Agent LangGraph System</p>
      </footer>
    </div>
  );
}

export default App;
