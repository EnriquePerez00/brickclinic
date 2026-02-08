import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    # 1. Find a theme with sets
    print("Searching for a populated theme...")
    theme_sql = text("""
        SELECT t.id, t.name, COUNT(s.set_num) as set_count 
        FROM themes t
        JOIN sets s ON t.id = s.theme_id
        GROUP BY t.id, t.name
        ORDER BY set_count DESC
        LIMIT 1;
    """)
    theme = connection.execute(theme_sql).fetchone()
    
    if not theme:
        print("No themes found with sets.")
        exit(0)
        
    theme_id, theme_name, count = theme
    print(f"Analyzing Theme: {theme_name} (ID: {theme_id}, Sets: {count})")
    
    # 2. Run DNA Analysis
    print("Running get_theme_dna()...")
    dna_sql = text("SELECT get_theme_dna(:tid)")
    result = connection.execute(dna_sql, {"tid": theme_id}).scalar()
    
    print("\n--- DNA RESULT ---")
    print(json.dumps(result, indent=2))
