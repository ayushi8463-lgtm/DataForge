"""
HTML Report Generator for Iterative Reverse Mapping
====================================================
Creates a beautiful, interactive HTML report with all analysis results
"""

import json
from datetime import datetime


def create_html_report(results: dict, output_path: str):
    """
    Generate a comprehensive HTML report from iterative mapping results
    
    Args:
        results: Dictionary containing all mapping results
        output_path: Path where HTML file should be saved
    """
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iterative Reverse Mapping Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 42px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .header p {
            font-size: 18px;
            opacity: 0.95;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 50px;
        }
        
        .section-title {
            font-size: 28px;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title .icon {
            font-size: 32px;
        }
        
        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .metric-value {
            font-size: 48px;
            font-weight: bold;
            margin: 15px 0;
        }
        
        .metric-label {
            font-size: 14px;
            opacity: 0.95;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Process Flow */
        .process-flow {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 12px;
            margin: 30px 0;
        }
        
        .flow-steps {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .flow-step {
            background: white;
            padding: 20px 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 150px;
            text-align: center;
            position: relative;
        }
        
        .flow-step::after {
            content: '→';
            position: absolute;
            right: -30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            color: #667eea;
            font-weight: bold;
        }
        
        .flow-step:last-child::after {
            content: '';
        }
        
        .flow-number {
            display: inline-block;
            width: 35px;
            height: 35px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            line-height: 35px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .flow-label {
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }
        
        /* Tables */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .data-table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .data-table th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        
        .data-table td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .data-table tbody tr:hover {
            background: #f8f9fa;
        }
        
        .data-table tbody tr:last-child td {
            border-bottom: none;
        }
        
        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-perfect {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-near-perfect {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .badge-acceptable {
            background: #fff3cd;
            color: #856404;
        }
        
        .badge-data-loss {
            background: #f8d7da;
            color: #721c24;
        }
        
        .badge-not-mapped {
            background: #e2e3e5;
            color: #383d41;
        }
        
        .badge-confirmed {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-improved {
            background: #cfe2ff;
            color: #084298;
        }
        
        .badge-kept {
            background: #fff3cd;
            color: #856404;
        }
        
        .badge-discarded {
            background: #f8d7da;
            color: #721c24;
        }
        
        /* Confidence Indicators */
        .confidence {
            font-weight: bold;
            font-size: 16px;
        }
        
        .confidence-high {
            color: #28a745;
        }
        
        .confidence-medium {
            color: #ffc107;
        }
        
        .confidence-low {
            color: #dc3545;
        }
        
        /* Progress Bars */
        .progress-bar {
            width: 100%;
            height: 25px;
            background: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 12px;
            transition: width 0.5s ease;
        }
        
        /* Info Boxes */
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .info-box h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .info-box p {
            color: #666;
            line-height: 1.8;
        }
        
        /* Expandable Details */
        .expandable {
            margin: 15px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .expandable-header {
            background: #f8f9fa;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s;
        }
        
        .expandable-header:hover {
            background: #e9ecef;
        }
        
        .expandable-content {
            padding: 20px;
            display: none;
            background: white;
        }
        
        .expandable.active .expandable-content {
            display: block;
        }
        
        .expandable-icon {
            transition: transform 0.3s;
        }
        
        .expandable.active .expandable-icon {
            transform: rotate(90deg);
        }
        
        /* Reason Text */
        .reason-text {
            font-size: 13px;
            color: #666;
            font-style: italic;
            margin-top: 5px;
        }
        
        /* Table Name Headers */
        .table-header {
            background: #667eea;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 25px 0 15px 0;
            font-size: 20px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Footer */
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        /* Recommendations */
        .recommendations {
            background: white;
            border: 2px solid #667eea;
            border-radius: 12px;
            padding: 25px;
            margin: 25px 0;
        }
        
        .recommendations h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 22px;
        }
        
        .recommendations ul {
            list-style: none;
            padding: 0;
        }
        
        .recommendations li {
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
            color: #333;
        }
        
        .recommendations li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .flow-steps {
                flex-direction: column;
            }
            
            .flow-step::after {
                content: '↓';
                right: auto;
                top: auto;
                bottom: -25px;
                left: 50%;
                transform: translateX(-50%);
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Print Styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
            }
            
            .expandable-content {
                display: block !important;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Iterative Reverse Mapping Report</h1>
            <p>AI-Powered Data Migration with Round-Trip Validation</p>
        </div>
        
        <div class="content">
"""
    
    # Add timestamp
    html += f"""
            <div class="info-box">
                <h4>Report Information</h4>
                <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
                <p><strong>Analysis Type:</strong> Iterative Reverse Mapping with Round-Trip Validation</p>
            </div>
"""
    
    # Process Flow
    html += """
            <section class="section">
                <h2 class="section-title">
                    <span class="icon">📊</span>
                    Migration Process Flow
                </h2>
                
                <div class="process-flow">
                    <div class="flow-steps">
                        <div class="flow-step">
                            <div class="flow-number">1</div>
                            <div class="flow-label">Source DB</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-number">2</div>
                            <div class="flow-label">Forward Migration</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-number">3</div>
                            <div class="flow-label">Target DB</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-number">4</div>
                            <div class="flow-label">Reverse Migration</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-number">5</div>
                            <div class="flow-label">Derived Source</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-number">6</div>
                            <div class="flow-label">Compare & Refine</div>
                        </div>
                    </div>
                </div>
                
                <div class="info-box">
                    <h4>How It Works</h4>
                    <p>The system performs actual data migration on sample rows, migrates them back, 
                    and compares the original with the derived data. This provides concrete evidence 
                    of mapping quality instead of theoretical predictions.</p>
                </div>
            </section>
"""
    
    # Summary Metrics
    summary = results['summary']
    html += f"""
            <section class="section">
                <h2 class="section-title">
                    <span class="icon">📈</span>
                    Executive Summary
                </h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Total Columns</div>
                        <div class="metric-value">{summary['total_columns_analyzed']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Perfect Matches</div>
                        <div class="metric-value">{summary['perfect_round_trip_matches']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Match Rate</div>
                        <div class="metric-value">{summary['perfect_match_percentage']:.0f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Improved</div>
                        <div class="metric-value">{summary['improved_mappings']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Discarded</div>
                        <div class="metric-value">{summary['discarded_mappings']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Overall Confidence</div>
                        <div class="metric-value">{summary['overall_confidence']:.0%}</div>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {summary['perfect_match_percentage']:.0f}%">
                        {summary['perfect_match_percentage']:.0f}% Perfect Match Rate
                    </div>
                </div>
            </section>
"""
    
    # Round-Trip Comparison Results
    html += """
            <section class="section">
                <h2 class="section-title">
                    <span class="icon">🔍</span>
                    Round-Trip Comparison Results
                </h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Comparison of original source data with derived source data after forward and reverse migration.
                </p>
"""
    
    for table_name, table_comp in results['comparison_results'].items():
        overall_conf = table_comp['overall_confidence']
        conf_class = 'confidence-high' if overall_conf >= 0.8 else 'confidence-medium' if overall_conf >= 0.5 else 'confidence-low'
        
        html += f"""
                <div class="table-header">
                    <span>📋</span>
                    <span>{table_name}</span>
                    <span style="margin-left: auto; font-size: 16px;">
                        Overall Confidence: <span class="{conf_class}">{overall_conf:.0%}</span>
                    </span>
                </div>
                
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Column Name</th>
                            <th>Status</th>
                            <th>Match Percentage</th>
                            <th>Confidence</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        for col_name, col_comp in table_comp['column_comparisons'].items():
            status = col_comp['status']
            match_pct = col_comp['match_percentage']
            confidence = col_comp['confidence']
            reason = col_comp['reason']
            
            # Map status to badge class and icon
            status_map = {
                'PERFECT_MATCH': ('badge-perfect', '✅'),
                'NEAR_PERFECT': ('badge-near-perfect', '✓'),
                'ACCEPTABLE': ('badge-acceptable', '⚠️'),
                'DATA_LOSS': ('badge-data-loss', '❌'),
                'NOT_MAPPED': ('badge-not-mapped', '❓')
            }
            
            badge_class, icon = status_map.get(status, ('badge-not-mapped', '❓'))
            conf_class = 'confidence-high' if confidence >= 0.9 else 'confidence-medium' if confidence >= 0.6 else 'confidence-low'
            
            html += f"""
                        <tr>
                            <td><strong>{icon} {col_name}</strong></td>
                            <td><span class="badge {badge_class}">{status.replace('_', ' ')}</span></td>
                            <td>{match_pct:.1f}%</td>
                            <td><span class="confidence {conf_class}">{confidence:.0%}</span></td>
                            <td><span class="reason-text">{reason}</span></td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
"""
    
    html += """
            </section>
"""
    
    # Refined Mappings
    html += """
            <section class="section">
                <h2 class="section-title">
                    <span class="icon">🎯</span>
                    Refined Mapping Recommendations
                </h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Final mapping recommendations after iterative refinement based on round-trip validation.
                </p>
"""
    
    for table_pair, mappings in results['refined_mappings'].items():
        src_table, tgt_table = table_pair.split('→')
        
        html += f"""
                <div class="table-header">
                    <span>🔄</span>
                    <span>{src_table} → {tgt_table}</span>
                </div>
                
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Source Column</th>
                            <th>Target Column</th>
                            <th>Confidence</th>
                            <th>Action</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        for mapping in mappings:
            src_col = mapping['source_column']
            tgt_col = mapping.get('target_column', None)
            confidence = mapping.get('refined_confidence', 0.0)
            reason = mapping.get('refinement_reason', '')
            
            # Determine action and styling
            if confidence == 1.0:
                icon = '✅'
                action = 'CONFIRMED'
                badge_class = 'badge-confirmed'
            elif tgt_col is None:
                icon = '❌'
                action = 'DISCARDED'
                badge_class = 'badge-discarded'
                tgt_col = '<em>(none)</em>'
            elif 'Re-mapped' in reason:
                icon = '🔄'
                action = 'IMPROVED'
                badge_class = 'badge-improved'
            else:
                icon = '⚠️'
                action = 'KEPT'
                badge_class = 'badge-kept'
            
            conf_class = 'confidence-high' if confidence >= 0.9 else 'confidence-medium' if confidence >= 0.6 else 'confidence-low'
            
            html += f"""
                        <tr>
                            <td><strong>{icon} {src_col}</strong></td>
                            <td>{tgt_col}</td>
                            <td><span class="confidence {conf_class}">{confidence:.0%}</span></td>
                            <td><span class="badge {badge_class}">{action}</span></td>
                            <td><span class="reason-text">{reason}</span></td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
"""
    
    html += """
            </section>
"""
    
    # Recommendations
    html += """
            <section class="section">
                <h2 class="section-title">
                    <span class="icon">💡</span>
                    Recommendations
                </h2>
                
                <div class="recommendations">
                    <h3>Next Steps</h3>
                    <ul>
                        <li><strong>CONFIRMED Mappings (100% confidence):</strong> Use these mappings directly in production migration without any concerns.</li>
                        <li><strong>IMPROVED Mappings:</strong> Review with business stakeholders to ensure the new target columns make semantic sense for your use case.</li>
                        <li><strong>KEPT Mappings:</strong> These have acceptable data loss. Verify that the loss is acceptable for your business requirements.</li>
                        <li><strong>DISCARDED Columns:</strong> Consider if the data is needed in the target system. Options include:
                            <ul style="margin-left: 30px; margin-top: 10px;">
                                <li>Adding new columns to the target schema</li>
                                <li>Storing data in a separate reference table</li>
                                <li>Confirming the data is not needed</li>
                            </ul>
                        </li>
                        <li><strong>Testing:</strong> Consider increasing the sample size (default 50 rows) for more comprehensive validation.</li>
                        <li><strong>Staging Migration:</strong> Run a staging migration on a larger subset before full production migration.</li>
                    </ul>
                </div>
                
                <div class="info-box">
                    <h4>Understanding Confidence Levels</h4>
                    <p><strong>100% (CONFIRMED):</strong> Data survives round-trip perfectly. Use confidently.</p>
                    <p><strong>90-99% (NEAR PERFECT):</strong> Minor formatting changes (e.g., trailing spaces, rounding). Usually acceptable.</p>
                    <p><strong>70-89% (ACCEPTABLE):</strong> Some data loss but may be acceptable (e.g., time information from timestamp to date).</p>
                    <p><strong>&lt;70% (DATA LOSS):</strong> Significant data loss. Review carefully or discard.</p>
                </div>
            </section>
"""
    
    # Key Insights
    perfect_pct = summary['perfect_match_percentage']
    if perfect_pct >= 80:
        status_class = 'badge-perfect'
        status_text = '✅ High Confidence Migration'
        recommendation = 'The migration shows high confidence with most mappings validated through round-trip testing. You can proceed with production migration after reviewing the improved mappings.'
    elif perfect_pct >= 50:
        status_class = 'badge-acceptable'
        status_text = '⚠️ Medium Confidence - Review Required'
        recommendation = 'The migration shows moderate confidence. Review all improved and kept mappings with business stakeholders before proceeding. Consider testing with a larger sample size.'
    else:
        status_class = 'badge-data-loss'
        status_text = '❌ Low Confidence - Caution Required'
        recommendation = 'The migration shows low confidence with significant data loss risks. Consider modifying the target schema, implementing custom transformation logic, or manual migration for critical data.'
    
    html += f"""
            <section class="section">
                <h2 class="section-title">
                    <span class="icon">🎯</span>
                    Overall Assessment
                </h2>
                
                <div style="text-align: center; padding: 30px; background: #f8f9fa; border-radius: 12px;">
                    <div style="font-size: 24px; margin-bottom: 15px;">
                        <span class="badge {status_class}" style="font-size: 18px; padding: 10px 20px;">
                            {status_text}
                        </span>
                    </div>
                    <p style="font-size: 16px; color: #666; max-width: 800px; margin: 0 auto;">
                        {recommendation}
                    </p>
                </div>
            </section>
"""
    
    # Footer
    html += f"""
        </div>
        
        <div class="footer">
            <p><strong>Iterative Reverse Mapping System</strong></p>
            <p>Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            <p>AI-Powered Data Migration with Round-Trip Validation</p>
            <p style="margin-top: 15px; font-size: 12px; color: #999;">
                This report analyzes data migration quality by performing actual forward and reverse migrations
                on sample data, providing evidence-based confidence scores for each mapping.
            </p>
        </div>
    </div>
    
    <script>
        // Make expandable sections work
        document.querySelectorAll('.expandable-header').forEach(header => {{
            header.addEventListener('click', function() {{
                this.parentElement.classList.toggle('active');
            }});
        }});
        
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ HTML report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    
    # Load results from JSON
    json_path = sys.argv[1] if len(sys.argv) > 1 else 'outputs/iterative_mapping_results.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'outputs/iterative_mapping_report.html'
    
    try:
        with open(json_path, 'r') as f:
            results = json.load(f)
        
        create_html_report(results, output_path)
        print(f"\n🎉 Success! Open {output_path} in your browser to view the report.")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {json_path}")
        print("Please run the iterative mapping first to generate results.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
