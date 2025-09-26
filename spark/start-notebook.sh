#!/usr/bin/env bash
set -euo pipefail

: "${NB_PORT:=8888}"
: "${NB_IP:=0.0.0.0}"
: "${NB_DIR:=/workspace}"

# Register a kernel name so it shows nicely in Jupyter
python -m ipykernel install --user --name pyspark --display-name "PySpark (Cluster)"

exec jupyter lab --ip="${NB_IP}" --port="${NB_PORT}" --no-browser \
  --NotebookApp.token='' --NotebookApp.password='' \
  --notebook-dir="${NB_DIR}"