# Agent Tools Guide

## Overview

This project implements a comprehensive toolkit for AI agents to interact with external systems and perform various operations. Each agent has access to specialized tools tailored to their domain.

---

## 🌐 Web Tools

### 1. **TavilySearchTool**
**Purpose**: AI-optimized web search for current information

```python
from tools.web_tools import TavilySearchTool

search = TavilySearchTool()
results = search.search_web("latest AI developments", max_results=5)
```

**Features**:
- Real-time web search via Tavily API
- AI-optimized results with relevance scoring
- Falls back to mock data in demo mode (no API key needed)
- Returns formatted, structured results

**Used by**: All agents when current information is needed

---

### 2. **WebScraperTool**
**Purpose**: Extract content from web pages

```python
from tools.web_tools import WebScraperTool

scraper = WebScraperTool()
content = scraper.scrape_url("https://example.com/article")
```

**Features**:
- Clean HTML parsing with BeautifulSoup
- Automatic script/style removal
- Content length limiting (5000 chars)
- User-agent spoofing to avoid blocks

**Used by**: DocumentAgent, EmailAgent

---

### 3. **URLExtractorTool**
**Purpose**: Find and validate URLs in text

```python
from tools.web_tools import URLExtractorTool

extractor = URLExtractorTool()
urls = extractor.extract_urls(email_body)
```

**Features**:
- Regex-based URL detection
- HTTP/HTTPS support
- Useful for analyzing emails and documents

**Used by**: EmailAgent, DocumentAgent

---

## 📧 Email Tools

### 4. **EmailSenderTool**
**Purpose**: Send emails (Gmail API integration ready)

```python
from tools.email_tools import EmailSenderTool

sender = EmailSenderTool()
status = sender.send_email(
    to="user@example.com",
    subject="Project Update",
    body="Here's the latest update...",
    cc="team@example.com"
)
```

**Features**:
- Email validation (regex)
- CC support
- Message ID tracking
- Timestamp logging
- Simulated for demo (ready for Gmail API)

**Used by**: EmailAgent

---

### 5. **EmailSearchTool**
**Purpose**: Search through email history

```python
from tools.email_tools import EmailSearchTool

search = EmailSearchTool()
results = search.search_emails("quarterly report", max_results=10)
```

**Features**:
- Keyword-based search
- Subject/sender filtering
- Returns email snippets
- Ready for Gmail API integration

**Used by**: EmailAgent, ContextAgent

---

### 6. **EmailAttachmentTool**
**Purpose**: List and download email attachments

```python
from tools.email_tools import EmailAttachmentTool

attachment = EmailAttachmentTool()
files = attachment.list_attachments("email_12345")
status = attachment.download_attachment("email_12345", "report.pdf")
```

**Features**:
- File type detection
- Size reporting
- Download tracking
- Preview availability checking

**Used by**: EmailAgent, DocumentAgent

---

## 📅 Calendar Tools

### 7. **CalendarSearchTool**
**Purpose**: Search calendar events

```python
from tools.calendar_tools import CalendarSearchTool

calendar = CalendarSearchTool()
events = calendar.search_events(
    "team meeting",
    start_date="2026-02-01",
    end_date="2026-02-28"
)
```

**Features**:
- Keyword search
- Date range filtering
- Location and attendee details
- Status tracking (confirmed/tentative)

**Used by**: CalendarAgent, ContextAgent

---

### 8. **CalendarCreateTool**
**Purpose**: Create new calendar events

```python
from tools.calendar_tools import CalendarCreateTool

creator = CalendarCreateTool()
event = creator.create_event(
    title="Sprint Planning",
    start_time="2026-02-01T10:00:00",
    end_time="2026-02-01T11:00:00",
    attendees="team@company.com",
    location="Conference Room A"
)
```

**Features**:
- ISO datetime support
- Attendee invitation
- Location specification
- Description/notes
- Automatic calendar invite sending

**Used by**: CalendarAgent, MeetingAgent

---

### 9. **CalendarUpdateTool**
**Purpose**: Update, reschedule, or cancel events

