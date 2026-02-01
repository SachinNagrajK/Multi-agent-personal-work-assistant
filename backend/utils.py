"""
Utility functions for the application.
"""

import json
import re


def extract_json_from_response(response_text: str) -> dict:
    """
    Extract JSON from LLM response that may contain markdown code blocks or extra formatting.
    
    Handles cases like:
    ```json
    {...}
    ```
    
    Or plain JSON:
    {...}
    
    Or JSON with extra whitespace/newlines
    """
    # DEBUG: Print raw response
    print(f"DEBUG - Raw response text (first 200 chars): {repr(response_text[:200])}")
    
    # Get the text content
    text = response_text.strip()
    
    # Remove markdown code block markers (both ```json and plain ```)
    text = re.sub(r'^```(?:json)?\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()
    
    print(f"DEBUG - After markdown removal (first 200 chars): {repr(text[:200])}")
    
    # Try to find JSON object in the text (handles cases with extra text before/after)
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    print(f"DEBUG - Final text to parse (first 200 chars): {repr(text[:200])}")
    
    # Parse JSON
    try:
        result = json.loads(text)
        print(f"DEBUG - Successfully parsed JSON")
        return result
    except json.JSONDecodeError as e:
        print(f"DEBUG - First parse failed: {e}")
        # If parsing fails, try to extract just the JSON part more aggressively
        # Look for content between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            print(f"DEBUG - Trying fallback with: {repr(text[:200])}")
            return json.loads(text)
        else:
            raise e

