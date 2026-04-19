import pandas as pd
import streamlit as st

@st.cache_data(ttl = 60 * 60 * 24 * 30)
def fetch_table(table_name, csv_path):
    """
        Try to fetch table from BigQuery, fallback to CSV if it fails.
        Returns: (dataframe, source)
    """
    
    try:
        import os
        import uuid
        from google.cloud import bigquery

        client = bigquery.Client()
        job_id = f"streamlit_query_{uuid.uuid4().hex}"  # unique per call

        project = os.environ.get('PROJECT')
        dataset = os.environ.get('DATASET')
        query_job = client.query(
            f"SELECT * FROM `{project}.{dataset}.{table_name}`",
            job_id=job_id
        )
        df = query_job.result().to_dataframe()
        return df, "BigQuery"
    except Exception:
        try:
            df = pd.read_csv(f'/opt/airflow/streamlit/{csv_path}')
        except:
            df = pd.read_csv(csv_path)
        return df, "CSV"