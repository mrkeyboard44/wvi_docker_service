from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DB_USER = os.getenv('MYSQL_USER')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
DB_HOST = os.getenv('MYSQL_HOST')
DB_NAME = os.getenv('MYSQL_DATABASE')

# Define the database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

Base = declarative_base()

class Jobs(Base):
    __tablename__ = 'jobs-test-1'
    UUID = Column(String(50), primary_key=True)
    SerialId = Column(Integer)
    JobDateTime = Column(DateTime)
    JobEndDateTime = Column(DateTime)
    CreatedDate = Column(DateTime)
    JobTotalPrice = Column(Float)
    JobAmountDue = Column(Float)
    SubTotal = Column(Float)
    item_cost = Column(Float)
    tech_cost = Column(Float)
    ClientId = Column(Integer)
    Status = Column(String(255))
    SubStatus = Column(String(255))
    PaymentDueDate = Column(DateTime)
    Phone = Column(String(20))
    SecondPhone = Column(String(20))
    PhoneExt = Column(String(10))
    SecondPhoneExt = Column(String(10))
    Email = Column(String(255))
    FirstName = Column(String(255))
    LastName = Column(String(255))
    LineItems = Column(JSON)
    Company = Column(String(255))
    City = Column(String(255))
    State = Column(String(255))
    PostalCode = Column(String(20))
    Country = Column(String(255))
    Latitude = Column(Float)
    Longitude = Column(Float)
    Unit = Column(String(50))
    ServiceArea = Column(String(255))
    JobType = Column(String(255))
    JobNotes = Column(Text)
    JobSource = Column(String(255))
    Tags = Column(JSON)
    LastStatusUpdate = Column(DateTime)
    TeamId = Column(Integer)
    TeamName = Column(String(255))
    CreatedBy = Column(String(255))
    Address = Column(String(255))

class Leads(Base):
    __tablename__ = 'leads-test-2'
    UUID = Column(String(50), primary_key=True)
    SerialId = Column(Integer)
    LeadDateTime = Column(DateTime)
    LeadEndDateTime = Column(DateTime)
    CreatedDate = Column(DateTime)
    ClientId = Column(Integer)
    Status = Column(String(255))
    SubStatus = Column(String(255))
    PaymentDueDate = Column(DateTime)
    Phone = Column(String(20))
    SecondPhone = Column(String(20))
    PhoneExt = Column(String(10))
    SecondPhoneExt = Column(String(10))
    Email = Column(String(255))
    Comments = Column(Text)
    FirstName = Column(String(255))
    LastName = Column(String(255))
    Company = Column(String(255))
    Address = Column(String(255))
    City = Column(String(255))
    State = Column(String(255))
    PostalCode = Column(String(20))
    Country = Column(String(255))
    Unit = Column(String(50))
    Latitude = Column(Float)
    Longitude = Column(Float)
    JobType = Column(String(255))
    ReferralCompany = Column(String(255))
    Timezone = Column(String(50))
    JobSource = Column(String(255))
    LeadNotes = Column(Text)
    Team = Column(JSON)  # Assuming Team is stored as JSON

# Create the table if it does not exist
Base.metadata.create_all(create_engine(DATABASE_URL))

