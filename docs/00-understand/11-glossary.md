# Plain-English glossary

| Term | Meaning |
|---|---|
| **Proxy** | Server players connect to first; routes them among backend servers. |
| **Backend** | The actual Paper/Forge/Fabric/NeoForge Minecraft server running a world. |
| **Runtime class** | A compatibility contract (MC version, loader, required client mods, server capabilities) a map may assume. |
| **Map definition** | Metadata for a playable map: runtime class, world source, capacity, persistence, routing policy. |
| **Map instance** | A running (or sleeping) concrete backend created from a map definition. |
| **World Controller** | Your control-plane service that turns player routing requests into Kubernetes lifecycle operations. |
| **StatefulSet** | A Kubernetes workload type with stable identity; fits persistent servers + PVC worlds. |
| **PVC** | PersistentVolumeClaim — the disk holding a world even when its Pod is scaled to zero. |
| **Scale-to-zero** | Keeping a world's data while running zero server Pods when idle. |
| **Agones Fleet** | A pool of game-server instances kept ready for allocation. |
| **Allocation** | Atomically reserving a game-server instance for a session. |
| **Presence** | Live info about whether a player is online and what they're doing. |
| **Protocol translation** | Translating between MC protocol versions. Does not install missing mods. |
| **Resource pack** | Assets a server requests clients to download (textures, sounds). Not Java mods. |
| **Modpack** | A defined set of loader/mod/config dependencies installed before startup. |
| **Pending invite** | A durable short-lived record that survives a launcher restart and knows where to send the player on reconnect. |