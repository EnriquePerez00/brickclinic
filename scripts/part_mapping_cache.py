#!/usr/bin/env python3
"""
Optimized RAM Cache for Part ID Mappings
Leverages Mac Pro unified memory architecture
"""

import os
import json
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from functools import lru_cache
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


@dataclass
class PartMapping:
    """Cached part mapping entry"""
    rebrickable_id: str
    ldraw_filename: str
    part_name: str
    category: Optional[str]
    confidence: float
    method: str


class PartMappingCache:
    """
    High-performance in-memory cache for part ID mappings
    Optimized for Mac Pro unified memory
    """
    
    def __init__(self, max_ram_gb: float = 4.0):
        """
        Args:
            max_ram_gb: Maximum RAM to use for cache (default 4GB)
        """
        self.max_ram_gb = max_ram_gb
        self.rb_to_ldraw: Dict[str, PartMapping] = {}  # Rebrickable → LDraw
        self.ldraw_to_rb: Dict[str, PartMapping] = {}  # LDraw → Rebrickable (reverse)
        self.cache_hits = 0
        self.cache_misses = 0
        
        print(f"💾 Initializing PartMappingCache (max {max_ram_gb}GB RAM)")
    
    def load_from_database(self, confidence_threshold: float = 0.7):
        """Load all high-confidence mappings into RAM"""
        
        print(f"🔄 Loading mappings from database (confidence > {confidence_threshold})...")
        start_time = time.time()
        
        sql = text("""
            SELECT 
                rebrickable_id,
                ldraw_filename,
                part_name,
                category,
                confidence_score,
                mapping_method
            FROM part_id_mapping
            WHERE confidence_score >= :threshold
            ORDER BY confidence_score DESC
        """)
        
        with engine.connect() as conn:
            results = conn.execute(sql, {'threshold': confidence_threshold}).fetchall()
        
        for row in results:
            mapping = PartMapping(
                rebrickable_id=row[0],
                ldraw_filename=row[1],
                part_name=row[2],
                category=row[3],
                confidence=row[4],
                method=row[5]
            )
            
            self.rb_to_ldraw[mapping.rebrickable_id] = mapping
            self.ldraw_to_rb[mapping.ldraw_filename] = mapping
        
        elapsed = time.time() - start_time
        print(f"✅ Loaded {len(self.rb_to_ldraw)} mappings in {elapsed:.2f}s")
        print(f"   RAM usage: ~{self._estimate_ram_mb():.1f} MB")
    
    def get_ldraw_filename(self, rebrickable_id: str) -> Optional[str]:
        """Get LDraw filename for Rebrickable ID"""
        
        if rebrickable_id in self.rb_to_ldraw:
            self.cache_hits += 1
            return self.rb_to_ldraw[rebrickable_id].ldraw_filename
        
        self.cache_misses += 1
        
        # Fallback to database (cache miss)
        sql = text("""
            SELECT ldraw_filename FROM part_id_mapping
            WHERE rebrickable_id = :rb_id
            ORDER BY confidence_score DESC
            LIMIT 1
        """)
        
        with engine.connect() as conn:
            result = conn.execute(sql, {'rb_id': rebrickable_id}).fetchone()
        
        if result:
            # Add to cache for next time
            mapping = PartMapping(
                rebrickable_id=rebrickable_id,
                ldraw_filename=result[0],
                part_name="",
                category=None,
                confidence=0.9,
                method="database_fallback"
            )
            self.rb_to_ldraw[rebrickable_id] = mapping
            return result[0]
        
        return None
    
    def get_rebrickable_id(self, ldraw_filename: str) -> Optional[str]:
        """Reverse lookup: LDraw → Rebrickable"""
        
        if ldraw_filename in self.ldraw_to_rb:
            self.cache_hits += 1
            return self.ldraw_to_rb[ldraw_filename].rebrickable_id
        
        self.cache_misses += 1
        return None
    
    def _estimate_ram_mb(self) -> float:
        """Estimate RAM usage"""
        # Rough estimate: ~200 bytes per mapping
        return (len(self.rb_to_ldraw) * 200) / (1024 * 1024)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_mappings': len(self.rb_to_ldraw),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_pct': hit_rate,
            'ram_mb': self._estimate_ram_mb()
        }
    
    def save_to_json(self, filepath: str):
        """Save cache to JSON for fast loading"""
        
        data = {
            'mappings': [asdict(m) for m in self.rb_to_ldraw.values()],
            'metadata': {
                'count': len(self.rb_to_ldraw),
                'generated_at': time.time()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Cache saved to {filepath}")
    
    def load_from_json(self, filepath: str):
        """Load cache from JSON (faster than database)"""
        
        print(f"📂 Loading cache from {filepath}...")
        start_time = time.time()
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for mapping_data in data['mappings']:
            mapping = PartMapping(**mapping_data)
            self.rb_to_ldraw[mapping.rebrickable_id] = mapping
            self.ldraw_to_rb[mapping.ldraw_filename] = mapping
        
        elapsed = time.time() - start_time
        print(f"✅ Loaded {len(self.rb_to_ldraw)} mappings in {elapsed:.2f}s")


# Singleton instance for global access
_global_cache: Optional[PartMappingCache] = None


def get_cache() -> PartMappingCache:
    """Get or create global cache instance"""
    global _global_cache
    
    if _global_cache is None:
        _global_cache = PartMappingCache(max_ram_gb=4.0)
        
        # Try to load from JSON first (fastest)
        json_path = "ai_data/part_mapping_cache.json"
        if os.path.exists(json_path):
            _global_cache.load_from_json(json_path)
        else:
            # Load from database and save JSON for next time
            _global_cache.load_from_database(confidence_threshold=0.7)
            os.makedirs("ai_data", exist_ok=True)
            _global_cache.save_to_json(json_path)
    
    return _global_cache


# Convenience functions
def rb_to_ldraw(rebrickable_id: str) -> Optional[str]:
    """Quick conversion: Rebrickable ID → LDraw filename"""
    return get_cache().get_ldraw_filename(rebrickable_id)


def ldraw_to_rb(ldraw_filename: str) -> Optional[str]:
    """Quick conversion: LDraw filename → Rebrickable ID"""
    return get_cache().get_rebrickable_id(ldraw_filename)


def main():
    """Test cache performance"""
    
    print("🚀 Part Mapping Cache - Performance Test")
    print("=" * 60)
    
    cache = get_cache()
    
    # Test lookups
    print("\n🧪 Testing lookups:")
    test_parts = ["3001", "3020", "3003", "32316", "4070", "999999"]
    
    for part in test_parts:
        ldraw = cache.get_ldraw_filename(part)
        status = "✅" if ldraw else "❌"
        print(f"   {status} {part:10} → {ldraw or 'NOT FOUND'}")
    
    # Show stats
    print("\n📊 Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Benchmark
    print("\n⚡ Benchmark (10,000 lookups):")
    start = time.time()
    for _ in range(10000):
        cache.get_ldraw_filename("3001")
    elapsed = time.time() - start
    print(f"   Time: {elapsed:.3f}s")
    print(f"   Throughput: {10000/elapsed:.0f} lookups/sec")


if __name__ == "__main__":
    main()
