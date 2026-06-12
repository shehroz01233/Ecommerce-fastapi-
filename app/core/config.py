import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_Zmlg6A0kfBWV@ep-frosty-firefly-aq7ec3ui-pooler.c-8.us-east-1.aws.neon.tech/LSM?sslmode=require")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60