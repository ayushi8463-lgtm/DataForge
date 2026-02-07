# Contextual Compression Engine for Extreme Long Documents

**Track 4 Solution: Hierarchical Document Compression with Full Traceability**

## 🎯 Problem Statement

Enterprise documents (500-5000 pages) need intelligent compression that:
- ✅ Preserves decision-critical content (numbers, dates, exceptions, risks)
- ✅ Maintains full traceability to source
- ✅ Detects contradictions and conflicts
- ✅ Supports drill-down from summary to original text
- ✅ Explains what was preserved vs. removed

Traditional summarization fails because it loses critical details and breaks traceability.

## 🏗️ Architecture

### Hierarchical Compression Strategy

```
Original Document (500-5000 pages)
         ↓
    LEVEL 1: PARAGRAPH PROCESSING
    ├─ GETS: Graph-based sentence extraction
    ├─ NER: Named entity recognition
    └─ Regex: Numbers, dates, exceptions, risks
         ↓
    LEVEL 2: SECTION COMPRESSION (5 paragraphs → 1 section)
    ├─ BART: Abstractive summarization
    └─ Contradiction Detection
         ↓
    LEVEL 3: CHAPTER COMPRESSION (3 sections → 1 chapter)
    └─ BART: Higher-level summarization
         ↓
    LEVEL 4: DOCUMENT SUMMARY
    └─ BART: Top-level overview
         ↓
    Interactive HTML Output
```

### Multi-Method Extraction Pipeline

At each paragraph, we run **parallel extraction**:

1. **GETS (Graph-based Extractive Text Summarization)**
   - Build similarity graph using sentence embeddings
   - Apply PageRank to find central sentences
   - Preserves coherent, representative content

2. **Critical Fact Extraction**
   - **Regex patterns** for:
     - Numbers & thresholds: "500 units", "maximum 10 days"
     - Dates: "January 15, 2024", "2024-01-15"
     - Exceptions: "unless", "except", "only if"
     - Risks: "may", "could", "potential danger"
     - Constraints: "must", "shall", "required"
   - **spaCy NER** for:
     - Organizations, people, locations
     - Money, percentages, quantities

3. **Contradiction Detection**
   - Numerical conflicts: Same context, different numbers
   - Logical negations: Contradictory statements
   - Preserves both conflicting statements with sources

### Traceability System

Every compressed element includes:
```python
{
  "content": "Maximum limit is 500 units",
  "source": {
    "page": 42,
    "paragraph_idx": 3,
    "sentence_idx": 2,
    "original_text": "The maximum allowable limit is 500 units per day."
  }
}
```

Users can drill down:
**Document Summary** → **Chapter Summary** → **Section Summary** → **Paragraph Summary** → **Original Text**

## 📦 Installation & Setup

### Option 1: Google Colab (Recommended)

1. Upload `Contextual_Compression_Engine.ipynb` to Google Colab
2. Run cells sequentially
3. Upload your PDF when prompted
4. Download the generated HTML visualization

### Option 2: Local Setup

```bash
# Clone or download the repository
git clone <your-repo-url>
cd contextual-compression-engine

# Install dependencies
pip install pdfplumber spacy sentence-transformers transformers networkx

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the engine
python contextual_compression_engine.py your_document.pdf

# Generate HTML visualization
python html_visualizer.py compression_result.json
```

## 🚀 Usage

### Basic Usage

```python
from contextual_compression_engine import HierarchicalCompressor

# Initialize
compressor = HierarchicalCompressor()

# Extract text from PDF
paragraphs = compressor.extract_text_from_pdf("document.pdf")

# Perform hierarchical compression
result = compressor.compress_hierarchically(
    paragraphs,
    section_size=5,    # 5 paragraphs per section
    chapter_size=3     # 3 sections per chapter
)

# Save results
import json
with open('result.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
```

### Generate HTML Visualization

```python
from html_visualizer import generate_visualization

# Create interactive HTML
generate_visualization('result.json', 'output.html')
```

### Query Critical Facts

```python
# Search for specific content
query = "500 units"
matches = [f for f in result['critical_facts'] 
           if query.lower() in f['content'].lower()]

for fact in matches:
    print(f"{fact['fact_type']}: {fact['content']}")
    print(f"Source: Page {fact['source']['page']}")
```

## 📊 Output Structure

### JSON Output

