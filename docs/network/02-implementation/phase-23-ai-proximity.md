# Phase 23 — Add AI proximity chat

Keep AI bots as special actors, not every MineColonies citizen.

Input gate:

```text
chat event
    ↓
same backend?
    ↓
same dimension?
    ↓
sender entity loaded?
    ↓
distance <= hearing radius?
    ↓
LLM
```

Example:

```python
if sender.backend_id != bot.backend_id:
    return

if sender.dimension != bot.dimension:
    return

if distance(sender.position, bot.position) > 12:
    return

respond_with_llm()
```

Presence/network state can tell you **where** the bot/player is. Actual entity distance should be computed by the backend bot/mod where positions are authoritative.