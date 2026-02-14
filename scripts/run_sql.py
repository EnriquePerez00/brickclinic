import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit(1)

def run_sql_file(file_path):
    print(f"📂 Reading SQL file: {file_path}")
    with open(file_path, 'r') as f:
        sql = f.read()

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("🚀 Executing SQL...")
            connection.execute(text(sql))
            connection.commit()
            print("✅ SQL Executed Successfully.")
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_sql_file(sys.argv[1])
    else:
        print("Usage: python scripts/run_sql.py <path_to_sql_file>")
