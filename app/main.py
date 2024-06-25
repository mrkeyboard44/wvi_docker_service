import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Jobs, Leads
from utils import fetch_data_in_batches
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DB_USER = os.getenv('MYSQL_USER')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_HOST = os.getenv('MYSQL_HOST')
DB_NAME = os.getenv('MYSQL_DATABASE')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


# Set up the database connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create the table if it does not exist
from models import Base
Base.metadata.create_all(engine)


def get_date_six_months_ago():
    # Get the current date
    current_date = datetime.now()
    # Calculate the date 6 months ago
    six_months_ago = current_date - timedelta(days=30*6)
    
    # Check if 6 months ago is in a different year
    if six_months_ago.year < current_date.year:
        # Return first day of the current year
        first_day_current_year = datetime(current_date.year, 1, 1)
        return [six_months_ago.strftime("%Y-%m-%d"), first_day_current_year.strftime("%Y-%m-%d")]
    else:
        return [six_months_ago.strftime("%Y-%m-%d"), False]


    return date


if __name__ == "__main__":
    session = Session()
    
    # Example variables for date and start offset
    six_months_ago, date_2 = get_date_six_months_ago()
    start_offset = 0
    
    # Fetch and save job data from multiple endpoints
    fetch_data_in_batches(API_TOKEN, 'job/all', six_months_ago, start_offset, Jobs, session)
    if date_2:
        fetch_data_in_batches(API_TOKEN, 'job/all', date_2, start_offset, Jobs, session)

    fetch_data_in_batches(API_TOKEN, 'lead/all', six_months_ago, start_offset, Leads, session)
    if date_2:
        fetch_data_in_batches(API_TOKEN, 'lead/all', date_2, start_offset, Jobs, session)

    
    session.close()

