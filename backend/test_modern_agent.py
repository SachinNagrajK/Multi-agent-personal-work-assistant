"""Test modern email agent with real Gmail."""
import sys
sys.path.append('..')

from agents.email_agent_modern import EmailAgent

print("=" * 70)
print("Testing Modern Email Agent")
print("=" * 70)

agent = EmailAgent()

# Test 1: Triage emails
print("\n1. Testing Email Triage...")
print("-" * 70)
result = agent.triage_emails(max_emails=5)
print(result)

print("\n" + "=" * 70)
print("✅ Test completed!")
print("=" * 70)
