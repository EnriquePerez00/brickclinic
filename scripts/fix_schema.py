import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit(1)

def run_step(connection, description, sql):
    print(f"👉 {description}...")
    try:
        connection.execute(text(sql))
        connection.commit()
        print("   ✅ Success.")
    except Exception as e:
        connection.rollback()
        print(f"   ⚠️  Failed/Skipped: {e}")

try:
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        print("🔧 Attempting to fix Schema (PKs and FKs)...")
        
        # 1. Add Primary Keys (Pandas doesn't create them)
        run_step(connection, "Adding PK to themes", "ALTER TABLE themes ADD PRIMARY KEY (id);")
        run_step(connection, "Adding PK to colors", "ALTER TABLE colors ADD PRIMARY KEY (id);")
        run_step(connection, "Adding PK to part_categories", "ALTER TABLE part_categories ADD PRIMARY KEY (id);")
        run_step(connection, "Adding PK to parts", "ALTER TABLE parts ADD PRIMARY KEY (part_num);")
        run_step(connection, "Adding PK to elements", "ALTER TABLE elements ADD PRIMARY KEY (element_id);")
        run_step(connection, "Adding PK to minifigs", "ALTER TABLE minifigs ADD PRIMARY KEY (fig_num);")
        run_step(connection, "Adding PK to sets", "ALTER TABLE sets ADD PRIMARY KEY (set_num);")
        run_step(connection, "Adding PK to inventories", "ALTER TABLE inventories ADD PRIMARY KEY (id);")
        
        # 2. Add Foreign Keys
        # inventory_parts -> inventories
        run_step(connection, "FK: inventory_parts -> inventories", 
                 "ALTER TABLE inventory_parts ADD CONSTRAINT fk_inventory_parts_inventory_id FOREIGN KEY (inventory_id) REFERENCES inventories(id);")
        
        # inventory_parts -> parts
        run_step(connection, "FK: inventory_parts -> parts", 
                 "ALTER TABLE inventory_parts ADD CONSTRAINT fk_inventory_parts_part_num FOREIGN KEY (part_num) REFERENCES parts(part_num);")
                 
        # inventory_parts -> colors
        run_step(connection, "FK: inventory_parts -> colors", 
                 "ALTER TABLE inventory_parts ADD CONSTRAINT fk_inventory_parts_color_id FOREIGN KEY (color_id) REFERENCES colors(id);")

        # inventories -> sets
        run_step(connection, "FK: inventories -> sets", 
                 "ALTER TABLE inventories ADD CONSTRAINT fk_inventories_set_num FOREIGN KEY (set_num) REFERENCES sets(set_num);")

        print("\n🏁 Schema Fix Complete.")
        
        # Reload PostgREST schema cache
        run_step(connection, "Reloading PostgREST config", "NOTIFY pgrst, 'reload config';")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
