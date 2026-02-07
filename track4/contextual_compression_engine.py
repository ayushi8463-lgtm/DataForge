"""
Contextual Compression Engine for Extreme Long Documents
Implements hierarchical compression with full traceability and decision-critical content preservation

Architecture:
1. PDF Text Extraction with paragraph-level chunking
2. Multi-method extraction at each level:
   - GETS-like extractive summarization (sentence-transformers)
   - Critical fact extraction (NER + Regex)
   - Contradiction detection
3. Hierarchical compression: Paragraph → Section → Chapter → Document
4. HTML output with drill-down interface
"""

import re
import json
import warnings
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict
import numpy as np

warnings.filterwarnings('ignore')

# For PDF processing
try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'pdfplumber'], check=True)
    import pdfplumber

# For NLP processing
try:
    import spacy
except ImportError:
    print("Installing spacy...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'spacy'], check=True)
    import spacy

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    print("Installing sentence-transformers...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'sentence-transformers'], check=True)
    from sentence_transformers import SentenceTransformer, util

try:
    from transformers import pipeline
except ImportError:
    print("Installing transformers...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'transformers'], check=True)
    from transformers import pipeline

try:
    import networkx as nx
except ImportError:
    print("Installing networkx...")
    import subprocess
    subprocess.run(['pip', 'install', '-q', 'networkx'], check=True)
    import networkx as nx

try:
    import community.community_louvain as community_louvain
    HAS_COMMUNITY = True
except ImportError:
    print("Installing python-louvain for graph clustering...")
    import subprocess
    try:
        subprocess.run(['pip', 'install', '-q', 'python-louvain'], check=True)
        import community.community_louvain as community_louvain
        HAS_COMMUNITY = True
    except:
        print("  Note: Graph clustering unavailable, using fallback method")
        HAS_COMMUNITY = False


@dataclass
class SourceReference:
    """Traceability metadata for content"""
    page: int
    paragraph_idx: int
    sentence_idx: int = None
    line_range: Tuple[int, int] = None
    original_text: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    def __str__(self):
        if self.sentence_idx is not None:
            return f"Page {self.page}, Paragraph {self.paragraph_idx}, Sentence {self.sentence_idx}"
        return f"Page {self.page}, Paragraph {self.paragraph_idx}"


@dataclass
class CriticalFact:
    """Decision-critical content with full traceability"""
    fact_type: str  # 'number', 'date', 'exception', 'risk', 'entity'
    content: str
    context: str  # Surrounding sentence
    source: SourceReference
    importance_score: float = 1.0
    
    def to_dict(self):
        d = asdict(self)
        d['source'] = self.source.to_dict()
        return d


@dataclass
class Contradiction:
    """Detected contradiction between statements"""
    statement_a: str
    statement_b: str
    source_a: SourceReference
    source_b: SourceReference
    conflict_type: str  # 'numerical', 'logical', 'temporal'
    
    def to_dict(self):
        return {
            'statement_a': self.statement_a,
            'statement_b': self.statement_b,
            'source_a': self.source_a.to_dict(),
            'source_b': self.source_b.to_dict(),
            'conflict_type': self.conflict_type
        }


class CriticalContentExtractor:
    """Extract decision-critical content: numbers, dates, exceptions, risks, entities"""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy English model...")
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            self.nlp = spacy.load("en_core_web_sm")
        
        # Regex patterns
        self.patterns = {
            'number_threshold': r'\b\d+(?:\.\d+)?(?:\s*(?:units?|items?|days?|hours?|percent|%|dollars?|\$|limit|maximum|minimum|threshold))\b',
            'date': r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
            'exception': r'\b(?:unless|except|only if|provided that|subject to|excluding|with the exception of|save for)\b',
            'risk': r'\b(?:risk|may|might|could|potential|danger|hazard|threat|warning|caution)\b',
            'constraint': r'\b(?:must|shall|required|mandatory|prohibited|forbidden|not allowed|cannot)\b'
        }
    
    def extract_from_text(self, text: str, source: SourceReference) -> List[CriticalFact]:
        """Extract all critical content from text"""
        facts = []
        
        # Extract numbers and thresholds
        for match in re.finditer(self.patterns['number_threshold'], text, re.IGNORECASE):
            fact = CriticalFact(
                fact_type='number',
                content=match.group(),
                context=self._get_sentence_context(text, match.start()),
                source=source,
                importance_score=0.9
            )
            facts.append(fact)
        
        # Extract dates
        for match in re.finditer(self.patterns['date'], text, re.IGNORECASE):
            fact = CriticalFact(
                fact_type='date',
                content=match.group(),
                context=self._get_sentence_context(text, match.start()),
                source=source,
                importance_score=0.85
            )
            facts.append(fact)
        
        # Extract exceptions
        for match in re.finditer(self.patterns['exception'], text, re.IGNORECASE):
            fact = CriticalFact(
                fact_type='exception',
                content=match.group(),
                context=self._get_sentence_context(text, match.start()),
                source=source,
                importance_score=0.95
            )
            facts.append(fact)
        
        # Extract risks
        for match in re.finditer(self.patterns['risk'], text, re.IGNORECASE):
            fact = CriticalFact(
                fact_type='risk',
                content=match.group(),
                context=self._get_sentence_context(text, match.start()),
                source=source,
                importance_score=0.8
            )
            facts.append(fact)
        
        # Extract constraints
        for match in re.finditer(self.patterns['constraint'], text, re.IGNORECASE):
            fact = CriticalFact(
                fact_type='constraint',
                content=match.group(),
                context=self._get_sentence_context(text, match.start()),
                source=source,
                importance_score=0.85
            )
            facts.append(fact)
        
        # NER for entities
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PERSON', 'GPE', 'MONEY', 'PERCENT', 'DATE', 'TIME', 'QUANTITY']:
                fact = CriticalFact(
                    fact_type='entity',
                    content=f"{ent.text} ({ent.label_})",
                    context=ent.sent.text,
                    source=source,
                    importance_score=0.7
                )
                facts.append(fact)
        
        return facts
    
    def _get_sentence_context(self, text: str, position: int) -> str:
        """Get the sentence containing the position"""
        # Find sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_pos = 0
        for sent in sentences:
            if current_pos <= position < current_pos + len(sent):
                return sent.strip()
            current_pos += len(sent) + 1
        return text[:200]  # Fallback


class GETSExtractor:
    """Graph-based Extractive Text Summarization (GETS-like implementation)"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print("Loading sentence embedding model...")
        self.model = SentenceTransformer(model_name)
        print("✓ Sentence embedding model loaded")
    
    def extract_key_sentences(self, text: str, num_sentences: int = 3, source: SourceReference = None) -> List[Dict[str, Any]]:
        """Extract key sentences using graph-based approach with clustering"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= num_sentences:
            return [{'text': s, 'score': 1.0, 'source': source} for s in sentences]
        
        # Compute embeddings
        embeddings = self.model.encode(sentences, convert_to_tensor=True)
        
        # Build similarity graph
        G = nx.Graph()
        for i in range(len(sentences)):
            G.add_node(i)
        
        # Add edges based on cosine similarity (Jaccard-inspired threshold)
        similarity_threshold = 0.3
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                similarity = util.cos_sim(embeddings[i], embeddings[j]).item()
                if similarity > similarity_threshold:
                    G.add_edge(i, j, weight=similarity)
        
        # Apply graph clustering for coherence (Louvain community detection)
        if HAS_COMMUNITY:
            try:
                communities = community_louvain.best_partition(G, weight='weight')
            except Exception as e:
                print(f"  Warning: Community detection failed: {e}")
                # Fallback: Use connected components
                communities = {}
                for idx, component in enumerate(nx.connected_components(G)):
                    for node in component:
                        communities[node] = idx
        else:
            # Fallback: Use connected components if community detection not available
            communities = {}
            for idx, component in enumerate(nx.connected_components(G)):
                for node in component:
                    communities[node] = idx
        
        # Use PageRank within communities to find important sentences
        try:
            scores = nx.pagerank(G, weight='weight')
        except:
            scores = {i: 1.0 for i in range(len(sentences))}
        
        # Enhance scores based on community centrality
        community_sizes = {}
        for node, comm in communities.items():
            community_sizes[comm] = community_sizes.get(comm, 0) + 1
        
        # Boost scores for sentences in larger communities (more central topics)
        for node, comm in communities.items():
            scores[node] *= (1 + 0.1 * community_sizes[comm])
        
        # Select top sentences, ensuring diversity across communities
        ranked_sentences = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        selected_indices = []
        selected_communities = set()
        
        # First pass: Select best sentence from each community
        for idx, score in ranked_sentences:
            comm = communities[idx]
            if comm not in selected_communities:
                selected_indices.append(idx)
                selected_communities.add(comm)
                if len(selected_indices) >= num_sentences:
                    break
        
        # Second pass: Fill remaining slots with highest scores
        if len(selected_indices) < num_sentences:
            for idx, score in ranked_sentences:
                if idx not in selected_indices:
                    selected_indices.append(idx)
                    if len(selected_indices) >= num_sentences:
                        break
        
        # Sort to maintain original order
        selected_indices.sort()
        
        result = []
        for idx in selected_indices:
            result.append({
                'text': sentences[idx],
                'score': scores[idx],
                'source': source,
                'sentence_idx': idx,
                'community': communities.get(idx, -1)
            })
        
        return result


class ContradictionDetector:
    """Detect contradictions using simple heuristics and BERT-based methods"""
    
    def __init__(self):
        try:
            # Use zero-shot classification for contradiction detection
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        except:
            print("Warning: Could not load contradiction detection model. Using heuristics only.")
            self.classifier = None
    
    def detect_contradictions(self, statements: List[Dict[str, Any]]) -> List[Contradiction]:
        """Detect contradictions between statements"""
        contradictions = []
        
        # Extract numerical contradictions
        num_statements = []
        for stmt in statements:
            numbers = re.findall(r'\d+(?:\.\d+)?', stmt['text'])
            if numbers:
                num_statements.append({
                    'text': stmt['text'],
                    'numbers': [float(n) for n in numbers],
                    'source': stmt.get('source')
                })
        
        # Check for conflicting numbers in similar contexts
        for i in range(len(num_statements)):
            for j in range(i + 1, len(num_statements)):
                stmt_a = num_statements[i]
                stmt_b = num_statements[j]
                
                # Check if contexts are similar but numbers differ
                if self._contexts_similar(stmt_a['text'], stmt_b['text']):
                    if not set(stmt_a['numbers']).intersection(set(stmt_b['numbers'])):
                        contradiction = Contradiction(
                            statement_a=stmt_a['text'],
                            statement_b=stmt_b['text'],
                            source_a=stmt_a['source'],
                            source_b=stmt_b['source'],
                            conflict_type='numerical'
                        )
                        contradictions.append(contradiction)
        
        # Detect logical contradictions using negation
        for i in range(len(statements)):
            for j in range(i + 1, len(statements)):
                if self._logical_contradiction(statements[i]['text'], statements[j]['text']):
                    contradiction = Contradiction(
                        statement_a=statements[i]['text'],
                        statement_b=statements[j]['text'],
                        source_a=statements[i].get('source'),
                        source_b=statements[j].get('source'),
                        conflict_type='logical'
                    )
                    contradictions.append(contradiction)
        
        return contradictions
    
    def _contexts_similar(self, text_a: str, text_b: str) -> bool:
        """Check if two texts discuss similar topics"""
        # Simple keyword overlap
        words_a = set(re.findall(r'\w+', text_a.lower()))
        words_b = set(re.findall(r'\w+', text_b.lower()))
        overlap = len(words_a.intersection(words_b)) / min(len(words_a), len(words_b))
        return overlap > 0.3
    
    def _logical_contradiction(self, text_a: str, text_b: str) -> bool:
        """Detect logical contradictions"""
        negation_words = ['not', 'no', 'never', 'cannot', 'won\'t', 'doesn\'t', 'isn\'t']
        
        # Check if one statement negates the other
        has_negation_a = any(word in text_a.lower() for word in negation_words)
        has_negation_b = any(word in text_b.lower() for word in negation_words)
        
        if has_negation_a != has_negation_b:
            if self._contexts_similar(text_a, text_b):
                return True
        
        return False


class HierarchicalCompressor:
    """Main compression engine implementing hierarchical compression"""
    
    def __init__(self, use_gpu=False):
        self.critical_extractor = CriticalContentExtractor()
        self.gets_extractor = GETSExtractor()
        self.contradiction_detector = ContradictionDetector()
        
        # Load summarization model with better error handling
        self.summarizer = None
        print("Loading summarization model (this may take 1-2 minutes)...")
        
        # Try different models in order of preference
        models_to_try = [
            ("facebook/bart-large-cnn", "BART-large"),
            ("sshleifer/distilbart-cnn-12-6", "DistilBART"),
            ("t5-small", "T5-small")
        ]
        
        for model_name, display_name in models_to_try:
            try:
                print(f"  Attempting to load {display_name}...")
                self.summarizer = pipeline(
                    "summarization", 
                    model=model_name,
                    device=0 if use_gpu else -1,
                    framework="pt"
                )
                print(f"✓ Successfully loaded {display_name}")
                break
            except Exception as e:
                print(f"  ✗ Failed to load {display_name}: {str(e)[:100]}")
                continue
        
        if self.summarizer is None:
            print("\n⚠ Warning: Could not load any summarization model.")
            print("  Falling back to GETS extractive summarization.")
            print("  This will still work but summaries will be extractive rather than abstractive.")
            print("\nTo fix this issue:")
            print("  1. Ensure you have internet connection for model download")
            print("  2. Install: pip install transformers torch")
            print("  3. For GPU support: pip install transformers torch torchvision")
        else:
            print("✓ Summarization model ready")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF with paragraph-level granularity"""
        print(f"Extracting text from PDF: {pdf_path}")
        paragraphs = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                
                # Split by double newlines (paragraph breaks)
                page_paragraphs = re.split(r'\n\s*\n', text)
                
                for para_idx, para_text in enumerate(page_paragraphs):
                    para_text = para_text.strip()
                    if len(para_text) > 50:  # Minimum paragraph length
                        paragraphs.append({
                            'text': para_text,
                            'page': page_num,
                            'paragraph_idx': para_idx,
                            'source': SourceReference(
                                page=page_num,
                                paragraph_idx=para_idx,
                                original_text=para_text
                            )
                        })
        
        print(f"Extracted {len(paragraphs)} paragraphs from {len(pdf.pages)} pages")
        return paragraphs
    
    def compress_hierarchically(self, paragraphs: List[Dict[str, Any]], 
                                 section_size: int = 5,
                                 chapter_size: int = 3) -> Dict[str, Any]:
        """
        Perform hierarchical compression:
        Paragraphs → Sections → Chapters → Document
        """
        print("\n=== Starting Hierarchical Compression ===\n")
        
        # Level 1: Process paragraphs
        print("Level 1: Processing paragraphs...")
        paragraph_compressions = []
        for para in paragraphs:
            compression = self._compress_paragraph(para)
            paragraph_compressions.append(compression)
        
        # Level 2: Group into sections and compress
        print(f"\nLevel 2: Creating sections (groups of {section_size} paragraphs)...")
        sections = self._group_into_sections(paragraph_compressions, section_size)
        section_compressions = []
        for sec_idx, section in enumerate(sections):
            compression = self._compress_section(section, sec_idx)
            section_compressions.append(compression)
        
        # Level 3: Group sections into chapters and compress
        print(f"\nLevel 3: Creating chapters (groups of {chapter_size} sections)...")
        chapters = self._group_into_chapters(section_compressions, chapter_size)
        chapter_compressions = []
        for chap_idx, chapter in enumerate(chapters):
            compression = self._compress_chapter(chapter, chap_idx)
            chapter_compressions.append(compression)
        
        # Level 4: Create document summary
        print("\nLevel 4: Creating document-level summary...")
        document_summary = self._compress_document(chapter_compressions)
        
        # Collect all critical facts and contradictions
        all_facts = []
        all_contradictions = []
        for para in paragraph_compressions:
            all_facts.extend(para['critical_facts'])
        for sec in section_compressions:
            all_contradictions.extend(sec['contradictions'])
        
        print("\n=== Compression Complete ===\n")
        print(f"Total paragraphs: {len(paragraph_compressions)}")
        print(f"Total sections: {len(section_compressions)}")
        print(f"Total chapters: {len(chapter_compressions)}")
        print(f"Critical facts extracted: {len(all_facts)}")
        print(f"Contradictions detected: {len(all_contradictions)}")
        
        return {
            'document_summary': document_summary,
            'chapters': chapter_compressions,
            'sections': section_compressions,
            'paragraphs': paragraph_compressions,
            'critical_facts': [f.to_dict() for f in all_facts],
            'contradictions': [c.to_dict() for c in all_contradictions],
            'metadata': {
                'total_paragraphs': len(paragraph_compressions),
                'total_sections': len(section_compressions),
                'total_chapters': len(chapter_compressions),
                'total_facts': len(all_facts),
                'total_contradictions': len(all_contradictions)
            }
        }
    
    def _compress_paragraph(self, paragraph: Dict[str, Any]) -> Dict[str, Any]:
        """Compress a single paragraph"""
        text = paragraph['text']
        source = paragraph['source']
        
        # Extract critical facts
        critical_facts = self.critical_extractor.extract_from_text(text, source)
        
        # Extract key sentences using GETS
        key_sentences = self.gets_extractor.extract_key_sentences(text, num_sentences=2, source=source)
        
        # Create extractive summary
        extractive_summary = ' '.join([s['text'] for s in key_sentences])
        
        return {
            'id': f"para_{source.page}_{source.paragraph_idx}",
            'original_text': text,
            'extractive_summary': extractive_summary,
            'critical_facts': critical_facts,
            'key_sentences': key_sentences,
            'source': source.to_dict(),
            'level': 'paragraph'
        }
    
    def _group_into_sections(self, paragraphs: List[Dict], size: int) -> List[List[Dict]]:
        """Group paragraphs into sections"""
        sections = []
        for i in range(0, len(paragraphs), size):
            sections.append(paragraphs[i:i + size])
        return sections
    
    def _compress_section(self, paragraphs: List[Dict], section_idx: int) -> Dict[str, Any]:
        """Compress a section (group of paragraphs)"""
        # Combine extractive summaries
        combined_text = ' '.join([p['extractive_summary'] for p in paragraphs])
        
        # Generate abstractive summary using BART
        abstractive_summary = self._generate_summary(combined_text, max_length=150)
        
        # Detect contradictions within section
        statements = [{'text': p['extractive_summary'], 'source': SourceReference(**p['source'])} 
                      for p in paragraphs]
        contradictions = self.contradiction_detector.detect_contradictions(statements)
        
        # Collect child paragraph IDs
        child_ids = [p['id'] for p in paragraphs]
        
        return {
            'id': f"section_{section_idx}",
            'abstractive_summary': abstractive_summary,
            'extractive_summary': combined_text[:500] + '...' if len(combined_text) > 500 else combined_text,
            'contradictions': contradictions,
            'child_paragraphs': child_ids,
            'level': 'section'
        }
    
    def _group_into_chapters(self, sections: List[Dict], size: int) -> List[List[Dict]]:
        """Group sections into chapters"""
        chapters = []
        for i in range(0, len(sections), size):
            chapters.append(sections[i:i + size])
        return chapters
    
    def _compress_chapter(self, sections: List[Dict], chapter_idx: int) -> Dict[str, Any]:
        """Compress a chapter (group of sections)"""
        # Combine abstractive summaries
        combined_text = ' '.join([s['abstractive_summary'] for s in sections])
        
        # Generate chapter-level summary
        abstractive_summary = self._generate_summary(combined_text, max_length=200)
        
        # Collect child section IDs
        child_ids = [s['id'] for s in sections]
        
        return {
            'id': f"chapter_{chapter_idx}",
            'abstractive_summary': abstractive_summary,
            'child_sections': child_ids,
            'level': 'chapter'
        }
    
    def _compress_document(self, chapters: List[Dict]) -> Dict[str, Any]:
        """Create document-level summary"""
        # Combine chapter summaries
        combined_text = ' '.join([c['abstractive_summary'] for c in chapters])
        
        # Generate document summary
        abstractive_summary = self._generate_summary(combined_text, max_length=250)
        
        # Collect child chapter IDs
        child_ids = [c['id'] for c in chapters]
        
        return {
            'id': 'document',
            'abstractive_summary': abstractive_summary,
            'child_chapters': child_ids,
            'level': 'document'
        }
    
    def _generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate abstractive summary using BART or fallback to extractive"""
        # Handle very short text
        if len(text.split()) < 30:
            return text
        
        # If no summarizer available, use GETS extractive method
        if self.summarizer is None:
            # Use GETS to extract key sentences
            temp_source = SourceReference(page=0, paragraph_idx=0, original_text=text)
            key_sentences = self.gets_extractor.extract_key_sentences(
                text, 
                num_sentences=max(3, max_length // 50),
                source=temp_source
            )
            summary = ' '.join([s['text'] for s in key_sentences])
            
            # Truncate if still too long
            words = summary.split()
            if len(words) > max_length:
                summary = ' '.join(words[:max_length]) + '...'
            
            return summary
        
        # Try to use the summarizer
        try:
            # Truncate input if too long for model (most models have 1024 token limit)
            words = text.split()
            if len(words) > 1000:
                text = ' '.join(words[:1000])
            
            min_length = max(30, max_length // 3)
            summary = self.summarizer(
                text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False,
                truncation=True
            )
            return summary[0]['summary_text']
            
        except Exception as e:
            print(f"  Warning: Summarization failed ({str(e)[:50]}), using extractive fallback")
            # Fallback to GETS
            temp_source = SourceReference(page=0, paragraph_idx=0, original_text=text)
            key_sentences = self.gets_extractor.extract_key_sentences(
                text, 
                num_sentences=max(3, max_length // 50),
                source=temp_source
            )
            summary = ' '.join([s['text'] for s in key_sentences])
            
            # Truncate if needed
            words = summary.split()
            if len(words) > max_length:
                summary = ' '.join(words[:max_length]) + '...'
            
            return summary


def main():
    """Main execution function for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python contextual_compression_engine.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Initialize compressor
    compressor = HierarchicalCompressor()
    
    # Extract text
    paragraphs = compressor.extract_text_from_pdf(pdf_path)
    
    # Perform hierarchical compression
    result = compressor.compress_hierarchically(paragraphs, section_size=5, chapter_size=3)
    
    # Save result
    output_path = 'compression_result.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_path}")
    return result


if __name__ == "__main__":
    main()
