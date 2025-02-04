import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from datetime import timedelta
from sqlalchemy import create_engine
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    
    DB_CONFIG={
        "dbname":os.getenv("DB_NAME"),
        "user":os.getenv("DB_USER"),
        "password":os.getenv("DB_PASSWORD"),
        "host":os.getenv("DB_HOST"),
        "port":os.getenv("DB_PORT")
    }

  

    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=45)
    DATABASE_URL="postgresql://postgres.jnprlgdommvwvtcoyfsj:kipkoech2024@aws-0-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=verify-full"
    engine = create_engine(DATABASE_URL)
    