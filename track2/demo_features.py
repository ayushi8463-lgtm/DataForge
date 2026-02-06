"""
Feature Demonstration Script
============================
Demonstrates specific features of the AI-powered migration system
"""

import json
import sys
sys.path.insert(0, '/home/claude')

from data_migration_system import (
    AIColumnMapper, BidirectionalMapper, DataTransformer
)


def demo_semantic_matching():
    """Demonstrate semantic column matching"""
    print("\n" + "="*80)
    print("DEMO 1: Semantic Column Matching")
    print("="*80)
    
    mapper = AIColumnMapper()
    
    test_pairs = [
        ('customer_name', 'client_full_name'),
        ('email_address', 'email'),
        ('order_date', 'purchase_timestamp'),
        ('product_id', 'item_identifier'),
        ('phone_number', 'contact_tel'),
        ('total_amount', 'total_cost'),
    ]
    
    print("\nTesting column name similarity:\n")
    for col1, col2 in test_pairs:
        score, explanation = mapper.semantic_similarity(col1, col2)
        print(f"  {col1:20s} ↔ {col2:20s}")
        print(f"  Score: {score:.2%} | {explanation}\n")


def demo_type_compatibility():
    """Demonstrate type compatibility checking"""
    print("\n" + "="*80)
    print("DEMO 2: Type Compatibility Analysis")
    print("="*80)
    
    mapper = AIColumnMapper()
    
    test_types = [
        ('INTEGER', 'INTEGER'),
        ('INTEGER', 'REAL'),
        ('REAL', 'INTEGER'),
        ('TEXT', 'VARCHAR'),
        ('DATE', 'TIMESTAMP'),
        ('TIMESTAMP', 'DATE'),
        ('INTEGER', 'TEXT'),
    ]
    
    print("\nTesting type compatibility:\n")
    for type1, type2 in test_types:
        score, explanation = mapper.type_compatibility(type1, type2)
        icon = '✅' if score >= 0.8 else '⚠️' if score >= 0.5 else '❌'
        print(f"  {icon} {type1:15s} → {type2:15s}")
        print(f"     Score: {score:.2%} | {explanation}\n")


def demo_data_transformation():
    """Demonstrate data transformations"""
    print("\n" + "="*80)
    print("DEMO 3: Data Transformation Examples")
    print("="*80)
    
    transformer = DataTransformer()
    
    test_cases = [
        (123, 'INTEGER', 'REAL'),
        (123.45, 'REAL', 'INTEGER'),
        (42, 'INTEGER', 'TEXT'),
        ('2024-01-15', 'DATE', 'TIMESTAMP'),
        ('2024-01-15 14:30:00', 'TIMESTAMP', 'DATE'),
        ('hello', 'TEXT', 'TEXT'),
    ]
    
    print("\nTesting data transformations:\n")
    for value, src_type, tgt_type in test_cases:
        result, explanation = transformer.transform_value(value, src_type, tgt_type)
        print(f"  {value} ({src_type}) → {result} ({tgt_type})")
        print(f"  {explanation}\n")


def demo_reversibility_analysis():
    """Demonstrate reversibility analysis"""
    print("\n" + "="*80)
    print("DEMO 4: Reversibility Analysis")
    print("="*80)
    
    # Create sample forward mappings
    forward_mappings = {
        'test_table→test_target': [
            {
                'source_column': 'id',
                'target_column': 'identifier',
                'confidence': 0.9,
                'source_type': 'INTEGER',
                'target_type': 'INTEGER',
                'transformation_required': False,
                'explanation': {}
            },
            {
                'source_column': 'created_date',
                'target_column': 'created_timestamp',
                'confidence': 0.85,
                'source_type': 'DATE',
                'target_type': 'TIMESTAMP',
                'transformation_required': True,
                'explanation': {}
            },
            {
                'source_column': 'amount',
                'target_column': 'total',
                'confidence': 0.75,
                'source_type': 'REAL',
                'target_type': 'INTEGER',
                'transformation_required': True,
                'explanation': {}
            },
            {
                'source_column': 'description',
                'target_column': 'notes',
                'confidence': 0.7,
                'source_type': 'TEXT',
                'target_type': 'TEXT',
                'transformation_required': False,
                'explanation': {}
            }
        ]
    }
    
    bi_mapper = BidirectionalMapper(forward_mappings)
    reverse_mappings = bi_mapper.generate_reverse_mappings()
    
    print("\nReversibility Analysis:\n")
    print(f"{'Column Mapping':<40s} {'Reversible':<12s} {'Reason'}")
    print("-" * 100)
    
    for mapping in forward_mappings['test_table→test_target']:
        src = mapping['source_column']
        tgt = mapping['target_column']
        
        # Find corresponding reverse mapping
        rev_key = 'test_target→test_table'
        rev_mapping = next(
            (r for r in reverse_mappings[rev_key] if r['target_column'] == src),
            None
        )
        
        if rev_mapping:
            reversible = "✅ Yes" if rev_mapping['reversible'] else "❌ No"
            print(f"{src:20s} → {tgt:18s} {reversible:12s} {rev_mapping['reversibility_reason']}")


