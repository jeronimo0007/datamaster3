# Imagem do Airflow para Azure e AWS (mesma stack do Docker local).
#
# Base: apache/airflow 2.9.3 (mesma versão do docker-compose).
# Contém o projeto de dados (src/scripts/config) + DAGs.
# Storage remoto: ADLS (adlfs) na Azure · S3 (s3fs) na AWS.
FROM apache/airflow:2.9.3-python3.11

# Dependências de processamento e storage remoto (ADLS + S3)
RUN pip install --no-cache-dir \
    pandas==2.1.3 \
    pyarrow>=14.0.0 \
    fsspec \
    adlfs \
    azure-identity \
    s3fs \
    boto3

USER root

# Código do pipeline (mesmo do repositório)
COPY src /opt/airflow/project/src
COPY scripts /opt/airflow/project/scripts
COPY config /opt/airflow/project/config
COPY airflow/dags /opt/airflow/dags

RUN mkdir -p /opt/airflow/data /opt/airflow/project/data && \
    chown -R airflow:root /opt/airflow/project /opt/airflow/dags /opt/airflow/data

USER airflow

ENV PYTHONPATH=/opt/airflow/project \
    AIRFLOW__CORE__LOAD_EXAMPLES=false \
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false \
    AIRFLOW__CORE__EXECUTOR=SequentialExecutor \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/data/airflow.db \
    AIRFLOW__WEBSERVER__EXPOSE_CONFIG=false \
    AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth

WORKDIR /opt/airflow/project
