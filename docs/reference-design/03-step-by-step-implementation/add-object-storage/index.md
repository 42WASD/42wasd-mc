# Add object storage for the community upload pipeline

The `community-map-upload-pipeline` assumes an object store to quarantine and
publish uploaded map archives, but nothing in the build order installs one.
This phase adds a private, versioned object store and the buckets the pipeline
needs.

> **Why not MinIO?** The MinIO repository was archived on 2026-04-25 and is no
> longer maintained. This design uses **SeaweedFS** (active, S3-compatible,
> with Kubernetes/Helm deployment paths) as the self-hosted object store.

---

## Why object storage

Uploaded maps must not land directly on a shared filesystem or in a running
server Pod. They need a **quarantine** area (untrusted, pending validation)
and a **published** area (immutable, validated revisions). Object storage is
the natural fit:

```text
upload (public/internal endpoint)
  ↓
s3://42wasd/maps-quarantine/     # untrusted, pending scan/validation
  ↓  (validate -> scan -> extract)
s3://42wasd/maps-published/      # immutable revisions, served to runtimes
```

Object storage also decouples map blobs from the K8s cluster lifecycle: the
upload service and the validation worker are stateless and scale independently
of any Minecraft server.

---

## Install SeaweedFS (private S3-compatible store)

Use SeaweedFS's Helm chart / operator in `minecraft-system`. Conceptual:

```bash
helm repo add seaweedfs https://seaweedfs.github.io/seaweedfs-helm/  # or operator chart
helm repo update
helm install seaweedfs seaweedfs/seaweedfs \
  --namespace minecraft-system \
  --set filer.replicas=1 \
  --set s3.enabled=true
```

Create a Kubernetes Secret with the S3 credentials and store it in Git-managed
encrypted form (or a secret manager):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: seaweedfs-s3-credentials
  namespace: minecraft-system
type: Opaque
stringData:
  access-key: "..."
  secret-key: "..."
```

(Backup staging may also use an object-store bucket; keep **PostgreSQL/
CockroachDB out of this role** — the database is not the artifact store.)

---

## Create the buckets

Using an S3 client:

```bash
s3cmd mb s3://42mc42/maps-quarantine --access_key="$AK" --secret_key="$SK"
s3cmd mb s3://42mc42/maps-published --access_key="$AK" --secret_key="$SK"
```

Policy: `maps-published` holds immutable content-addressed objects (no
overwrite); `maps-quarantine` is write-mostly (upload only, no direct
execution).

---

## Content-addressed immutable map artifacts

Community artifacts are stored **content-addressed** (keyed by SHA-256) so a
published revision is never overwritten:

```text
maps/sha256/ab/abcdef0123...    # blob named by its hash
```

`MapDefinition`/runtime metadata points at an immutable revision:

```yaml
worldArtifact:
  sha256: "abcdef0123..."
  object: "maps/sha256/ab/abcdef0123..."
  size: 89423423
```

A new community revision becomes a **new object** (new hash) — the old one is
never mutated:

```text
Floating Kingdom v1  →  hash A  →  maps/sha256/.../A
Floating Kingdom v2  →  hash B  →  maps/sha256/.../B
```

`MapDefinition.spec` simply changes which immutable revision it references.
This improves rollback, auditing, malware review, backup deduplication, and
reproducibility without depending on vendor-specific object-lock semantics.

---

## Consumers

- The **upload endpoint / worker** from `community-map-upload-pipeline` writes
  new uploads to `quarantine` and, after validation, copies the immutable
  (content-addressed) revision to `published`.
- The runtime/World Controller reads `published` to fetch a validated map
  revision when a `MapDefinition` points at an object-storage revision.

> The bucket names and credentials are referenced by
> `community-map-upload-pipeline`; this phase makes that pipeline real rather
> than assuming an object store exists.

---

## Acceptance

```text
kubectl get deploy -n minecraft-system seaweedfs    # running
kubectl get pods -n minecraft-system -l app=seaweedfs  # ready
s3cmd ls s3://42.42/maps-quarantine                  # can list the bucket
s3cmd ls s3://42.42/maps-published                  # can list the bucket
```

After this phase, the community-map-upload-pipeline can actually quarantine,
validate, and publish a map revision end to end.