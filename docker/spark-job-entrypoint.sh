#!/bin/bash
set -e
export HOME=/tmp
export USER="${USER:-root}"
export HADOOP_USER_NAME="${HADOOP_USER_NAME:-root}"
export IVY_HOME=/tmp/.ivy2
mkdir -p "$IVY_HOME"
if [[ "${SPARK_DEMO_LOCAL:-1}" == "1" ]]; then
  SPARK_MASTER="local[*]"
else
  SPARK_MASTER="${SPARK_MASTER_URL:-spark://spark-master:7077}"
fi
echo "Aguardando Spark master..."
for i in $(seq 1 60); do
  if curl -sf http://spark-master:8080/ >/dev/null 2>&1; then
    echo "Spark master OK"
    break
  fi
  sleep 2
done
echo "Spark master: $SPARK_MASTER"
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Duser.home=/tmp -Duser.name=root"
export PYSPARK_PYTHON="${PYSPARK_PYTHON:-python3}"
export PYSPARK_DRIVER_PYTHON="${PYSPARK_DRIVER_PYTHON:-python3}"
export PROJECT_ROOT="${PROJECT_ROOT:-/workspace}"
export PYTHONPATH="${PYTHONPATH:-/workspace}"
LAYER="${MEDALLION_LAYER:-all}"
exec python3 /workspace/scripts/medallion_job.py "$LAYER" --backend spark --master "$SPARK_MASTER"
