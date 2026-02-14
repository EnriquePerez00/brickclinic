import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

themes_to_find = ["Technic", "Architecture", "City", "Icons", "Star Wars", "Creator Expert"] # Icons is often Creator Expert

with engine.connect() as connection:
    print("Searching for Theme IDs...")
    for name in themes_to_find:
        sql = text("SELECT id, name FROM themes WHERE name ILIKE :name")
        result = connection.execute(sql, {"name": f"%{name}%"}).fetchall()
        for row in result:
            print(f"Found: {row[1]} (ID: {row[0]})")
