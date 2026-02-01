# 🚀 Interactive AI Workspace Assistant - User Guide

## ✅ Setup Complete!

Your interactive AI workspace assistant is now running with:

### 🖥️ **Servers Running:**
- **Backend**: http://localhost:8000 (FastAPI + LangGraph)
- **Frontend**: http://localhost:5173 (React + Vite)

Both servers are configured with venv activation.

---

## 💬 How to Use the Chat Interface

### Main Features:

#### 1. **Chat Tab (💬)** - Primary Interface
The chat interface is your main way to interact with the AI. You can:

**Email Operations:**
- "What unread emails do I have?"
- "Triage my emails by priority"
- "Show me emails from Sarah about the project"
- "Reply to the email from john@example.com saying I'll review it tomorrow"
- "Send an email to team@company.com about the meeting"

**Calendar Operations:**
- "What's on my calendar today?"
- "Schedule a meeting with Sarah tomorrow at 2pm"
- "Find free slots for a meeting next week"
- "Show me my schedule for this week"
- "Delete the meeting scheduled for Friday"

**Task Operations:**
- "Create a task to review the budget report"
- "What are my high priority tasks?"
- "Mark the design task as complete"

**Smart Features:**
- "Give me my daily brief"
- "Summarize the email thread about the project"
- "Find all action items from my emails"

#### 2. **Quick Actions** - One-Click Operations
Four quick action buttons below the chat:
- **🎯 Triage Emails**: AI analyzes and prioritizes all emails
- **📊 Daily Brief**: Comprehensive morning summary
- **📅 Smart Schedule**: Calendar optimization
- **✅ Task Extraction**: Extract tasks from emails

#### 3. **Email Tab (📧)**
- View all your emails in one place
- Click any email to see full details
- Priority badges (Urgent/High/Medium/Low)
- Quick reply and forward options

#### 4. **Calendar Tab (📅)**
- View upcoming events
- See event details and attendees
- Create new events (redirects to chat for natural language)

#### 5. **Stats Sidebar** (Right Panel)
Real-time monitoring:
- **Context Stats**: Messages, context length, summarization status
- **Safety Guardrails**: Blocked actions, triggered rules, rate limits
- **System Info**: Backend status, API connections
- **Active Features**: Human-in-loop, guardrails, auto-summary, etc.

---

## 🎯 Try These Example Commands:

### Getting Started:
1. Click in the chat input at the bottom
2. Type or click a quick prompt
3. Press Enter or click "📤 Send"

### Example Conversations:

**Morning Routine:**
```
You: "Give me my daily brief"
AI: [Provides comprehensive summary of emails, calendar, and tasks]

You: "What are the most urgent items?"
AI: [Lists prioritized action items]

You: "Schedule time to handle these"
AI: [Suggests optimal time blocks]
```

**Email Management:**
```
You: "What unread emails do I have?"
AI: [Shows count and summaries]

You: "Triage them by priority"
AI: [Categorizes as Urgent/High/Medium/Low with reasons]

You: "Draft a reply to the urgent one about the budget"
AI: [Generates contextual reply, asks for approval]
```

**Calendar Planning:**
```
You: "What's my schedule today?"
AI: [Lists all events]

You: "Find a 30-minute slot for a call with the team"
AI: [Suggests available times]

You: "Book it for 2pm"
AI: [Creates calendar event]
```

---

## 🛡️ Safety Features

### Human-in-the-Loop
The AI will **always ask for approval** before:
- Sending emails
- Deleting calendar events
- Making bulk changes
- Accessing sensitive data

