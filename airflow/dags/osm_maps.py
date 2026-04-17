from airflow.sdk import dag, task
from datetime import datetime
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

@dag(
    dag_id = 'osm_by_country',
    start_date = datetime(2026, 1, 1),
    schedule = "@once",
    max_active_tasks = 1,
    description = 'Ingest OSM maps by country, clean, transform and load to BigQuery.'
)
def osm_pipeline():

    @task
    def get_countries():
        import os
        countries = ['-'.join(c.lower().split()) for c in os.environ.get('COUNTRIES').split(',')]
        return countries

    @task.bash
    def download_and_clean_osm_maps(country):
        from helpers.fetch_url import urls
        from helpers.fetch_command import command

        entries = urls(country)
        commands = list()

        for filename, url, country in entries:
            region = filename.removesuffix('.osm.pbf')
            commands.append(command(filename, url, region, country))

        return(f"{''.join(commands)}")

    spark = SparkSubmitOperator(
        task_id = 'spark_job',
        application = '/spark/transform.py',
        conn_id = 'spark_default',
        py_files = '/spark/helpers/utils.py,/spark/helpers/fetch_score.py',
        total_executor_cores = 4,
        executor_memory = '2g',
        name = 'osm_transform',
        verbose = False
    )

    @task
    def load():
        from helpers.load import load_table
        load_table()

    from cosmos import DbtTaskGroup
    from cosmos.config import RenderConfig
    from helpers.dbt_configurations import dbt_objects

    PROFILE, PROJECT, EXECUTION = dbt_objects()

    dbt = DbtTaskGroup(
        profile_config = PROFILE,
        project_config = PROJECT,
        execution_config = EXECUTION,
        render_config = RenderConfig(
            select = ["path:models/+"]
        )
    )

    @task.bash
    def clean():
        return("echo 'This will remove stary parquet files in future.'")


    countries = get_countries()
    downloader = download_and_clean_osm_maps.expand(country = countries)
    loader = load()
    cleaner = clean()

    downloader >> spark >> loader >> dbt >> cleaner

osm_pipeline()