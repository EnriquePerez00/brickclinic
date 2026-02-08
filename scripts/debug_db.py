import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        # Check extensions
        print("--- Extensions ---")
        result = connection.execute(text("SELECT extname FROM pg_extension;"))
        for row in result:
            print(row[0])
            
        # Check Columns in Parts Table
        print("\n--- Columns in 'parts' table ---")
        sql = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'parts';
        """
        result = connection.execute(text(sql))
        for row in result:
            print(row)
            
        print("\n--- Sample Parts Data ---")
        result = connection.execute(text("SELECT part_num, name FROM parts LIMIT 10;"))
        for row in result:
            print(row)

except Exception as e:
    print(f"Error: {e}")
