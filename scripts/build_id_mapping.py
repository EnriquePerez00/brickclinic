#!/usr/bin/env python3
"""
Module 1: ID Cross-Reference Mapper
Maps Rebrickable part IDs to LDraw filenames using multiple strategies
"""

import os
import re
from typing import Dict, Tuple, Optional
from difflib import SequenceMatcher
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import requests
from pathlib import Path

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


class IDMapper:
    """Maps Rebrickable IDs to LDraw filenames"""
    
    def __init__(self, ldraw_parts_dir: str = None):
        self.ldraw_parts_dir = ldraw_parts_dir or os.path.expanduser("~/ldraw/parts")
        self.ldraw_files = self._scan_ldraw_files()
        self.cache = {}  # In-memory cache
        
        print(f"📁 Found {len(self.ldraw_files)} LDraw part files")
    
    def _scan_ldraw_files(self) -> Dict[str, str]:
        """Scan LDraw directory and extract part numbers"""
        files = {}
        
        if not os.path.exists(self.ldraw_parts_dir):
            print(f"⚠️ LDraw directory not found: {self.ldraw_parts_dir}")
            print("   Using placeholder data for PoC")
            # Common parts for demo
            return {
                "3001": "3001.dat",
                "3003": "3003.dat",
                "3004": "3004.dat",
                "3005": "3005.dat",
                "3020": "3020.dat",
                "3023": "3023.dat",
                "3024": "3024.dat",
                "3062b": "3062b.dat",
                "4070": "4070.dat",
                "32316": "32316.dat",
                "32523": "32523.dat",
            }
        
        parts_path = Path(self.ldraw_parts_dir)
        for file in parts_path.glob("*.dat"):
            part_num = file.stem
            files[part_num] = file.name
        
        return files
    
    def map_exact(self, rebrickable_id: str) -> Optional[Tuple[str, float]]:
        """Exact match: '3001' → '3001.dat'"""
        
        # Clean Rebrickable ID (remove suffixes like '-1')
        clean_id = rebrickable_id.split('-')[0]
        
        if clean_id in self.ldraw_files:
            return self.ldraw_files[clean_id], 1.0
        
        return None
    
    def map_fuzzy(self, rebrickable_id: str, threshold: float = 0.8) -> Optional[Tuple[str, float]]:
        """Fuzzy match using string similarity"""
        
        clean_id = rebrickable_id.split('-')[0].lower()
        
        best_match = None
        best_score = 0.0
        
        for ldraw_part, filename in self.ldraw_files.items():
            ldraw_clean = ldraw_part.lower()
            
            # Try direct substring match
            if clean_id in ldraw_clean or ldraw_clean in clean_id:
                score = 0.95
            else:
                # Compute similarity ratio
                score = SequenceMatcher(None, clean_id, ldraw_clean).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = filename
        
        if best_match:
            return best_match, best_score
        
        return None
    
    def map_with_fallback(self, rebrickable_id: str) -> Tuple[Optional[str], str, float]:
        """
        Try multiple mapping strategies with fallback
        
        Returns:
            (ldraw_filename, method, confidence_score)
        """
        
        # Check cache first
        if rebrickable_id in self.cache:
            cached = self.cache[rebrickable_id]
            return cached['filename'], cached['method'], cached['confidence']
        
        # Strategy 1: Exact match
        result = self.map_exact(rebrickable_id)
        if result:
            self.cache[rebrickable_id] = {
                'filename': result[0],
                'method': 'exact',
                'confidence': result[1]
            }
            return result[0], 'exact', result[1]
        
        # Strategy 2: Fuzzy match
        result = self.map_fuzzy(rebrickable_id)
        if result:
            self.cache[rebrickable_id] = {
                'filename': result[0],
                'method': 'fuzzy',
                'confidence': result[1]
            }
            return result[0], 'fuzzy', result[1]
        
        # No match found
        return None, 'none', 0.0
    
    def build_database_mappings(self):
        """Build mappings for all parts in Rebrickable database"""
        
        print("\n🔄 Building ID mappings from Rebrickable parts...")
        
        # Get all parts from Rebrickable
        sql = text("SELECT part_num, name, part_cat_id FROM parts LIMIT 1000")
        
        with engine.connect() as conn:
            parts = conn.execute(sql).fetchall()
        
        print(f"   Processing {len(parts)} parts...")
        
        mapped_count = 0
        exact_count = 0
        fuzzy_count = 0
        
        for part in parts:
            rebrickable_id = part[0]
            part_name = part[1]
            category_id = part[2]
            
            ldraw_filename, method, confidence = self.map_with_fallback(rebrickable_id)
            
            if ldraw_filename:
                # Save to database
                insert_sql = text("""
                    INSERT INTO part_id_mapping 
                    (rebrickable_id, ldraw_filename, part_name, category, 
                     verified, mapping_method, confidence_score)
                    VALUES (:rb_id, :ld_file, :name, :cat, :verified, :method, :conf)
                    ON CONFLICT (rebrickable_id) 
                    DO UPDATE SET
                        ldraw_filename = EXCLUDED.ldraw_filename,
                        mapping_method = EXCLUDED.mapping_method,
                        confidence_score = EXCLUDED.confidence_score,
                        last_updated = CURRENT_TIMESTAMP
                """)
                
                with engine.connect() as conn:
                    conn.execute(insert_sql, {
                        'rb_id': rebrickable_id,
                        'ld_file': ldraw_filename,
                        'name': part_name,
                        'cat': str(category_id) if category_id else None,
                        'verified': method == 'exact',
                        'method': method,
                        'conf': confidence
                    })
                    conn.commit()
                
                mapped_count += 1
                if method == 'exact':
                    exact_count += 1
                elif method == 'fuzzy':
                    fuzzy_count += 1
        
        print(f"\n✅ Mapping complete:")
        print(f"   Total mapped: {mapped_count}/{len(parts)} ({100*mapped_count/len(parts):.1f}%)")
        print(f"   Exact matches: {exact_count}")
        print(f"   Fuzzy matches: {fuzzy_count}")
        print(f"   Unmapped: {len(parts) - mapped_count}")
    
    def get_mapping(self, rebrickable_id: str) -> Optional[str]:
        """Get LDraw filename for a Rebrickable ID (production method)"""
        
        # Check cache
        if rebrickable_id in self.cache:
            return self.cache[rebrickable_id]['filename']
        
        # Check database
        sql = text("""
            SELECT ldraw_filename FROM part_id_mapping 
            WHERE rebrickable_id = :rb_id
            AND confidence_score > 0.7
            LIMIT 1
        """)
        
        with engine.connect() as conn:
            result = conn.execute(sql, {'rb_id': rebrickable_id}).fetchone()
        
        if result:
            ldraw_filename = result[0]
            # Cache it
            self.cache[rebrickable_id] = {
                'filename': ldraw_filename,
                'method': 'database',
                'confidence': 1.0
            }
            return ldraw_filename
        
        # Fallback to live mapping
        ldraw_filename, method, confidence = self.map_with_fallback(rebrickable_id)
        return ldraw_filename


def main():
    """Build initial mappings"""
    
    print("🚀 Module 1: ID Cross-Reference System")
    print("=" * 60)
    
    mapper = IDMapper()
    
    # Test some common parts
    print("\n🧪 Testing mapping:")
    test_parts = ["3001", "3020", "3003-1", "32316", "4070"]
    
    for part in test_parts:
        ldraw, method, conf = mapper.map_with_fallback(part)
        status = "✅" if ldraw else "❌"
        print(f"   {status} {part:10} → {ldraw or 'NOT FOUND':15} ({method}, {conf:.2f})")
    
    # Build full database
    print("\n" + "=" * 60)
    mapper.build_database_mappings()


if __name__ == "__main__":
    main()
