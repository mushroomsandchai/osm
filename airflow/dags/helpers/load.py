import os
from google.cloud import bigquery

def load_table():
    base_dir = '/spark/transformed/'
    project = os.environ.get('PROJECT')
    dataset = os.environ.get('DATASET')

    client = bigquery.Client()

    table_id = f'{project}.{dataset}.raw_osm'

    files = [file for file in os.listdir(base_dir) if file.endswith('.parquet')]
    
    job_config = bigquery.LoadJobConfig(
                        source_format = bigquery.SourceFormat.PARQUET,
                        write_disposition = bigquery.WriteDisposition.WRITE_APPEND,
                    )

    for file in files:
        file_path = f'{base_dir}{file}'

        with open(file_path, "rb") as source_file:
            load_job = client.load_table_from_file(
                file_obj = source_file,  # Pass the object, not the string path
                destination = table_id,
                job_config = job_config,
                num_retries = 2
            )

            load_job.result()
            print(f"Loaded {load_job.output_rows} records.")