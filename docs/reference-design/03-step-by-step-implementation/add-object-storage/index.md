# Add object storage for the community upload pipeline

The `community-map-upload-pipeline` assumes an object store to quarantine and
publish uploaded map archives, but nothing in the build order installs one.
This phase adds a private, versioned object store (MinIO) and the buckets the
pipeline needs.

---

## Why object storage

Uploaded maps must not land directly on a shared filesystem or in a running
server Pod. They need a **quarantine** area (untrusted, pending validation)
and a **published** area (immutable, validated revisions). Object storage is
the natural fit:

```text
upload (public/internal endpoint)
  ↓
s3://minecraft/maps-quarantine/     # untrusted, pending scan/validation
  ↓  (validate -> scan -> extract)
s3://minecraft/maps-published/      # immutable revisions, served to runtimes
```

Object storage also decouples map blobs from the K8s cluster lifecycle: the
upload service and the validation worker are stateless and scale independently
of any Minecraft server.

---

## Install MinIO (private S3-compatible store)

```bash
helm repo add minio https://charts.min.io/  # community MinIO chart
helm repo update
helm install minio minio/minio \
  --namespace minecraft-system \
  --set rootUser=minio-admin \
  --set rootPassword="$(openssl rand -base64 24)"
```

Create a Kubernetes Secret with the credentials and store it in Git-managed
encrypted form (or a secret manager):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: minio-credentials
  namespace: minecraft-system
type: Opaque
stringData:
  access-key: "..."
  secret-key: "..."
```

---

## Create the buckets

Using the MinIO client:

```bash
mc alias set minecraft https://minio.minecraft-system.svc:9000 "$AK" "$SK"
mc mb minecraft/maps-quarantine
mc mb minecraft/maps-published
```

Apply policy so `maps-published` is immutable (object lock / no delete after
publish) and `maps-quarantine` is write-mostly (upload only, no direct
execution).

---

## Consumers

- The **upload endpoint / worker** from `community-map-upload-pipeline` writes
  new uploads to `quarantine` and, after validation, copies the immutable
  revision to `published`.
- The runtime/World Controller reads `published` to fetch a validated map
  revision when a `MapDefinition` points at an object-storage revision.

> The bucket names and credentials are referenced by
> `community-map-upload-pipeline`; this phase makes that pipeline real rather
> than assuming an object store exists.

---

## Acceptance

```text
kubectl get deploy -n minecraft-system minio      # running
kubectl get pods -n minecraft-system -l app=minio  # ready
mc ls minecraft/maps-quarantine                    # can list the bucket
mc ls minecraft/maps-published                     # can list the bucket
```

After this phase, the community-map-upload-pipeline can actually quarantine,
validate, and publish a map revision end to end.