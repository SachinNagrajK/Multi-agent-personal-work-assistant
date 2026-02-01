import { useState, useEffect } from 'react';

function CalendarPanel() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewEvent, setShowNewEvent] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '',
    start: '',
    end: '',
    description: ''
  });

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/calendar');
      if (response.ok) {
        const data = await response.json();
        setEvents(data);
      }
    } catch (error) {
      console.error('Failed to load calendar:', error);
    } finally {
      setLoading(false);
    }
  };

  const createEvent = async () => {
    // This would integrate with the backend
    alert('Use the chat interface to create events: "Schedule a meeting tomorrow at 2pm"');
    setShowNewEvent(false);
  };

  if (loading) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-8 text-center">
        <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-300">Loading calendar...</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 overflow-hidden">
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">📅 Calendar</h2>
          <p className="text-green-100 text-sm">{events.length} upcoming events</p>
        </div>
        <button
          onClick={() => setShowNewEvent(true)}
          className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
        >
          + New Event
        </button>
      </div>

      <div className="p-6 space-y-4">
        {events.length === 0 ? (
          <div className="text-center text-slate-400 py-8">
            <p>No upcoming events</p>
            <p className="text-sm mt-2">Try using the chat to check your real calendar!</p>
          </div>
        ) : (
          events.map((event, index) => (
            <div key={index} className="bg-slate-700/30 rounded-xl p-4 border border-slate-600 hover:border-purple-500/50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-1">{event.title || event.summary}</h3>
                  <p className="text-slate-400 text-sm mb-2">{event.description}</p>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-slate-300">
                      📅 {event.start || event.date}
                    </span>
                    {event.end && (
                      <span className="text-slate-300">
                        ⏰ {event.start} - {event.end}
                      </span>
                    )}
                    {event.attendees && (
                      <span className="text-slate-300">
                        👥 {event.attendees.length} attendees
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="text-slate-400 hover:text-purple-400 transition-colors">
                    ✏️
                  </button>
                  <button className="text-slate-400 hover:text-red-400 transition-colors">
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* New Event Modal */}
      {showNewEvent && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setShowNewEvent(false)}>
          <div className="bg-slate-800 rounded-2xl border border-purple-500/20 max-w-md w-full" onClick={(e) => e.stopPropagation()}>
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4">
              <h2 className="text-xl font-bold text-white">New Event</h2>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-slate-300 text-sm mb-4">
                💡 <strong>Tip:</strong> Use the chat interface for natural language event creation!
                <br />
                <span className="text-slate-400">Example: "Schedule a team meeting tomorrow at 2pm"</span>
              </p>
              <button
                onClick={() => setShowNewEvent(false)}
                className="w-full px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors"
              >
                Go to Chat
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CalendarPanel;
