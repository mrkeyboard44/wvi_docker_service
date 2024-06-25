import time
from datetime import datetime
import requests
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch data from the API
def fetch_data_from_api(api_token, endpoint, date, offset):
    url = f"https://api.workiz.com/api/v1/{api_token}/{endpoint}/?start_date={date}&offset={offset}&records=100&only_open=false"
    headers = {
        'accept': '*/*'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Function to flatten nested JSON fields
def flatten_nested_json_old(item, parent_key='', sep='_'):
    flattened_item = {}
    for key, value in item.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            flattened_item.update(flatten_nested_json(value, new_key, sep))
        elif isinstance(value, list):
            for i, sublist in enumerate(value):
                if isinstance(sublist, dict):
                    flattened_item.update(flatten_nested_json(sublist, f"{new_key}_{i}", sep))
                else:
                    flattened_item[f"{new_key}_{i}"] = sublist
        else:
            flattened_item[new_key] = value
    return flattened_item

# Function to flatten nested JSON fields
def flatten_nested_json(item, parent_key='', sep='_'):
    flattened_item = {}
    for key, value in item.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            flattened_item.update(flatten_nested_json(value, new_key, sep))
        elif isinstance(value, list):
            for i, sublist in enumerate(value):
                if isinstance(sublist, dict):
                    flattened_item.update(flatten_nested_json(sublist, f"{new_key}_{i}", sep))
                else:
                    flattened_item[f"{new_key}_{i}"] = sublist
        else:
            
            if value == '' or value is None:
                flattened_item[new_key] = None
            
            # Convert empty strings to None for datetime fields
            elif key.endswith('DateTime') or key.endswith('Date'):
                if value == '' or value is None:
                    flattened_item[new_key] = None
                else:
                    try:
                        # Attempt to parse the datetime string
                        flattened_item[new_key] = datetime.fromisoformat(value)
                    except ValueError:
                        # If parsing fails, set to None
                        flattened_item[new_key] = None
            else:
                flattened_item[new_key] = value
    return flattened_item

# Function to save data to the database
def save_data_to_db(data, table, session):
    table_columns = {column.name for column in table.__table__.columns}
    added_count = 0
    replaced_count = 0

    # Assuming 'data' is a list of dictionaries and mapping it to the table structure
    for item in data:
        flattened_item = flatten_nested_json(item)
        filtered_item = {key: value for key, value in flattened_item.items() if key in table_columns}
        new_record = table(**filtered_item)
        
        # Check if the record already exists
        existing_record = session.query(table).filter_by(UUID=new_record.UUID).first()
        if existing_record:
            replaced_count += 1
        else:
            added_count += 1
        
        session.merge(new_record)  # Use merge to handle duplicates based on primary key (UUID)
    
    session.commit()
    return added_count, replaced_count

# Function to fetch data in batches with incremented offset
def fetch_data_in_batches(api_token, endpoint, date, start_offset, table, session, batch_size=100):
    offset = start_offset
    total_added = 0
    total_replaced = 0
    try:
        while True:
            print('fetching data... offset', offset, 'enpoint', endpoint, 'date', date)
            api_data = fetch_data_from_api(api_token, endpoint, date, offset)
            if not api_data or not api_data.get('data'):
                print('api_data from utils', api_data)
                break
            added, replaced = save_data_to_db(api_data['data'], table, session)  # Assuming 'data' is the list containing job data
            total_added += added
            total_replaced += replaced
            logger.info(f"Endpoint {endpoint}: Date {date}: Batch offset {offset}: Added {added}, Replaced {replaced}")
            offset += 1
            # Waiting for 30 seconds to prevent API lockout :P.
            time.sleep(30)
    except Exception as e:
        logger.error(f"Error fetching data in batches: {e}")
    finally:
        session.close()
    
    logger.info(f"Endpoint {endpoint}: Total added: {total_added}, Total replaced: {total_replaced}")

