# Kafka SOC Project

## Overview
This repository simulates a Security Operations Center (SOC) streaming pipeline.  
It ingests synthetic authentication events (brute-force, password-spray, etc.), streams them into Apache Kafka, and supports downstream processing with Apache Spark and Delta Lake using MinIO (S3-compatible storage).

## Current Status & Progress (realistic)
- Infrastructure (Docker, Kafka, Zookeeper, MinIO, Spark images) — 75%  
  - Docker compose, custom Spark image with Delta/jars, MinIO, Kafka/Zookeeper up and running.
- Producer / Consumer (Python) — 90%  
  - Python producer implemented (`ingestor/producer.py`) and tested locally and in Docker.
- Notebook & Exploration (JupyterLab) — 70%  
  - Notebook image and JupyterLab running, some issues resolved (permissions, packages).
- Spark + Delta integration — 50%  
  - Delta jars and S3A configuration are present; writing Delta to MinIO still requires final jar/config validation and testing.
- Detection logic & Rules (brute-force, spray detection) — 10%  
  - Conceptual detection logic exists; implementation and tests still pending.
- Visualization & Monitoring (Grafana/Superset/Kafka UI) — 10%  
  - Kafka UI added; dashboards not yet built.
- Tests, CI, and Documentation — 20%  
  - Basic README and project structure documented; more examples, unit tests, and CI are needed.

**Overall completion (approximate): 60%**

## What is Done (summary)
- Docker Compose stack with Kafka, Zookeeper, MinIO, Spark (notebook & job), and Kafka UI.
- Custom Spark Dockerfile that pre-bakes Delta/jars (work in progress due to jar/package versions).
- Python event producer that can generate different attack patterns (random, bruteforce, spray, success).
- Consumer examples and CLI commands to read topics and verify messages.
- Local testing showing messages flow from producer → Kafka → consumer; basic Spark notebook tests executed (Delta class not found errors resolved partially).

## What Remains
- Finalize Spark image packaging of Delta + Kafka connector jars for consistent runtime (avoid `--packages` in production).
- Complete Spark Structured Streaming job that reads from Kafka and writes Delta tables to MinIO.
- Implement detection logic (aggregation windows, stateful detection for brute-force/password-spray).
- Add dashboards (Grafana or Superset) and alerting pipelines.
- Add CI, example env files, and automated tests.
- Clean up Dockerfiles and `docker-compose.yml` (remove obsolete `version:` field, parameterize ports/credentials).

## Quick Start (local dev)

1. Build and start the stack:
```bash
docker compose up -d --build
```

2. Run the producer (example):
```bash
docker compose run --rm python-producer \
  python ingestor/producer.py --mode bruteforce --rate 5 --duration 60
```

3. Consume from Kafka (example):
```bash
docker compose exec kafka \
  kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic auth_events --from-beginning --timeout-ms 5000
```

4. Open monitoring UIs:
- Kafka UI: http://localhost:18080 (or the port configured in `docker-compose.yml`)
- Spark UI (if running a job): http://localhost:4040
- MinIO Console: http://localhost:9001 (default credentials in `.env` or `docker-compose.yml`)

## Folder Structure
```
kafka-soc-project/
├── docker-compose.yml
├── infra/
│   ├── Dockerfile.spark
│   ├── Dockerfile.producer
│   └── Dockerfile.flask
├── src/
│   ├── ingest/
│   │   ├── producer.py
│   │   └── requirements.txt
│   └── streaming/
│       └── stream_job.py
├── spark/
│   ├── start-notebook.sh
│   └── submit.sh
├── notebooks/
├── data/            # optional host-mounted test data
├── kafka-data/      # Docker volume mount for Kafka broker data
└── README.md
```

## Recommended Commands (useful cheatsheet)

- Build everything (no cache):
```bash
docker compose build --no-cache
```

- Start stack:
```bash
docker compose up -d
```

- Stop and remove containers:
```bash
docker compose down
```

- Rebuild a single service:
```bash
docker compose build spark-notebook
```

- Run producer (service runs inside its container network so use `kafka:9092`):
```bash
docker compose run --rm python-producer \
  python ingestor/producer.py --mode spray --rate 8 --duration 20
```

- Check running containers:
```bash
docker compose ps
docker ps -a
```

- Tail logs for a service:
```bash
docker compose logs -f spark-notebook
```

## Notes / Troubleshooting
- If Jupyter fails to start due to permissions, check `HOME`, `JUPYTER_RUNTIME_DIR`, and mounted volumes (ensure the notebook user can write to runtime directories).
- If Spark cannot find the `delta` data source, verify Delta JARs are present in `/opt/bitnami/spark/jars` or use `--packages` with matching Scala/Spark versions (beware of network access during container build).
- For Kafka "NoBrokersAvailable" errors from inside containers, make sure the Kafka container is healthy and that you are using the Docker network name `kafka:9092` (not `localhost:9092`) when invoked from another container.
- When using `kafka-console-producer/consumer.sh` from host, prefer `--bootstrap-server localhost:9092` (host port mapping) rather than `--broker-list`.

## Next Steps & Suggestions
1. Finalize Spark image (bake jars or switch to `--packages` at `spark-submit` time). Lock Delta and connector versions to Spark version.
2. Implement and test Spark Structured Streaming job with exactly-once semantics (Delta + S3A + checkpointing).
3. Add detection rules and unit/integration tests.
4. Add simple Flask ingestion app (optional) or keep Python producer for simulation.
5. Create a short HOWTO for onboarding new contributors (env vars, ports, credentials).


