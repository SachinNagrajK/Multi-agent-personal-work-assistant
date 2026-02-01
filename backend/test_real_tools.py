"""Test real Gmail and Calendar tools."""
import sys
sys.path.append('..')

from tools.gmail_tools import (
    gmail_read_recent,
    gmail_get_unread_count,
    gmail_search
)
from tools.calendar_tools import (
    calendar_get_today_schedule,
    calendar_list_events
)

print("=" * 70)
print("Testing Real Google API Tools")
print("=" * 70)

# Test Gmail
print("\n📧 Testing Gmail Tools...")
print("-" * 70)

print("\n1. Getting unread count...")
result = gmail_get_unread_count.invoke({})
print(result)

print("\n2. Reading recent emails (last 5)...")
result = gmail_read_recent.invoke({"max_results": 5})
print(result[:500] + "..." if len(result) > 500 else result)

# Test Calendar
print("\n\n📅 Testing Calendar Tools...")
print("-" * 70)

print("\n1. Getting today's schedule...")
result = calendar_get_today_schedule.invoke({})
print(result)

print("\n2. Listing upcoming events (next 7 days)...")
result = calendar_list_events.invoke({"days_ahead": 7, "max_results": 5})
print(result[:500] + "..." if len(result) > 500 else result)

print("\n" + "=" * 70)
print("✅ All tests completed!")
print("=" * 70)
