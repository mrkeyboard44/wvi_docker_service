import requests
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, PrimaryKeyConstraint
from sqlalchemy.dialects.mysql import insert
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the environment variables
api_token = os.getenv('API_TOKEN')
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_database = os.getenv('MYSQL_DATABASE')

# Define the API endpoints
lead_api_url = f'https://api.workiz.com/api/v1/{api_token}/lead/all/'
job_api_url = f'https://api.workiz.com/api/v1/{api_token}/job/all/'

offset = 0
limit = 100

def fetch_json_from_api(url, start_date, offset, limit, entity_type):
    params = {
        'start_date': start_date,
        'offset': offset,
        'records': limit,
        'only_open': 'false'
    }
    headers = {
        'accept': 'application/json'
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    json_data = response.json()
    
    # Extract the actual data part and check 'found' status
    data = json_data.get('data', [])
    found = json_data.get('found', 0)
    
    print(f"Received {entity_type} data: {len(data)} items")

    return data, found

def flatten_json(nested_json, parent_key='', sep='_'):
    """
    Flatten a nested json object
    """
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_json({f"{new_key}{sep}{i}": item}, '', sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def infer_table_schema(json_data, table_name, metadata):
    sample_data = json_data[0]  # Assuming the JSON data is a list of dictionaries
    sample_data = flatten_json(sample_data)  # Flatten the sample data
    columns = []
    for key, value in sample_data.items():
        if isinstance(value, int):
            columns.append(Column(key, Integer))
        elif isinstance(value, float):
            columns.append(Column(key, Float))
        elif isinstance(value, bool):
            columns.append(Column(key, Boolean))
        elif isinstance(value, str):
            columns.append(Column(key, String(255)))
        else:
            columns.append(Column(key, String(255)))
    columns.append(PrimaryKeyConstraint('uuid'))  # Ensure UUID is the primary key
    return Table(table_name, metadata, *columns)

def insert_data(engine, table, data, entity_type):
    flattened_data = [flatten_json(item) for item in data]
    with engine.connect() as connection:
        for item in flattened_data:
            stmt = insert(table).values(item)
            # Create update statement for existing UUIDs
            update_stmt = stmt.on_duplicate_key_update(
                {key: value for key, value in item.items() if key != 'uuid'}
            )
            connection.execute(update_stmt)
    
    print(f"Successfully added {len(flattened_data)} {entity_type} to the database")

def process_data(api_url, table_name, engine, metadata, entity_type):
    global offset

    # Calculate the start date 6 months before the current date
    current_date = datetime.now()
    start_date = (current_date - timedelta(days=6*30)).strftime('%Y-%m-%d')

    json_response, found = fetch_json_from_api(api_url, start_date, offset, limit, entity_type)
    
    # Infer the table schema from JSON data
    table = infer_table_schema(json_response, table_name, metadata)

    # Create the table if it doesn't exist
    metadata.create_all(engine)

    while found != 0:
        # Insert data into the table
        insert_data(engine, table, json_response, entity_type)

        # Increment the offset for the next batch of data
        offset += limit

        # Pause for 20 seconds to prevent API lockout
        time.sleep(20)

        # Fetch the next batch of data
        json_response, found = fetch_json_from_api(api_url, start_date, offset, limit, entity_type)

def main():
    # Connect to the MySQL database
    engine = create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}")
    metadata = MetaData()

    # Process leads data
    print("Processing leads...")
    process_data(lead_api_url, 'leads', engine, metadata, 'leads')

    # Reset the offset
    global offset
    offset = 0

    # Process jobs data
    print("Processing jobs...")
    process_data(job_api_url, 'jobs', engine, metadata, 'jobs')

if __name__ == '__main__':
    main()

