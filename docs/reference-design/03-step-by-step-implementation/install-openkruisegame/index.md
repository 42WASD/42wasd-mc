# Install OpenKruiseGame

The World Controller drives a **`GameServerSet`** (`game.kruise.io/v1alpha1`)
as the persistent-world workload, and KEDA fires its 0↔1 scale transitions.
None of that works until OpenKruiseGame (OKG) is actually installed in the
cluster. This is a platform prerequisite and must happen before the first
persistent map is authored or the World Controller is built.

OpenKruiseGame requires **both** components:

```text
Kruise        (the core OpenKruise controllers)
Kruise-Game   (the game-server CRDs: GameServer, GameServerSet; plus
               features such as opsState and service qualities)
```

Kubernetes version must be **>= 1.18** (per current OKG install docs).

---

## Install Kruise

Use Helm (v3.5 or later):

```bash
helm repo add openkruise https://openkruise.github.io/charts/
helm repo update
helm install kruise openkruise/kruise
```

Pin a tested version rather than `latest` (mirror the `PIN_EXACT_TESTED_VERSION`
discipline used elsewhere). Kruise installs its controllers into a dedicated
namespace and registers its CRDs.

---

## Install Kruise-Game

```bash
helm install kruise-game openkruise/kruise-game
```

By default this creates and runs in the `kruise-game-system` namespace and
installs the `game.kruise.io/v1alpha1` API group (GameServerSet, GameServer).

If you run a China-region cluster and need an accessible image registry,
override the image repository, e.g.:

```bash
helm install kruise-game openkruise/kruise-game \
  --set image.repository=registry.cn-hangzhou.aliyuncs.com/acs/kruise-game-manager
```

---

## Verify the CRDs are present

After install, confirm the API group is served:

```text
kubectl api-resources --api-group=game.kruise.io

NAME            APIVERSION             KIND
gameservers     game.kruise.io/v1alpha1  GameServer
gameserversets  game.kruise.io/v1alpha1  GameServerSet
...
```

You should be able to author a trivial `GameServerSet` and scale it 0→1 before
proceeding — this is the exact primitive the World Controller later drives
(see `build-the-world-controller`).

> **Acceptance:** `kubectl get crd gameserversets.game.kruise.io` returns the
> CRD, and a scratch `GameServerSet` with `replicas: 1` reaches a running
> `GameServer`. The controller-manager pods are `Running` in
> `kruise-game-system`.

---

## Relationship to the World Controller

The World Controller talks to OKG through the Kubernetes API with a narrow
RBAC role (`game.kruise.io/gameserversets`, `gameservers` get/list/watch/patch/
update). It scales a GameServerSet's `spec.replicas` 0↔1; it does not manage
OKG's installation. Keep OKG as a platform-level component installed once,
alongside namespaces, not as something the World Controller owns.

---