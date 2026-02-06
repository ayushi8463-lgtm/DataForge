"""
Standalone Iterative Reverse Mapping Demo
==========================================
Shows the complete process without requiring user input
"""

from data_migration_system import run_iterative_migration


def main():
    print("\n" + "=" * 80)
    print("ITERATIVE REVERSE MAPPING DEMONSTRATION")
    print("=" * 80)

    print("""
This demonstration shows how the improved reverse mapping works:

CONCEPT:
========
Traditional Approach:
- Map Source → Target using AI
- Hope the mapping is correct
- Limited validation

Our Iterative Approach:
- Map Source → Target (forward)
- Actually migrate sample data
- Map Target → Source_derived (reverse)  
- Compare Source_original vs Source_derived
- Columns that match 100% = confirmed mappings
- Columns that don't match = re-attempt with remaining columns
- Columns that still don't match = discard or manual review

WHY THIS MATTERS:
=================
- Provides concrete evidence of mapping quality
- Identifies which mappings preserve data perfectly
- Automatically refines poor mappings
- Gives stakeholders confidence in the migration

Let's see it in action!
    """)

    source_db = "outputs/source_database.db"
    target_db = "outputs/target_database.db"

    print("\n" + "=" * 80)
    print("RUNNING ITERATIVE MAPPING PROCESS")
    print("=" * 80)

    results = run_iterative_migration(source_db, target_db, sample_size=50)

    print("\n" + "=" * 80)
    print("DETAILED RESULTS")
    print("=" * 80)

    # Show comparison results
    print("\n1. ROUND-TRIP COMPARISON (Original vs Derived Source)")
    print("-" * 80)

    for table_name, table_comp in results['comparison_results'].items():
        print(f"\nTable: {table_name}")
        print(f"Overall Confidence: {table_comp['overall_confidence']:.1%}\n")

        print(f"{'Column':<25} {'Status':<20} {'Match %':<10} {'Confidence':<12}")
        print("-" * 75)

        for col_name, col_comp in table_comp['column_comparisons'].items():
            status = col_comp['status']
            match_pct = col_comp['match_percentage']
            confidence = col_comp['confidence']

            if status == 'PERFECT_MATCH':
                icon = '✅'
            elif status in ['NEAR_PERFECT', 'ACCEPTABLE']:
                icon = '⚠️'
            else:
                icon = '❌'

            print(f"{icon} {col_name:<23} {status:<20} {match_pct:>6.1f}%   {confidence:>6.1%}")
            print(f"   Reason: {col_comp['reason']}\n")

    # Show refined mappings
    print("\n2. REFINED MAPPINGS (After Iterative Process)")
    print("-" * 80)

    for table_pair, mappings in results['refined_mappings'].items():
        src_table, tgt_table = table_pair.split('→')
        print(f"\n{src_table} → {tgt_table}\n")

        print(f"{'Source':<25} {'Target':<25} {'Confidence':<12} {'Action'}")
        print("-" * 90)

        for mapping in mappings:
            src_col = mapping['source_column']
            tgt_col = mapping.get('target_column', None)
            confidence = mapping.get('refined_confidence', 0.0)
            reason = mapping.get('refinement_reason', '')

            if confidence == 1.0:
                icon = '✅'
                action = 'CONFIRMED'
            elif tgt_col is None:
                icon = '❌'
                action = 'DISCARDED'
                tgt_col = '(none)'
            elif 'Re-mapped' in reason:
                icon = '🔄'
                action = 'IMPROVED'
            else:
                icon = '⚠️'
                action = 'KEPT'

            print(f"{icon} {src_col:<23} {tgt_col:<25} {confidence:>6.1%}      {action}")
            if reason:
                print(f"   └─ {reason}\n")

    # Show summary
    print("\n3. SUMMARY")
    print("-" * 80)

    summary = results['summary']
    print(f"\nTotal Columns Analyzed: {summary['total_columns_analyzed']}")
    print(
        f"Perfect Round-Trip Matches: {summary['perfect_round_trip_matches']} ({summary['perfect_match_percentage']:.1f}%)")
    print(f"Improved Mappings: {summary['improved_mappings']}")
    print(f"Discarded Mappings: {summary['discarded_mappings']}")
    print(f"Overall Confidence: {summary['overall_confidence']:.1%}")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    print("""
1. CONFIRMED MAPPINGS (100% confidence):
   These columns perfectly preserve data through round-trip migration.
   Use these mappings without any concerns.

2. IMPROVED MAPPINGS:
   These columns were re-mapped to better target columns after analyzing
   the round-trip results. Review to ensure they make business sense.

3. DISCARDED MAPPINGS:
   These columns couldn't find suitable target columns. Options:
   - Add new columns to target schema
   - Store in reference table
   - Verify if data is actually needed

4. DATA PRESERVATION:
   The round-trip test shows which transformations are reversible and
   which lose data, giving you concrete evidence of migration quality.
    """)

    print("\n" + "=" * 80)
    print("FILES GENERATED")
    print("=" * 80)
    print("\n✅ outputs/iterative_mapping_results.json")
    print("   Full results in JSON format")

    return results


if __name__ == "__main__":
    try:
        results = main()
        print("\n🎉 Demonstration completed successfully!")
        print("\nThe iterative reverse mapping approach provides:")
        print("  • Concrete validation of mapping quality")
        print("  • Automatic refinement of poor mappings")
        print("  • Clear confidence levels for each column")
        print("  • Evidence-based migration strategy")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()