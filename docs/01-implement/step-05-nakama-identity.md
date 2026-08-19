# Step 5 — Nakama identity mapping

Bring Nakama into the network as the social identity layer, and map each authenticated Minecraft identity to a stable Nakama identity.

## Goal

Every authenticated player has a stable, unique Nakama identity tied to their Minecraft UUID, forming the base for friends/parties (Step 6).

## Tasks

### 1. Deploy Nakama

Nakama 3.40.0 with CockroachDB as its backing store.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nakama
  namespace: minecraft-system
spec:
  selector:
    matchLabels:
      app: nakama
  template:
    metadata:
      labels:
        app: nakama
    spec:
      containers:
        - name: nakama
          image: heroiclabs/nakama:3.40.0
          env:
            - name: DB_SERVER
              value: "cockroachdb:26257"
            - name: DB_USER
              value: "root"
            - name: DB_PASSWORD
              value: "root"
```

CockroachDB runs as a separate stateful service (see Operations).

### 2. Define the identity mapping

Store a record mapping:

```text
minecraft_uuid  ->  nakama_user_id (stable)
```

This is the single source of truth linking the game identity to the social identity. Keep it stable — parties and friends reference it.

### 3. Authenticate through Nakama

On login, the backend (or a small service) calls Nakama's authenticate API with a device/unique identifier derived from the player's verified UUID.

```bash
curl -X POST "http://nakama:7350/v2/account/authenticate/custom" \
  -H "Authorization: Basic <key>" \
  -d '{"id": "<minecraft-uuid>"}'
```

## Acceptance criteria

```text
[ ] Nakama is reachable from backends
[ ] a Minecraft UUID maps to exactly one stable Nakama identity
[ ] re-login returns the same identity (no duplicates)
[ ] mapping stored out-of-band from display names
```

## Why stable identity matters

Display names change; UUIDs and Nakama IDs do not. Everything social (friends, parties, invites) hangs off this stable ID.

## Next step

[Step 6 — Friends + parties](step-06-friends-parties.md)