from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid


class DemoDataGenerator:
    """Generate realistic demo data for the workspace assistant"""
    
    @staticmethod
    def generate_emails() -> List[Dict[str, Any]]:
        """Generate demo emails"""
        emails = [
            {
                "id": str(uuid.uuid4()),
                "subject": "URGENT: Q1 Revenue Report Due Tomorrow",
                "sender": "cfo@company.com",
                "recipient": "you@company.com",
                "body": "Hi, We need the Q1 revenue report submitted by EOD tomorrow for the board meeting. Please include the regional breakdowns and forecast adjustments. Let me know if you have any questions. Thanks!",
                "timestamp": datetime.now() - timedelta(hours=2),
                "priority": "urgent",
                "status": "unread"
            },
            {
                "id": str(uuid.uuid4()),
                "subject": "Project Phoenix - Status Update",
                "sender": "sarah.johnson@company.com",
                "recipient": "you@company.com",
                "body": "Hey! Just wanted to check in on the Phoenix project. Are we still on track for the March deadline? The client is asking for an update. Also, Bob mentioned some API issues - have those been resolved?",
                "timestamp": datetime.now() - timedelta(hours=5),
                "priority": "high",
                "status": "unread"
            },
            {
                "id": str(uuid.uuid4()),
                "subject": "Team Lunch Friday?",
                "sender": "mike.chen@company.com",
                "recipient": "you@company.com",
                "body": "Hey team, want to grab lunch this Friday at the new Thai place? Let me know if you're in!",
                "timestamp": datetime.now() - timedelta(hours=8),
                "priority": "low",
                "status": "unread"
            },
            {
                "id": str(uuid.uuid4()),
                "subject": "Meeting Notes - Product Roadmap Review",
                "sender": "product@company.com",
                "recipient": "you@company.com",
                "body": "Hi all, Attached are the notes from yesterday's roadmap review. Key takeaways: 1) AI features moving to Q2, 2) Mobile app priority increased, 3) Need resource allocation plan by next week.",
                "timestamp": datetime.now() - timedelta(days=1),
                "priority": "medium",
                "status": "unread"
            },
            {
                "id": str(uuid.uuid4()),
                "subject": "Interview Candidate - Alex Rivera",
                "sender": "hr@company.com",
                "recipient": "you@company.com",
                "body": "Please review Alex Rivera's resume for the Senior Engineer position. Interview scheduled for next Tuesday at 2 PM. Let me know your thoughts on their experience with distributed systems.",
                "timestamp": datetime.now() - timedelta(hours=12),
                "priority": "high",
                "status": "unread"
            }
        ]
        return emails
    
    @staticmethod
    def generate_calendar_events() -> List[Dict[str, Any]]:
        """Generate demo calendar events"""
        now = datetime.now()
        
        events = [
            {
                "id": str(uuid.uuid4()),
                "title": "1:1 with Sarah - Project Phoenix",
                "start_time": now.replace(hour=10, minute=0, second=0, microsecond=0),
                "end_time": now.replace(hour=10, minute=30, second=0, microsecond=0),
                "attendees": ["sarah.johnson@company.com", "you@company.com"],
                "description": "Weekly check-in on Project Phoenix progress",
                "location": "Conference Room A"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Q1 Board Meeting Prep",
                "start_time": now.replace(hour=14, minute=0, second=0, microsecond=0),
                "end_time": now.replace(hour=15, minute=30, second=0, microsecond=0),
                "attendees": ["cfo@company.com", "ceo@company.com", "you@company.com"],
                "description": "Prepare materials for board meeting. Review financials and projections.",
                "location": "Executive Suite"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Engineering Team Stand-up",
                "start_time": (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0),
                "end_time": (now + timedelta(days=1)).replace(hour=9, minute=15, second=0, microsecond=0),
                "attendees": ["eng-team@company.com"],
                "description": "Daily team sync",
                "location": "Zoom"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Product Roadmap Planning",
                "start_time": (now + timedelta(days=2)).replace(hour=13, minute=0, second=0, microsecond=0),
                "end_time": (now + timedelta(days=2)).replace(hour=15, minute=0, second=0, microsecond=0),
                "attendees": ["product@company.com", "eng-leads@company.com", "you@company.com"],
                "description": "Q2 roadmap planning session",
                "location": "Conference Room B"
            }
        ]
        return events
    
    @staticmethod
    def generate_tasks() -> List[Dict[str, Any]]:
        """Generate demo tasks"""
        now = datetime.now()
        
        tasks = [
            {
                "id": str(uuid.uuid4()),
                "title": "Complete Q1 Revenue Report",
                "description": "Compile revenue data, regional breakdowns, and forecast adjustments for board meeting",
                "priority": "urgent",
                "status": "in_progress",
                "due_date": now + timedelta(days=1),
                "dependencies": [],
                "created_at": now - timedelta(days=3),
                "updated_at": now - timedelta(hours=2),
                "related_emails": [],
                "related_documents": []
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Review Alex Rivera's Resume",
                "description": "Evaluate candidate for Senior Engineer position, focus on distributed systems experience",
                "priority": "high",
                "status": "todo",
                "due_date": now + timedelta(days=2),
                "dependencies": [],
                "created_at": now - timedelta(hours=12),
                "updated_at": now - timedelta(hours=12),
                "related_emails": [],
                "related_documents": []
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Fix Project Phoenix API Issues",
                "description": "Resolve API integration problems blocking client demo",
                "priority": "high",
                "status": "blocked",
                "due_date": now + timedelta(days=5),
                "dependencies": ["infrastructure-update"],
                "created_at": now - timedelta(days=2),
                "updated_at": now - timedelta(hours=5),
                "related_emails": [],
                "related_documents": []
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Resource Allocation Plan for Q2",
                "description": "Create resource plan for Q2 roadmap priorities",
                "priority": "medium",
                "status": "todo",
                "due_date": now + timedelta(days=7),
                "dependencies": [],
                "created_at": now - timedelta(days=1),
                "updated_at": now - timedelta(days=1),
                "related_emails": [],
                "related_documents": []
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Update Team Wiki Documentation",
                "description": "Add new onboarding materials and update API docs",
                "priority": "low",
                "status": "todo",
                "due_date": now + timedelta(days=14),
                "dependencies": [],
                "created_at": now - timedelta(days=5),
                "updated_at": now - timedelta(days=5),
                "related_emails": [],
                "related_documents": []
            }
        ]
        return tasks
    
    @staticmethod
    def generate_documents() -> List[Dict[str, Any]]:
        """Generate demo documents"""
        now = datetime.now()
        
        documents = [
            {
                "id": str(uuid.uuid4()),
                "title": "Q4 2025 Performance Review",
                "content": "Overall strong performance. Key achievements: Led Project Phoenix to successful beta launch, improved API response time by 40%, mentored 2 junior engineers. Areas for growth: Improve communication with stakeholders, delegate more effectively.",
                "file_type": "pdf",
                "created_at": now - timedelta(days=30),
                "updated_at": now - timedelta(days=30),
                "tags": ["performance", "review", "2025"]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Project Phoenix - Technical Spec",
                "content": "Architecture: Microservices-based system with React frontend, Python backend (FastAPI), PostgreSQL database. Key features: Real-time data sync, AI-powered recommendations, multi-tenant support. Timeline: 3 months development, 1 month testing.",
                "file_type": "markdown",
                "created_at": now - timedelta(days=60),
                "updated_at": now - timedelta(days=10),
                "tags": ["project-phoenix", "technical", "spec"]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Company OKRs Q1 2026",
                "content": "Objective 1: Grow revenue by 30%. KR1: Acquire 50 new enterprise customers. KR2: Increase average deal size by 20%. Objective 2: Improve product quality. KR1: Reduce bug count by 40%. KR2: Achieve 95% uptime.",
                "file_type": "pdf",
                "created_at": now - timedelta(days=15),
                "updated_at": now - timedelta(days=15),
                "tags": ["okrs", "goals", "2026"]
            }
        ]
        return documents
    
    @staticmethod
    def get_demo_data() -> Dict[str, List[Dict[str, Any]]]:
        """Get all demo data"""
        return {
            "emails": DemoDataGenerator.generate_emails(),
            "calendar_events": DemoDataGenerator.generate_calendar_events(),
            "tasks": DemoDataGenerator.generate_tasks(),
            "documents": DemoDataGenerator.generate_documents()
        }


# Singleton instance
demo_data = DemoDataGenerator()