```python
from tools.calendar_tools import CalendarUpdateTool

updater = CalendarUpdateTool()

# Reschedule
updater.reschedule_event("event_123", new_start="...", new_end="...")

# Cancel
updater.cancel_event("event_123", reason="Project postponed")

# Update fields
updater.update_event("event_123", {"location": "Virtual - Zoom"})
```

**Features**:
- Flexible field updates
- Reschedule notifications
- Cancellation with reason
- Attendee notifications

**Used by**: CalendarAgent

---

## 📁 File Tools

### 10. **FileReadTool**
**Purpose**: Read files from workspace

```python
from tools.file_tools import FileReadTool

reader = FileReadTool()
content = reader.read_file("reports/q1_summary.txt", max_lines=50)
```

**Features**:
- Safe path handling (sandbox)
- Optional line limiting
- UTF-8 encoding support
- Error handling

**Used by**: DocumentAgent, ContextAgent

---

### 11. **FileWriteTool**
**Purpose**: Write files to workspace

```python
from tools.file_tools import FileWriteTool

writer = FileWriteTool()
status = writer.write_file(
    "outputs/summary.txt",
    "Generated summary...",
    mode="w"  # 'w' for write, 'a' for append
)
```

**Features**:
- Automatic directory creation
- Append mode support
- Byte count reporting
- Sandboxed to workspace directory

**Used by**: DocumentAgent, MeetingAgent

---

### 12. **FileSearchTool**
**Purpose**: Search for files by pattern

```python
from tools.file_tools import FileSearchTool

searcher = FileSearchTool()
files = searcher.search_files("*.pdf", directory="./workspace")
```

**Features**:
- Wildcard pattern support
- Recursive search
- File size reporting
- Result limiting (20 max)

**Used by**: DocumentAgent, ContextAgent

---

## 📊 Analysis Tools

### 13. **DataAnalysisTool**
**Purpose**: Analyze text and numerical data

```python
from tools.analysis_tools import DataAnalysisTool

analyzer = DataAnalysisTool()

# Text analysis
text_stats = analyzer.analyze_text_stats(document_content)

# Number analysis
num_stats = analyzer.analyze_numbers([23, 45, 67, 89, 12, 34])
```

**Features**:
- **Text Analysis**:
  - Word/sentence counts
  - Word frequency (top 10)
  - Average word length
  - Readability assessment
  
- **Numerical Analysis**:
  - Mean, median, min, max
  - Sum, range
  - Distribution analysis
  - Percentage breakdowns

**Used by**: DocumentAgent, TaskAgent, MeetingAgent

---

### 14. **SentimentAnalysisTool**
**Purpose**: Analyze emotional tone of text

```python
from tools.analysis_tools import SentimentAnalysisTool

sentiment = SentimentAnalysisTool()
analysis = sentiment.analyze_sentiment(email_body)
```

**Features**:
- Positive/Negative/Neutral classification
- Confidence scoring (0-100%)
- Urgency detection
- Keyword indicators count
- Response recommendations

**Indicators**:
- **Positive**: good, great, excellent, happy, pleased, wonderful, fantastic, amazing, love, best, success, perfect
- **Negative**: bad, terrible, awful, sad, disappointed, poor, worst, hate, failure, problem, issue, concern
- **Urgent**: urgent, asap, immediately, critical, emergency, now

**Used by**: EmailAgent, MeetingAgent

---

### 15. **KeywordExtractionTool**
**Purpose**: Extract important keywords and phrases

```python
from tools.analysis_tools import KeywordExtractionTool

extractor = KeywordExtractionTool()
keywords = extractor.extract_keywords(document_text, top_n=10)
```

**Features**:
- Stop word filtering
- Frequency-based ranking
- Top N keywords
- 2-word phrase extraction
- Occurrence counting

**Used by**: DocumentAgent, EmailAgent, ContextAgent

---

## 💬 Communication Tools

### 16. **SlackMessageTool**
**Purpose**: Send and search Slack messages

