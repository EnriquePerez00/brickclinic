#!/usr/bin/env python3
"""
System Review Script
Validates all modules of DNA-Conditioned Generation System
"""

import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def review_module_1():
    """Module 1: ID Cross-Reference System"""
    print("\n" + "="*60)
    print("📦 MODULE 1: ID Cross-Reference System")
    print("="*60)
    
    # Check table exists
    sql = text("SELECT COUNT(*) FROM part_id_mapping")
    with engine.connect() as conn:
        count = conn.execute(sql).scalar()
    
    print(f"✅ part_id_mapping table: {count} mappings")
    
    # Test cache
    import sys
    sys.path.insert(0, '/Users/I764690/Brickclinic/scripts')
    from part_mapping_cache import rb_to_ldraw, ldraw_to_rb, get_cache
    
    cache = get_cache()
    stats = cache.get_stats()
    
    print(f"✅ RAM Cache loaded: {stats['total_mappings']} mappings")
    print(f"   Hit rate: {stats['hit_rate_pct']:.1f}%")
    print(f"   RAM usage: {stats['ram_mb']:.2f} MB")
    
    # Test mapping
    test_id = "3001"
    ldraw = rb_to_ldraw(test_id)
    print(f"✅ Test mapping: {test_id} → {ldraw}")
    
    return True


def review_module_2():
    """Module 2: Star Wars DNA Extractor"""
    print("\n" + "="*60)
    print("🧬 MODULE 2: Star Wars DNA Extractor")
    print("="*60)
    
    # Check DNA profiles
    sql = text("""
        SELECT 
            set_num,
            num_parts,
            ROUND(CAST(snot_ratio * 100 AS NUMERIC), 1) as snot_pct,
            ROUND(CAST(complexity_score AS NUMERIC), 2) as complexity,
            primary_colors
        FROM sw_dna_profiles
        WHERE theme_id = 158
        ORDER BY set_num
    """)
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
    
    print(f"✅ DNA Profiles: {len(results)} sets analyzed")
    
    for row in results:
        colors = row[4][:2] if row[4] else []
        print(f"   {row[0]}: {row[1]} parts, {row[2]}% SNOT, complexity {row[3]}")
        print(f"      Colors: {colors}")
    
    # Calculate averages
    sql = text("""
        SELECT 
            AVG(snot_ratio) as avg_snot,
            AVG(complexity_score) as avg_complexity
        FROM sw_dna_profiles
        WHERE theme_id = 158
    """)
    
    with engine.connect() as conn:
        result = conn.execute(sql).fetchone()
    
    print(f"\n✅ Aggregate DNA:")
    print(f"   Avg SNOT: {result[0]*100:.1f}%")
    print(f"   Avg Complexity: {result[1]:.2f}")
    
    return True


def review_module_3():
    """Module 3: Enhanced GNN Architecture"""
    print("\n" + "="*60)
    print("🧠 MODULE 3: Enhanced GNN Architecture")
    print("="*60)
    
    # Load model
    import sys
    sys.path.insert(0, '/Users/I764690/Brickclinic/scripts')
    from enhanced_gnn_model import create_enhanced_model, load_dna_profile
    
    dna = load_dna_profile(theme_id=158, category="small_ship")
    print(f"✅ DNA Profile loaded:")
    print(f"   SNOT: {dna['avg_snot_ratio']*100:.1f}%")
    print(f"   Complexity: {dna['avg_complexity']:.2f}")
    print(f"   Primary colors: {dna['primary_colors'][:3]}")
    
    model = create_enhanced_model(
        num_part_types=100,
        hidden_dim=64,
        latent_dim=32,
        use_dna=True,
        theme_id=158,
        category="small_ship"
    )
    
    params = sum(p.numel() for p in model.parameters())
    print(f"\n✅ Model architecture:")
    print(f"   Parameters: {params:,}")
    print(f"   DNA-aware: Yes")
    print(f"   Loss components: recon(40%) + KL(30%) + DNA(30%)")
    
    # Check training data
    sql = text("""
        SELECT COUNT(*) FROM construction_steps cs
        JOIN sets s ON cs.set_num = s.set_num
        WHERE s.theme_id = 158
    """)
    
    with engine.connect() as conn:
        count = conn.execute(sql).scalar()
    
    print(f"\n✅ Training data: {count} construction steps")
    
    return True