```json
{
  "document_summary": {
    "abstractive_summary": "...",
    "child_chapters": ["chapter_0", "chapter_1", ...]
  },
  "chapters": [
    {
      "id": "chapter_0",
      "abstractive_summary": "...",
      "child_sections": ["section_0", "section_1", ...]
    }
  ],
  "sections": [
    {
      "id": "section_0",
      "abstractive_summary": "...",
      "contradictions": [...],
      "child_paragraphs": ["para_1_0", "para_1_1", ...]
    }
  ],
  "paragraphs": [
    {
      "id": "para_1_0",
      "original_text": "...",
      "extractive_summary": "...",
      "critical_facts": [...],
      "source": {...}
    }
  ],
  "critical_facts": [
    {
      "fact_type": "number",
      "content": "500 units",
      "context": "Maximum limit is 500 units per day",
      "source": {"page": 42, "paragraph_idx": 3}
    }
  ],
  "contradictions": [
    {
      "statement_a": "Policy A allows 5 days",
      "statement_b": "Policy B allows 3 days",
      "source_a": {...},
      "source_b": {...},
      "conflict_type": "numerical"
    }
  ]
}
```

### HTML Output

Interactive visualization with:
- **Document overview** with statistics
- **Critical facts** grouped by type
- **Contradictions** highlighted
- **Hierarchical drill-down** (collapsible chapters → sections → paragraphs)
- **Source traceability** for every claim

## 🎨 Features

### ✅ Hierarchical Compression
- Multi-level structure maintains document organization
- Each level is independently queryable
- Drill-down preserves context

### ✅ Decision-Critical Content Preservation
- **Numbers & Thresholds**: Regex + NER capture all numerical constraints
- **Dates**: Multiple format support
- **Exceptions**: Pattern matching for conditional language
- **Risks**: Keyword + context analysis
- **Entities**: Organizations, people, locations preserved

### ✅ Full Traceability
- Every fact links to exact source location
- Page number, paragraph index, sentence index
- Original text always accessible
- No information is "lost" - just organized

### ✅ Contradiction Detection
- Numerical conflicts (same topic, different numbers)
- Logical contradictions (negations, conflicts)
- Both statements preserved with sources

### ✅ Explainability
- Clear view of what was preserved vs. removed
- Importance scores for critical facts
- Summary quality metrics

## 🔧 Configuration

### Adjust Hierarchy Levels

```python
# For very long documents (2000+ pages)
result = compressor.compress_hierarchically(
    paragraphs,
    section_size=10,   # More paragraphs per section
    chapter_size=5     # More sections per chapter
)

# For shorter documents (100-500 pages)
result = compressor.compress_hierarchically(
    paragraphs,
    section_size=3,
    chapter_size=2
)
```

### Customize Critical Content Patterns

Edit `CriticalContentExtractor.patterns` in `contextual_compression_engine.py`:

```python
self.patterns = {
    'number_threshold': r'your_regex_here',
    'custom_pattern': r'your_custom_pattern'
}
```

## 📈 Performance

### Model Loading
- **First run**: ~2-3 minutes (downloading models)
- **Subsequent runs**: ~30 seconds (models cached)

### Processing Speed
- **Small docs (50-100 pages)**: ~5-10 minutes
- **Medium docs (500 pages)**: ~30-45 minutes
- **Large docs (2000+ pages)**: ~2-3 hours

**Note**: Using GPU in Colab significantly speeds up BART summarization.

### Memory Requirements
- **Minimum**: 4GB RAM
- **Recommended**: 8GB+ RAM for 1000+ page documents
- **Google Colab**: Free tier is sufficient (12GB RAM)

## 🧪 Testing

The solution has been tested with:
- ✅ Legal documents (policies, contracts)
- ✅ Technical manuals
- ✅ Research papers
- ✅ Corporate reports
- ✅ Government regulations

## 🎯 Evaluation Criteria Alignment

| Criterion | Implementation |
|-----------|----------------|
| **Hierarchical Design** | 4-level hierarchy (Paragraph → Section → Chapter → Document) |
| **Traceability** | Every fact has source reference (page, paragraph, sentence) |
| **Critical Content** | Multi-method extraction (GETS + NER + Regex) |
| **Contradictions** | Dedicated detector with source preservation |
| **Drill-Down** | Interactive HTML with collapsible hierarchy |
| **Explainability** | Clear preservation vs. removal analysis |
| **Enterprise-Ready** | JSON output, API-ready structure, scalable architecture |

## 🤝 Contributing

This is a competition submission. For improvements:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **sentence-transformers**: Sentence embeddings for GETS
- **spaCy**: Named entity recognition
- **HuggingFace Transformers**: BART summarization
- **pdfplumber**: PDF text extraction

## 📞 Contact

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ for Track 4: Contextual Compression for Extreme Long Inputs**
