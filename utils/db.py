import json
import boto3


def get_secret(secret_name):

    session = boto3.session.Session(region_name="eu-west-1")
    client = session.client(
        service_name="secretsmanager",
        region_name="eu-west-1",
    )

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    return get_secret_value_response


secrets = json.loads(get_secret("Secret_name")["SecretString"])
# Database connection
username = secrets["username"]
password = secrets["password"]
host = secrets["host"]
port = secrets["port"]
dbname = secrets["dbname"]

# PostgreSQL connection string
connection_str = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"

from sqlalchemy import create_engine
from sqlalchemy import inspect, MetaData, Table

engine = create_engine(connection_str)
