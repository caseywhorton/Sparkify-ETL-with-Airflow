import datetime
from datetime import timedelta
import logging
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators import StageToRedshiftOperator, LoadDimensionOperator, LoadFactOperator, DataQualityOperator
from airflow.operators.dummy_operator import DummyOperator
from helpers import SqlQueries                              

default_args = {
    'owner': 'caseyw',
    'start_date': datetime.datetime.now(),
    'depends_on_past': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup':False
}

dag = DAG(
        'udacity-dend.project5',
        default_args=default_args
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

copy_events_task = StageToRedshiftOperator(
    task_id="Stage_events",
    dag=dag,
    sql=SqlQueries.stg_events_table_create,
    s3_bucket = "udacity-dend/log_data",
    table="stg_events",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    aws_iam_role = ""
)


copy_songs_task = StageToRedshiftOperator(
    task_id="Stage_songs",
    dag=dag,
    sql=SqlQueries.stg_songs_table_create,
    s3_bucket = "udacity-dend/song_data",
    table="stg_songs",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    aws_iam_role = ""
)


load_dimension_song_task = LoadDimensionOperator(
    task_id='Load_song_dim_table',   
    dag=dag,
    create_table_sql=SqlQueries.song_table_create,
    insert_table_sql=SqlQueries.song_table_insert,
    redshift_conn_id="redshift"
)

load_dimension_user_task = LoadDimensionOperator(
    task_id='Load_user_dim_table',   
    dag=dag,
    create_table_sql=SqlQueries.user_table_create,
    insert_table_sql=SqlQueries.user_table_insert,
    redshift_conn_id="redshift"
)

load_dimension_artist_task = LoadDimensionOperator(
    task_id='Load_artist_dim_table',   
    dag=dag,
    create_table_sql=SqlQueries.artist_table_create,
    insert_table_sql=SqlQueries.artist_table_insert,
    redshift_conn_id="redshift"
)

load_dimension_time_task = LoadDimensionOperator(
    task_id='Load_time_dim_table',   
    dag=dag,
    create_table_sql=SqlQueries.time_table_create,
    insert_table_sql=SqlQueries.time_table_insert,
    redshift_conn_id="redshift"
)

load_songplays_table_task = LoadFactOperator(
    task_id='Load_songplays_fact_table',   
    dag=dag,
    create_table_sql=SqlQueries.songplay_table_create,
    insert_table_sql=SqlQueries.songplay_table_insert,
    redshift_conn_id="redshift"
)

data_quality_task = DataQualityOperator(
    task_id='Data_Quality_Check',   
    dag=dag,
    redshift_conn_id="redshift"
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> copy_events_task >> load_songplays_table_task 
start_operator >> copy_songs_task >> load_songplays_table_task
load_songplays_table_task >> load_dimension_song_task >> data_quality_task 
load_songplays_table_task >> load_dimension_user_task >> data_quality_task 
load_songplays_table_task >> load_dimension_artist_task >> data_quality_task 
load_songplays_table_task >> load_dimension_time_task >> data_quality_task
data_quality_task >> end_operator
