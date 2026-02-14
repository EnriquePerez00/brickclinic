#!/usr/bin/env python3
"""
Enhanced OMR Scraper with Fallback Strategy
Downloads Star Wars sets from LDraw OMR + generates synthetic alternatives
"""

import os
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import re


class EnhancedOMRDownloader:
    """
    Downloads Star Wars sets from LDraw OMR with improved error handling
    """
    
    def __init__(self, output_dir: str = "omr_data"):
        self.base_url = "https://www.ldraw.org"
        self.omr_list_url = f"{self.base_url}/cgi-bin/ptlist.cgi?c=omr"
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Known Star Wars set numbers from research
        self.known_sw_sets = [
            "7150", "7180", "7190",  # Early 2000s
            "75211", "75212", "75213",  # Recent battle packs
            "75301", "75302", "75311",  # 2021-2022 releases
            "10030", "10179", "10221",  # UCS sets (from research)
        ]
    
    def scrape_omr_listing(self) -> List[Dict]:
        """Scrape OMR listing page for all Star Wars sets"""
        
        print("🔍 Scraping OMR listing...")
        
        try:
            response = requests.get(self.omr_list_url, timeout=15)
            if response.status_code != 200:
                print(f"   ⚠️  Failed to fetch listing (HTTP {response.status_code})")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all model links
            models = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                
                # Look for .mpd or .ldr files
                if '.mpd' in href or '.ldr' in href:
                    filename = href.split('/')[-1]
                    set_num = filename.replace('.mpd', '').replace('.ldr', '')
                    
                    # Check if it looks like a set number
                    if re.match(r'^\d{4,5}', set_num):
                        models.append({
                            'set_num': set_num,
                            'filename': filename,
                            'url': f"{self.base_url}{href}" if not href.startswith('http') else href
                        })
            
            print(f"   Found {len(models)} models in OMR listing")
            return models
            
        except Exception as e:
            print(f"   ❌ Error scraping listing: {e}")
            return []
    
    def download_mpd(self, set_num: str, url: Optional[str] = None) -> bool:
        """
        Download .mpd file for a set number
        
        Args:
            set_num: LEGO set number (e.g., "75301")
            url: Direct URL if known, otherwise construct
        
        Returns:
            True if successful
        """
        
        if not url:
            # Try multiple URL patterns
            urls_to_try = [
                f"{self.base_url}/library/official/omr/{set_num}.mpd",
                f"{self.base_url}/library/official/omr/models/{set_num}.mpd",
                f"{self.base_url}/cgi-bin/ptreleases.cgi?file={set_num}.mpd",
            ]
        else:
            urls_to_try = [url]
        
        for url_attempt in urls_to_try:
            try:
                print(f"   Trying {url_attempt}...")
                response = requests.get(url_attempt, timeout=10)
                
                if response.status_code == 200 and len(response.content) > 100:
                    # Verify it's actually an MPD file
                    content = response.text
                    if 'FILE' in content or '1 ' in content:  # Basic MPD validation
                        output_path = os.path.join(self.output_dir, f"{set_num}.mpd")
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"   ✅ Downloaded {set_num}.mpd ({len(response.content)} bytes)")
                        return True
                
            except Exception as e:
                continue  # Try next URL
        
        print(f"   ❌ Failed to download {set_num}")
        return False
    
    def batch_download_star_wars(self, max_sets: int = 20) -> Dict:
        """
        Download as many Star Wars sets as possible
        
        Returns:
            Statistics dict
        """
        
        print("\n🚀 Batch Download: Star Wars Sets")
        print("=" * 60)
        
        # Strategy 1: Known sets
        print("\n📋 Strategy 1: Known Star Wars sets")
        success_count = 0
        failed_sets = []
        
        for set_num in self.known_sw_sets[:max_sets]:
            if self.download_mpd(set_num):
                success_count += 1
                time.sleep(0.5)  # Be respectful
            else:
                failed_sets.append(set_num)
        
        # Strategy 2: Scraped listing
        if success_count < max_sets:
            print("\n📋 Strategy 2: Scraped OMR listing")
            models = self.scrape_omr_listing()
            
            # Filter for potential Star Wars sets (75xxx, 10xxx ranges)
            sw_models = [
                m for m in models
                if m['set_num'].startswith(('75', '10', '71'))
            ]
            
            for model in sw_models[:max_sets - success_count]:
                if self.download_mpd(model['set_num'], model['url']):
                    success_count += 1
                    time.sleep(0.5)
                else:
                    failed_sets.append(model['set_num'])
        
        print("\n" + "=" * 60)
        print(f"✅ Downloaded: {success_count} sets")
        print(f"❌ Failed: {len(failed_sets)} sets")
        
        if failed_sets[:5]:
            print(f"   Failed sets: {', '.join(failed_sets[:5])}...")
        
        return {
            'success': success_count,
            'failed': len(failed_sets),
            'failed_sets': failed_sets
        }


def main():
    """Run enhanced OMR downloader"""
    
    downloader = EnhancedOMRDownloader()
    stats = downloader.batch_download_star_wars(max_sets=15)
    
    # List downloaded files
    print("\n📦 Downloaded Files:")
    mpd_files = [f for f in os.listdir("omr_data") if f.endswith('.mpd')]
    for f in mpd_files:
        size = os.path.getsize(os.path.join("omr_data", f))
        print(f"   {f} ({size:,} bytes)")
    
    print(f"\n✅ Total: {len(mpd_files)} MPD files ready for processing")
    
    if stats['success'] < 10:
        print("\n⚠️  WARNING: Low download success rate")
        print("   → Falling back to synthetic generation recommended")


if __name__ == "__main__":
    main()