```python
from tools.communication_tools import SlackMessageTool

slack = SlackMessageTool()

# Send message
slack.send_message(
    channel="engineering",
    message="Deploy completed successfully!",
    thread_ts="1234567890.123456"  # Optional: reply to thread
)

# Search messages
results = slack.search_messages("deployment", channel="engineering")
```

**Features**:
- Channel messaging
- Thread replies
- Message search
- Timestamp tracking
- Delivery confirmation

**Used by**: MeetingAgent, TaskAgent

---

### 17. **TeamsMessageTool**
**Purpose**: Microsoft Teams integration

```python
from tools.communication_tools import TeamsMessageTool

teams = TeamsMessageTool()

# Send message
teams.send_message(
    team="Engineering",
    channel="General",
    message="Sprint review notes attached",
    mention_users="john@company.com,sarah@company.com"
)

# Schedule meeting
teams.schedule_meeting(
    title="Code Review",
    attendees="team@company.com",
    start_time="2026-02-01T14:00:00",
    duration=60
)
```

**Features**:
- Team/channel messaging
- User mentions (@user)
- Meeting scheduling
- Meeting link generation
- Calendar integration

**Used by**: MeetingAgent, CalendarAgent

---

### 18. **NotificationTool**
**Purpose**: Multi-channel notifications

```python
from tools.communication_tools import NotificationTool

notifier = NotificationTool()
status = notifier.send_notification(
    recipient="user@company.com",
    message="Your report is ready for review",
    priority="high",  # low/normal/high/urgent
    channels=["email", "push", "sms"]
)
```

**Features**:
- Multi-channel delivery (email, SMS, push)
- Priority levels (low, normal, high, urgent)
- Delivery confirmation
- Channel-specific status
- High-priority alerts

**Used by**: All agents for critical notifications

---

## 🔧 Tool Integration Architecture

### Agent-Tool Mapping

```python
EmailAgent:
    - TavilySearchTool (research context)
    - URLExtractorTool (find links)
    - EmailSenderTool (send emails)
    - EmailSearchTool (search history)
    - SentimentAnalysisTool (analyze tone)
    - KeywordExtractionTool (extract topics)

DocumentAgent:
    - TavilySearchTool (research)
    - WebScraperTool (fetch content)
    - FileReadTool (read docs)
    - FileWriteTool (save outputs)
    - FileSearchTool (find files)
    - DataAnalysisTool (stats)
    - KeywordExtractionTool (topics)

CalendarAgent:
    - CalendarSearchTool (find events)
    - CalendarCreateTool (create events)
    - CalendarUpdateTool (modify events)
    - TavilySearchTool (research)
    - NotificationTool (alerts)

TaskAgent:
    - TavilySearchTool (research)
    - DataAnalysisTool (analyze workload)
    - NotificationTool (reminders)

ContextAgent:
    - TavilySearchTool (research)
    - FileSearchTool (find resources)
    - DataAnalysisTool (analyze patterns)
    - KeywordExtractionTool (identify themes)

MeetingAgent:
    - TavilySearchTool (research)
    - SentimentAnalysisTool (meeting tone)
    - KeywordExtractionTool (action items)
    - SlackMessageTool (share notes)
    - TeamsMessageTool (schedule follow-ups)
    - NotificationTool (send summaries)
```

---

## 🚀 Using Tools with LangChain

All tools implement `.as_langchain_tool()` for easy integration:

```python
from langchain.agents import initialize_agent, AgentType
from tools.web_tools import TavilySearchTool
from tools.analysis_tools import SentimentAnalysisTool

# Initialize tools
search_tool = TavilySearchTool()
sentiment_tool = SentimentAnalysisTool()

# Convert to LangChain tools
tools = [
    search_tool.as_langchain_tool(),
    sentiment_tool.as_langchain_tool()
]

# Create agent with tools
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
response = agent.run("Search for recent AI news and analyze the sentiment")
```

---

## 🔑 API Keys Required

### Optional (but Recommended):

