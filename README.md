# Sparkify-ETL-with-Airflow

This project's purpose is to effectively move data from a cloud storage location (S3) to a relational database (Redshift), then tranform that data into fact and dimension tables. A data quality check is conducted to make sure the extraction, transformation and loading to the fact and dimension tables worked. This project uses Airflow to manage and run a **D**irected **A**cyclic **G**raph (DAG).



# Installation & Setup

## Files

The files used in this project are all Python files. For convenience, below is the folder structure and names of files. Notice that the main directories are for 'dags' and 'plugins'. This subdirectories under 'plugins' are 'helpers' and 'operators'. All of the sql queries used in the project are under the 'helper' directory and all of the operators used are in the 'operators' directory.

+ airflow
    +  dags
         + project5_dag.py: the directed acyclic graph (DAG) python file
     + plugins
          + _ _ init _ _.py
          + helpers
               + _ _ init _ _ .py
               + sql_queries.py: SQL queries
          + operators
               + _ _ init _ _ .py
               + data_quality.py: defines the operator class that checks the dimension and fact tables for data quality
               + load_dimension.py: defines the operator class to transform staging tables into dimension tables
               + load_fact.py: defines the operator class to transform staging tables into fact tables 
               + stage_redshift.py: defines the operator class to copy json files in S3 directories to staging tables in Redshift


## Amazon S3

All input data is stored in S3 (Simple Storage Service) in JSON format.

**input filepaths (us-west-2)**
+ log_data: s3://udacity-dend/log_data
+ song_data: s3://udacity-dend/song_data

## Redshift (Elastic Map Reduce on Amazon Web Services)

For this project, I used a Redshift cluster to host a Postgres database. The database is where the staging, fact and dimension tables are stored.

_Note:_ The Redshift cluster endpoint is the host name of the postgres database. You can find this under _General information_ for the Redshift cluster.

**Creating a Redshift Cluster**

Creating a redshift cluster is easy. For this project I used the Free Tier machine that comes pre-loaded with some data. Go to this link for a tutorial on creating cluster in Redshift: https://docs.aws.amazon.com/redshift/latest/dg/tutorial-loading-data-launch-cluster.html.

**Modify publicly accessible settings**

If you want to make the Redshift cluster publicly available to access to a larger number of you can change this by going to the _Actions_ menu on the Redshift cluster page.

**Manage IAM Roles**

Add a role to the Redshift cluster that has access to read S3 buckets and full access to Redshift. This will require you to make a role that has the required permissions. Go to this link to see more about creating Roles in AWS: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html. Under _Actions_ in the Redshift cluster page (once you click on the cluster name, when available) you will see an option to _Manage IAM roles_ and there you will be able to add roles to the cluster.

**VPC Security Group**

Add a VPC security group to the list of security groups. You can edit the VPC security groups by going to the _Properties_ tab on the Redshift cluster page and going down the page and choosing to edit the _Network and security settings_.  Adding a security group to the list of security groups that can access the Redshift cluster can allow your computer access. Go to this link to see more about creating VPC security groups in AWS: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html

## Airflow

**Airflow Links**

Airflow has numerous links to run and manage your directed acyclic graphs (DAGs). This DAG is configured to run once triggered by the user. The 'play button' all the way to the left under _Links_ will trigger the DAG. The remaining links allow you to view the running of the DAG, the completion (or failure) of tasks, the code and refresh Airflow.

**Connections**

Airflow makes it easy to store access credentials to commonly used services such as Amazon Web Services and Postgres. These services can be accessed within Airflow using hooks to let you programmatically perform tasks on these services. For this project, the original data is stored in S3 and the database is on Redshift (both on Amazon Web Services), so connections to both of these services need set up. Under the _Admin_ section on Airflow there is an option for _Connections_. There is the option to create new connections.

_Postgres Connection_

How to configure the connection details for a Postgres type connection:

+ Conn Id: Name the connection
+ Conn Type: Postgres
+ Host: Redshift cluster endpoint
+ Schema: Schema Name
+ Login: Redshift username
+ Password: Redshift password
+ Port: 5439

_AWS Connection_

An access key and secret access key are needed, and these act as the username and password in the connection configuration for an Amazon Web Services connection. You can find out how to create your access key and secret access key here: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey.

How to configure the connection details for a Amazon Web Services type connection:

+ Conn Id: Name the connection
+ Conn Type: Amazon Web Services
+ Login: AWS access key
+ Password: AWS secret access key

# ETL Process

**Process**

Extract from song_data, log_data filepaths -> Load to staging tables in Amazon Redshift -> Transform -> load transformed data to fact and dimension tables in Amazon Redshift -> Conduct data quality check

# Redshift


# Data Table Schema

The data are stored in JSON format, but each JSON file contains tables that follow a predictable format (schema). Below is a reference of the schema for the tables contained in the JSON files under the S3 filepaths for this project:


**s3://udacity-dend/log_data**

Type | Column | Type
-----|--------|------
null | artist | varchar
null | auth | varchar
null | firstname | varchar
null | gender | varchar
null | iteminsession | bigint
null | lastname | varchar
null | length | decimal
null | level | varchar
null | location | varchar
null | method | varchar
null | page | varchar
null | registration | decimal
null | sessionid | int
null | song | varchar
null | status | int
null | ts | bigint
null | useragent | varchar
null | userid | int

**s3://udacity-dend/song_data**

Type | Column | Type
-----|--------|------
null | num_songs | int
null | artist_id | varchar
null | artist_latitude | decimal
null | artist_longitude | decimal
null | artist_name | varchar 
null | song_id | varchar
null | title | varchar
null | duration | decimal
null | year | int


**songplay**

Contains data to show the songs listened to by **Sparkify** platform users. Also shows the time and location of when and where the user listened to the song.

Type | Column | Type
-----|--------|------
PK | songplay_id | int
FK | start_time | timestamp
FK | user_id | int
null | level | varchar
FK | song_id | varchar
FK | artist_id | varchar
null | session_id | varchar
null| location | varchar
null | user_agent | varchar

**dim_user** 

Contains data on the Sparkify platform user.

Type | Column | Type
-----|--------|------
PK | user_id | int
null | first_name | varchar
null | last_name | varchar
null | gender | varchar
null | level | varchar

**dim_song**

Contains song data.

Type | Column | Type
-----|--------|------
PK | song_id | varchar
null | title | varchar
FK | artist_id | varchar
null | year | int
null | duration | decimal
 
**dim_artist**

Contains artist data.

Type | Column | Type
-----|--------|------
PK | artist_id | varchar
null | artist_name | varchar
null | artist_location | varchar
null | artist_latitude | varchar
null | artist_longitude | varchar

**dim_time**

Contains timestamp data from song listens as well as other time related.

Type | Column | Type
-----|--------|------
PK | start_time | timestamp
null | hour | int
null | day | int
null | week | int
null | month | int
null | year | int
null | weekday | int
