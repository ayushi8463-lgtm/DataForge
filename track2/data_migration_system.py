"""
AI-Powered Intelligent Data Migration System with Iterative Reverse Mapping
============================================================================
Features:
- Schema discovery and analysis
- AI-powered column mapping with similarity scoring
- Forward migration: Source → Target
- Reverse migration: Target → Source (derived)
- Iterative confidence refinement by comparing original vs derived source
- Comprehensive validation and explainability
"""

import sqlite3
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import json
import re
from difflib import SequenceMatcher
import warnings
warnings.filterwarnings('ignore')


class SchemaAnalyzer:
    """Analyzes database schemas and extracts metadata"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

    def get_schema_info(self) -> Dict[str, Any]:
        """Extract complete schema information"""
        cursor = self.conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}
        for table in tables:
            # Get column information
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    'name': col[1],
                    'type': col[2],
                    'nullable': not col[3],
                    'primary_key': bool(col[5])
                })

            # Get sample data
            cursor.execute(f"SELECT * FROM {table} LIMIT 10")
            sample_data = cursor.fetchall()

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            schema[table] = {
                'columns': columns,
                'sample_data': sample_data,
                'row_count': row_count
            }

        return schema

    def get_full_table_data(self, table: str, limit: int = None) -> List[Tuple]:
        """Get full table data for comparison"""
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table}"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        return cursor.fetchall()

    def get_column_names(self, table: str) -> List[str]:
        """Get column names for a table"""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        return [col[1] for col in cursor.fetchall()]

    def close(self):
        self.conn.close()


class AIColumnMapper:
    """AI-powered intelligent column mapping with explainability"""

    def __init__(self):
        self.mapping_explanations = []

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def semantic_similarity(self, col1: str, col2: str) -> Tuple[float, str]:
        """Calculate semantic similarity with explanation"""
        # Convert to lowercase
        col1_lower = col1.lower()
        col2_lower = col2.lower()

        # Extract keywords
        keywords1 = set(re.split(r'[_\s]+', col1_lower))
        keywords2 = set(re.split(r'[_\s]+', col2_lower))

        # Synonym mapping
        synonyms = {
            'customer': ['client', 'cust', 'buyer'],
            'order': ['purchase', 'transaction', 'sale'],
            'product': ['item', 'goods'],
            'email': ['mail', 'e-mail'],
            'phone': ['telephone', 'tel', 'contact'],
            'date': ['timestamp', 'time', 'datetime'],
            'id': ['identifier', 'key'],
            'name': ['title', 'label'],
            'amount': ['total', 'cost', 'price', 'sum'],
            'status': ['state', 'condition'],
            'quantity': ['qty', 'count'],
        }

        # Expand keywords with synonyms
        expanded1 = keywords1.copy()
        expanded2 = keywords2.copy()

        for word in keywords1:
            for key, syns in synonyms.items():
                if word == key or word in syns:
                    expanded1.update([key] + syns)

        for word in keywords2:
            for key, syns in synonyms.items():
                if word == key or word in syns:
                    expanded2.update([key] + syns)

        # Calculate overlap
        common = keywords1 & keywords2
        common_semantic = expanded1 & expanded2

        if common:
            score = 0.9
            explanation = f"Exact match: common keywords {common}"
        elif common_semantic:
            score = 0.75
            explanation = f"Semantic match: common keywords {common_semantic}"
        else:
            # Use string similarity as fallback
            score = self.calculate_similarity(col1, col2)
            if score > 0.6:
                explanation = f"String similarity: {score:.2%}"
            else:
                explanation = "Low similarity"

        return score, explanation

    def type_compatibility(self, type1: str, type2: str) -> Tuple[float, str]:
        """Check if types are compatible with explanation"""
        type1 = type1.upper()
        type2 = type2.upper()

        if type1 == type2:
            return 1.0, "Identical types"

        # Text types
        text_types = ['TEXT', 'VARCHAR', 'CHAR', 'STRING']
        if any(t in type1 for t in text_types) and any(t in type2 for t in text_types):
            return 0.95, "Compatible text types"

        # Numeric types
        if 'INT' in type1 and 'INT' in type2:
            return 0.95, "Compatible integer types"

        if 'REAL' in type1 and 'REAL' in type2:
            return 0.95, "Compatible real/float types"

        # Integer to Real (safe)
        if 'INT' in type1 and 'REAL' in type2:
            return 0.85, "Safe conversion: INTEGER → REAL"

        # Real to Integer (data loss)
        if 'REAL' in type1 and 'INT' in type2:
            return 0.6, "Lossy conversion: REAL → INTEGER (precision loss)"

        # Date/Time types
        date_types = ['DATE', 'TIMESTAMP', 'DATETIME']
        if any(t in type1 for t in date_types) and any(t in type2 for t in date_types):
            if 'TIMESTAMP' in type1 and 'DATE' in type2:
                return 0.7, "Lossy conversion: TIMESTAMP → DATE (time lost)"
            if 'DATE' in type1 and 'TIMESTAMP' in type2:
                return 0.85, "Safe conversion: DATE → TIMESTAMP"
            return 0.9, "Compatible date/time types"

        # Any to Text (always possible)
        if any(t in type2 for t in text_types):
            return 0.5, f"Generic conversion: {type1} → TEXT"

        return 0.3, f"Incompatible types: {type1} ↔ {type2}"

    def data_pattern_similarity(self, sample_data1: List, sample_data2: List) -> Tuple[float, str]:
        """Compare data patterns"""
        if not sample_data1 or not sample_data2:
            return 0.5, "Insufficient sample data"

        pattern_score = 0.0
        explanations = []

        # Check for email patterns
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        has_email1 = any(re.search(email_pattern, str(val)) for val in sample_data1 if val)
        has_email2 = any(re.search(email_pattern, str(val)) for val in sample_data2 if val)

        if has_email1 and has_email2:
            pattern_score += 0.4
            explanations.append("Both contain email patterns")

        # Check for phone patterns
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        has_phone1 = any(re.search(phone_pattern, str(val)) for val in sample_data1 if val)
        has_phone2 = any(re.search(phone_pattern, str(val)) for val in sample_data2 if val)

        if has_phone1 and has_phone2:
            pattern_score += 0.4
            explanations.append("Both contain phone patterns")

        # Check for date patterns
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        has_date1 = any(re.search(date_pattern, str(val)) for val in sample_data1 if val)
        has_date2 = any(re.search(date_pattern, str(val)) for val in sample_data2 if val)

        if has_date1 and has_date2:
            pattern_score += 0.3
            explanations.append("Both contain date patterns")

        if pattern_score > 0:
            return min(pattern_score, 1.0), "; ".join(explanations)

        return 0.5, "No specific patterns detected"

    def map_columns(self,
                   source_schema: Dict[str, Any],
                   target_schema: Dict[str, Any],
                   confidence_threshold: float = 0.3) -> Dict[str, Any]:
        """
        Generate intelligent column mappings with confidence scores and explanations
        """
        mappings = {}

        for src_table, src_info in source_schema.items():
            # Find best matching target table
            target_table = self._find_matching_table(src_table, target_schema)

            if not target_table:
                continue

            tgt_info = target_schema[target_table]
            table_mappings = []

            for src_col in src_info['columns']:
                src_col_name = src_col['name']
                best_match = None
                best_score = 0.0
                best_explanation = {}

                for tgt_col in tgt_info['columns']:
                    tgt_col_name = tgt_col['name']

                    # Calculate multiple similarity metrics
                    name_sim, name_exp = self.semantic_similarity(src_col_name, tgt_col_name)
                    type_sim, type_exp = self.type_compatibility(src_col['type'], tgt_col['type'])

                    # Get sample data for pattern matching
                    src_col_idx = next(i for i, c in enumerate(src_info['columns']) if c['name'] == src_col_name)
                    tgt_col_idx = next(i for i, c in enumerate(tgt_info['columns']) if c['name'] == tgt_col_name)

                    src_samples = [row[src_col_idx] for row in src_info['sample_data'] if len(row) > src_col_idx]
                    tgt_samples = [row[tgt_col_idx] for row in tgt_info['sample_data'] if len(row) > tgt_col_idx]

                    pattern_sim, pattern_exp = self.data_pattern_similarity(src_samples, tgt_samples)

                    # Weighted score
                    total_score = (name_sim * 0.5 + type_sim * 0.3 + pattern_sim * 0.2)

                    if total_score > best_score:
                        best_score = total_score
                        best_match = tgt_col_name
                        best_explanation = {
                            'name_similarity': name_sim,
                            'name_explanation': name_exp,
                            'type_compatibility': type_sim,
                            'type_explanation': type_exp,
                            'pattern_similarity': pattern_sim,
                            'pattern_explanation': pattern_exp,
                            'total_score': total_score
                        }

                if best_score > confidence_threshold:  # Threshold for considering a match
                    table_mappings.append({
                        'source_column': src_col_name,
                        'target_column': best_match,
                        'confidence': best_score,
                        'source_type': src_col['type'],
                        'target_type': next(c['type'] for c in tgt_info['columns']
                                          if c['name'] == best_match),
                        'explanation': best_explanation,
                        'transformation_required': src_col['type'] != next(
                            c['type'] for c in tgt_info['columns'] if c['name'] == best_match
                        )
                    })

            mappings[f"{src_table}→{target_table}"] = table_mappings

        return mappings

    def _find_matching_table(self, src_table: str, target_schema: Dict) -> Optional[str]:
        """Find best matching table in target schema"""
        best_match = None
        best_score = 0.0

        for tgt_table in target_schema.keys():
            score = self.calculate_similarity(src_table, tgt_table)
            if score > best_score:
                best_score = score
                best_match = tgt_table

        return best_match if best_score > 0.4 else None


class DataTransformer:
    """Handles data transformations during migration"""

    def __init__(self):
        self.transformations_applied = []

    def transform_value(self, value: Any, source_type: str, target_type: str) -> Tuple[Any, str]:
        """Transform a value from source type to target type with explanation"""

        if value is None:
            return None, "NULL value preserved"

        source_type = source_type.upper()
        target_type = target_type.upper()

        # No transformation needed
        if source_type == target_type:
            return value, "No transformation (same type)"

        try:
            # INTEGER/REAL conversions
            if 'INT' in target_type and 'REAL' in source_type:
                return int(float(value)), "Converted REAL to INTEGER (precision loss)"

            if 'REAL' in target_type and 'INT' in source_type:
                return float(value), "Converted INTEGER to REAL"

            # To TEXT conversions
            if 'TEXT' in target_type or 'VARCHAR' in target_type:
                return str(value), f"Converted {source_type} to TEXT"

            # DATE/TIMESTAMP conversions
            if 'DATE' in target_type or 'TIMESTAMP' in target_type:
                if isinstance(value, str):
                    # Try to parse date
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y']:
                        try:
                            parsed = datetime.strptime(value, fmt)
                            if 'DATE' in target_type and 'TIME' not in target_type:
                                return parsed.strftime('%Y-%m-%d'), "Converted to DATE (time removed)"
                            return parsed.strftime('%Y-%m-%d %H:%M:%S'), "Converted to TIMESTAMP"
                        except:
                            continue

            # Default: convert to string
            return str(value), f"Default conversion to TEXT"

        except Exception as e:
            return value, f"Transformation failed: {str(e)}, kept original"


class IterativeReverseMapper:
    """
    Performs iterative reverse mapping by:
    1. Migrating Source → Target (forward)
    2. Migrating Target → Source_derived (reverse)
    3. Comparing Source_original vs Source_derived
    4. Identifying 100% confidence mappings
    5. Re-attempting mapping for low-confidence fields
    """

    def __init__(self, source_db: str, target_db: str, sample_size: int = 50):
        self.source_db = source_db
        self.target_db = target_db
        self.sample_size = sample_size
        self.mapper = AIColumnMapper()
        self.transformer = DataTransformer()

    def perform_iterative_mapping(self) -> Dict[str, Any]:
        """
        Main method to perform iterative reverse mapping
        """
        print("\n" + "="*80)
        print("ITERATIVE REVERSE MAPPING - ROUND-TRIP VALIDATION")
        print("="*80)

        # Step 1: Analyze schemas
        print("\n📊 Step 1: Analyzing schemas...")
        src_analyzer = SchemaAnalyzer(self.source_db)
        tgt_analyzer = SchemaAnalyzer(self.target_db)

        source_schema = src_analyzer.get_schema_info()
        target_schema = tgt_analyzer.get_schema_info()

        # Step 2: Generate forward mappings
        print("📊 Step 2: Generating initial forward mappings...")
        forward_mappings = self.mapper.map_columns(source_schema, target_schema)

        # Step 3: Perform forward migration on sample
        print("📊 Step 3: Performing forward migration on sample...")
        forward_data = self._migrate_sample(
            src_analyzer,
            forward_mappings,
            'forward'
        )

        # Step 4: Generate reverse mappings
        print("📊 Step 4: Generating reverse mappings...")
        reverse_mappings = self.mapper.map_columns(target_schema, source_schema)

        # Step 5: Perform reverse migration
        print("📊 Step 5: Performing reverse migration...")
        reverse_data = self._migrate_reverse(
            tgt_analyzer,
            reverse_mappings,
            forward_data
        )

        # Step 6: Compare original vs derived
        print("📊 Step 6: Comparing original source vs derived source...")
        comparison_results = self._compare_original_vs_derived(
            src_analyzer,
            reverse_data,
            source_schema
        )

        # Step 7: Refine mappings based on comparison
        print("📊 Step 7: Refining mappings based on comparison...")
        refined_results = self._refine_mappings(
            comparison_results,
            forward_mappings,
            reverse_mappings,
            source_schema,
            target_schema
        )

        src_analyzer.close()
        tgt_analyzer.close()

        return {
            'forward_mappings': forward_mappings,
            'reverse_mappings': reverse_mappings,
            'comparison_results': comparison_results,
            'refined_mappings': refined_results,
            'summary': self._generate_summary(comparison_results, refined_results)
        }

    def _migrate_sample(self, analyzer: SchemaAnalyzer, mappings: Dict, direction: str) -> Dict:
        """Migrate sample data"""
        migrated_data = {}

        for table_pair, column_mappings in mappings.items():
            src_table, tgt_table = table_pair.split('→')

            # Get sample data
            sample_data = analyzer.get_full_table_data(src_table, self.sample_size)
            src_columns = analyzer.get_column_names(src_table)

            # Migrate each row
            migrated_rows = []
            for row in sample_data:
                migrated_row = {}

                for mapping in column_mappings:
                    src_col = mapping['source_column']
                    tgt_col = mapping['target_column']

                    # Get source value
                    src_idx = src_columns.index(src_col)
                    src_value = row[src_idx] if src_idx < len(row) else None

                    # Transform value
                    transformed_value, _ = self.transformer.transform_value(
                        src_value,
                        mapping['source_type'],
                        mapping['target_type']
                    )

                    migrated_row[tgt_col] = transformed_value

                migrated_rows.append(migrated_row)

            migrated_data[tgt_table] = {
                'rows': migrated_rows,
                'column_mappings': column_mappings
            }

        return migrated_data

    def _migrate_reverse(self, tgt_analyzer: SchemaAnalyzer,
                        reverse_mappings: Dict,
                        forward_data: Dict) -> Dict:
        """Migrate data in reverse using forward migrated data"""
        reverse_data = {}

        for table_pair, column_mappings in reverse_mappings.items():
            tgt_table, src_table = table_pair.split('→')

            if tgt_table not in forward_data:
                continue

            # Get forward migrated data
            forward_rows = forward_data[tgt_table]['rows']

            # Reverse migrate each row
            reverse_rows = []
            for row_dict in forward_rows:
                reverse_row = {}

                for mapping in column_mappings:
                    src_col = mapping['source_column']  # from target
                    tgt_col = mapping['target_column']  # to source

                    # Get value from forward migrated data
                    src_value = row_dict.get(src_col)

                    # Transform back
                    transformed_value, _ = self.transformer.transform_value(
                        src_value,
                        mapping['source_type'],
                        mapping['target_type']
                    )

                    reverse_row[tgt_col] = transformed_value

                reverse_rows.append(reverse_row)

            reverse_data[src_table] = {
                'rows': reverse_rows,
                'column_mappings': column_mappings
            }

        return reverse_data

    def _compare_original_vs_derived(self, src_analyzer: SchemaAnalyzer,
                                    reverse_data: Dict,
                                    source_schema: Dict) -> Dict:
        """Compare original source with derived source after round-trip"""
        comparison_results = {}

        for table_name, table_info in source_schema.items():
            if table_name not in reverse_data:
                continue

            # Get original data
            original_data = src_analyzer.get_full_table_data(table_name, self.sample_size)
            original_columns = src_analyzer.get_column_names(table_name)

            # Get derived data
            derived_rows = reverse_data[table_name]['rows']

            # Compare column by column
            column_comparisons = {}

            for col_info in table_info['columns']:
                col_name = col_info['name']
                col_idx = original_columns.index(col_name)

                # Check if column exists in derived data
                if not derived_rows or col_name not in derived_rows[0]:
                    column_comparisons[col_name] = {
                        'status': 'NOT_MAPPED',
                        'confidence': 0.0,
                        'match_percentage': 0.0,
                        'reason': 'Column not present in derived data'
                    }
                    continue

                # Compare values
                matches = 0
                total = min(len(original_data), len(derived_rows))

                for i in range(total):
                    original_val = original_data[i][col_idx]
                    derived_val = derived_rows[i].get(col_name)

                    # Normalize for comparison
                    if self._values_match(original_val, derived_val):
                        matches += 1

                match_percentage = (matches / total * 100) if total > 0 else 0

                # Determine status
                if match_percentage == 100.0:
                    status = 'PERFECT_MATCH'
                    confidence = 1.0
                    reason = '100% match - Perfect round-trip'
                elif match_percentage >= 95.0:
                    status = 'NEAR_PERFECT'
                    confidence = 0.95
                    reason = f'{match_percentage:.1f}% match - Minor discrepancies'
                elif match_percentage >= 70.0:
                    status = 'ACCEPTABLE'
                    confidence = 0.7
                    reason = f'{match_percentage:.1f}% match - Acceptable data loss'
                else:
                    status = 'DATA_LOSS'
                    confidence = match_percentage / 100.0
                    reason = f'{match_percentage:.1f}% match - Significant data loss'

                column_comparisons[col_name] = {
                    'status': status,
                    'confidence': confidence,
                    'match_percentage': match_percentage,
                    'matches': matches,
                    'total': total,
                    'reason': reason
                }

            comparison_results[table_name] = {
                'column_comparisons': column_comparisons,
                'overall_confidence': np.mean([c['confidence'] for c in column_comparisons.values()])
            }

        return comparison_results

    def _values_match(self, val1: Any, val2: Any) -> bool:
        """Check if two values match (with normalization)"""
        # Handle None/NULL
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False

        # Normalize strings
        if isinstance(val1, str) and isinstance(val2, str):
            return val1.strip().lower() == val2.strip().lower()

        # Numeric comparison with tolerance
        try:
            num1 = float(val1)
            num2 = float(val2)
            return abs(num1 - num2) < 0.01
        except:
            pass

        # Direct comparison
        return str(val1) == str(val2)

    def _refine_mappings(self, comparison_results: Dict,
                        forward_mappings: Dict,
                        reverse_mappings: Dict,
                        source_schema: Dict,
                        target_schema: Dict) -> Dict:
        """
        Refine mappings based on comparison results
        - Keep 100% confidence mappings
        - Re-attempt mapping for low confidence fields using available columns
        """
        refined_mappings = {}

        for table_name, comparison in comparison_results.items():
            # Identify columns by confidence level
            perfect_columns = []
            low_confidence_columns = []
            unmapped_columns = []

            for col_name, col_comparison in comparison['column_comparisons'].items():
                if col_comparison['status'] == 'PERFECT_MATCH':
                    perfect_columns.append(col_name)
                elif col_comparison['status'] in ['NOT_MAPPED', 'DATA_LOSS']:
                    low_confidence_columns.append(col_name)
                    if col_comparison['status'] == 'NOT_MAPPED':
                        unmapped_columns.append(col_name)

            # Get available unmapped columns from target
            # Find the corresponding target table
            corresponding_forward_key = None
            for key in forward_mappings.keys():
                if key.startswith(table_name + '→'):
                    corresponding_forward_key = key
                    break

            if not corresponding_forward_key:
                continue

            target_table = corresponding_forward_key.split('→')[1]

            # Get columns that are not yet mapped with 100% confidence
            mapped_target_cols = set()
            for mapping in forward_mappings[corresponding_forward_key]:
                # Find corresponding source col
                src_col = mapping['source_column']
                if comparison['column_comparisons'].get(src_col, {}).get('status') == 'PERFECT_MATCH':
                    mapped_target_cols.add(mapping['target_column'])

            available_target_cols = []
            for col in target_schema[target_table]['columns']:
                if col['name'] not in mapped_target_cols:
                    available_target_cols.append(col)

            # Re-attempt mapping for low confidence columns
            refined_column_mappings = []

            # Add perfect matches
            for col_name in perfect_columns:
                # Find original mapping
                for mapping in forward_mappings[corresponding_forward_key]:
                    if mapping['source_column'] == col_name:
                        refined_mapping = mapping.copy()
                        refined_mapping['refined_confidence'] = 1.0
                        refined_mapping['refinement_reason'] = '100% round-trip match - Confirmed'
                        refined_column_mappings.append(refined_mapping)
                        break

            # Re-attempt low confidence columns
            for col_name in low_confidence_columns:
                src_col_info = next((c for c in source_schema[table_name]['columns']
                                   if c['name'] == col_name), None)

                if not src_col_info or not available_target_cols:
                    # Keep original mapping but mark as low confidence
                    for mapping in forward_mappings[corresponding_forward_key]:
                        if mapping['source_column'] == col_name:
                            refined_mapping = mapping.copy()
                            refined_mapping['refined_confidence'] = comparison['column_comparisons'][col_name]['confidence']
                            refined_mapping['refinement_reason'] = comparison['column_comparisons'][col_name]['reason']
                            refined_column_mappings.append(refined_mapping)
                            break
                    continue

                # Try to find better match from available columns
                best_match = None
                best_score = 0.0

                for tgt_col in available_target_cols:
                    name_sim, _ = self.mapper.semantic_similarity(col_name, tgt_col['name'])
                    type_sim, _ = self.mapper.type_compatibility(src_col_info['type'], tgt_col['type'])

                    score = (name_sim * 0.6 + type_sim * 0.4)

                    if score > best_score and score > 0.4:
                        best_score = score
                        best_match = tgt_col

                if best_match:
                    refined_column_mappings.append({
                        'source_column': col_name,
                        'target_column': best_match['name'],
                        'confidence': best_score,
                        'refined_confidence': best_score,
                        'source_type': src_col_info['type'],
                        'target_type': best_match['type'],
                        'refinement_reason': f'Re-mapped after round-trip validation (original had {comparison["column_comparisons"][col_name]["match_percentage"]:.1f}% match)',
                        'transformation_required': src_col_info['type'] != best_match['type']
                    })
                else:
                    # No better match found - discard or keep original with warning
                    refined_column_mappings.append({
                        'source_column': col_name,
                        'target_column': None,
                        'confidence': 0.0,
                        'refined_confidence': 0.0,
                        'source_type': src_col_info['type'],
                        'target_type': None,
                        'refinement_reason': f'Discarded - No suitable mapping found (original had {comparison["column_comparisons"][col_name]["match_percentage"]:.1f}% match)',
                        'transformation_required': False
                    })

            refined_mappings[corresponding_forward_key] = refined_column_mappings

        return refined_mappings

    def _generate_summary(self, comparison_results: Dict, refined_results: Dict) -> Dict:
        """Generate summary of iterative mapping process"""
        total_columns = 0
        perfect_matches = 0
        improved_mappings = 0
        discarded_mappings = 0

        for table_name, comparison in comparison_results.items():
            for col_name, col_comp in comparison['column_comparisons'].items():
                total_columns += 1
                if col_comp['status'] == 'PERFECT_MATCH':
                    perfect_matches += 1

        for table_pair, mappings in refined_results.items():
            for mapping in mappings:
                if 'Re-mapped' in mapping.get('refinement_reason', ''):
                    improved_mappings += 1
                if mapping.get('target_column') is None:
                    discarded_mappings += 1

        return {
            'total_columns_analyzed': total_columns,
            'perfect_round_trip_matches': perfect_matches,
            'perfect_match_percentage': (perfect_matches / total_columns * 100) if total_columns > 0 else 0,
            'improved_mappings': improved_mappings,
            'discarded_mappings': discarded_mappings,
            'overall_confidence': (perfect_matches / total_columns) if total_columns > 0 else 0
        }


def run_iterative_migration(source_db: str, target_db: str, sample_size: int = 50) -> Dict:
    """
    Main function to run the iterative migration process
    """
    mapper = IterativeReverseMapper(source_db, target_db, sample_size)
    results = mapper.perform_iterative_mapping()

    # Print summary
    print("\n" + "="*80)
    print("ITERATIVE MAPPING SUMMARY")
    print("="*80)
    summary = results['summary']
    print(f"\nTotal Columns Analyzed: {summary['total_columns_analyzed']}")
    print(f"Perfect Round-Trip Matches: {summary['perfect_round_trip_matches']} ({summary['perfect_match_percentage']:.1f}%)")
    print(f"Improved Mappings: {summary['improved_mappings']}")
    print(f"Discarded Mappings: {summary['discarded_mappings']}")
    print(f"Overall Confidence: {summary['overall_confidence']:.2%}")

    return results


if __name__ == "__main__":
    # Example usage
    source_db = "outputs/source_database.db"
    target_db = "outputs/target_database.db"

    results = run_iterative_migration(source_db, target_db, sample_size=50)

    # Save results
    with open('outputs/iterative_mapping_results.json', 'w') as f:
        # Convert numpy types to native Python for JSON serialization
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            else:
                return obj

        json.dump(convert_types(results), f, indent=2)

    print("\n✅ Results saved to iterative_mapping_results.json")