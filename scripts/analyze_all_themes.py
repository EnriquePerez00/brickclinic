import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Theme IDs mapped to names
# Dynamic Switch: Fetch Top 50 themes by set count
print("Fetching top 50 themes by set count...")
with engine.connect() as connection:
    theme_sql = text("""
        SELECT t.id, t.name, COUNT(s.set_num) as set_count
        FROM themes t
        JOIN sets s ON t.id = s.theme_id
        GROUP BY t.id, t.name
        HAVING COUNT(s.set_num) > 50
        ORDER BY set_count DESC
        LIMIT 50;
    """)
    target_themes = connection.execute(theme_sql).fetchall()

results = {}

with engine.connect() as connection:
    for tid, name, count in target_themes:
        print(f"Analyzing {name} (ID: {tid}, Sets: {count})...")
        try:
            sql = text("SELECT get_theme_dna(:tid)")
            result = connection.execute(sql, {"tid": tid}).scalar()
            results[name] = result
            # print(f"✅ DNA Extracted for {name}")
        except Exception as e:
            print(f"❌ Error for {name}: {e}")

print("\n--- DNA SUMMARY (Top 50 Themes) ---")
for name, data in results.items():
    print(f"\n[{name}]")
    if data:
        # Print top 3 colors
        if 'color_palette' in data and data['color_palette']:
            print("  🎨 Colors:", list(data['color_palette'].items())[:3])
        # Print top 3 part categories
        if 'part_categories' in data and data['part_categories']:
            print("  🧱 Parts:", list(data['part_categories'].items())[:3])
    else:
        print("  No Data.")
