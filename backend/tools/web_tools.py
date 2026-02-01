"""
Web-related tools for agents.
"""

import os
import re
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
import requests
from bs4 import BeautifulSoup


class TavilySearchTool:
    """
    Web search using Tavily API.
    Tavily is optimized for AI agents and LLM applications.
    """
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        self.api_url = "https://api.tavily.com/search"
    
    def _mock_search(self, query: str) -> Dict[str, Any]:
        """Mock search results for demo purposes."""
        return {
            "results": [
                {
                    "title": f"Sample Result for '{query}'",
                    "url": "https://example.com/result1",
                    "content": f"This is a sample search result about {query}. "
                              f"In a production environment, this would contain real web search results from Tavily.",
                    "score": 0.95
                },
                {
                    "title": f"Another Result - {query}",
                    "url": "https://example.com/result2",
                    "content": f"Additional information about {query}. "
                              f"Tavily provides AI-optimized search results with high relevance.",
                    "score": 0.87
                }
            ],
            "query": query
        }
    
    def _format_mock_results(self, query: str) -> str:
        """Format mock results as fallback."""
        results = self._mock_search(query)
        formatted = f"Search results for: {query}\n\n"
        for i, result in enumerate(results.get("results", []), 1):
            formatted += f"{i}. {result.get('title', 'No title')}\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n"
            formatted += f"   {result.get('content', 'No content')[:200]}...\n\n"
        return formatted
    
    def search_web(self, query: str, max_results: int = 5) -> str:
        """
        Search the web using Tavily.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Formatted search results
        """
        try:
            if self.tavily_api_key:
                # Use real Tavily API
                payload = {
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "max_results": max_results
                }
                response = requests.post(self.api_url, json=payload, timeout=10)
                response.raise_for_status()
                results = response.json()
            else:
                # Use mock data
                results = self._mock_search(query)
            
            # Format results
            formatted = f"Search results for: {query}\n\n"
            for i, result in enumerate(results.get("results", []), 1):
                formatted += f"{i}. {result.get('title', 'No title')}\n"
                formatted += f"   URL: {result.get('url', 'No URL')}\n"
                formatted += f"   {result.get('content', 'No content')[:200]}...\n\n"
            
            return formatted
        except Exception as e:
            # Fallback to mock on any error
            return self._format_mock_results(query)
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="web_search",
            description="Search the web for current information. Use this when you need recent data, facts, or information not in your training data.",
            func=self.search_web
        )


class WebScraperTool:
    """
    Web page scraping tool.
    Extracts content from web pages.
    """
    
    def scrape_url(self, url: str) -> str:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Extracted text content
        """
        try:
            # Add user agent to avoid blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit length
            if len(text) > 5000:
                text = text[:5000] + "... (truncated)"
            
            return f"Content from {url}:\n\n{text}"
            
        except Exception as e:
            return f"Failed to scrape {url}: {str(e)}"
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="scrape_webpage",
            description="Scrape and extract text content from a web page. Use when you need to read the full content of a specific URL.",
            func=self.scrape_url
        )


class URLExtractorTool:
    """
    Extract and validate URLs from text.
    """
    
    def extract_urls(self, text: str) -> str:
        """
        Extract all URLs from text.
        
        Args:
            text: Text to extract URLs from
            
        Returns:
            List of URLs found
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        if urls:
            return "Found URLs:\n" + "\n".join(f"- {url}" for url in urls)
        else:
            return "No URLs found in the text."
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="extract_urls",
            description="Extract all URLs from a text. Use when you need to find links in emails, documents, or messages.",
            func=self.extract_urls
        )
