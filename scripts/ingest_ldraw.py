import os
import requests
import json
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# LDraw Constants
LDRAW_BASE_URL = "https://library.ldraw.org/library/official"
PARTS_DIR = "./ldraw_cache/parts"
P_DIR = "./ldraw_cache/p"

os.makedirs(PARTS_DIR, exist_ok=True)
os.makedirs(P_DIR, exist_ok=True)

class LDrawParser:
    def __init__(self):
        self.stud_refs = ["stud.dat", "stud2.dat", "stud3.dat", "stud4.dat", "stud6.dat", "stud10.dat", "stud12.dat", "stud15.dat", "studp01.dat", "studel.dat"]
        self.tube_refs = ["tube.dat"]
        
    def download_part(self, filename):
        """Downloads a part or primitive from LDraw library if not cached."""
        # Determine if it's a part or primitive
        is_primitive = filename.lower() in [s.lower() for s in self.stud_refs + self.tube_refs] or filename.startswith("s/") or filename.startswith("48/")
        
        local_path = os.path.join(PARTS_DIR, filename)
        # Check cache
        if os.path.exists(local_path):
            return local_path
            
        # URL construction (simplified logic, real LDraw logic is complex with p/ vs parts/)
        # Trying 'parts/' first, then 'p/'
        urls_to_try = [
            f"{LDRAW_BASE_URL}/parts/{filename}",
            f"{LDRAW_BASE_URL}/p/{filename}"
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    logging.info(f"Downloaded: {filename}")
                    return local_path
            except Exception as e:
                logging.warning(f"Failed to fetch {url}: {e}")
                
        logging.error(f"Could not download {filename}")
        return None

    def parse_file(self, file_path):
        """Parses LDraw file to find bounding box and connectivity."""
        vertices = []
        connectivity = {"studs": 0, "tubes": 0}
        
        if not file_path or not os.path.exists(file_path):
            return None, None

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.split()
            if not parts: continue
            line_type = parts[0]
            
            # Type 1: Sub-file reference (Recursive)
            if line_type == '1':
                # Format: 1 <colour> x y z a b c d e f g h i <file>
                # We simplified: just counting specific primitives for now
                # In a full recursive parser, we'd apply matrix transform to sub-file vertices
                ref_file = " ".join(parts[14:]).lower()
                
                if ref_file in self.stud_refs:
                    connectivity["studs"] += 1
                elif ref_file in self.tube_refs:
                    connectivity["tubes"] += 1
                else:
                    # Recursive download & parsing? 
                    # For MVP, we might skip deep recursion for BBox to avoid infinite loops/complexity
                    pass

            # Type 2, 3, 4: Geometry Lines, Triangles, Quads
            # Just collecting vertices to estimate BBox
            # 2 <colour> x1 y1 z1 x2 y2 z2
            elif line_type == '2':
                vertices.append((float(parts[2]), float(parts[3]), float(parts[4])))
                vertices.append((float(parts[5]), float(parts[6]), float(parts[7])))
            # 3 <colour> x1 y1 z1 x2 y2 z2 x3 y3 z3
            elif line_type == '3':
                vertices.append((float(parts[2]), float(parts[3]), float(parts[4])))
                vertices.append((float(parts[5]), float(parts[6]), float(parts[7])))
                vertices.append((float(parts[8]), float(parts[9]), float(parts[10])))
            # 4 <colour> x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4
            elif line_type == '4':
                vertices.append((float(parts[2]), float(parts[3]), float(parts[4])))
                vertices.append((float(parts[5]), float(parts[6]), float(parts[7])))
                vertices.append((float(parts[8]), float(parts[9]), float(parts[10])))
                vertices.append((float(parts[11]), float(parts[12]), float(parts[13])))
                
        if not vertices:
             return {"min": (0,0,0), "max":(0,0,0), "size": (0,0,0)}, connectivity
             
        # Calculate BBox
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        
        bbox = {
            "min": (min(xs), min(ys), min(zs)),
            "max": (max(xs), max(ys), max(zs)),
            "size": (max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
        }
        
        return bbox, connectivity

def main():
    if not DATABASE_URL:
        logging.error("DATABASE_URL must be set")
        exit(1)
        
    engine = create_engine(DATABASE_URL)
    parser = LDrawParser()
    
    with engine.connect() as connection:
        # Fetch ALL parts from the database that don't have spatial data yet
        # Removing specific theme filters to cover ALL series.
        # LIMIT 500 for this batch run (User can re-run script to process more)
        logging.info("Fetching parts list from database (All Themes)...")
        
        sql_fetch = text("""
            SELECT p.part_num 
            FROM parts p
            LEFT JOIN part_spatial_data s ON p.part_num = s.part_num
            WHERE s.part_num IS NULL
            LIMIT 500;
        """)
        
        result = connection.execute(sql_fetch)
        parts_to_process = [row[0] for row in result]
        
        logging.info(f"Found {len(parts_to_process)} parts to process (Batch 1).")
        
        for part_num in parts_to_process:
            # LDraw files usually end in .dat. DB part_num might not.
            # Some DB part_nums have suffixes like '3001' or '3001-1'. LDraw usually wants '3001.dat'.
            # We try adding .dat
            part_file = f"{part_num}.dat"
            
            logging.info(f"Processing {part_num} ({part_file})...")
            
            # Download
            path = parser.download_part(part_file)
            if not path:
                # Try stripping version if exists e.g. "3001-1" -> "3001.dat"
                if "-" in part_num:
                     clean_num = part_num.split("-")[0]
                     part_file = f"{clean_num}.dat"
                     path = parser.download_part(part_file)
                
                if not path:
                    logging.warning(f"Skipping {part_num}: File not found in LDraw.")
                    continue
                
            # Parse
            bbox, conn = parser.parse_file(path)
            if not bbox:
                continue
            
            sql_insert = text("""
                INSERT INTO part_spatial_data (part_num, size_x, size_y, size_z, connectivity_json)
                VALUES (:pn, :sx, :sy, :sz, :cj)
                ON CONFLICT (part_num) DO UPDATE 
                SET size_x = :sx, size_y = :sy, size_z = :sz, connectivity_json = :cj;
            """)
            
            try:
                connection.execute(sql_insert, {
                    "pn": part_num,
                    "sx": bbox["size"][0],
                    "sy": bbox["size"][1],
                    "sz": bbox["size"][2],
                    "cj": json.dumps(conn)
                })
                connection.commit()
                logging.info(f"✅ Saved spatial data for {part_num}")
            except Exception as e:
                logging.error(f"DB Error for {part_num}: {e}")

if __name__ == "__main__":
    main()
