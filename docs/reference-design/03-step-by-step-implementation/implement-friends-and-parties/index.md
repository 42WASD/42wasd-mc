# Implement friends and parties

Do this before random routing.

Commands:

```text
/friend add <player>
/friend accept <player>
/friends

/party create
/party invite <player>
/party accept <player>
/party leave
```

Back them with Nakama.

Acceptance criteria:

```text
[ ] friend survives Minecraft reconnect
[ ] party state is visible across backends
[ ] invite can be accepted from a different backend
[ ] party leader can request a world for entire party
```

---
