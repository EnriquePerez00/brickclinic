#!/usr/bin/env python3
"""
Module 2A: OMR Downloader
Downloads official Star Wars .mpd files from LDraw OMR
"""

import os
import requests
from pathlib import Path
from typing import List, Dict
import time
from bs4 import BeautifulSoup

class OMRDownloader:
    """Downloads Star Wars sets from LDraw Official Model Repository"""
    
    def __init__(self, output_dir: str = "omr_data/star_wars"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://omr.ldraw.org"
        self.sets_url = f"{self.base_url}/sets"
        
        # Star Wars set prefixes (common numbers)
        self.star_wars_prefixes = [
            "75", "7", "10", "4", "6"  # Common SW set prefixes
        ]
    
    def get_star_wars_sets(self) -> List[Dict]:
        """
        Get list of Star Wars sets from OMR
        
        Note: This is a simplified implementation.
        Full implementation would scrape OMR website or use API.
        """
        
        # Hardcoded list of known Star Wars sets for PoC
        # In production, this would scrape OMR catalog
        star_wars_sets = [
            {"set_num": "75192-1", "name": "Millennium Falcon (UCS)", "category": "ucs"},
            {"set_num": "75181-1", "name": "Y-wing Starfighter (UCS)", "category": "ucs"},
            {"set_num": "75095-1", "name": "TIE Fighter (UCS)", "category": "ucs"},
            {"set_num": "75060-1", "name": "UCS Slave I", "category": "ucs"},
            
            {"set_num": "75301-1", "name": "Luke's X-wing Fighter", "category": "medium_ship"},
            {"set_num": "75300-1", "name": "Imperial TIE Fighter", "category": "medium_ship"},
            {"set_num": "75302-1", "name": "Imperial Shuttle", "category": "medium_ship"},
            
            {"set_num": "75321-1", "name": "Razor Crest Microfighter", "category": "small_ship"},
            {"set_num": "75295-1", "name": "Millennium Falcon Microfighter", "category": "small_ship"},
            {"set_num": "75263-1", "name": "Resistance Y-wing Microfighter", "category": "small_ship"},
        ]
        
        print(f"📋 Found {len(star_wars_sets)} Star Wars sets")
        return star_wars_sets
    
    def download_mpd(self, set_num: str) -> bool:
        """
        Download MPD file for a specific set
        
        Args:
            set_num: Set number (e.g., "75192-1")
        
        Returns:
            True if successful, False otherwise
        """
        
        # OMR file naming: usually set_num without suffix
        # Example: 75192-1.mpd or 75192.mpd
        clean_num = set_num.split('-')[0]
        
        # Try both formats
        for filename in [f"{clean_num}.mpd", f"{set_num}.mpd"]:
            mpd_url = f"{self.base_url}/models/{filename}"
            output_path = self.output_dir / filename
            
            # Skip if already downloaded
            if output_path.exists():
                print(f"   ⏭️  {filename} already exists")
                return True
            
            print(f"   📥 Downloading {mpd_url}...")
            
            try:
                response = requests.get(mpd_url, timeout=30)
                
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"   ✅ Downloaded {filename} ({len(response.content)} bytes)")
                    return True
                elif response.status_code == 404:
                    print(f"   ⚠️  {filename} not found (404)")
                    continue
                else:
                    print(f"   ❌ Error {response.status_code}")
                    continue
                    
            except requests.RequestException as e:
                print(f"   ❌ Download failed: {e}")
                continue
            
            # Rate limiting
            time.sleep(1)
        
        return False
    
    def download_all(self, max_sets: int = 50):
        """Download Star Wars sets from OMR"""
        
        print(f"\n🚀 OMR Star Wars Downloader")
        print(f"   Output: {self.output_dir}")
        print("=" * 60)
        
        sets = self.get_star_wars_sets()[:max_sets]
        
        downloaded = 0
        failed = 0
        
        for set_info in sets:
            set_num = set_info["set_num"]
            name = set_info["name"]
            
            print(f"\n{set_num} - {name}")
            
            if self.download_mpd(set_num):
                downloaded += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Download complete:")
        print(f"   Downloaded: {downloaded}")
        print(f"   Failed: {failed}")
        print(f"   Output dir: {self.output_dir}")


def main():
    """Download Star Wars OMR files"""
    
    downloader = OMRDownloader()
    downloader.download_all(max_sets=10)  # Start with 10 sets
    
    # List downloaded files
    mpd_files = list(Path("omr_data/star_wars").glob("*.mpd"))
    print(f"\n📁 Total MPD files: {len(mpd_files)}")
    for mpd in mpd_files:
        size_kb = mpd.stat().st_size / 1024
        print(f"   - {mpd.name:20} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