def demo_confidence_scoring():
    """Demonstrate confidence score calculation"""
    print("\n" + "="*80)
    print("DEMO 5: Confidence Score Breakdown")
    print("="*80)
    
    mapper = AIColumnMapper()
    
    # Simulate a mapping scenario
    print("\nExample: Mapping 'customer_email' to 'client_email_address'\n")
    
    # Individual scores
    name_score, name_exp = mapper.semantic_similarity('customer_email', 'client_email_address')
    type_score, type_exp = mapper.type_compatibility('TEXT', 'VARCHAR')
    pattern_score = 0.8  # Simulated pattern score
    
    # Weighted total
    total_score = (name_score * 0.5) + (type_score * 0.3) + (pattern_score * 0.2)
    
    print(f"Name Similarity:    {name_score:.2%} (weight: 50%)")
    print(f"  → {name_exp}")
    print()
    print(f"Type Compatibility: {type_score:.2%} (weight: 30%)")
    print(f"  → {type_exp}")
    print()
    print(f"Pattern Similarity: {pattern_score:.2%} (weight: 20%)")
    print(f"  → Both contain email patterns")
    print()
    print("-" * 80)
    print(f"Total Confidence:   {total_score:.2%}")
    print()
    
    if total_score >= 0.7:
        print("✅ HIGH CONFIDENCE - Recommended for automatic mapping")
    elif total_score >= 0.5:
        print("⚠️ MEDIUM CONFIDENCE - Manual review suggested")
    else:
        print("❌ LOW CONFIDENCE - Manual mapping required")


def demo_edge_cases():
    """Demonstrate handling of edge cases"""
    print("\n" + "="*80)
    print("DEMO 6: Edge Cases and Special Scenarios")
    print("="*80)
    
    transformer = DataTransformer()
    
    edge_cases = [
        (None, 'TEXT', 'TEXT', 'Null value handling'),
        ('', 'TEXT', 'INTEGER', 'Empty string to number'),
        (0, 'INTEGER', 'TEXT', 'Zero to text'),
        ('invalid_date', 'TEXT', 'DATE', 'Invalid date format'),
    ]
    
    print("\nEdge case handling:\n")
    for value, src_type, tgt_type, description in edge_cases:
        result, explanation = transformer.transform_value(value, src_type, tgt_type)
        print(f"  {description}:")
        print(f"    Input:  {repr(value)} ({src_type})")
        print(f"    Output: {repr(result)} ({tgt_type})")
        print(f"    Result: {explanation}\n")


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print("AI-POWERED DATA MIGRATION - FEATURE DEMONSTRATIONS")
    print("="*80)
    print("\nThis script demonstrates the key features of the migration system:")
    print("  1. Semantic column matching with AI")
    print("  2. Type compatibility analysis")
    print("  3. Data transformation capabilities")
    print("  4. Reversibility analysis")
    print("  5. Confidence score calculation")
    print("  6. Edge case handling")
    print()
    
    input("Press Enter to start demonstrations...")
    
    demo_semantic_matching()
    input("\nPress Enter for next demo...")
    
    demo_type_compatibility()
    input("\nPress Enter for next demo...")
    
    demo_data_transformation()
    input("\nPress Enter for next demo...")
    
    demo_reversibility_analysis()
    input("\nPress Enter for next demo...")
    
    demo_confidence_scoring()
    input("\nPress Enter for next demo...")
    
    demo_edge_cases()
    
    print("\n" + "="*80)
    print("DEMONSTRATIONS COMPLETE")
    print("="*80)
    print("\n✨ All features demonstrated successfully!")
    print("\n💡 Next steps:")
    print("   • Run 'python run_simple_demo.py' for full migration demo")
    print("   • Check README.md for detailed documentation")
    print("   • Review the generated reports for real-world examples")


if __name__ == "__main__":
    main()
