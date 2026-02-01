"""
Data analysis and NLP tools for agents.
"""

from typing import Dict, List, Any
from langchain.tools import Tool
import re
from collections import Counter


class DataAnalysisTool:
    """
    Analyze data and extract insights.
    """
    
    def analyze_text_stats(self, text: str) -> str:
        """
        Analyze text and return statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Text statistics
        """
        # Basic stats
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Word frequency
        word_freq = Counter(word.lower() for word in words if len(word) > 3)
        top_words = word_freq.most_common(10)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        return f"""
Text Analysis Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Statistics:
  • Total words: {len(words)}
  • Total sentences: {len(sentences)}
  • Average word length: {avg_word_length:.1f} characters
  • Total characters: {len(text)}

🔤 Top 10 Words:
{chr(10).join(f"  {i+1}. {word}: {count} times" for i, (word, count) in enumerate(top_words))}

📈 Readability: {"Easy" if avg_word_length < 5 else "Moderate" if avg_word_length < 7 else "Complex"}
"""
    
    def analyze_numbers(self, numbers: List[float]) -> str:
        """
        Analyze a list of numbers.
        
        Args:
            numbers: List of numbers to analyze
            
        Returns:
            Statistical analysis
        """
        if not numbers:
            return "No numbers provided for analysis"
        
        sorted_nums = sorted(numbers)
        n = len(numbers)
        
        # Calculate statistics
        total = sum(numbers)
        mean = total / n
        median = sorted_nums[n // 2] if n % 2 else (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
        min_val = min(numbers)
        max_val = max(numbers)
        range_val = max_val - min_val
        
        return f"""
Numerical Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Statistics:
  • Count: {n}
  • Sum: {total:.2f}
  • Mean: {mean:.2f}
  • Median: {median:.2f}
  • Min: {min_val:.2f}
  • Max: {max_val:.2f}
  • Range: {range_val:.2f}

📈 Distribution:
  • Below average: {sum(1 for x in numbers if x < mean)} ({sum(1 for x in numbers if x < mean)/n*100:.1f}%)
  • Above average: {sum(1 for x in numbers if x > mean)} ({sum(1 for x in numbers if x > mean)/n*100:.1f}%)
"""
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="analyze_data",
            description="Analyze text or numerical data and extract statistical insights. Useful for reports and summaries.",
            func=self.analyze_text_stats
        )


class SentimentAnalysisTool:
    """
    Analyze sentiment of text.
    """
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis
        """
        # Simple sentiment analysis using keyword matching
        positive_words = ['good', 'great', 'excellent', 'happy', 'pleased', 'wonderful', 
                         'fantastic', 'amazing', 'love', 'best', 'success', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'sad', 'disappointed', 'poor', 
                         'worst', 'hate', 'failure', 'problem', 'issue', 'concern']
        urgent_words = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'now']
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        urgent_count = sum(1 for word in urgent_words if word in text_lower)
        
        # Determine overall sentiment
        if pos_count > neg_count:
            sentiment = "Positive"
            confidence = min(95, 60 + (pos_count - neg_count) * 10)
        elif neg_count > pos_count:
            sentiment = "Negative"
            confidence = min(95, 60 + (neg_count - pos_count) * 10)
        else:
            sentiment = "Neutral"
            confidence = 50
        
        urgency = "High" if urgent_count > 0 else "Low"
        
        return f"""
Sentiment Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
😊 Overall Sentiment: {sentiment}
📊 Confidence: {confidence}%
⚡ Urgency Level: {urgency}

📈 Indicators:
  • Positive signals: {pos_count}
  • Negative signals: {neg_count}
  • Urgent keywords: {urgent_count}

💡 Recommendation: {"Respond positively" if sentiment == "Positive" else "Address concerns carefully" if sentiment == "Negative" else "Standard response appropriate"}
"""
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="analyze_sentiment",
            description="Analyze the sentiment and emotional tone of text. Useful for emails, messages, and feedback.",
            func=self.analyze_sentiment
        )


class KeywordExtractionTool:
    """
    Extract keywords and key phrases from text.
    """
    
    def extract_keywords(self, text: str, top_n: int = 10) -> str:
        """
        Extract important keywords from text.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to return
            
        Returns:
            Extracted keywords
        """
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has'}
        
        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Filter and count
        filtered_words = [word for word in words if word not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = word_freq.most_common(top_n)
        
        # Extract potential phrases (2-word combinations)
        word_list = text.lower().split()
        phrases = [f"{word_list[i]} {word_list[i+1]}" 
                  for i in range(len(word_list)-1) 
                  if word_list[i] not in stop_words and word_list[i+1] not in stop_words]
        phrase_freq = Counter(phrases)
        top_phrases = phrase_freq.most_common(5)
        
        result = "Keywords Extracted:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += "🔑 Top Keywords:\n"
        for i, (keyword, count) in enumerate(top_keywords, 1):
            result += f"  {i}. {keyword} ({count} occurrences)\n"
        
        result += "\n📝 Key Phrases:\n"
        for i, (phrase, count) in enumerate(top_phrases, 1):
            result += f"  {i}. {phrase} ({count} occurrences)\n"
        
        return result
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="extract_keywords",
            description="Extract important keywords and phrases from text. Useful for summarization and topic identification.",
            func=self.extract_keywords
        )
