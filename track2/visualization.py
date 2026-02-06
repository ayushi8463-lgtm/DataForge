"""
Interactive Visualization Generator for Data Migration
=======================================================
Creates comprehensive visualizations:
- Table mapping diagrams
- Column relationship flows
- Confidence heatmaps
- Round-trip analysis charts
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import networkx as nx
from typing import Dict, List, Any


class MigrationVisualizer:
    """Generate interactive visualizations for migration analysis"""
    
    def __init__(self):
        self.figures = {}
    
    def create_sankey_diagram(self, mappings: Dict[str, Any]) -> go.Figure:
        """Create Sankey diagram showing data flow from source to target"""
        
        # Prepare data for Sankey
        sources = []
        targets = []
        values = []
        labels = []
        colors = []
        
        label_map = {}
        current_idx = 0
        
        for table_pair, column_mappings in mappings.items():
            src_table, tgt_table = table_pair.split('→')
            
            # Add source table if not exists
            if src_table not in label_map:
                label_map[src_table] = current_idx
                labels.append(f"📁 {src_table}")
                current_idx += 1
            
            # Add target table if not exists
            if tgt_table not in label_map:
                label_map[tgt_table] = current_idx
                labels.append(f"📁 {tgt_table}")
                current_idx += 1
            
            for mapping in column_mappings:
                src_col = f"{src_table}.{mapping['source_column']}"
                tgt_col = f"{tgt_table}.{mapping['target_column']}"
                
                # Add columns if not exists
                if src_col not in label_map:
                    label_map[src_col] = current_idx
                    labels.append(f"  {mapping['source_column']}")
                    current_idx += 1
                
                if tgt_col not in label_map:
                    label_map[tgt_col] = current_idx
                    labels.append(f"  {mapping['target_column']}")
                    current_idx += 1
                
                # Create flow from source column to target column
                sources.append(label_map[src_col])
                targets.append(label_map[tgt_col])
                
                # Color based on confidence
                confidence = mapping['confidence']
                if confidence >= 0.8:
                    color = 'rgba(0, 200, 0, 0.5)'  # Green for high confidence
                elif confidence >= 0.5:
                    color = 'rgba(255, 200, 0, 0.5)'  # Yellow for medium
                else:
                    color = 'rgba(255, 0, 0, 0.5)'  # Red for low confidence
                
                values.append(confidence)
                colors.append(color)
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color='lightblue'
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                label=[f"Confidence: {v:.2%}" for v in values]
            )
        )])
        
        fig.update_layout(
            title="Data Migration Flow - Source to Target Mapping",
            font=dict(size=12),
            height=800
        )
        
        return fig
    
    def create_confidence_heatmap(self, mappings: Dict[str, Any]) -> go.Figure:
        """Create heatmap showing mapping confidence scores"""
        
        data = []
        for table_pair, column_mappings in mappings.items():
            for mapping in column_mappings:
                data.append({
                    'Table': table_pair,
                    'Source Column': mapping['source_column'],
                    'Target Column': mapping['target_column'],
                    'Confidence': mapping['confidence'],
                    'Name Score': mapping['explanation']['name_similarity'],
                    'Type Score': mapping['explanation']['type_compatibility'],
                    'Pattern Score': mapping['explanation']['pattern_similarity']
                })
        
        df = pd.DataFrame(data)
        
        # Create subplot with multiple heatmaps
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Overall Confidence', 'Name Similarity', 'Type Compatibility'),
            horizontal_spacing=0.15
        )
        
        # Overall confidence heatmap
        pivot1 = df.pivot_table(
            index='Source Column', 
            columns='Target Column', 
            values='Confidence',
            aggfunc='first'
        )
        
        fig.add_trace(
            go.Heatmap(
                z=pivot1.values,
                x=pivot1.columns,
                y=pivot1.index,
                colorscale='RdYlGn',
                text=[[f'{val:.2%}' if not pd.isna(val) else '' 
                       for val in row] for row in pivot1.values],
                texttemplate='%{text}',
                textfont={"size": 10},
                showscale=True,
                colorbar=dict(x=0.28)
            ),
            row=1, col=1
        )
        
        # Name similarity
        pivot2 = df.pivot_table(
            index='Source Column', 
            columns='Target Column', 
            values='Name Score',
            aggfunc='first'
        )
        
        fig.add_trace(
            go.Heatmap(
                z=pivot2.values,
                x=pivot2.columns,
                y=pivot2.index,
                colorscale='Blues',
                showscale=True,
                colorbar=dict(x=0.62)
            ),
            row=1, col=2
        )
        
        # Type compatibility
        pivot3 = df.pivot_table(
            index='Source Column', 
            columns='Target Column', 
            values='Type Score',
            aggfunc='first'
        )
        
        fig.add_trace(
            go.Heatmap(
                z=pivot3.values,
                x=pivot3.columns,
                y=pivot3.index,
                colorscale='Purples',
                showscale=True,
                colorbar=dict(x=1.0)
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            title="Column Mapping Confidence Analysis",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_round_trip_chart(self, round_trip_results: Dict[str, Any]) -> go.Figure:
        """Create chart showing round-trip analysis"""
        
        # Extract data
        details = round_trip_results['details']
        
        table_names = []
        perfect = []
        acceptable = []
        data_loss = []
        
        for table_pair, detail in details.items():
            table_names.append(table_pair)
            perfect.append(len(detail['perfect_round_trip_fields']))
            acceptable.append(len(detail['acceptable_loss_fields']))
            data_loss.append(len(detail['data_loss_fields']))
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Perfect Round-Trip',
            x=table_names,
            y=perfect,
            marker_color='green',
            text=perfect,
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            name='Acceptable Loss',
            x=table_names,
            y=acceptable,
            marker_color='yellow',
            text=acceptable,
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            name='Data Loss Risk',
            x=table_names,
            y=data_loss,
            marker_color='red',
            text=data_loss,
            textposition='inside'
        ))
        
        fig.update_layout(
            title='Round-Trip Validation Analysis by Table',
            xaxis_title='Table Mapping',
            yaxis_title='Number of Fields',
            barmode='stack',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_network_graph(self, mappings: Dict[str, Any]) -> go.Figure:
        """Create network graph showing table relationships"""
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for table_pair, column_mappings in mappings.items():
            src_table, tgt_table = table_pair.split('→')
            
            # Add nodes
            G.add_node(src_table, node_type='source')
            G.add_node(tgt_table, node_type='target')
            
            # Add edge with average confidence
            avg_confidence = sum(m['confidence'] for m in column_mappings) / len(column_mappings)
            G.add_edge(src_table, tgt_table, weight=avg_confidence, mappings=len(column_mappings))
        
        # Create layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Extract node positions
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            weight = G[edge[0]][edge[1]]['weight']
            
            # Color based on confidence
            if weight >= 0.8:
                color = 'green'
            elif weight >= 0.5:
                color = 'orange'
            else:
                color = 'red'
            
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=2, color=color),
                    hoverinfo='text',
                    text=f"{edge[0]} → {edge[1]}<br>Confidence: {weight:.2%}<br>Mappings: {G[edge[0]][edge[1]]['mappings']}",
                    showlegend=False
                )
            )
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
            # Color by type
            if G.nodes[node]['node_type'] == 'source':
                node_color.append('lightblue')
            else:
                node_color.append('lightgreen')
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition='top center',
            marker=dict(
                showscale=False,
                color=node_color,
                size=30,
                line=dict(width=2, color='black')
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title='Table Mapping Network Graph',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        return fig
    
    def create_transformation_pie(self, mappings: Dict[str, Any]) -> go.Figure:
        """Create pie chart showing transformation statistics"""
        
        total = 0
        transformations_needed = 0
        high_confidence = 0
        medium_confidence = 0
        low_confidence = 0
        
        for table_pair, column_mappings in mappings.items():
            for mapping in column_mappings:
                total += 1
                if mapping['transformation_required']:
                    transformations_needed += 1
                
                conf = mapping['confidence']
                if conf >= 0.7:
                    high_confidence += 1
                elif conf >= 0.5:
                    medium_confidence += 1
                else:
                    low_confidence += 1
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Transformation Requirements', 'Mapping Confidence Distribution'),
            specs=[[{'type': 'pie'}, {'type': 'pie'}]]
        )
        
        # Transformation pie
        fig.add_trace(
            go.Pie(
                labels=['Transformation Required', 'No Transformation'],
                values=[transformations_needed, total - transformations_needed],
                marker=dict(colors=['#ff9999', '#99ff99']),
                hole=0.3
            ),
            row=1, col=1
        )
        
        # Confidence pie
        fig.add_trace(
            go.Pie(
                labels=['High (≥70%)', 'Medium (50-70%)', 'Low (<50%)'],
                values=[high_confidence, medium_confidence, low_confidence],
                marker=dict(colors=['#00cc00', '#ffcc00', '#ff0000']),
                hole=0.3
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Migration Statistics Overview',
            showlegend=True,
            height=400
        )
        
        return fig
    
    def generate_all_visualizations(self, mapping_report: Dict, 
                                   validation_report: Dict) -> Dict[str, go.Figure]:
        """Generate all visualizations"""
        
        visualizations = {}
        
        print("🎨 Generating Sankey diagram...")
        visualizations['sankey'] = self.create_sankey_diagram(
            mapping_report['forward_mappings']
        )
        
        print("🎨 Generating confidence heatmap...")
        visualizations['heatmap'] = self.create_confidence_heatmap(
            mapping_report['forward_mappings']
        )
        
        print("🎨 Generating round-trip chart...")
        visualizations['round_trip'] = self.create_round_trip_chart(
            validation_report['round_trip_analysis']
        )
        
        print("🎨 Generating network graph...")
        visualizations['network'] = self.create_network_graph(
            mapping_report['forward_mappings']
        )
        
        print("🎨 Generating statistics overview...")
        visualizations['statistics'] = self.create_transformation_pie(
            mapping_report['forward_mappings']
        )
        
        return visualizations
    
    def save_visualizations(self, visualizations: Dict[str, go.Figure], 
                           output_dir: str = '/home/claude'):
        """Save all visualizations as HTML files"""
        
        for name, fig in visualizations.items():
            filename = f"{output_dir}/visualization_{name}.html"
            fig.write_html(filename)
            print(f"   Saved: {filename}")
    
    def create_combined_dashboard(self, visualizations: Dict[str, go.Figure],
                                 output_dir: str = '/home/claude') -> str:
        """Create a combined HTML dashboard with all visualizations"""
        
        html_parts = ['''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Data Migration Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1400px;
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
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .viz-section {
            margin: 30px 0;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background: #fafafa;
        }
        .viz-title {
            font-size: 20px;
            font-weight: bold;
            color: #444;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .legend {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            padding: 5px 10px;
        }
        .green { background: #00cc00; color: white; border-radius: 3px; }
        .yellow { background: #ffcc00; color: black; border-radius: 3px; }
        .red { background: #ff0000; color: white; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI-Powered Data Migration Dashboard</h1>
        <p class="subtitle">Intelligent Schema Mapping • Bidirectional Analysis • Round-Trip Validation</p>
        
        <div class="legend">
            <strong>Confidence Levels:</strong>
            <span class="legend-item green">High (≥80%)</span>
            <span class="legend-item yellow">Medium (50-80%)</span>
            <span class="legend-item red">Low (<50%)</span>
        </div>
''']
        
        # Add each visualization
        viz_titles = {
            'statistics': 'Migration Statistics Overview',
            'sankey': 'Data Flow Visualization (Sankey Diagram)',
            'network': 'Table Relationship Network',
            'heatmap': 'Column Mapping Confidence Analysis',
            'round_trip': 'Round-Trip Validation Results'
        }
        
        for name, title in viz_titles.items():
            if name in visualizations:
                html_parts.append(f'''
        <div class="viz-section">
            <div class="viz-title">{title}</div>
            <div id="{name}"></div>
        </div>
''')
        
        html_parts.append('''
    </div>
    
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
''')
        
        # Add Plotly data for each visualization
        for name, fig in visualizations.items():
            fig_json = fig.to_json()
            html_parts.append(f'''
        var fig_{name} = {fig_json};
        Plotly.newPlot('{name}', fig_{name}.data, fig_{name}.layout);
''')
        
        html_parts.append('''
    </script>
</body>
</html>
''')
        
        # Save combined dashboard
        dashboard_path = f"{output_dir}/migration_dashboard.html"
        with open(dashboard_path, 'w') as f:
            f.write(''.join(html_parts))
        
        print(f"   📊 Combined dashboard saved: {dashboard_path}")
        return dashboard_path


if __name__ == "__main__":
    pass
