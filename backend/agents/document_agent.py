from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from memory import memory_manager
from config import settings
from tools.web_tools import TavilySearchTool, WebScraperTool
from tools.file_tools import FileReadTool, FileWriteTool, FileSearchTool
from tools.analysis_tools import DataAnalysisTool, KeywordExtractionTool
from schemas import DocumentAnalysis
import json


class DocumentAgent:
    """Handles document summarization, Q&A, and analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create structured output LLM
        self.analysis_llm = self.llm.with_structured_output(DocumentAnalysis)
        
        # Initialize tools
        self.search_tool = TavilySearchTool()
        self.web_scraper = WebScraperTool()
        self.file_reader = FileReadTool()
        self.file_writer = FileWriteTool()
        self.file_search = FileSearchTool()
        self.data_analyzer = DataAnalysisTool()
        self.keyword_extractor = KeywordExtractionTool()
    
    async def summarize_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive summary of a document"""
        
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document analysis assistant. Create a comprehensive summary including:
1. Main summary (2-3 sentences)
2. Key points (bullet points)
3. Main topics/themes
4. Overall sentiment/tone
5. Important dates, numbers, or deadlines mentioned

Return JSON format:
{
    "summary": "main summary",
    "key_points": ["point1", "point2", "point3"],
    "topics": ["topic1", "topic2"],
    "sentiment": "positive|negative|neutral|mixed",
    "important_details": {
        "dates": ["date1"],
        "numbers": ["number1"],
        "deadlines": ["deadline1"]
    }
}"""),
            ("user", "Document Title: {title}\n\nContent:\n{content}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                summary_prompt.format_messages(
                    title=document.get("title", "Untitled"),
                    content=document.get("content", "")[:8000]  # Truncate very long docs
                )
            )
            
            result = extract_json_from_response(response.content)
            
            # Store in memory
            await memory_manager.store_document_context(
                doc_id=document["id"],
                doc_data={
                    **document,
                    "summary": result["summary"],
                    "topics": result["topics"]
                }
            )
            
            return {
                "document_id": document["id"],
                "document_title": document.get("title"),
                "summary_result": result
            }
            
        except Exception as e:
            print(f"Error summarizing document: {e}")
            return {
                "document_id": document["id"],
                "document_title": document.get("title"),
                "summary_result": {
                    "summary": "Unable to summarize",
                    "key_points": [],
                    "topics": [],
                    "sentiment": "unknown"
                },
                "error": str(e)
            }
    
    async def answer_question_about_document(
        self,
        question: str,
        document: Dict[str, Any]
    ) -> str:
        """Answer a question about a specific document"""
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that answers questions about documents. Be concise and accurate."),
            ("user", """Document: {title}
Content: {content}

Question: {question}

Provide a clear, concise answer based only on the document content.""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                qa_prompt.format_messages(
                    title=document.get("title", ""),
                    content=document.get("content", "")[:8000],
                    question=question
                )
            )
            
            return response.content
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return f"I couldn't answer that question. Error: {str(e)}"
    
    async def find_relevant_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find documents relevant to a query"""
        
        # Use memory to find similar documents
        similar = await memory_manager.retrieve_similar_context(
            query=query,
            context_type="document",
            top_k=5
        )
        
        # Also use LLM for relevance scoring
        if not similar and documents:
            relevance_prompt = ChatPromptTemplate.from_messages([
                ("system", """Rate the relevance of each document to the query on a scale of 0-10.
Return JSON array: [{"document_id": "id", "relevance_score": 8, "reason": "why relevant"}, ...]"""),
                ("user", """Query: {query}

Documents:
{documents}""")
            ])
            
            try:
                response = await self.llm.ainvoke(
                    relevance_prompt.format_messages(
                        query=query,
                        documents=json.dumps([{
                            "id": d.get("id"),
                            "title": d.get("title"),
                            "content_preview": d.get("content", "")[:200]
                        } for d in documents[:20]])
                    )
                )
                
                scores = extract_json_from_response(response.content)
                # Sort by relevance
                scores.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                return scores[:5]
                
            except Exception as e:
                print(f"Error finding relevant documents: {e}")
                return []
        
        return similar
    
    async def extract_key_information(
        self,
        document: Dict[str, Any],
        information_type: str
    ) -> Dict[str, Any]:
        """Extract specific types of information from document"""
        
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Extract {information_type} from the document.
Return structured JSON with the extracted information."""),
            ("user", "Document: {title}\n\nContent:\n{content}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                extract_prompt.format_messages(
                    title=document.get("title", ""),
                    content=document.get("content", "")[:8000]
                )
            )
            
            result = extract_json_from_response(response.content)
            return result
            
        except Exception as e:
            print(f"Error extracting information: {e}")
            return {"error": str(e)}
    
    async def compare_documents(
        self,
        doc1: Dict[str, Any],
        doc2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two documents and highlight differences/similarities"""
        
        compare_prompt = ChatPromptTemplate.from_messages([
            ("system", """Compare these two documents and provide:
1. Main similarities
2. Key differences
3. Which document is more comprehensive
4. Recommendation on which to use when

Return JSON format:
{
    "similarities": ["sim1", "sim2"],
    "differences": ["diff1", "diff2"],
    "comparison_summary": "overall comparison",
    "recommendation": "when to use each"
}"""),
            ("user", """Document 1: {title1}
{content1}

Document 2: {title2}
{content2}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                compare_prompt.format_messages(
                    title1=doc1.get("title", ""),
                    content1=doc1.get("content", "")[:4000],
                    title2=doc2.get("title", ""),
                    content2=doc2.get("content", "")[:4000]
                )
            )
            
            result = extract_json_from_response(response.content)
            return result
            
        except Exception as e:
            print(f"Error comparing documents: {e}")
            return {
                "similarities": [],
                "differences": [],
                "comparison_summary": "Unable to compare",
                "error": str(e)
            }


# Singleton instance
document_agent = DocumentAgent()
