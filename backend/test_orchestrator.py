"""
Test the modern orchestrator with multi-agent coordination.
"""
import sys
sys.path.append('..')

from orchestrator_modern import WorkspaceOrchestrator

print("=" * 70)
print("Testing Modern Multi-Agent Orchestrator")
print("=" * 70)

orchestrator = WorkspaceOrchestrator()

# Test 1: Email request
print("\n1. Testing Email Agent Routing...")
print("-" * 70)
result = orchestrator.process_request("Check my recent emails and tell me what's urgent")
print(result)

# Test 2: Calendar request
print("\n\n2. Testing Calendar Agent Routing...")
print("-" * 70)
result = orchestrator.process_request("What's on my calendar today?")
print(result)

# Test 3: Combined request (should use both agents)
print("\n\n3. Testing Multi-Agent Coordination...")
print("-" * 70)
result = orchestrator.process_request("Check my emails and calendar for today")
print(result)

# Test 4: Loop prevention
print("\n\n4. Testing Loop Prevention...")
print("-" * 70)
# This would normally cause issues, but orchestrator should prevent loops
result = orchestrator.process_request("Check my emails about calendar events about emails")
print(result)

# Show stats
print("\n\n" + "=" * 70)
print("Session Statistics:")
print("=" * 70)
print(orchestrator.get_session_stats())

print("\n✅ All orchestrator tests completed!")
print("=" * 70)
