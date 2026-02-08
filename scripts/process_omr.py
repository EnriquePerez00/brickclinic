#!/usr/bin/env python3
"""
Process OMR sets - Parse downloaded LDraw files and populate construction_steps
"""

import os
import sys
from pathlib import Path
from parse_ldraw_steps import LDrawParser

def process_omr_directory(omr_dir: str = "omr_data"):
    """Process all .mpd/.ldr files in the OMR directory"""
    
    if not os.path.exists(omr_dir):
        print(f"❌ Directory {omr_dir} not found. Run download_omr.py first.")
        return
    
    files = list(Path(omr_dir).glob("*.mpd")) + list(Path(omr_dir).glob("*.ldr"))
    
    if not files:
        print(f"❌ No .mpd/.ldr files found in {omr_dir}")
        return
    
    print(f"🔍 Found {len(files)} files to process")
    
    for filepath in files:
        # Extract set number from filename (e.g., "75033-1 - Star Destroyer.mpd" -> "75033-1")
        set_num = filepath.stem.split(' - ')[0]
        
        print(f"\n📦 Processing {set_num}...")
        try:
            parser = LDrawParser(str(filepath))
            steps = parser.parse()
            
            print(f"   Found {len(steps)} construction steps")
            
            # Save to database
            parser.save_to_db(set_num)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print("\n✅ Processing complete")


if __name__ == "__main__":
    process_omr_directory()
