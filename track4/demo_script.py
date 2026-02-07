"""
Demo Script for Contextual Compression Engine

This script demonstrates the compression engine on the uploaded PDF.
Run this to test the complete pipeline.
"""

import sys
import json
from contextual_compression_engine import HierarchicalCompressor
from html_visualizer import HTMLVisualizer

def run_demo(pdf_path, section_size=5, chapter_size=3):
    """
    Run complete compression pipeline demo
    
    Args:
        pdf_path: Path to input PDF
        section_size: Number of paragraphs per section
        chapter_size: Number of sections per chapter
    """
    print("="*70)
    print("CONTEXTUAL COMPRESSION ENGINE - DEMO")
    print("="*70)
    
    # Initialize compressor
    print("\n[1/6] Initializing compression engine...")
    compressor = HierarchicalCompressor()
    print("✓ Engine initialized")
    
    # Extract text from PDF
    print(f"\n[2/6] Extracting text from: {pdf_path}")
    paragraphs = compressor.extract_text_from_pdf(pdf_path)
    print(f"✓ Extracted {len(paragraphs)} paragraphs")
    
    # Show sample paragraph
    if paragraphs:
        sample = paragraphs[0]
        print(f"\nSample paragraph (Page {sample['page']}):")
        print("-" * 70)
        print(sample['text'][:200] + "..." if len(sample['text']) > 200 else sample['text'])
        print("-" * 70)
    
    # Perform hierarchical compression
    print(f"\n[3/6] Running hierarchical compression...")
    print(f"  Configuration: {section_size} paragraphs/section, {chapter_size} sections/chapter")
    
    result = compressor.compress_hierarchically(
        paragraphs,
        section_size=section_size,
        chapter_size=chapter_size
    )
    
    # Display statistics
    print("\n[4/6] Compression Statistics:")
    print("-" * 70)
    metadata = result['metadata']
    print(f"  Paragraphs:      {metadata['total_paragraphs']}")
    print(f"  Sections:        {metadata['total_sections']}")
    print(f"  Chapters:        {metadata['total_chapters']}")
    print(f"  Critical Facts:  {metadata['total_facts']}")
    print(f"  Contradictions:  {metadata['total_contradictions']}")
    
    # Calculate compression ratio
    original_length = sum(len(p['original_text']) for p in result['paragraphs'])
    compressed_length = len(result['document_summary']['abstractive_summary'])
    ratio = (1 - compressed_length / original_length) * 100 if original_length > 0 else 0
    
    print(f"\n  Original text:   {original_length:,} characters")
    print(f"  Compressed to:   {compressed_length:,} characters")
    print(f"  Compression:     {ratio:.1f}%")
    print("-" * 70)
    
    # Display document summary
    print("\n[5/6] Document Summary:")
    print("=" * 70)
    print(result['document_summary']['abstractive_summary'])
    print("=" * 70)
    
    # Show sample critical facts
    print("\n[5/6] Sample Critical Facts (first 5):")
    print("-" * 70)
    for i, fact in enumerate(result['critical_facts'][:5], 1):
        print(f"\n{i}. Type: {fact['fact_type'].upper()}")
        print(f"   Content: {fact['content']}")
        print(f"   Source: Page {fact['source']['page']}, Para {fact['source']['paragraph_idx']}")
    
    if len(result['critical_facts']) > 5:
        print(f"\n... and {len(result['critical_facts']) - 5} more facts")
    print("-" * 70)
    
    # Show contradictions
    print("\n[5/6] Contradictions:")
    print("-" * 70)
    if result['contradictions']:
        for i, contra in enumerate(result['contradictions'][:3], 1):
            print(f"\n{i}. Type: {contra['conflict_type']}")
            print(f"   A: {contra['statement_a'][:100]}...")
            print(f"   B: {contra['statement_b'][:100]}...")
        if len(result['contradictions']) > 3:
            print(f"\n... and {len(result['contradictions']) - 3} more contradictions")
    else:
        print("\nNo contradictions detected")
    print("-" * 70)
    
    # Save outputs
    print("\n[6/6] Saving outputs...")
    
    # Save JSON
    json_path = 'compression_result.json'
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"✓ Saved JSON: {json_path}")
    
    # Generate HTML
    html_path = 'compression_visualization.html'
    visualizer = HTMLVisualizer(result)
    visualizer.save_html(html_path)
    print(f"✓ Saved HTML: {html_path}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print(f"\nOutput files:")
    print(f"  1. {json_path} - Complete compression data")
    print(f"  2. {html_path} - Interactive visualization")
    print(f"\nOpen {html_path} in your browser to explore the compressed document!")
    print("="*70)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python demo_script.py <pdf_path> [section_size] [chapter_size]")
        print("\nExample: python demo_script.py document.pdf 5 3")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    section_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    chapter_size = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    result = run_demo(pdf_path, section_size, chapter_size)
