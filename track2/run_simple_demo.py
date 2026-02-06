"""
Simplified Demo Runner - No External Dependencies
==================================================
Runs the complete migration system without plotly visualizations
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, '/home/claude')

from create_test_data import create_databases
from data_migration_system import run_complete_migration
import json


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")


def create_html_table(headers, rows):
    """Create simple HTML table"""
    html = '<table border="1" style="border-collapse: collapse; width: 100%;">\n'
    html += '  <thead><tr style="background-color: #667eea; color: white;">\n'
    for header in headers:
        html += f'    <th style="padding: 10px;">{header}</th>\n'
    html += '  </tr></thead>\n  <tbody>\n'
    
    for i, row in enumerate(rows):
        bg_color = '#f9f9f9' if i % 2 == 0 else 'white'
        html += f'  <tr style="background-color: {bg_color};">\n'
        for cell in row:
            html += f'    <td style="padding: 8px;">{cell}</td>\n'
        html += '  </tr>\n'
    
    html += '  </tbody>\n</table>\n'
    return html


def generate_simple_visualization(all_results, output_dir):
    """Generate simple HTML visualization without plotly"""
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Data Migration Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 32px;
        }
        h2 {
            color: #444;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 18px;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 14px;
            opacity: 0.9;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }
        .success { background: #00cc00; color: white; }
        .warning { background: #ffcc00; color: black; }
        .error { background: #ff0000; color: white; }
        .info { background: #0099ff; color: white; }
        table {
            margin: 20px 0;
            font-size: 14px;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }
        .confidence-high { color: #00cc00; font-weight: bold; }
        .confidence-medium { color: #ff9900; font-weight: bold; }
        .confidence-low { color: #ff0000; font-weight: bold; }
        .mapping-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }
        .arrow {
            color: #667eea;
            font-weight: bold;
            padding: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI-Powered Data Migration Report</h1>
        <p class="subtitle">Intelligent Schema Mapping • Bidirectional Analysis • Round-Trip Validation</p>
'''
    
    # Executive Summary Metrics
    mr = all_results['migration_results']
    ms = all_results['mapping_report']['summary']
    rt = all_results['validation_report']['round_trip_analysis']
    
    html += '''
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Tables Migrated</div>
                <div class="metric-value">''' + str(mr['tables_migrated']) + '''</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Rows Migrated</div>
                <div class="metric-value">''' + str(mr['rows_migrated']) + '''</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Average Confidence</div>
                <div class="metric-value">''' + f"{ms['average_confidence']:.0%}" + '''</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Perfect Round-Trips</div>
                <div class="metric-value">''' + str(rt['perfect_round_trips']) + '/' + str(rt['tables_tested']) + '''</div>
            </div>
        </div>
'''
    
    # Migration Status
    html += '<div class="section">'
    html += '<h2>Migration Status</h2>'
    status_class = 'success' if mr['success'] else 'error'
    status_text = '✅ SUCCESS' if mr['success'] else '❌ FAILED'
    html += f'<span class="status-badge {status_class}">{status_text}</span>'
    html += f'<p><strong>Tables Migrated:</strong> {mr["tables_migrated"]}</p>'
    html += f'<p><strong>Total Rows:</strong> {mr["rows_migrated"]}</p>'
    html += '</div>'
    
    # Forward Mappings
    html += '<div class="section">'
    html += '<h2>Forward Mappings (Source → Target)</h2>'
    
    for table_pair, mappings in all_results['mapping_report']['forward_mappings'].items():
        html += f'<h3>📋 {table_pair}</h3>'
        
        for mapping in mappings:
            conf = mapping['confidence']
            conf_class = 'confidence-high' if conf >= 0.7 else 'confidence-medium' if conf >= 0.5 else 'confidence-low'
            conf_icon = '✅' if conf >= 0.7 else '⚠️' if conf >= 0.5 else '❌'
            
            html += '<div class="mapping-item">'
            html += f'{conf_icon} <strong>{mapping["source"]}</strong> <span class="arrow">→</span> <strong>{mapping["target"]}</strong><br>'
            html += f'<span class="{conf_class}">Confidence: {conf:.1%}</span> | '
            html += f'Types: {mapping["types"]} | '
            html += f'Transformation: {"Yes" if mapping["transformation_required"] else "No"}<br>'
            html += '<small>'
            html += f'• {mapping["explanation"]["name_match"]}<br>'
            html += f'• {mapping["explanation"]["type_match"]}<br>'
            html += f'• {mapping["explanation"]["pattern_match"]}'
            html += '</small>'
            html += '</div>'
    
    html += '</div>'
    
    # Reverse Mappings & Reversibility
    html += '<div class="section">'
    html += '<h2>Reverse Mappings & Reversibility Analysis</h2>'
    
    total_rev = 0
    perfect_rev = 0
    data_loss_rev = 0
    
    for table_pair, mappings in all_results['mapping_report']['reverse_mappings'].items():
        html += f'<h3>🔄 {table_pair}</h3>'
        
        for mapping in mappings:
            total_rev += 1
            is_reversible = mapping['reversible']
            
            if is_reversible:
                if 'perfect' in mapping['reversibility_reason'].lower():
                    perfect_rev += 1
                icon = '✅'
                status_class = 'success'
            else:
                data_loss_rev += 1
                icon = '❌'
                status_class = 'error'
            
            html += '<div class="mapping-item">'
            html += f'{icon} <strong>{mapping["source"]}</strong> <span class="arrow">→</span> <strong>{mapping["target"]}</strong><br>'
            html += f'<span class="status-badge {status_class}">{"Reversible" if is_reversible else "Data Loss Risk"}</span><br>'
            html += f'<small>{mapping["reversibility_reason"]}</small>'
            html += '</div>'
    
    # Reversibility summary
    html += '<div style="background: white; padding: 15px; margin-top: 20px; border-radius: 5px;">'
    html += '<h4>Reversibility Summary</h4>'
    html += f'<p>Total Mappings: {total_rev}</p>'
    html += f'<p>✅ Perfectly Reversible: {perfect_rev} ({perfect_rev/total_rev*100:.1f}%)</p>'
    html += f'<p>⚠️ Reversible with Warnings: {total_rev - perfect_rev - data_loss_rev}</p>'
    html += f'<p>❌ Data Loss Risk: {data_loss_rev} ({data_loss_rev/total_rev*100:.1f}%)</p>'
    html += '</div>'
    html += '</div>'
    
    # Round-Trip Validation
    html += '<div class="section">'
    html += '<h2>Round-Trip Validation Results</h2>'
    
    for table_pair, details in rt['details'].items():
        status_icon = {
            'PERFECT': '✅',
            'ACCEPTABLE_LOSS': '⚠️',
            'DATA_LOSS': '❌'
        }[details['status']]
        
        status_class = {
            'PERFECT': 'success',
            'ACCEPTABLE_LOSS': 'warning',
            'DATA_LOSS': 'error'
        }[details['status']]
        
        html += f'<h3>{status_icon} {table_pair}</h3>'
        html += f'<span class="status-badge {status_class}">{details["status"]}</span>'
        html += f'<p>Perfect Round-Trip: <strong>{details["perfect_percentage"]:.1f}%</strong></p>'
        
        if details['perfect_round_trip_fields']:
            html += f'<p>✅ <strong>Perfect Fields:</strong> {", ".join(details["perfect_round_trip_fields"][:10])}'
            if len(details['perfect_round_trip_fields']) > 10:
                html += f' <em>(+{len(details["perfect_round_trip_fields"]) - 10} more)</em>'
            html += '</p>'
        
        if details['data_loss_fields']:
            html += '<p>❌ <strong>Data Loss Risk Fields:</strong></p><ul>'
            for field in details['data_loss_fields']:
                html += f'<li>{field["field"]}: {field["reason"]}</li>'
            html += '</ul>'
    
    html += '</div>'
    
    # Validation Checks
    html += '<div class="section">'
    html += '<h2>Data Validation Checks</h2>'
    
    for table_pair, checks in all_results['validation_report']['validation_checks'].items():
        html += f'<h3>{table_pair}</h3>'
        
        for check_name, check_result in checks.items():
            passed = check_result.get('passed', True)
            icon = '✅' if passed else '❌'
            status_class = 'success' if passed else 'error'
            
            html += f'<div class="mapping-item">'
            html += f'{icon} <strong>{check_result["check"]}</strong>'
            
            if 'message' in check_result:
                html += f'<br><small>{check_result["message"]}</small>'
            
            html += '</div>'
    
    html += '</div>'
    
    # Recommendations
    html += '<div class="section">'
    html += '<h2>Recommendations</h2>'
    html += '<ul>'
    for rec in all_results['validation_report']['recommendations']:
        html += f'<li>{rec}</li>'
    html += '</ul>'
    html += '</div>'
    
    html += '''
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f0f0f0; border-radius: 5px;">
            <p><strong>Report Generated:</strong> ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            <p><em>AI-Powered Data Migration System</em></p>
        </div>
    </div>
</body>
</html>
'''
    
    # Save HTML report
    report_path = f"{output_dir}/migration_report.html"
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"   📊 HTML report saved: {report_path}")
    return report_path


def main():
    """Run the simplified migration demo"""
    
    print_banner("AI-POWERED DATA MIGRATION SYSTEM")
    
    # Step 1: Create databases
    print_banner("Creating Synthetic Databases")
    source_db, target_db = create_databases()
    
    # Step 2: Run migration
    print_banner("Running Migration Pipeline")
    all_results = run_complete_migration(source_db, target_db)
    
    # Step 3: Generate HTML report
    print_banner("Generating HTML Report")
    report_path = generate_simple_visualization(all_results, '/Users/ayushigupta/Documents/GitHub/DataForge/track2/outputs')
    
    # Final summary
    print_banner("MIGRATION COMPLETE!")
    
    print("📁 Generated Files:")
    print(f"   • Source Database: {source_db}")
    print(f"   • Target Database: {target_db}")
    print(f"   • HTML Report: {report_path}")
    print(f"   • JSON Reports: /Users/ayushigupta/Documents/GitHub/DataForge/track2/outputs/*.json")
    print(f"   • Text Summaries: /Users/ayushigupta/Documents/GitHub/DataForge/track2/outputs/*.txt")
    
    print("\n✨ All tasks completed successfully!")
    print("\n💡 Open migration_report.html in a browser to view the interactive report")
    
    return all_results


if __name__ == "__main__":
    try:
        results = main()
        print("\n🎉 Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
