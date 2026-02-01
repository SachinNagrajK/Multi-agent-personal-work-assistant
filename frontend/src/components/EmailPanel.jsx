import { useState, useEffect } from 'react';

function EmailPanel() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState(null);

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/emails');
      if (response.ok) {
        const data = await response.json();
        setEmails(data);
      }
    } catch (error) {
      console.error('Failed to load emails:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'urgent':
        return 'text-red-400 bg-red-900/30';
      case 'high':
        return 'text-orange-400 bg-orange-900/30';
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/30';
      default:
        return 'text-green-400 bg-green-900/30';
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-8 text-center">
        <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-300">Loading emails...</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">📧 Email Inbox</h2>
        <p className="text-blue-100 text-sm">{emails.length} emails</p>
      </div>

      <div className="divide-y divide-slate-700">
        {emails.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            <p>No emails to display</p>
            <p className="text-sm mt-2">Try using the chat to check your real emails!</p>
          </div>
        ) : (
          emails.map((email, index) => (
            <div
              key={index}
              onClick={() => setSelectedEmail(email)}
              className="p-4 hover:bg-slate-700/30 cursor-pointer transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-white">{email.sender || email.from}</span>
                    {email.priority && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(email.priority)}`}>
                        {email.priority}
                      </span>
                    )}
                  </div>
                  <h3 className="text-slate-200 font-medium mb-1">{email.subject}</h3>
                  <p className="text-slate-400 text-sm line-clamp-2">{email.preview || email.snippet}</p>
                </div>
                <span className="text-slate-500 text-xs whitespace-nowrap ml-4">{email.date || email.timestamp}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Email Detail Modal */}
      {selectedEmail && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setSelectedEmail(null)}>
          <div className="bg-slate-800 rounded-2xl border border-purple-500/20 max-w-2xl w-full max-h-[80vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-6 py-4">
              <h2 className="text-xl font-bold text-white">{selectedEmail.subject}</h2>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <p className="text-slate-400 text-sm">From: <span className="text-white">{selectedEmail.sender || selectedEmail.from}</span></p>
                <p className="text-slate-400 text-sm">Date: <span className="text-white">{selectedEmail.date || selectedEmail.timestamp}</span></p>
              </div>
              <div className="text-slate-200 whitespace-pre-wrap">{selectedEmail.body || selectedEmail.content || selectedEmail.preview}</div>
            </div>
            <div className="p-6 border-t border-slate-700 flex gap-3">
              <button className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors">
                ↩️ Reply
              </button>
              <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors">
                ➡️ Forward
              </button>
              <button onClick={() => setSelectedEmail(null)} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors ml-auto">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmailPanel;
