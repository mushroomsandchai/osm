FROM apache/airflow:3.1.6-python3.12
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        git \
        gcc \
        python3-dev \
        osmium-tool \
        default-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$JAVA_HOME/bin:$PATH
ENV PYSPARK_PYTHON=python3

USER airflow

RUN curl https://install.duckdb.org | sh

RUN pip install --no-cache-dir --upgrade \
    apache-airflow-providers-apache-spark \
    astronomer-cosmos \
    pyspark==3.5.1 \
    h3 \
    opening-hours-py \
    streamlit \
    altair

RUN python -m venv /opt/airflow/.dbt_venv && \
    /opt/airflow/.dbt_venv/bin/pip install --no-cache-dir \
    dbt-core \
    dbt-bigquery