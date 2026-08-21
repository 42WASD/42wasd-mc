# Plain-English glossary

## Proxy
A server that players connect to first and that can route one player connection among multiple Minecraft backend servers.

## Backend
The actual Paper/Forge/Fabric/NeoForge Minecraft server process running a world or mode.

## Runtime class
A compatibility contract describing the Minecraft version, loader, required client mods, and server capabilities a map is allowed to assume.

## Map definition
Metadata describing a playable map: runtime class, world source, tags, capacity, persistence, owner, and routing policy.

## Map instance
A running or sleeping concrete backend created from a map definition.

## World Controller
Your small control-plane service that turns player routing requests into safe Kubernetes lifecycle operations.

## StatefulSet
A Kubernetes workload type with stable identity that fits persistent server instances and PVC-backed worlds.

## PVC
PersistentVolumeClaim. The persistent disk claim holding a world even while its server Pod is scaled to zero.

## Scale-to-zero
Keeping a world definition and data while running zero server Pods when nobody is using it.

## Agones Fleet
A set of game-server instances kept available for allocation.

## Allocation
Atomically selecting/reserving a game-server instance for a session.

## Presence
Live information describing whether a player is online and what they are currently doing.

## Protocol translation
Translation between Minecraft network protocol versions. It does not install missing mods.

## Resource pack
Assets that Minecraft servers can request clients to download, such as textures, sounds, fonts, and models. It is not equivalent to Java mods.

## Modpack
A defined set of Minecraft loader/mod/config dependencies installed before game startup.

## Pending invite
A durable short-lived record that survives a launcher restart and tells the network where the player intended to go when they reconnect.

---
