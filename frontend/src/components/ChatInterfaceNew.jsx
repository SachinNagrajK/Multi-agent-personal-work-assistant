import { useState, useRef, useEffect } from 'react';

function ChatInterfaceNew({ onStatsUpdate }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hi! I\'m your AI Workspace Assistant. I can help you with:\n\n• 📧 Reading and managing emails\n• 📅 Scheduling calendar events\n• ✅ Creating and organizing tasks\n• 🔍 Searching your workspace\n• 📊 Generating daily briefs\n\nTry asking me something like:\n- "What unread emails do I have?"\n- "Schedule a meeting tomorrow at 2pm"\n- "Triage my emails by priority"',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    console.log('🚀 sendMessage called with input:', input);

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = input;
    setInput('');
    setIsLoading(true);

    try {
      console.log('📤 Sending request to backend:', messageToSend);
      const response = await fetch('http://localhost:8000/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageToSend })
      });
      console.log('📥 Response received:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('📊 Response data:', data);

      const assistantMessage = {
        role: 'assistant',
        content: data.response || 'I processed your request.',
        stats: data.stats,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update stats in parent
      if (onStatsUpdate) {
        onStatsUpdate();
      }
    } catch (error) {
      console.error('❌ Chat error:', error);
      console.error('Error details:', error.message, error.stack);
      const errorMessage = {
        role: 'assistant',
        content: `❌ Error: ${error.message}\n\nMake sure the backend server is running on http://localhost:8000`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      console.log('✅ Request complete, setting loading to false');
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickPrompts = [
    "What unread emails do I have?",
    "Give me my daily brief",
    "Triage my emails by priority",
    "What's on my calendar today?",
    "Find emails about the project"
  ];

  const useQuickPrompt = (prompt) => {
    setInput(prompt);
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 overflow-hidden shadow-2xl">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Chat with AI Assistant</h2>
        <p className="text-purple-100 text-sm">Ask me anything about your emails, calendar, or tasks</p>
      </div>

      {/* Messages */}
      <div className="h-[500px] overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : message.isError
                  ? 'bg-red-900/50 text-red-200 border border-red-500/50'
                  : 'bg-slate-700/50 text-slate-100'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.stats && (
                <div className="mt-2 pt-2 border-t border-slate-600 text-xs text-slate-300">
                  <div className="flex gap-4">
                    <span>🤖 Agents: {message.stats.agents_used}</span>
                    <span>📝 Messages: {message.stats.total_messages}</span>
                    <span>🔄 Delegations: {message.stats.delegation_count}</span>
                  </div>
                </div>
              )}
              <div className="text-xs mt-1 opacity-60">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-700/50 rounded-2xl px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      <div className="px-6 py-3 bg-slate-900/30 border-t border-slate-700">
        <p className="text-xs text-slate-400 mb-2">Quick prompts:</p>
        <div className="flex flex-wrap gap-2">
          {quickPrompts.map((prompt, index) => (
            <button
              key={index}
              onClick={() => useQuickPrompt(prompt)}
              className="px-3 py-1 bg-slate-700 hover:bg-purple-600 text-slate-300 hover:text-white text-xs rounded-full transition-all"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-6 bg-slate-900/30 border-t border-slate-700">
        <div className="flex space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Shift+Enter for new line)"
            className="flex-1 bg-slate-700/50 text-white placeholder-slate-400 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
          >
            {isLoading ? '⏳' : '📤'} Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatInterfaceNew;
