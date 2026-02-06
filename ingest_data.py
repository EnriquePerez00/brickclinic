import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string
# Ensure you have DATABASE_URL set in your .env file
# Example: postgresql://postgres:password@db.supabase.co:5432/postgres
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    print("Error: DATABASE_URL not found in .env file.")
    print("Please set it to your Supabase connection string.")
    print("Example: DATABASE_URL=postgresql://postgres.yourproject:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    exit(1)

# Initialize database engine
try:
    engine = create_engine(DB_URL)
    connection = engine.connect()
    print("Connected to database successfully.")
    connection.close()
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit(1)

# Path to CSV files
DATA_DIR = "./lego_inventory_data"

# Mapping of file names to table names (Order matters for Foreign Keys!)
# Table Name -> CSV File Name
ingest_order = [
    ("themes", "themes.csv"),
    ("colors", "colors.csv"),
    ("part_categories", "part_categories.csv"),
    ("parts", "parts.csv"),
    # "elements" depends on parts and colors
    ("elements", "elements.csv"),
    # "part_relationships" depends on parts
    ("part_relationships", "part_relationships.csv"),
    ("minifigs", "minifigs.csv"),
    # "sets" depends on themes
    ("sets", "sets.csv"),
    # "inventories" depends on sets
    ("inventories", "inventories.csv"),
    # Dependents on inventories
    ("inventory_parts", "inventory_parts.csv"),
    ("inventory_minifigs", "inventory_minifigs.csv"),
    ("inventory_sets", "inventory_sets.csv"),
]

def ingest_table(table_name, file_name, chunksize=5000):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"⚠️ Skipping {table_name}: {file_name} not found.")
        return

    print(f"🚀 Processing {table_name} from {file_name}...")
    
    try:
        # Define converters for boolean fields
        converters = {}
        if table_name == 'colors':
            converters = {'is_trans': lambda x: True if str(x).lower() in ['t', 'true', '1'] else False}
        elif table_name == 'inventory_parts':
            converters = {'is_spare': lambda x: True if str(x).lower() in ['t', 'true', '1'] else False}
            
        # Read CSV in chunks
        chunk_iter = pd.read_csv(file_path, chunksize=chunksize, converters=converters)
        
        total_rows = 0
        for i, chunk in enumerate(chunk_iter):
            # Clean up columns: remove 'Unnamed' index columns if they exist
            chunk = chunk.loc[:, ~chunk.columns.str.contains('^Unnamed')]
            
            # Additional cleaning if necessary
            # e.g., ensure NaN in integer columns are handled if schema allows nulls, 
            # or fillna if not.
            
            # Using 'append' to respect the existing schema created by SQL
            chunk.to_sql(
                table_name, 
                engine, 
                if_exists='append', 
                index=False, 
                method='multi'  # standard insert compatible with postgres
            )
            total_rows += len(chunk)
            print(f"   Inserted chunk {i+1} ({len(chunk)} rows). Total: {total_rows}")
                
        print(f"✅ Successfully ingested {table_name}.")

    except Exception as e:
        print(f"❌ Error ingesting {table_name}: {e}")

def main():
    print("Starting LEGO Data Ingestion...")
    print("Make sure you have run schema.sql in Supabase first to create tables!")
    
    for table, file_name in ingest_order:
        ingest_table(table, file_name)

    print("\n🎉 Ingestion complete!")

if __name__ == "__main__":
    main()
