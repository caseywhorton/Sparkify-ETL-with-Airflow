from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class StageToRedshiftOperator(BaseOperator):
    template_fields = ('sql',)
    ui_color = '#006400'
    copy_sql = """
        copy {}
        from 's3://{}'
        credentials 'aws_iam_role={}' 
        compupdate on
        format as json 'auto ignorecase'
        region 'us-west-2';
        """

    @apply_defaults
    def __init__(self,
                 sql,
                 redshift_conn_id="",
                 aws_credentials_id="",
                 aws_iam_role="",
                 table="",
                 s3_bucket="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.table = table
        self.sql = sql
        self.redshift_conn_id = redshift_conn_id
        self.aws_iam_role = aws_iam_role
        self.s3_bucket = s3_bucket
        self.aws_credentials_id = aws_credentials_id

    def execute(self, context):
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        self.log.info("Creating destination table in Redshift")
        redshift.run(self.sql)
        
        self.log.info("Clearing data from destination Redshift table")
        redshift.run("DELETE FROM {}".format(self.table))

        self.log.info("Copying json data from S3 to Redshift")
        formatted_sql = StageToRedshiftOperator.copy_sql.format(
            self.table,
            self.s3_bucket,
            self.aws_iam_role
        )
        redshift.run(formatted_sql)
