from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.sql.models import Server, Database
import sqlalchemy
from sqlalchemy import create_engine

subscription_id = '86c82398-3448-43c6-9f4b-954558c30c5a'

resource_group_name = 'Rohan-RG'
location = 'centralindia'

server_name = 'Rohansqllab'
admin_user = 'rohan'
admin_password = 'Password@123'
database_name = 'rohanlabdb'

credential = DefaultAzureCredential()

resource_client = ResourceManagementClient(credential, subscription_id)

resource_group = resource_client.resource_groups.create_or_update(
    resource_group_name,
    {'location': location}
)

sql_client = SqlManagementClient(credential, subscription_id)

server = sql_client.servers.begin_create_or_update(
    resource_group_name,
    server_name,
    Server(
        location=location,
        administrator_login=admin_user,
        administrator_login_password=admin_password
    )
).result()

database = sql_client.databases.begin_create_or_update(
    resource_group_name,
    server_name,
    database_name,
    Database(location=location)
).result()

print(f'Server {server.name} created in resource group {resource_group_name}.')
print(f'Database {database.name} created in server {server.name}.')

# Connection string
server = f'{server_name}.database.windows.net'
database = database_name
username = admin_user
password = admin_password
driver = '{ODBC Driver 17 for SQL Server}'

# Connection URL
connection_url = f'mssql+pyodbc://{username}:{password}@{server}:1433/{database}?driver={driver}'

engine = create_engine(connection_url)

query = 'SELECT 1 AS number'

# Execute query
with engine.connect() as connection:
    result = connection.execute(query)
    for row in result:
        print(row)
