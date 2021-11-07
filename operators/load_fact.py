from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 create_table_sql="",
                 insert_table_sql="",
                 redshift_conn_id="",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.create_table_sql = create_table_sql
        self.insert_table_sql = insert_table_sql
        self.redshift_conn_id = redshift_conn_id


    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        self.log.info('Creating table')
        redshift.run(self.create_table_sql)
        self.log.info('Inserting rows')
        redshift.run(self.insert_table_sql)