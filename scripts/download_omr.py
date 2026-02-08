#!/usr/bin/env python3
"""
OMR Downloader - Fetch Star Wars sets from Official Model Repository
PoC: Download 3 small sets for testing
"""

import os
import requests
from pathlib import Path

# OMR GitHub repository
OMR_BASE = "https://raw.githubusercontent.com/ldraw-org/omr/main/ldraw/models/"

# PoC: 3 small Star Wars sets (easier to parse, faster to train)
STAR_WARS_SETS = [
    "30497-1 - First Order Heavy Assault Walker.mpd",
    "75033-1 - Star Destroyer.mpd", 
    "75229-1 - Death Star Escape.mpd"
]

def download_omr_set(filename: str, output_dir: str = "omr_data"):
    """Download a single set from OMR"""
    os.makedirs(output_dir, exist_ok=True)
    
    url = OMR_BASE + filename.replace(" ", "%20")
    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        print(f"⏭️  Already exists: {filename}")
        return output_path
    
    print(f"📥 Downloading: {filename}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {filename} ({len(response.content)} bytes)")
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {filename}: {e}")
        return None


def download_poc_sets():
    """Download PoC sets for testing"""
    print("🚀 Downloading Star Wars PoC sets from OMR...")
    
    downloaded = []
    for set_file in STAR_WARS_SETS:
        path = download_omr_set(set_file)
        if path:
            downloaded.append(path)
    
    print(f"\n✅ Downloaded {len(downloaded)}/{len(STAR_WARS_SETS)} sets")
    return downloaded


if __name__ == "__main__":
    download_poc_sets()
