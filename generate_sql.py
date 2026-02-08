import os
import pandas as pd
import numpy as np

# Configuration
DATA_DIR = "./lego_inventory_data"
OUTPUT_DIR = "./supabase_inserts"
CHUNK_SIZE_ROWS = 2000 # Reduced to prevent "Query too large" errors in Supabase Editor

# Strict Schema Definition (Columns must match schema.sql exactly)
SCHEMA_COLUMNS = {
    "themes": ["id", "name", "parent_id"],
    "colors": ["id", "name", "rgb", "is_trans"],
    "part_categories": ["id", "name"],
    "parts": ["part_num", "name", "part_cat_id", "part_material"],
    "elements": ["element_id", "part_num", "color_id"],
    "part_relationships": ["rel_type", "child_part_num", "parent_part_num"],
    "minifigs": ["fig_num", "name", "num_parts"],
    "sets": ["set_num", "name", "year", "theme_id", "num_parts"],
    "inventories": ["id", "version", "set_num"],
    "inventory_parts": ["inventory_id", "part_num", "color_id", "quantity", "is_spare"],
    "inventory_minifigs": ["inventory_id", "fig_num", "quantity"],
    "inventory_sets": ["inventory_id", "set_num", "quantity"]
}

# Table map: (Table Name, CSV File)
tables = [
    ("themes", "themes.csv"),
    ("colors", "colors.csv"),
    ("part_categories", "part_categories.csv"),
    ("parts", "parts.csv"),
    ("elements", "elements.csv"),
    ("part_relationships", "part_relationships.csv"),
    ("minifigs", "minifigs.csv"),
    ("sets", "sets.csv"),
    ("inventories", "inventories.csv"),
    ("inventory_parts", "inventory_parts.csv"),
    ("inventory_minifigs", "inventory_minifigs.csv"),
    ("inventory_sets", "inventory_sets.csv"),
]

def escape_sql_string(val):
    if pd.isna(val):
        return "NULL"
    # Check for bool BEFORE int because isinstance(True, int) is True
    if isinstance(val, bool):
        return 'TRUE' if val else 'FALSE'
    if isinstance(val, (int, float)):
        # Check for NaN again just in case (pandas float/int handling)
        if np.isnan(val):
             return "NULL"
        if int(val) == val:
            return str(int(val))
        return str(val)
    
    val_str = str(val).replace("'", "''")
    return f"'{val_str}'"

def generate_insert_statement(table, df):
    # Filter columns to only those in the schema
    allowed_cols = SCHEMA_COLUMNS.get(table, [])
    if not allowed_cols:
        print(f"Warning: No schema defined for {table}, using all CSV columns.")
    else:
        # Only keep columns that are in schema AND in the df
        valid_cols = [c for c in allowed_cols if c in df.columns]
        
        # Check if we are missing any required columns
        missing_cols = set(allowed_cols) - set(valid_cols)
        if missing_cols:
            # If valid columns like 'parent_id' are missing in CSV, we might need to add them as NULL
            # This handles cases where CSV is cleaner than Schema or vice versa
            for col in missing_cols:
                # parts.part_material might be missing in older CSVs
                df[col] = np.nan
            valid_cols.extend(list(missing_cols))
            
        # Reorder df to match schema order (purely for readability)
        df = df[valid_cols]

    # Convert booleans
    if 'is_trans' in df.columns:
        df['is_trans'] = df['is_trans'].apply(lambda x: True if str(x).lower() in ['t', 'true', '1'] else False)
    if 'is_spare' in df.columns:
        df['is_spare'] = df['is_spare'].apply(lambda x: True if str(x).lower() in ['t', 'true', '1'] else False)

    statements = []
    columns = ", ".join(df.columns)
    
    for _, row in df.iterrows():
        values = ", ".join([escape_sql_string(x) for x in row])
        statements.append(f"({values})")
    
    if not statements:
        return ""

    return f"INSERT INTO {table} ({columns}) VALUES\n" + ",\n".join(statements) + ";"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Generating Clean SQL scripts in {OUTPUT_DIR}...")
    
    for i, (table, csv_file) in enumerate(tables):
        file_path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(file_path):
            print(f"Skipping {table}: Not found")
            continue
            
        print(f"Processing {table}...")
        prefix = f"{i+1:02d}"
        
        try:
            # Read first chunk to validate headers
            df_iter = pd.read_csv(file_path, chunksize=CHUNK_SIZE_ROWS)
            
            chunk_count = 0
            for chunk in df_iter:
                chunk_count += 1
                chunk = chunk.loc[:, ~chunk.columns.str.contains('^Unnamed')]
                
                sql_content = generate_insert_statement(table, chunk)
                
                filename = f"{prefix}_{table}_part{chunk_count}.sql"
                out_path = os.path.join(OUTPUT_DIR, filename)
                
                with open(out_path, "w", encoding='utf-8') as f:
                    f.write(sql_content)
                
                print(f"  Generated {filename} ({len(chunk)} rows)")
                
        except Exception as e:
            print(f"Error processing {table}: {e}")

    print("\nRegeneration Complete! Please try running the SQL files again.")

if __name__ == "__main__":
    main()
