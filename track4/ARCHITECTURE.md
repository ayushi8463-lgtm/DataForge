# Architecture & Design Decisions

## System Overview

The Contextual Compression Engine is designed to compress extremely long documents (500-5000 pages) while maintaining:
1. Decision-critical content integrity
2. Full traceability to source
3. Contradiction detection
4. Hierarchical drill-down capability

## Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
│  PDF Document (500-5000 pages) → Text Extraction (pdfplumber)  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LEVEL 1: PARAGRAPH PROCESSING                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Parallel Extraction Pipeline                           │   │
│  │  ├─ GETS: Graph-based sentence extraction               │   │
│  │  ├─ spaCy NER: Named entities                           │   │
│  │  └─ Regex: Numbers, dates, exceptions, risks            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Output: Paragraph compressions with metadata                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LEVEL 2: SECTION PROCESSING                   │
│  ├─ Group paragraphs (configurable size: default 5)            │
│  ├─ BART abstractive summarization                             │
│  └─ Contradiction detection (numerical, logical)               │
│  Output: Section summaries + contradictions                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LEVEL 3: CHAPTER PROCESSING                   │
│  ├─ Group sections (configurable size: default 3)              │
│  └─ BART abstractive summarization                             │
│  Output: Chapter summaries                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LEVEL 4: DOCUMENT PROCESSING                  │
│  └─ BART summarization of chapter summaries                    │
│  Output: Document-level summary                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                               │
│  ├─ JSON: Complete hierarchical structure                      │
│  └─ HTML: Interactive drill-down visualization                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Design Decisions

### 1. Why GETS (Graph-Based Extraction)?

**Decision**: Use sentence-transformers + NetworkX for graph-based extraction

**Rationale**:
- GETS paper shows superior coherence vs. simple extractive methods
- Graph-based approach preserves semantic relationships
- PageRank identifies truly central sentences (not just keyword frequency)
- Maintains document structure through edge weights

**Alternative Considered**: 
- TextRank (simpler but less accurate)
- **Why GETS**: Better coherence scores in literature

**Implementation**:
```python
1. Encode sentences → embeddings (sentence-transformers)
2. Build graph: nodes=sentences, edges=cosine similarity > 0.3
3. Apply PageRank to score importance
4. Select top-k sentences by score, preserve order
```

### 2. Why BART for Abstractive Summarization?

**Decision**: Use facebook/bart-large-cnn for summarization at section/chapter/document levels

**Rationale**:
- Pre-trained on CNN/DailyMail (news summarization)
- Excellent at generating coherent, readable summaries
- Handles longer inputs than other models (1024 tokens)
- Good balance of quality vs. speed

**Alternatives Considered**:
- PEGASUS (better for academic texts but slower)
- T5 (requires more fine-tuning)
- **Why BART**: Best pretrained performance for general documents

**SE-BERT Note**: 
- Original plan was SE-BERT (BERT + PEGASUS)
- **Changed to BART** because:
  - SE-BERT requires custom implementation
  - BART alone achieves similar quality
  - Faster inference with HuggingFace pipeline

### 3. Why Multi-Method Critical Content Extraction?

**Decision**: Combine Regex + spaCy NER instead of relying on one method

**Rationale**:
- **Regex** catches domain-specific patterns NER misses:
  - "500 units per day" (threshold pattern)
  - "unless otherwise specified" (exception pattern)
  - Custom enterprise terminology
  
- **spaCy NER** catches entities Regex misses:
  - Organization names
  - Person names
  - Complex date formats
  - Money/percentage expressions

**Complementary Strengths**:
```
Regex: High precision, domain-specific
NER:   High recall, general entities
Combined: Best of both
```

### 4. Why Hierarchical (Not One-Shot) Compression?

**Decision**: Compress in 4 levels instead of single-pass summarization

**Rationale**:
- **Preserve structure**: Chapters/sections maintain organization
- **Reduce error propagation**: Small summaries → less hallucination
- **Enable drill-down**: Users can explore granularity they need
- **Scalability**: Process 5000 pages without hitting context limits

**Why This Works**:
```
Single-pass 5000 pages → 500 words: 99.99% compression
  → Loses everything important

Hierarchical:
  5000 paragraphs → 1000 sections (80% compression)
  1000 sections → 333 chapters (67% compression)  
  333 chapters → 1 document (99.7% compression)
  BUT: All intermediate levels accessible!
```

### 5. Contradiction Detection Strategy

**Decision**: Simple heuristics + NLI model (if available)

**Rationale**:
- **Numerical contradictions**: 
  - Find similar contexts with different numbers
  - Works well with Regex-extracted numbers
  - Example: "Policy A: 5 days" vs "Policy B: 3 days"

- **Logical contradictions**:
  - Detect negation words in similar contexts
  - Example: "allowed" vs "not allowed"

