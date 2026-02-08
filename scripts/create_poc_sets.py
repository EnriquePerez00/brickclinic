#!/usr/bin/env python3
"""
Create synthetic Star Wars LDraw files for PoC
Simulates realistic construction sequences
"""

import os

def create_poc_sets():
    """Create 3 synthetic Star Wars sets with realistic step sequences"""
    
    os.makedirs("omr_data", exist_ok=True)
    
    # Set 1: Mini X-Wing (Simple, 15 parts, 5 steps)
    xwing = """0 Mini X-Wing Fighter
0 Name: poc_xwing-1.ldr
0 Author: AI Generated PoC
0 !THEME Star Wars

0 // Step 1: Base plate
1 72 0 0 0 1 0 0 0 1 0 0 0 1 3020.dat
0 STEP

0 // Step 2: Wings (left/right plates)
1 72 -40 0 0 1 0 0 0 1 0 0 0 1 3023.dat
1 72 40 0 0 1 0 0 0 1 0 0 0 1 3023.dat
0 STEP

0 // Step 3: Fuselage bricks
1 72 0 -8 0 1 0 0 0 1 0 0 0 1 3004.dat
1 72 0 -16 0 1 0 0 0 1 0 0 0 1 3005.dat
0 STEP

0 // Step 4: Cockpit
1 47 0 -24 0 1 0 0 0 1 0 0 0 1 4070.dat
1 1 0 -28 0 1 0 0 0 1 0 0 0 1 3062b.dat
0 STEP

0 // Step 5: Detail pieces
1 15 -20 -8 10 1 0 0 0 1 0 0 0 1 3024.dat
1 15 20 -8 10 1 0 0 0 1 0 0 0 1 3024.dat
1 4 0 -8 -20 1 0 0 0 1 0 0 0 1 3023.dat
0 STEP
"""
    
    # Set 2: TIE Fighter (Medium, 20 parts, 6 steps)
    tie = """0 Mini TIE Fighter
0 Name: poc_tie-1.ldr
0 Author: AI Generated PoC

0 // Step 1: Central sphere frame
1 72 0 0 0 1 0 0 0 1 0 0 0 1 3003.dat
1 72 0 -8 0 1 0 0 0 1 0 0 0 1 3003.dat
0 STEP

0 // Step 2: Cockpit details
1 85 0 -16 0 1 0 0 0 1 0 0 0 1 3062b.dat
1 0 0 -4 0 1 0 0 0 1 0 0 0 1 3024.dat
0 STEP

0 // Step 3: Wing connectors (technic)
1 72 -20 -4 0 0 1 0 0 0 1 1 0 0 32316.dat
1 72 20 -4 0 0 1 0 0 0 1 -1 0 0 32316.dat
0 STEP

0 // Step 4: Large wing panels left
1 85 -60 -4 -20 1 0 0 0 1 0 0 0 1 3958.dat
1 85 -60 -4 20 1 0 0 0 1 0 0 0 1 3958.dat
0 STEP

0 // Step 5: Large wing panels right
1 85 60 -4 -20 1 0 0 0 1 0 0 0 1 3958.dat
1 85 60 -4 20 1 0 0 0 1 0 0 0 1 3958.dat
0 STEP

0 // Step 6: Greebling
1 72 0 -12 0 1 0 0 0 1 0 0 0 1 3070b.dat
1 15 -40 -8 0 1 0 0 0 1 0 0 0 1 3024.dat
1 15 40 -8 0 1 0 0 0 1 0 0 0 1 3024.dat
0 STEP
"""
    
    # Set 3: AT-ST Walker (Complex, 25 parts, 7 steps)
    atst = """0 Mini AT-ST Walker
0 Name: poc_atst-1.ldr
0 Author: AI Generated PoC

0 // Step 1: Base foot left
1 72 -30 0 0 1 0 0 0 1 0 0 0 1 3003.dat
1 72 -30 0 20 1 0 0 0 1 0 0 0 1 3024.dat
0 STEP

0 // Step 2: Base foot right
1 72 30 0 0 1 0 0 0 1 0 0 0 1 3003.dat
1 72 30 0 20 1 0 0 0 1 0 0 0 1 3024.dat
0 STEP

0 // Step 3: Leg joints (technic pins)
1 72 -30 -20 10 1 0 0 0 1 0 0 0 1 32523.dat
1 72 30 -20 10 1 0 0 0 1 0 0 0 1 32523.dat
0 STEP

0 // Step 4: Upper legs
1 85 -20 -40 10 1 0 0 0 1 0 0 0 1 3004.dat
1 85 20 -40 10 1 0 0 0 1 0 0 0 1 3004.dat
0 STEP

0 // Step 5: Body core
1 85 0 -50 10 1 0 0 0 1 0 0 0 1 3003.dat
1 85 0 -58 10 1 0 0 0 1 0 0 0 1 3003.dat
1 72 0 -66 10 1 0 0 0 1 0 0 0 1 3062b.dat
0 STEP

0 // Step 6: Head/Cockpit
1 47 0 -74 10 1 0 0 0 1 0 0 0 1 3039.dat
1 1 0 -78 10 1 0 0 0 1 0 0 0 1 4073.dat
0 STEP

0 // Step 7: Weapons and details
1 72 -10 -66 0 1 0 0 0 1 0 0 0 1 3024.dat
1 72 10 -66 0 1 0 0 0 1 0 0 0 1 3024.dat
1 4 0 -70 -10 1 0 0 0 1 0 0 0 1 3023.dat
0 STEP
"""
    
    sets = {
        "poc_xwing-1.ldr": xwing,
        "poc_tie-1.ldr": tie,
        "poc_atst-1.ldr": atst
    }
    
    for filename, content in sets.items():
        filepath = os.path.join("omr_data", filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Created: {filepath}")
    
    print(f"\n🎯 Created {len(sets)} PoC Star Wars sets")
    return list(sets.keys())


if __name__ == "__main__":
    create_poc_sets()
