import os
import logging
from dotenv import load_dotenv
from prettytable import PrettyTable
from sqlalchemy import create_engine, MetaData, Table

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
    metadata.reflect(bind=engine)
    return sorted(metadata.tables.keys())

# Function to fetch table data
def fetch_table_data(table_name, limit=None):
    conn = engine.connect()
    table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    columns = table.columns.keys()
    if limit:
        query = table.select().limit(limit)
    else:
        query = table.select()
    result = conn.execute(query)
    data = result.fetchall()
    conn.close()
    return data, columns

# Function to display table data
def display_table(data, column_names):
    table = PrettyTable()
    table.field_names = column_names
    for row in data:
        table.add_row(row)
    print(table)

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
                print("\nTables in the database:")
                for table in tables:
                    print(table)

            elif choice == '2':
                tables = fetch_all_tables()
                print("\nTables in the database:")
                for table in tables:
                    print(table)
                table_name = input("\nEnter table name: ")
                if table_name in tables:
                    limit = int(input("Enter the number of lines to display: "))
                    data, column_names = fetch_table_data(table_name, limit)
                    display_table(data, column_names)
                else:
                    print(f"Table {table_name} does not exist.")

            elif choice == '3':
                tables = fetch_all_tables()
                print("\nTables in the database:")
                for table in tables:
                    print(table)
                table_name = input("\nEnter table name: ")
                if table_name in tables:
                    data, column_names = fetch_table_data(table_name)
                    display_table(data, column_names)
                else:
                    print(f"Table {table_name} does not exist.")

            elif choice == '4':
                break

            else:
                print("Invalid option, please try again.")

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()