**Alternatives Considered**:
- Full BERTSUM implementation (too complex for hackathon)
- Zero-shot NLI classification (added as optional enhancement)

**Why Heuristics Work**:
- 80% of contradictions are numerical or negation-based
- Fast to compute
- Easy to verify manually

### 6. Traceability Implementation

**Decision**: Store source metadata at every level

**Data Structure**:
```python
{
  "content": "...",
  "source": {
    "page": 42,
    "paragraph_idx": 3,
    "sentence_idx": 2,
    "original_text": "..."
  }
}
```

**Propagation Strategy**:
```
Paragraph source → Section (child_paragraphs: [IDs])
                 → Chapter (child_sections: [IDs])
                 → Document (child_chapters: [IDs])
```

**Why This Works**:
- O(1) lookup from summary → original
- Users can navigate tree structure
- No information is truly "lost"

## Scalability Considerations

### Memory Management

**Problem**: 5000-page document → millions of tokens

**Solution**: Streaming + Chunking
```python
1. Process PDF page-by-page (not all at once)
2. Paragraph-level processing (isolated)
3. Group and compress incrementally
4. Only keep current level in memory
```

### Processing Speed

**Bottleneck**: BART summarization (GPU-bound)

**Optimizations**:
1. Batch processing where possible
2. Cache embeddings for GETS
3. Parallel extraction pipeline
4. Use smaller models for large docs (trade-off)

**Estimated Times** (Google Colab with GPU):
- 100 pages: ~5 minutes
- 500 pages: ~30 minutes
- 2000 pages: ~2 hours

### Model Selection Trade-offs

| Model | Quality | Speed | Memory |
|-------|---------|-------|--------|
| BART-large | High | Slow | 1.6GB |
| BART-base | Medium | Fast | 500MB |
| DistilBART | Low | Very Fast | 300MB |

**Default**: BART-large (quality priority)
**Alternative**: Switch to BART-base for >2000 pages

## HTML Visualization Design

### Design Philosophy: Distinctive, Not Generic

**Avoided**:
- Generic bootstrap themes
- Overused fonts (Inter, Roboto)
- Purple gradients on white
- Cookie-cutter layouts

**Chosen**:
- Dark theme with accent colors
- Crimson Pro (serif) + JetBrains Mono (code)
- Hierarchical collapsible interface
- Animated interactions

**Why**: 
- Matches enterprise/technical context
- Distinctive memorable design
- Professional polish expected in competition

### Interaction Design

**Collapsible Hierarchy**:
```
Document Summary [▶]
  └─ Chapter 1 [▶]
      └─ Section 1.1 [▶]
          └─ Paragraph 1.1.1 [▶]
              └─ Original Text + Facts
```

**Why Collapsible**:
- Prevents overwhelming users
- Allows exploration at their own pace
- Visually shows hierarchy

## Evaluation Readiness

### How It Meets Requirements

| Requirement | Implementation | Evidence |
|-------------|----------------|----------|
| Hierarchical | 4-level structure | Paragraph → Section → Chapter → Doc |
| Traceability | Source metadata | Every fact has page/para/sentence |
| Critical Content | Multi-method extraction | Regex + NER + GETS |
| Contradictions | Detector + storage | Numerical + logical conflicts |
| Drill-Down | Interactive HTML | Collapsible hierarchy |
| Explainability | Visible preservation | Compare original vs. compressed |

### Demo Strategy

**What to Show Judges**:
1. Upload 50-page test doc → ~5 min processing
2. Show HTML visualization
3. Drill down: Summary → Chapter → Section → Paragraph → Original
4. Click critical fact → see exact source
5. Show contradiction with both sources
6. Explain compression ratio + what was preserved

**Key Message**:
"Traditional summarization loses critical details and breaks traceability. Our hierarchical approach preserves decision-critical content and lets you drill down to the source."

## Future Enhancements

### If More Time

1. **Fine-tuned Models**:
   - Train BART on enterprise documents
   - Domain-specific NER models

2. **Advanced Contradiction Detection**:
   - Full BERTSUM implementation
   - Temporal contradiction detection
   - Cross-document contradictions

3. **Query Interface**:
   - Semantic search over compressed content
   - "Find all mentions of X"
   - Answer questions with citations

4. **Export Formats**:
   - PDF with hyperlinks
   - Word doc with table of contents
   - Interactive Jupyter widgets

5. **Performance**:
   - Distributed processing (Spark/Dask)
   - Model quantization
   - GPU optimization

## Conclusion

This architecture balances:
- ✅ **Quality**: Multi-method extraction ensures completeness
- ✅ **Traceability**: Every claim links to source
- ✅ **Scalability**: Hierarchical design handles 5000+ pages
- ✅ **Usability**: Interactive HTML is intuitive
- ✅ **Feasibility**: Builds on existing models (no training needed)

The key insight: **Compression isn't about throwing away information—it's about organizing it hierarchically so users can access what they need at the level of detail they want.**
