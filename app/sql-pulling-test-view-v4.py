import os
import logging
from dotenv import load_dotenv
from prettytable import PrettyTable
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DB_USER = os.getenv('MYSQL_USER')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_HOST = os.getenv('MYSQL_HOST')  # Example: "192.168.1.20:1231"
DB_NAME = os.getenv('MYSQL_DATABASE')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the database URL
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create SQLAlchemy engine and MetaData
engine = create_engine(DATABASE_URL)
metadata = MetaData()

metadata.bind = engine

# Function to fetch all tables
def fetch_all_tables():
    try:
        metadata.reflect(bind=engine)
        return sorted(metadata.tables.keys())
    except SQLAlchemyError as e:
        logger.error(f"Error fetching tables: {e}")
        return []
'''
# Function to fetch table data
def fetch_table_data(table_name, limit=None, selected_columns=None):
    try:
        conn = engine.connect()
        table = Table(table_name, metadata, autoload=True, autoload_with=engine)
        columns = table.columns.keys()

        # Handle selected columns input
        if selected_columns:
            try:
                selected_indices = [int(idx.strip()) for idx in selected_columns.split(',') if idx.strip().isdigit() and int(idx.strip()) < len(columns)]
                selected_columns = [columns[idx] for idx in selected_indices]
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing selected columns: {e}")
                selected_columns = columns  # Fallback to all columns
        else:
            selected_columns = columns
        
        # Construct the query with selected columns
        if limit:
            query = select([getattr(table.c, col) for col in selected_columns]).limit(limit)
        else:
            query = select([getattr(table.c, col) for col in selected_columns])
        print(query)
        result = conn.execute(query)
        data = result.fetchall()
        conn.close()
        return data, selected_columns
    except SQLAlchemyError as e:
        logger.error(f"Error fetching table data: {e}")
        return [], []

'''
def fetch_table_data(table_name, limit=None, selected_columns=None):
    try:
        conn = engine.connect()
        table = Table(table_name, metadata, autoload=True, autoload_with=engine)
        columns = table.columns.keys()

        if selected_columns:
            selected_columns = [columns[int(idx)] for idx in selected_columns.split(',') if idx.isdigit() and int(idx) < len(columns)]
        else:
            selected_columns = columns
        print(selected_columns)
        if limit:
            query = select([getattr(table.c, col) for col in selected_columns]).limit(limit)
        else:
            query = select([getattr(table.c, col) for col in selected_columns])

        result = conn.execute(query)
        data = result.fetchall()
        conn.close()
        return data, selected_columns
    except SQLAlchemyError as e:
        logger.error(f"Error fetching table data: {e}")
        return [], []

# Function to display table data
def display_table(data, column_names):
    try:
        if not data:
            print("No data to display.")
            return
        
        table = PrettyTable()
        table.field_names = column_names
        for row in data:
            if len(row) == len(column_names):  # Check if number of columns matches expected
                table.add_row(row)
            else:
                logger.warning(f"Skipping row: Number of columns ({len(row)}) does not match expected ({len(column_names)})")
        print(table)
    except Exception as e:
        logger.error(f"Error displaying table data: {e}")

def main():
    try:
        while True:
            print("\nOptions:")
            print("1. Show all tables")
            print("2. Show first N lines of a table")
            print("3. Show all lines of a table")
            print("4. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                tables = fetch_all_tables()
                if tables:
                    print("\nTables in the database:")
                    for table in tables:
                        print(table)
                else:
                    print("No tables found.")
                    
            elif choice == '2':
                tables = fetch_all_tables()
                if tables:
                    print("\nTables in the database:")
                    for table in tables:
                        print(table)
                    table_name = input("\nEnter table name: ")
                    if table_name in tables:
                        try:
                            limit = int(input("Enter the number of lines to display: "))
                            columns_selection = input("Enter column indices (comma-separated) to display (leave blank for all): ").strip()
                            if columns_selection:
                                selected_columns = [idx.strip() for idx in columns_selection.split(',') if idx.strip().isdigit()]
                                data, column_names = fetch_table_data(table_name, limit, ','.join(selected_columns))
                            else:
                                data, column_names = fetch_table_data(table_name, limit)
                            display_table(data, column_names)
                        except ValueError as ve:
                            print(f"Invalid input: {ve}")
                        except SQLAlchemyError as se:
                            print(f"Error fetching table data: {se}")
                    else:
                        print(f"Table {table_name} does not exist.")
                else:
                    print("No tables found.")
                    
            elif choice == '3':
                tables = fetch_all_tables()
                if tables:
                    print("\nTables in the database:")
                    for table in tables:
                        print(table)
                    table_name = input("\nEnter table name: ")
                    if table_name in tables:
                        try:
                            columns_selection = input("Enter column indices (comma-separated) to display (leave blank for all): ").strip()
                            if columns_selection:
                                selected_columns = [idx.strip() for idx in columns_selection.split(',') if idx.strip().isdigit()]
                                data, column_names = fetch_table_data(table_name, selected_columns=','.join(selected_columns))
                            else:
                                data, column_names = fetch_table_data(table_name)
                            display_table(data, column_names)
                        except SQLAlchemyError as se:
                            print(f"Error fetching table data: {se}")
                    else:
                        print(f"Table {table_name} does not exist.")
                else:
                    print("No tables found.")

            elif choice == '4':
                break

            else:
                print("Invalid option, please try again.")

    except KeyboardInterrupt:
        print("\nExiting...")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

