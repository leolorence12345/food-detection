#!/usr/bin/env python3
"""
Master script to generate all 5 patent figures
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Generate all figures"""
    print("=" * 70)
    print("PATENT FIGURES GENERATOR")
    print("Generating all 5 figures for nutrition video analysis patent")
    print("=" * 70)
    print()
    
    # Import and run each figure generator
    figures = [
        ('generate_figure_1', 'Figure 1: Multi-Food Meal'),
        ('generate_figure_2', 'Figure 2: Temporal Tracking'),
        ('generate_figure_3', 'Figure 3: Partial Occlusion'),
        ('generate_figure_4', 'Figure 4: Single Image'),
        ('generate_figure_5', 'Figure 5: Region-Specific'),
    ]
    
    success_count = 0
    failed = []
    
    for module_name, description in figures:
        try:
            print(f"\n{'=' * 70}")
            print(f"Generating: {description}")
            print('=' * 70)
            
            # Import module
            module = __import__(module_name)
            
            # Run main function
            module.main()
            
            success_count += 1
            print(f"✓ {description} completed successfully")
            
        except Exception as e:
            print(f"✗ {description} failed: {e}")
            failed.append((description, str(e)))
    
    # Summary
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"Success: {success_count}/5 figures generated")
    
    if failed:
        print(f"\nFailed: {len(failed)} figure(s)")
        for desc, error in failed:
            print(f"  ✗ {desc}: {error}")
    else:
        print("\n✓ All 5 patent figures generated successfully!")
        print("\nOutput files:")
        for i in range(1, 6):
            print(f"  - Figure_{i}_*.png")
        
        print("\nFiles are saved in:")
        print(f"  {os.path.dirname(os.path.abspath(__file__))}")
        
        print("\nNext steps:")
        print("  1. Review all generated figures")
        print("  2. Verify data accuracy and labels")
        print("  3. Use figures in patent application")
        print("  4. Consider converting to TIFF for USPTO submission")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
