from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id


    def execute(self, context):
        self.log.info("Running data quality operator")
        
        # make a list of tables to run sql checks on
        table_list = ['songplay', 'dim_user', 'dim_artist', 'dim_time', 'dim_song']
        
        for table in table_list:
            self.log.info("checking data quality for {}".format(table))
            redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

            records = redshift.get_records(f"SELECT COUNT(*) FROM {table}")
            if len(records) < 1 or len(records[0]) < 1:
                raise ValueError(f"Data quality check failed. {table} returned no results")
            num_records = records[0][0]
            if num_records < 1:
                raise ValueError(f"Data quality check failed. {table} contained 0 rows")
            self.log.info(f"Data quality on table {table} check passed with {records[0][0]} records")
