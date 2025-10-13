from airflow import DAG
import pendulum
import logging
from datetime import timedelta, datetime
from api.video_stats import get_playlist_id, get_video_ids, extract_video_data, save_to_json
from datawarehouse.dwh import staging_table, core_table
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "pg_datasource"


def yt_elt_data_quality(schema):
    try:
        task = BashOperator(
            task_id=f"soda_test_{schema}",
            bash_command=f"soda scan -d {DATASOURCE} -c {SODA_PATH}/configuration.yml -v SCHEMA={schema} {SODA_PATH}/checks.yml",
        )
        return task
    except Exception as e:
        logger.error(f"Error running data quality check for schema: {schema}")
        raise e

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,  
    'email_on_retry': False,
    'retries': 1,   
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,
    'start_date': datetime(2023, 10, 9, tzinfo=pendulum.timezone('Asia/Karachi')),
}

# Variables
staging_schema = "staging"
core_schema = "core"

with DAG(
    dag_id='youtube_data_pipeline',
    default_args=default_args,
    description='A DAG to extract YouTube video data and save it to a JSON file',
    schedule='0 14 * * *',  # At 14:00 (2 PM) every day
    catchup=False,
) as dag:

    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extracted_data = extract_video_data(video_ids)
    save_to_json_task = save_to_json(extracted_data)

    playlist_id >> video_ids >> extracted_data >> save_to_json_task


with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="DAG to process JSON file and insert data into both staging and core schemas",
    catchup=False,
    schedule=None,
) as dag_update:

    # Define tasks
    update_staging = staging_table()
    update_core = core_table()

    # Define dependencies
    update_staging >> update_core


with DAG(
    dag_id="data_quality",
    default_args=default_args,
    description="DAG to check the data quality on both layers in the database",
    catchup=False,
    schedule=None,
) as dag_quality:

    # Define tasks
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    # Define dependencies
    soda_validate_staging >> soda_validate_core

