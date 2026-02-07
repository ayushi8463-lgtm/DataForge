"""
HTML Visualization Generator
Creates an interactive HTML interface with drill-down capability
"""

import json
from typing import Dict, Any


class HTMLVisualizer:
    """Generate interactive HTML visualization with drill-down functionality"""
    
    def __init__(self, compression_result: Dict[str, Any]):
        self.result = compression_result
        self.doc_summary = compression_result['document_summary']
        self.chapters = compression_result['chapters']
        self.sections = compression_result['sections']
        self.paragraphs = compression_result['paragraphs']
        self.facts = compression_result['critical_facts']
        self.contradictions = compression_result['contradictions']
        self.metadata = compression_result['metadata']
    
    def generate_html(self) -> str:
        """Generate complete HTML document"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contextual Compression Engine - Document Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=JetBrains+Mono:wght@400;600&family=Spectral:wght@400;600;700&display=swap" rel="stylesheet">
    {self._generate_css()}
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_stats_panel()}
        {self._generate_document_summary()}
        {self._generate_critical_facts()}
        {self._generate_contradictions()}
        {self._generate_hierarchical_view()}
    </div>
    {self._generate_javascript()}
</body>
</html>"""
        return html
    
    def _generate_css(self) -> str:
        """Generate CSS with distinctive design"""
        return """<style>
        :root {
            --primary: #1a1a2e;
            --secondary: #16213e;
            --accent: #e94560;
            --accent-light: #ff6b6b;
            --bg: #0f0f1e;
            --text: #e8e8e8;
            --text-dim: #a0a0a0;
            --border: #2a2a3e;
            --code-bg: #1e1e2e;
            --success: #4ecdc4;
            --warning: #f9ca24;
            --info: #74b9ff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Spectral', serif;
            background: linear-gradient(135deg, var(--bg) 0%, var(--primary) 100%);
            color: var(--text);
            line-height: 1.7;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* Header */
        header {
            text-align: center;
            margin-bottom: 60px;
            position: relative;
        }
        
        header::before {
            content: '';
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 4px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            animation: glow 2s ease-in-out infinite;
        }
        
        @keyframes glow {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        h1 {
            font-family: 'Crimson Pro', serif;
            font-size: 3.5rem;
            font-weight: 700;
            letter-spacing: -1px;
            margin-bottom: 15px;
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: var(--text-dim);
            font-style: italic;
        }
        
        /* Stats Panel */
        .stats-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 50px;
        }
        
        .stat-card {
            background: var(--secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(233, 69, 96, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .stat-card:hover::before {
            left: 100%;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent);
            box-shadow: 0 10px 30px rgba(233, 69, 96, 0.2);
        }
        
        .stat-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Section Containers */
        .section {
            background: var(--secondary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 35px;
            margin-bottom: 35px;
            transition: all 0.3s ease;
        }
        
        .section:hover {
            border-color: var(--accent);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }
        
        h2 {
            font-family: 'Crimson Pro', serif;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 25px;
            color: var(--accent-light);
            border-bottom: 2px solid var(--border);
            padding-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        h2::before {
            content: '';
            width: 6px;
            height: 30px;
            background: linear-gradient(180deg, var(--accent), var(--accent-light));
            border-radius: 3px;
        }
        
        /* Document Summary */
        .summary-box {
            background: var(--code-bg);
            border-left: 4px solid var(--accent);
            padding: 25px;
            border-radius: 8px;
            font-size: 1.1rem;
            line-height: 1.8;
            margin-bottom: 20px;
        }
        
        /* Critical Facts */
        .facts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .fact-card {
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .fact-card:hover {
            transform: translateX(5px);
            border-color: var(--success);
            box-shadow: 0 4px 15px rgba(78, 205, 196, 0.2);
        }
        
        .fact-type {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--success);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .fact-content {
            font-size: 1.05rem;
            margin-bottom: 12px;
            font-weight: 600;
        }
        
        .fact-context {
            font-size: 0.9rem;
            color: var(--text-dim);
            margin-bottom: 12px;
            font-style: italic;
        }
        
        .fact-source {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--info);
            padding: 8px 12px;
            background: rgba(116, 185, 255, 0.1);
            border-radius: 6px;
            display: inline-block;
        }
        
        /* Contradictions */
        .contradiction-card {
            background: var(--code-bg);
            border-left: 4px solid var(--warning);
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        
        .contradiction-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--warning);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .statement {
            background: rgba(249, 202, 36, 0.05);
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 3px solid var(--warning);
        }
        
        .statement-text {
            margin-bottom: 8px;
        }
        
        .statement-source {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--text-dim);
        }
        
        /* Hierarchical View */
        .hierarchy {
            margin-top: 20px;
        }
        
        .hierarchy-level {
            margin-bottom: 25px;
        }
        
        .collapsible {
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .collapsible:hover {
            border-color: var(--accent);
        }
        
        .collapsible-header {
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        
        .collapsible-header:hover {
            background: rgba(233, 69, 96, 0.05);
        }
        
        .collapsible-title {
            font-family: 'Crimson Pro', serif;
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .level-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            padding: 4px 10px;
            background: var(--accent);
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .expand-icon {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            color: var(--accent);
            transition: transform 0.3s ease;
        }
        
        .collapsible.active .expand-icon {
            transform: rotate(90deg);
        }
        
        .collapsible-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease;
        }
        
        .collapsible.active .collapsible-content {
            max-height: 5000px;
        }
        
        .content-inner {
            padding: 25px;
            border-top: 1px solid var(--border);
            background: rgba(0,0,0,0.2);
        }
        
        .summary-text {
            line-height: 1.8;
            margin-bottom: 15px;
        }
        
        .children-list {
            margin-top: 15px;
            padding-left: 20px;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .section {
            animation: fadeIn 0.6s ease forwards;
        }
        
        .section:nth-child(1) { animation-delay: 0.1s; }
        .section:nth-child(2) { animation-delay: 0.2s; }
        .section:nth-child(3) { animation-delay: 0.3s; }
        .section:nth-child(4) { animation-delay: 0.4s; }
        .section:nth-child(5) { animation-delay: 0.5s; }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 40px;
            color: var(--text-dim);
            font-style: italic;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            h1 {
                font-size: 2.5rem;
            }
            
            .stats-panel {
                grid-template-columns: 1fr;
            }
            
            .facts-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>"""
    
    def _generate_header(self) -> str:
        """Generate header section"""
        return f"""
    <header>
        <h1>Contextual Compression Engine</h1>
        <p class="subtitle">Hierarchical Document Analysis with Full Traceability</p>
    </header>
    """
    
    def _generate_stats_panel(self) -> str:
        """Generate statistics panel"""
        return f"""
    <div class="stats-panel">
        <div class="stat-card">
            <div class="stat-number">{self.metadata['total_paragraphs']}</div>
            <div class="stat-label">Paragraphs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.metadata['total_sections']}</div>
            <div class="stat-label">Sections</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.metadata['total_chapters']}</div>
            <div class="stat-label">Chapters</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.metadata['total_facts']}</div>
            <div class="stat-label">Critical Facts</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.metadata['total_contradictions']}</div>
            <div class="stat-label">Contradictions</div>
        </div>
    </div>
    """
    
    def _generate_document_summary(self) -> str:
        """Generate document summary section"""
        return f"""
    <div class="section">
        <h2>Document Summary</h2>
        <div class="summary-box">
            {self.doc_summary['abstractive_summary']}
        </div>
    </div>
    """
    
    def _generate_critical_facts(self) -> str:
        """Generate critical facts section"""
        if not self.facts:
            return f"""
    <div class="section">
        <h2>Critical Facts Extracted</h2>
        <div class="empty-state">No critical facts extracted</div>
    </div>
    """
        
        # Group by type
        facts_by_type = {}
        for fact in self.facts[:50]:  # Limit to first 50 for display
            fact_type = fact['fact_type']
            if fact_type not in facts_by_type:
                facts_by_type[fact_type] = []
            facts_by_type[fact_type].append(fact)
        
        html = """
    <div class="section">
        <h2>Critical Facts Extracted</h2>
        <div class="facts-grid">
    """
        
        for fact_type, facts in facts_by_type.items():
            for fact in facts[:10]:  # Show max 10 per type
                source_str = f"Page {fact['source']['page']}, Para {fact['source']['paragraph_idx']}"
                html += f"""
            <div class="fact-card">
                <div class="fact-type">{fact_type}</div>
                <div class="fact-content">{fact['content']}</div>
                <div class="fact-context">"{fact['context'][:100]}{'...' if len(fact['context']) > 100 else ''}"</div>
                <div class="fact-source">{source_str}</div>
            </div>
        """
        
        html += """
        </div>
    </div>
    """
        return html
    
    def _generate_contradictions(self) -> str:
        """Generate contradictions section"""
        if not self.contradictions:
            return f"""
    <div class="section">
        <h2>Contradictions Detected</h2>
        <div class="empty-state">No contradictions detected</div>
    </div>
    """
        
        html = """
    <div class="section">
        <h2>Contradictions Detected</h2>
    """
        
        for idx, contradiction in enumerate(self.contradictions[:10], 1):  # Show max 10
            source_a = f"Page {contradiction['source_a']['page']}, Para {contradiction['source_a']['paragraph_idx']}"
            source_b = f"Page {contradiction['source_b']['page']}, Para {contradiction['source_b']['paragraph_idx']}"
            
            html += f"""
        <div class="contradiction-card">
            <div class="contradiction-label">Contradiction {idx} ({contradiction['conflict_type']})</div>
            <div class="statement">
                <div class="statement-text">{contradiction['statement_a']}</div>
                <div class="statement-source">Source: {source_a}</div>
            </div>
            <div class="statement">
                <div class="statement-text">{contradiction['statement_b']}</div>
                <div class="statement-source">Source: {source_b}</div>
            </div>
        </div>
        """
        
        html += """
    </div>
    """
        return html
    
    def _generate_hierarchical_view(self) -> str:
        """Generate hierarchical drill-down view"""
        html = """
    <div class="section">
        <h2>Hierarchical Structure (Drill-Down)</h2>
        <div class="hierarchy">
    """
        
        # Chapters level
        for chapter in self.chapters:
            html += f"""
            <div class="collapsible">
                <div class="collapsible-header">
                    <div class="collapsible-title">
                        <span class="level-badge">Chapter</span>
                        <span>{chapter['id']}</span>
                    </div>
                    <span class="expand-icon">▶</span>
                </div>
                <div class="collapsible-content">
                    <div class="content-inner">
                        <div class="summary-text">{chapter['abstractive_summary']}</div>
                        <div class="children-list">
            """
            
            # Sections within chapter
            for section_id in chapter['child_sections']:
                section = next((s for s in self.sections if s['id'] == section_id), None)
                if section:
                    html += f"""
                            <div class="collapsible">
                                <div class="collapsible-header">
                                    <div class="collapsible-title">
                                        <span class="level-badge">Section</span>
                                        <span>{section['id']}</span>
                                    </div>
                                    <span class="expand-icon">▶</span>
                                </div>
                                <div class="collapsible-content">
                                    <div class="content-inner">
                                        <div class="summary-text">{section['abstractive_summary']}</div>
                                        <div class="children-list">
                    """
                    
                    # Paragraphs within section
                    for para_id in section['child_paragraphs']:
                        para = next((p for p in self.paragraphs if p['id'] == para_id), None)
                        if para:
                            source_str = f"Page {para['source']['page']}, Para {para['source']['paragraph_idx']}"
                            html += f"""
                                            <div class="collapsible">
                                                <div class="collapsible-header">
                                                    <div class="collapsible-title">
                                                        <span class="level-badge">Paragraph</span>
                                                        <span>{para['id']}</span>
                                                    </div>
                                                    <span class="expand-icon">▶</span>
                                                </div>
                                                <div class="collapsible-content">
                                                    <div class="content-inner">
                                                        <div class="summary-text"><strong>Extractive:</strong> {para['extractive_summary']}</div>
                                                        <div class="summary-text"><strong>Original:</strong> {para['original_text'][:300]}{'...' if len(para['original_text']) > 300 else ''}</div>
                                                        <div class="fact-source">{source_str}</div>
                                                    </div>
                                                </div>
                                            </div>
                            """
                    
                    html += """
                                        </div>
                                    </div>
                                </div>
                            </div>
                    """
            
            html += """
                        </div>
                    </div>
                </div>
            </div>
            """
        
        html += """
        </div>
    </div>
    """
        return html
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript for interactivity"""
        return """
    <script>
        // Collapsible functionality
        document.addEventListener('DOMContentLoaded', function() {
            const collapsibles = document.querySelectorAll('.collapsible-header');
            
            collapsibles.forEach(header => {
                header.addEventListener('click', function() {
                    const collapsible = this.parentElement;
                    collapsible.classList.toggle('active');
                });
            });
            
            // Smooth scroll animation
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
        });
    </script>
    """
    
    def save_html(self, output_path: str):
        """Save HTML to file"""
        html_content = self.generate_html()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML visualization saved to: {output_path}")


def generate_visualization(json_path: str, output_path: str = 'compression_visualization.html'):
    """Generate HTML visualization from JSON result"""
    with open(json_path, 'r') as f:
        result = json.load(f)
    
    visualizer = HTMLVisualizer(result)
    visualizer.save_html(output_path)
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python html_visualizer.py <compression_result.json>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = generate_visualization(json_path)
    print(f"Visualization created: {output_path}")