1. **Tavily API** (web search):
   - Get key: https://tavily.com
   - Add to `.env`: `TAVILY_API_KEY=tvly-xxxxx`
   - **Fallback**: Mock data if no key

2. **Gmail API** (email operations):
   - Get credentials: https://console.cloud.google.com
   - Currently simulated (ready for integration)

3. **Google Calendar API** (calendar operations):
   - Get credentials: https://console.cloud.google.com
   - Currently simulated (ready for integration)

---

## 💡 Demo Mode vs Production

### Demo Mode (Default)
- No additional API keys needed (beyond OpenAI/Pinecone/LangSmith)
- Tools return realistic simulated data
- Perfect for demonstrations and testing
- All features work end-to-end

### Production Mode
- Add optional API keys (Tavily, Gmail, Calendar)
- Tools connect to real services
- Real web search, email sending, calendar management
- Ready for production deployment

---

## 📈 Tool Usage Examples

### Example 1: Email Agent with Tools

```python
async def triage_email_with_tools(email):
    # Extract URLs from email
    urls = url_extractor.extract_urls(email['body'])
    
    # Analyze sentiment
    sentiment = sentiment_analyzer.analyze_sentiment(email['body'])
    
    # Search for context if needed
    if "research" in email['subject'].lower():
        context = search_tool.search_web(email['subject'])
    
    # Determine priority based on sentiment
    if "High" in sentiment:
        priority = "urgent"
    
    return {
        "email": email,
        "sentiment": sentiment,
        "urls": urls,
        "priority": priority
    }
```

### Example 2: Document Agent with Tools

```python
async def analyze_document_with_tools(document):
    # Read file
    content = file_reader.read_file(document['path'])
    
    # Extract keywords
    keywords = keyword_extractor.extract_keywords(content)
    
    # Analyze statistics
    stats = data_analyzer.analyze_text_stats(content)
    
    # Search for related information
    main_topic = keywords.split('\n')[1].split('.')[1].strip()
    research = search_tool.search_web(f"latest information about {main_topic}")
    
    # Write summary
    summary = generate_summary(content, keywords, stats, research)
    file_writer.write_file("summaries/latest.txt", summary)
    
    return summary
```

### Example 3: Meeting Agent with Tools

```python
async def process_meeting_with_tools(transcript):
    # Analyze sentiment
    sentiment = sentiment_analyzer.analyze_sentiment(transcript)
    
    # Extract keywords
    keywords = keyword_extractor.extract_keywords(transcript)
    
    # Generate summary
    summary = generate_summary(transcript, sentiment, keywords)
    
    # Send to Slack
    slack_tool.send_message(
        channel="team-updates",
        message=f"Meeting summary ready:\n\n{summary}"
    )
    
    # Notify participants
    notification_tool.send_notification(
        recipient="team@company.com",
        message="Meeting notes are now available",
        priority="normal",
        channels=["email", "push"]
    )
    
    return summary
```

---

## 🎯 Best Practices

1. **Error Handling**: All tools have try-catch blocks and return error messages instead of crashing

2. **Fallback Data**: Web tools provide mock data when API keys aren't available

3. **Security**: File tools are sandboxed to `./workspace` directory

4. **Rate Limiting**: Consider adding rate limiting for production use

5. **Logging**: Tools log operations for debugging and monitoring

6. **Validation**: Input validation (email formats, file paths, etc.)

7. **Async Support**: Most agents use async methods for better performance

---

## 🔮 Future Tool Additions

Consider adding:
- GitHub tool (create issues, PRs)
- Jira tool (task management)
- Database tool (query databases)
- Code execution tool (run code safely)
- Image generation tool (DALL-E)
- Audio transcription tool (Whisper)
- Translation tool (multi-language)
- Weather tool (current conditions)

---

## 📊 Tool Effectiveness Metrics

Track these metrics in production:
- Tool usage frequency
- Success/failure rates
- Average execution time
- API costs per tool
- User satisfaction with tool results

Add to LangSmith for automatic tracking!

---

This toolkit gives your agents **real capabilities** to interact with the world, making them genuinely useful for workplace productivity! 🚀