### Guardrails Active
- ✅ Sensitive content detection (credit cards, SSNs, passwords)
- ✅ Dangerous action prevention (bulk deletes, directory traversal)
- ✅ Rate limiting (email sending, API calls)
- ✅ Loop prevention (agents won't call each other infinitely)

### Context Management
- Auto-summarization kicks in at 10,000 characters
- Preserves important information while reducing token usage
- Search through conversation history anytime

---

## 🎨 Modern UI Features

### Visual Feedback:
- **Purple/Pink gradients**: User messages and primary actions
- **Dark slate backgrounds**: Assistant responses
- **Red borders**: Error messages
- **Green indicators**: Active systems and successful actions
- **Animated dots**: AI is thinking/processing

### Responsive Design:
- Works on desktop and tablets
- Sidebar collapses on smaller screens
- Touch-friendly buttons

---

## 🔧 Technical Details

### Backend Architecture:
- **LangGraph**: Modern orchestration with StateGraph
- **ReAct Pattern**: Reasoning and acting agents
- **Tool Binding**: `.bind_tools()` for seamless integration
- **Conditional Edges**: Intelligent routing between agents
- **Loop Prevention**: Max 3 delegation depth

### Real APIs Connected:
- ✅ Gmail API (7 tools)
- ✅ Google Calendar API (6 tools)
- ✅ OAuth 2.0 authenticated

### AI Models:
- Primary: GPT-4o (intelligent, context-aware)
- Fallback: GPT-3.5-turbo (if needed)
- LangSmith tracing enabled for debugging

---

## 🚨 Troubleshooting

### If Chat Doesn't Respond:
1. Check terminal for backend errors
2. Make sure backend is running on port 8000
3. Try refreshing the page
4. Check browser console (F12) for errors

### If Gmail/Calendar Don't Work:
1. Ensure `token.pickle` exists in backend folder
2. Check OAuth credentials are valid
3. Re-run Google authentication if needed

### If Components Don't Load:
1. Check frontend terminal for build errors
2. Try `npm install` in frontend folder
3. Clear browser cache and reload

---

## 🎓 Advanced Tips

### Natural Language Power:
The AI understands context! You can:
- Reference previous messages: "Reply to that email"
- Use pronouns: "Schedule it for tomorrow"
- Be vague: "Find that thing Sarah sent"
- Chain requests: "Triage emails, then create tasks for urgent ones"

### Keyboard Shortcuts:
- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Tab**: Cycle through quick prompts

### Multi-Agent Coordination:
The system automatically:
- Routes to the right agent (Email/Calendar/Task)
- Coordinates between agents for complex requests
- Prevents infinite loops
- Tracks delegation history

---

## 📊 Demo Showcase Points

**For Your HP IQ Demo, Highlight:**

1. **Natural Language Interface** ✨
   - Show how you can just talk naturally to manage work

2. **Real Gmail Integration** 📧
   - Live email reading, not mock data

3. **Intelligent Triage** 🎯
   - AI understands urgency and importance

4. **Human-in-the-Loop** 👤
   - Safety approvals for critical actions

5. **Multi-Agent System** 🤖
   - Different specialized agents working together

6. **Context Awareness** 🧠
   - AI remembers conversation, auto-summarizes

7. **Safety Guardrails** 🛡️
   - Built-in protection against dangerous operations

8. **Modern Tech Stack** 🚀
   - LangGraph, GPT-4, React, FastAPI

---

## 📝 What to Say During Demo

**Opening:**
> "I've built an AI-powered workspace assistant that uses LangGraph's multi-agent architecture. It connects to real Gmail and Calendar APIs, and I can control everything through natural language."

**Show Chat:**
> "Watch how I can just ask naturally: 'What unread emails do I have?' and it connects to my real Gmail account..."

**Show Triage:**
> "Now let me triage these. Notice how the AI analyzes urgency, importance, and even suggests actions—and it does this using multiple specialized agents working together."

**Show Safety:**
> "When I try to send an email, it asks for approval first. We have guardrails that detect sensitive content, prevent dangerous operations, and enforce rate limits."

**Show Stats:**
> "On the right, you can see the context manager tracking our conversation, and the guardrails system monitoring for any safety issues."

**Closing:**
> "This demonstrates modern LangGraph patterns: ReAct agents, tool binding, conditional routing, human-in-the-loop, automatic context summarization, and loop prevention—all the advanced features you'd want in a production AI system."

---

## 🎉 Enjoy Your AI Assistant!

You now have a fully functional, interactive AI workspace assistant. The chat interface makes it easy to use, while the underlying multi-agent system handles all the complexity.

**Have fun exploring what it can do!** 🚀

---

*Built with: LangGraph • LangChain • OpenAI GPT-4 • FastAPI • React • Vite • Tailwind CSS*
