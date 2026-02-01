from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from config import settings


class MemoryManager:
    """Manages long-term memory using Pinecone vector store"""
    
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.index_name = settings.PINECONE_INDEX_NAME
        self._ensure_index_exists()
        # Connect to index using host
        self.index = self.pc.Index(name=self.index_name, host=settings.PINECONE_HOST)
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist"""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-west-2"
                )
            )
    
    async def store_context(
        self,
        context_id: str,
        context_type: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Store context in vector memory"""
        try:
            # Generate embedding
            embedding = await self.embeddings.aembed_query(content)
            
            # Prepare metadata
            full_metadata = {
                "context_id": context_id,
                "context_type": context_type,
                "timestamp": datetime.now().isoformat(),
                "content": content[:1000],  # Store truncated content in metadata
                **metadata
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": f"{context_type}_{context_id}_{datetime.now().timestamp()}",
                    "values": embedding,
                    "metadata": full_metadata
                }]
            )
            
            return True
        except Exception as e:
            print(f"Error storing context: {e}")
            return False
    
    async def retrieve_similar_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve similar contexts from memory"""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Build filter
            filter_dict = {}
            if context_type:
                filter_dict["context_type"] = {"$eq": context_type}
            if filter_metadata:
                filter_dict.update(filter_metadata)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # Format results
            contexts = []
            for match in results.matches:
                contexts.append({
                    "score": match.score,
                    "metadata": match.metadata,
                    "id": match.id
                })
            
            return contexts
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    async def store_email_context(self, email_id: str, email_data: Dict[str, Any]):
        """Store email in memory"""
        content = f"Email from {email_data.get('sender')} about {email_data.get('subject')}: {email_data.get('body', '')}"
        await self.store_context(
            context_id=email_id,
            context_type="email",
            content=content,
            metadata={
                "sender": email_data.get("sender"),
                "subject": email_data.get("subject"),
                "priority": email_data.get("priority", "medium")
            }
        )
    
    async def store_meeting_context(self, meeting_id: str, meeting_data: Dict[str, Any]):
        """Store meeting in memory"""
        content = f"Meeting: {meeting_data.get('title')} with {', '.join(meeting_data.get('attendees', []))}"
        await self.store_context(
            context_id=meeting_id,
            context_type="meeting",
            content=content,
            metadata={
                "title": meeting_data.get("title"),
                "attendees": json.dumps(meeting_data.get("attendees", [])),
                "date": meeting_data.get("start_time")
            }
        )
    
    async def store_task_context(self, task_id: str, task_data: Dict[str, Any]):
        """Store task in memory"""
        content = f"Task: {task_data.get('title')} - {task_data.get('description')}"
        await self.store_context(
            context_id=task_id,
            context_type="task",
            content=content,
            metadata={
                "title": task_data.get("title"),
                "priority": task_data.get("priority", "medium"),
                "status": task_data.get("status", "todo")
            }
        )
    
    async def store_document_context(self, doc_id: str, doc_data: Dict[str, Any]):
        """Store document in memory"""
        content = f"Document: {doc_data.get('title')} - {doc_data.get('content', '')}"
        await self.store_context(
            context_id=doc_id,
            context_type="document",
            content=content,
            metadata={
                "title": doc_data.get("title"),
                "file_type": doc_data.get("file_type"),
                "tags": json.dumps(doc_data.get("tags", []))
            }
        )
    
    async def get_project_context(self, project_name: str) -> Dict[str, Any]:
        """Get all context related to a project"""
        # Search for related items
        emails = await self.retrieve_similar_context(
            query=project_name,
            context_type="email",
            top_k=5
        )
        
        meetings = await self.retrieve_similar_context(
            query=project_name,
            context_type="meeting",
            top_k=5
        )
        
        tasks = await self.retrieve_similar_context(
            query=project_name,
            context_type="task",
            top_k=5
        )
        
        documents = await self.retrieve_similar_context(
            query=project_name,
            context_type="document",
            top_k=5
        )
        
        return {
            "emails": emails,
            "meetings": meetings,
            "tasks": tasks,
            "documents": documents
        }
    
    async def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Store learned behavior patterns"""
        content = f"User pattern: {pattern_type} - {json.dumps(pattern_data)}"
        await self.store_context(
            context_id=f"pattern_{datetime.now().timestamp()}",
            context_type="pattern",
            content=content,
            metadata={
                "pattern_type": pattern_type,
                **pattern_data
            }
        )


# Singleton instance
memory_manager = MemoryManager()
