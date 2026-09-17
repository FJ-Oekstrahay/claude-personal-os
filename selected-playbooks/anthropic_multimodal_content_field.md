---
name: Anthropic Multimodal Content Field Handling
description: Messages API content field can be string or list of content blocks; text extraction requires helper function
type: feedback
---

## Rule

In the Anthropic Messages API, the `content` field can be:
- A string (text-only messages)
- A list of content blocks (multimodal messages with text + images)

Any code that assumes `content` is always a string will fail when processing multimodal messages. This includes:
- Serialization/JSON encoding
- Classification routing (checking message text to route to correct handler)
- LLM context extraction
- Logging/debugging output

**Solution:** Extract text from content field using a helper function that handles both cases.

## Why

Session 2026-04-22: Added image upload to `dt agent`. The proxy code and classification logic both broke because they assumed `message['content']` was a string. The Anthropic API spec allows both string and list; client code must normalize for text extraction.

## How to apply

Create a utility function early when adding multimodal support:

```python
def extract_text_from_content(content):
    """Extract text from message content field.
    
    Content can be either:
    - str: text-only message
    - list: multimodal with text and/or image blocks
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                texts.append(block.get('text', ''))
        return ''.join(texts)
    return ''
```

Apply this everywhere content text is needed:
- Logging: `text = extract_text_from_content(msg['content'])`
- Classification: `if "keyword" in extract_text_from_content(msg['content']):`
- JSON serialization: convert before writing to files

**Timing:** Implement at the boundary where messages enter the system (API client, proxy), not throughout the codebase.
