"""
Demo script showing agent tools in action.
Run this to see how agents use their tools.
"""

import asyncio
from tools.web_tools import TavilySearchTool, URLExtractorTool
from tools.analysis_tools import SentimentAnalysisTool, KeywordExtractionTool
from tools.communication_tools import NotificationTool


async def demo_email_agent_tools():
    """Demonstrate EmailAgent tools"""
    print("\n" + "="*60)
    print("📧 EMAIL AGENT TOOLS DEMO")
    print("="*60 + "\n")
    
    # Sample email
    email_body = """
    Hi team,
    
    URGENT: We need to discuss the Q1 results immediately. The report 
    shows significant growth but there are concerns about sustainability.
    
    Please review the dashboard at https://analytics.company.com/q1
    and share your thoughts ASAP.
    
    Best regards,
    Sarah
    """
    
    # Tool 1: Sentiment Analysis
    print("1️⃣ Analyzing email sentiment...")
    sentiment_tool = SentimentAnalysisTool()
    sentiment = sentiment_tool.analyze_sentiment(email_body)
    print(sentiment)
    
    # Tool 2: URL Extraction
    print("\n2️⃣ Extracting URLs from email...")
    url_tool = URLExtractorTool()
    urls = url_tool.extract_urls(email_body)
    print(urls)
    
    # Tool 3: Keyword Extraction
    print("\n3️⃣ Extracting key topics...")
    keyword_tool = KeywordExtractionTool()
    keywords = keyword_tool.extract_keywords(email_body, top_n=5)
    print(keywords)
    
    print("\n✅ Email Agent Tools Demo Complete!")


async def demo_web_search_tool():
    """Demonstrate Web Search tool"""
    print("\n" + "="*60)
    print("🌐 WEB SEARCH TOOL DEMO (Tavily)")
    print("="*60 + "\n")
    
    search_tool = TavilySearchTool()
    
    # Search for current AI news
    print("Searching: 'latest AI agent developments'...\n")
    results = search_tool.search_web("latest AI agent developments", max_results=3)
    print(results)
    
    print("\n✅ Web Search Demo Complete!")


async def demo_notification_tool():
    """Demonstrate Notification tool"""
    print("\n" + "="*60)
    print("🔔 NOTIFICATION TOOL DEMO")
    print("="*60 + "\n")
    
    notif_tool = NotificationTool()
    
    # Send high-priority notification
    print("Sending high-priority notification...\n")
    result = notif_tool.send_notification(
        recipient="team@company.com",
        message="Your Q1 report analysis is complete. Urgent action items identified.",
        priority="high",
        channels=["email", "push", "sms"]
    )
    print(result)
    
    print("\n✅ Notification Tool Demo Complete!")


async def demo_all_tools():
    """Run all tool demos"""
    print("\n" + "🚀"*30)
    print("\n🎯 AI AGENT TOOLS DEMONSTRATION")
    print("   Showing 18 specialized tools in action\n")
    print("🚀"*30)
    
    await demo_email_agent_tools()
    await demo_web_search_tool()
    await demo_notification_tool()
    
    print("\n" + "="*60)
    print("🎉 ALL TOOL DEMOS COMPLETE!")
    print("="*60)
    print("""
📚 Available Tool Categories:
   • Web Tools (3): Search, Scrape, URL Extract
   • Email Tools (3): Send, Search, Attachments
   • Calendar Tools (3): Search, Create, Update
   • File Tools (3): Read, Write, Search
   • Analysis Tools (3): Data, Sentiment, Keywords
   • Communication Tools (3): Slack, Teams, Notifications

🔧 All tools work in demo mode (no extra API keys needed)
📖 See TOOLS_GUIDE.md for complete documentation
    """)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_all_tools())
