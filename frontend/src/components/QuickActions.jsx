function QuickActions() {
  const handleAction = async (action) => {
    try {
      let response;
      
      switch (action) {
        case 'triage':
          response = await fetch('http://localhost:8000/api/ai/triage');
          break;
        case 'daily-brief':
          response = await fetch('http://localhost:8000/api/ai/daily-brief');
          break;
        default:
          return;
      }
      
      if (response.ok) {
        const data = await response.json();
        alert(data.response || 'Action completed!');
      }
    } catch (error) {
      console.error('Action error:', error);
      alert('Failed to execute action');
    }
  };

  const actions = [
    {
      id: 'triage',
      icon: '🎯',
      title: 'Triage Emails',
      description: 'AI analyzes and prioritizes your emails',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'daily-brief',
      icon: '📊',
      title: 'Daily Brief',
      description: 'Get comprehensive daily summary',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'schedule',
      icon: '📅',
      title: 'Smart Schedule',
      description: 'Optimize your calendar',
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'tasks',
      icon: '✅',
      title: 'Task Extraction',
      description: 'Extract tasks from emails',
      color: 'from-orange-500 to-red-500'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => handleAction(action.id)}
          className="group bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6 hover:border-purple-500/50 transition-all hover:shadow-lg hover:shadow-purple-500/20"
        >
          <div className={`w-12 h-12 bg-gradient-to-br ${action.color} rounded-lg flex items-center justify-center text-2xl mb-3 group-hover:scale-110 transition-transform`}>
            {action.icon}
          </div>
          <h3 className="text-white font-semibold mb-1">{action.title}</h3>
          <p className="text-slate-400 text-sm">{action.description}</p>
        </button>
      ))}
    </div>
  );
}

export default QuickActions;