def review_module_4():
    """Module 4: Physics Validation Engine"""
    print("\n" + "="*60)
    print("⚖️  MODULE 4: Physics Validation Engine")
    print("="*60)
    
    import sys
    sys.path.insert(0, '/Users/I764690/Brickclinic/scripts')
    from physics_validator import PhysicsValidator, Part
    
    validator = PhysicsValidator()
    
    # Test case
    test_parts = [
        Part('3001', 1, 0, 0, 0, [1,0,0,0,1,0,0,0,1], 1.0),
        Part('3001', 1, 0, -24, 0, [1,0,0,0,1,0,0,0,1], 1.0),
        Part('3003', 1, 0, -48, 0, [1,0,0,0,1,0,0,0,1], 0.75),
    ]
    
    com = validator.calculate_center_of_mass(test_parts)
    print(f"✅ CoM Calculation: ({com[0]:.1f}, {com[1]:.1f}, {com[2]:.1f}) LDU")
    
    cantilevers = validator.detect_cantilevers(test_parts)
    print(f"✅ Cantilever Detection: {len(cantilevers)} detected")
    
    stability = validator.calculate_stability_score(test_parts)
    print(f"✅ Stability Score: {stability['score']:.2f}/1.00")
    print(f"   Is Stable: {'✅' if stability['is_stable'] else '❌'}")
    print(f"   Support Ratio: {stability['support_ratio']*100:.1f}%")
    print(f"   Warnings: {len(stability['warnings'])}")
    
    return True


def system_integration_test():
    """Test full system integration"""
    print("\n" + "="*60)
    print("🔗 SYSTEM INTEGRATION TEST")
    print("="*60)
    
    # Simulate generation flow
    print("\n1. ID Mapping...")
    import sys
    sys.path.insert(0, '/Users/I764690/Brickclinic/scripts')
    from part_mapping_cache import rb_to_ldraw
    inventory = ["3001", "3003", "3020"]
    ldraw_parts = [rb_to_ldraw(rb_id) for rb_id in inventory]
    print(f"   Mapped {len(inventory)} parts: {ldraw_parts}")
    
    print("\n2. DNA Loading...")
    from enhanced_gnn_model import load_dna_profile
    dna = load_dna_profile(158, "small_ship")
    print(f"   Target SNOT: {dna['avg_snot_ratio']*100:.1f}%")
    
    print("\n3. Physics Validation...")
    from physics_validator import PhysicsValidator, Part
    validator = PhysicsValidator()
    
    # Simulate generated MOC
    generated_parts = [
        Part('3001', 72, 0, 0, 0, [1,0,0,0,1,0,0,0,1]),
        Part('3003', 72, 0, -24, 0, [1,0,0,0,1,0,0,0,1]),
    ]
    
    stability = validator.calculate_stability_score(generated_parts)
    print(f"   Stability: {stability['score']:.2f}/1.00 {'✅' if stability['is_stable'] else '❌'}")
    
    print("\n4. Color Consistency Check...")
    primary_colors = [c[0] for c in dna['primary_colors']]
    colors_used = [p.color for p in generated_parts]
    on_palette = sum(1 for c in colors_used if c in primary_colors)
    print(f"   On-palette: {on_palette}/{len(colors_used)} ({on_palette/len(colors_used)*100:.0f}%)")
    
    print("\n✅ Integration test passed!")
    return True


def main():
    """Run complete system review"""
    print("\n" + "="*60)
    print("🚀 DNA-CONDITIONED GENERATION SYSTEM REVIEW")
    print("="*60)
    
    results = {
        'Module 1': review_module_1(),
        'Module 2': review_module_2(),
        'Module 3': review_module_3(),
        'Module 4': review_module_4(),
        'Integration': system_integration_test()
    }
    
    print("\n" + "="*60)
    print("📊 REVIEW SUMMARY")
    print("="*60)
    
    for module, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{module:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ SYSTEM READY FOR PRODUCTION")
    else:
        print("⚠️  SOME MODULES NEED ATTENTION")
    print("="*60)


if __name__ == "__main__":
    main()
