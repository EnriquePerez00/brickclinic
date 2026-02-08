import os
import json
import torch
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def build_node_features():
    print("Fetching part data...")
    
    # query to get all parts with their features
    # distinct parts
    sql = text("""
        SELECT 
            p.part_num, 
            p.name, 
            pc.name as category, 
            COALESCE(psd.size_x, 0) as x, 
            COALESCE(psd.size_y, 0) as y, 
            COALESCE(psd.size_z, 0) as z, 
            COALESCE(psd.volume, 0) as vol,
            psd.connectivity_json
        FROM parts p
        LEFT JOIN part_categories pc ON p.part_cat_id = pc.id
        LEFT JOIN part_spatial_data psd ON p.part_num = psd.part_num
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    
    print(f"Loaded {len(df)} parts.")
    
    # 1. Process Connectivity (Extract stud count)
    def get_stud_count(json_data):
        if json_data is None: return 0
        if isinstance(json_data, (dict, list)): # Already parsed by SQLAlchemy
             if isinstance(json_data, dict):
                 return json_data.get('studs', 0)
             return 0
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
                return data.get('studs', 0)
        except:
            return 0
        return 0
        
    df['studs'] = df['connectivity_json'].apply(get_stud_count)
    
    # Fill NaN categories
    # df['category'] = df['category'].fillna('Unknown') -> This was causing a SettingWithCopyWarning potentially or valid.
    # Let's clean up dataframe before
    df['category'] = df['category'].fillna('Unknown')
    
    # 2. Normalize Numerical Features (x, y, z, vol, studs)
    scaler = StandardScaler()
    num_features = df[['x', 'y', 'z', 'vol', 'studs']].values
    num_features_scaled = scaler.fit_transform(num_features)
    
    # 3. One-Hot Encode Categories
    # Fill NaN categories
    df['category'] = df['category'].fillna('Unknown')
    encoder = OneHotEncoder(sparse_output=False)
    cat_features = encoder.fit_transform(df[['category']])
    
    # 4. Combine
    node_features = np.hstack([num_features_scaled, cat_features])
    
    # 5. Convert to Tensor
    x_tensor = torch.tensor(node_features, dtype=torch.float32)
    
    # 6. Create Mapping
    part_to_idx = {str(row['part_num']): idx for idx, row in df.iterrows()}
    
    # 7. Save
    os.makedirs("ai_data", exist_ok=True)
    torch.save(x_tensor, "ai_data/node_features.pt")
    with open("ai_data/part_to_idx.json", "w") as f:
        json.dump(part_to_idx, f)
        
    print(f"✅ Saved node features: {x_tensor.shape}")
    print(f"   - {num_features.shape[1]} physical features")
    print(f"   - {cat_features.shape[1]} categories")

if __name__ == "__main__":
    build_node_features()
