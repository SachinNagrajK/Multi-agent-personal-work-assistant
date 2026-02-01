"""
Guardrails system for safe multi-agent operations.
Prevents dangerous actions, detects sensitive content, enforces policies.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from langchain_core.messages import BaseMessage, AIMessage


class GuardrailsSystem:
    """Comprehensive guardrails for agent safety."""
    
    # Sensitive content patterns
    SENSITIVE_PATTERNS = {
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "password": r"password[\s:=]+[\w@#$%]+",
        "api_key": r"[Aa][Pp][Ii]_?[Kk][Ee][Yy][\s:=]+[\w-]+",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    }
    
    # Dangerous action keywords
    DANGEROUS_KEYWORDS = [
        "delete all",
        "remove all",
        "drop table",
        "truncate",
        "format drive"
    ]
    
    # Rate limits per operation type
    RATE_LIMITS = {
        "email_send": {"count": 10, "window": 3600},  # 10 per hour
        "calendar_create": {"count": 20, "window": 3600},  # 20 per hour
        "api_calls": {"count": 100, "window": 60},  # 100 per minute
    }
    
    def __init__(self):
        self.triggered_guardrails: List[Dict[str, Any]] = []
        self.action_history: List[Dict[str, Any]] = []
    
    def check_sensitive_content(self, text: str) -> Dict[str, Any]:
        """
        Scan text for sensitive information.
        
        Returns:
            dict with 'detected' (bool) and 'patterns' (list)
        """
        detected_patterns = []
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_patterns.append({
                    "type": pattern_name,
                    "count": len(matches)
                })
        
        return {
            "detected": len(detected_patterns) > 0,
            "patterns": detected_patterns
        }
    
    def check_dangerous_action(self, action: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if action is potentially dangerous.
        
        Returns:
            dict with 'dangerous' (bool) and 'reason' (str)
        """
        # Check action text for dangerous keywords
        action_text = f"{action} {str(args)}".lower()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in action_text:
                return {
                    "dangerous": True,
                    "reason": f"Contains dangerous keyword: '{keyword}'",
                    "severity": "high"
                }
        
        # Check for bulk operations
        if "delete" in action and any(k in args for k in ["all", "multiple", "batch"]):
            return {
                "dangerous": True,
                "reason": "Bulk delete operation detected",
                "severity": "medium"
            }
        
        # Check for file system operations
        if action in ["file_delete", "file_write"] and ".." in str(args):
            return {
                "dangerous": True,
                "reason": "Potential directory traversal attack",
                "severity": "high"
            }
        
        return {"dangerous": False, "reason": None, "severity": "none"}
    
    def check_rate_limit(self, operation_type: str) -> Dict[str, Any]:
        """
        Check if operation is within rate limits.
        
        Returns:
            dict with 'allowed' (bool) and 'reset_time' (optional)
        """
        if operation_type not in self.RATE_LIMITS:
            return {"allowed": True, "reason": "No limit defined"}
        
        limit_config = self.RATE_LIMITS[operation_type]
        window = limit_config["window"]
        max_count = limit_config["count"]
        
        # Count recent actions of this type
        now = datetime.now()
        recent_actions = [
            a for a in self.action_history
            if a["type"] == operation_type and
            (now - a["timestamp"]).total_seconds() < window
        ]
        
        if len(recent_actions) >= max_count:
            return {
                "allowed": False,
                "reason": f"Rate limit exceeded: {max_count} per {window}s",
                "reset_time": recent_actions[0]["timestamp"]
            }
        
        return {"allowed": True, "remaining": max_count - len(recent_actions)}
    
    def check_email_send(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Comprehensive checks for email sending.
        
        Returns:
            dict with 'approved' (bool), 'warnings' (list), 'requires_human' (bool)
        """
        warnings = []
        requires_human = False
        
        # Check sensitive content in body
        sensitive_check = self.check_sensitive_content(body)
        if sensitive_check["detected"]:
            warnings.append(f"⚠️ Sensitive content detected: {sensitive_check['patterns']}")
            requires_human = True
        
        # Check rate limit
        rate_check = self.check_rate_limit("email_send")
        if not rate_check["allowed"]:
            warnings.append(f"🚫 {rate_check['reason']}")
            return {
                "approved": False,
                "warnings": warnings,
                "requires_human": False,
                "reason": "Rate limit exceeded"
            }
        
        # Check recipient
        if not self._is_valid_email(to):
            warnings.append(f"❌ Invalid email address: {to}")
            return {
                "approved": False,
                "warnings": warnings,
                "requires_human": False,
                "reason": "Invalid recipient"
            }
        
        # Check for mass emailing
        if "," in to or ";" in to:
            recipients = [r.strip() for r in re.split("[,;]", to)]
            if len(recipients) > 5:
                warnings.append(f"⚠️ Mass email to {len(recipients)} recipients")
                requires_human = True
        
        # Log action
        self.action_history.append({
            "type": "email_send",
            "timestamp": datetime.now(),
            "to": to
        })
        
        return {
            "approved": True,
            "warnings": warnings,
            "requires_human": requires_human
        }
    
    def check_calendar_operation(self, operation: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check calendar operations for safety.
        
        Returns:
            dict with 'approved' (bool), 'warnings' (list)
        """
        warnings = []
        
        # Check rate limit
        if operation == "create":
            rate_check = self.check_rate_limit("calendar_create")
            if not rate_check["allowed"]:
                return {
                    "approved": False,
                    "warnings": [f"🚫 {rate_check['reason']}"]
                }
        
        # Log action
        self.action_history.append({
            "type": "calendar_create",
            "timestamp": datetime.now()
        })
        
        return {
            "approved": True,
            "warnings": warnings
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    def get_status_report(self) -> str:
        """Get current guardrails status."""
        return f"""Guardrails Status:
- Total checks performed: {len(self.action_history)}
- Guardrails triggered: {len(self.triggered_guardrails)}
- Recent actions (last 10):
{self._format_recent_actions()}
"""
    
    def _format_recent_actions(self) -> str:
        """Format recent actions for display."""
        if not self.action_history:
            return "  None"
        
        recent = self.action_history[-10:]
        return "\n".join([
            f"  - {a['type']} at {a['timestamp'].strftime('%H:%M:%S')}"
            for a in recent
        ])


# Singleton instance
guardrails = GuardrailsSystem()


def apply_guardrails(action: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all relevant guardrails to an action.
    
    Args:
        action: Action name (e.g., 'gmail_send_email', 'user_request')
        args: Action arguments
    
    Returns:
        Guardrail check results
    """
    # For user requests, only check for dangerous actions, not sensitive content
    # (email addresses, etc. are expected in normal user input)
    if action == "user_request":
        text_to_check = str(args.get("input", ""))
        dangerous = guardrails.check_dangerous_action(action, args)
        
        # Check for critical sensitive data (passwords, credit cards, SSN)
        critical_patterns = ["credit_card", "ssn", "password", "api_key"]
        has_critical = False
        for pattern_name in critical_patterns:
            pattern = guardrails.SENSITIVE_PATTERNS.get(pattern_name, "")
            if pattern and re.search(pattern, text_to_check, re.IGNORECASE):
                has_critical = True
                break
        
        return {
            "approved": not dangerous["dangerous"] and not has_critical,
            "reason": dangerous.get("reason", "Contains sensitive data like passwords or credit cards") if (dangerous["dangerous"] or has_critical) else None,
            "warnings": [],
            "requires_human": False
        }
    
    # Sensitive content check for actual operations
    text_to_check = str(args)
    sensitive = guardrails.check_sensitive_content(text_to_check)
    
    # Dangerous action check
    dangerous = guardrails.check_dangerous_action(action, args)
    
    # Specific checks based on action type
    if action == "gmail_send_email":
        email_check = guardrails.check_email_send(
            args.get("to", ""),
            args.get("subject", ""),
            args.get("body", "")
        )
        return email_check
    
    elif action in ["calendar_create_event", "calendar_delete_event"]:
        return guardrails.check_calendar_operation(
            "create" if "create" in action else "delete",
            args
        )
    
    # Default checks
    return {
        "approved": not dangerous["dangerous"] and not sensitive["detected"],
        "warnings": [
            dangerous["reason"] if dangerous["dangerous"] else None,
            f"Sensitive content: {sensitive['patterns']}" if sensitive["detected"] else None
        ],
        "requires_human": dangerous["dangerous"] or sensitive["detected"]
    }


__all__ = ["GuardrailsSystem", "guardrails", "apply_guardrails"]
