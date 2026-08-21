# Random routing scoring

Do not use pure random if maps differ in health and capacity.

Example:

```python
eligible = [
    m for m in maps
    if m.enabled
    and m.runtime_id == player.runtime_id
    and m.random_eligible
    and m.free_slots >= party_size
]

for m in eligible:
    score = (
        m.weight
        * freshness_factor(m)
        * health_factor(m)
        * capacity_factor(m)
        * novelty_factor(player, m)
    )

selected = weighted_random(eligible, score)
```

This lets you prefer:

```text
healthy
underused
new
not recently visited
community-promoted
```

without violating compatibility.

---
