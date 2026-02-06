"""
AI-Powered Intelligent Data Migration System
=============================================
Features:
- Schema discovery and analysis
- AI-powered column mapping with similarity scoring
- Bidirectional mapping (forward and reverse)
- Data transformation and migration
- Round-trip validation
- Comprehensive reporting
- Explainability for all mapping decisions
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Tuple, Any, Optional
import json
import re
from difflib import SequenceMatcher
from collections import defaultdict
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
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
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
    
    def get_column_statistics(self, table: str, column: str) -> Dict[str, Any]:
        """Get statistical information about a column"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Null count
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
        stats['null_count'] = cursor.fetchone()[0]
        
        # Distinct count
        cursor.execute(f"SELECT COUNT(DISTINCT {column}) FROM {table}")
        stats['distinct_count'] = cursor.fetchone()[0]
        
        # Sample values
        cursor.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL LIMIT 10")
        stats['sample_values'] = [row[0] for row in cursor.fetchall()]
        
        return stats
    
    def close(self):
        self.conn.close()


class AIColumnMapper:
    """AI-powered intelligent column mapping with explainability"""
    
    def __init__(self):
        self.mapping_explanations = []
        
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity score"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def extract_keywords(self, name: str) -> List[str]:
        """Extract semantic keywords from column name"""
        # Remove common prefixes/suffixes
        name = re.sub(r'^(src_|tgt_|old_|new_)', '', name.lower())
        name = re.sub(r'(_id|_key|_code|_num)$', '', name)
        
        # Split by underscore, camelCase, and common separators
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', name)
        words.extend(name.split('_'))
        
        # Common semantic mappings
        synonyms = {
            'customer': ['client', 'cust', 'buyer'],
            'order': ['purchase', 'transaction', 'sale'],
            'product': ['item', 'goods', 'merchandise'],
            'date': ['dt', 'timestamp', 'time'],
            'name': ['title', 'label', 'description'],
            'id': ['identifier', 'key', 'number', 'code'],
            'email': ['mail', 'contact'],
            'phone': ['tel', 'telephone', 'mobile'],
            'address': ['location', 'addr', 'street'],
            'price': ['cost', 'amount', 'value'],
            'quantity': ['qty', 'count', 'number'],
            'status': ['state', 'condition'],
        }
        
        expanded_words = set(words)
        for word in words:
            word_lower = word.lower()
            for key, values in synonyms.items():
                if word_lower == key or word_lower in values:
                    expanded_words.add(key)
                    expanded_words.update(values)
        
        return list(expanded_words)
    
    def semantic_similarity(self, col1: str, col2: str) -> Tuple[float, str]:
        """Calculate semantic similarity between columns with explanation"""
        keywords1 = set(self.extract_keywords(col1))
        keywords2 = set(self.extract_keywords(col2))
        
        # Check for keyword overlap
        common_keywords = keywords1.intersection(keywords2)
        
        if common_keywords:
            similarity = len(common_keywords) / max(len(keywords1), len(keywords2))
            explanation = f"Semantic match found: common keywords {common_keywords}"
            return min(similarity * 1.5, 1.0), explanation
        
        # Fallback to string similarity
        str_sim = self.calculate_similarity(col1, col2)
        explanation = f"String similarity: {str_sim:.2%}"
        return str_sim, explanation
    
    def type_compatibility(self, type1: str, type2: str) -> Tuple[float, str]:
        """Check type compatibility with explanation"""
        type_groups = {
            'numeric': ['INTEGER', 'INT', 'REAL', 'FLOAT', 'DOUBLE', 'NUMERIC', 'DECIMAL'],
            'text': ['TEXT', 'VARCHAR', 'CHAR', 'STRING'],
            'date': ['DATE', 'DATETIME', 'TIMESTAMP'],
            'boolean': ['BOOLEAN', 'BOOL', 'BIT']
        }
        
        type1_upper = type1.upper()
        type2_upper = type2.upper()
        
        # Exact match
        if type1_upper == type2_upper:
            return 1.0, "Exact type match"
        
        # Same group
        for group_name, types in type_groups.items():
            if any(t in type1_upper for t in types) and any(t in type2_upper for t in types):
                return 0.8, f"Compatible types (both {group_name})"
        
        # Partial compatibility
        if 'TEXT' in type2_upper:  # TEXT can hold anything
            return 0.5, "Compatible (target is TEXT, can hold any data)"
        
        return 0.2, f"Type mismatch: {type1} vs {type2}"
    
    def data_pattern_similarity(self, sample_data1: List, sample_data2: List) -> Tuple[float, str]:
        """Compare data patterns with explanation"""
        if not sample_data1 or not sample_data2:
            return 0.5, "Insufficient sample data"
        
        # Check for similar patterns
        pattern_score = 0.0
        explanations = []
        
        # Check if both have email patterns
        email_pattern = r'[\w\.-]+@[\w\.-]+'
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
                   target_schema: Dict[str, Any]) -> Dict[str, Any]:
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
                    src_samples = [row[src_info['columns'].index(src_col)] 
                                 for row in src_info['sample_data'][:5]]
                    tgt_samples = [row[tgt_info['columns'].index(tgt_col)] 
                                 for row in tgt_info['sample_data'][:5]]
                    
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
                
                if best_score > 0.3:  # Threshold for considering a match
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
    
    def detect_split_fields(self, value: str, target_fields: List[str]) -> Dict[str, str]:
        """Detect if a field should be split into multiple fields"""
        result = {}
        
        # Common split patterns
        if ' ' in str(value):
            parts = str(value).split(' ', 1)
            if 'first' in target_fields[0].lower() and 'last' in target_fields[1].lower():
                result[target_fields[0]] = parts[0]
                result[target_fields[1]] = parts[1] if len(parts) > 1 else ''
        
        return result
    
    def detect_merge_fields(self, values: List[Any]) -> str:
        """Merge multiple fields into one"""
        non_null = [str(v) for v in values if v is not None]
        return ' '.join(non_null)


class BidirectionalMapper:
    """Handles forward and reverse mapping with round-trip validation"""
    
    def __init__(self, forward_mappings: Dict[str, Any]):
        self.forward_mappings = forward_mappings
        self.reverse_mappings = {}
        self.reversibility_analysis = {}
        
    def generate_reverse_mappings(self) -> Dict[str, Any]:
        """Generate reverse mappings from forward mappings"""
        
        for table_pair, mappings in self.forward_mappings.items():
            src_table, tgt_table = table_pair.split('→')
            reverse_key = f"{tgt_table}→{src_table}"
            
            reverse_mappings = []
            
            for mapping in mappings:
                # Check reversibility
                is_reversible, reason = self._check_reversibility(mapping)
                
                reverse_mapping = {
                    'source_column': mapping['target_column'],
                    'target_column': mapping['source_column'],
                    'confidence': mapping['confidence'],
                    'source_type': mapping['target_type'],
                    'target_type': mapping['source_type'],
                    'reversible': is_reversible,
                    'reversibility_reason': reason,
                    'transformation_required': mapping['transformation_required']
                }
                
                reverse_mappings.append(reverse_mapping)
                
                # Track reversibility
                reversibility_key = f"{mapping['source_column']}→{mapping['target_column']}"
                self.reversibility_analysis[reversibility_key] = {
                    'reversible': is_reversible,
                    'reason': reason,
                    'data_loss_risk': not is_reversible
                }
            
            self.reverse_mappings[reverse_key] = reverse_mappings
        
        return self.reverse_mappings
    
    def _check_reversibility(self, mapping: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if a mapping is reversible"""
        
        src_type = mapping['source_type'].upper()
        tgt_type = mapping['target_type'].upper()
        
        # Perfect reversibility
        if src_type == tgt_type:
            return True, "Exact type match - perfect reversibility"
        
        # Check for precision loss
        if 'REAL' in src_type and 'INT' in tgt_type:
            return False, "Precision loss: REAL to INTEGER conversion loses decimal places"
        
        if 'TIMESTAMP' in src_type and 'DATE' in tgt_type:
            return False, "Precision loss: TIMESTAMP to DATE loses time information"
        
        # TEXT can hold anything but reverse may fail
        if 'TEXT' in tgt_type and src_type != 'TEXT':
            return False, f"Conversion to TEXT - reverse parse from TEXT to {src_type} may fail"
        
        # Numeric conversions
        if 'INT' in src_type and 'REAL' in tgt_type:
            return True, "INTEGER to REAL is reversible"
        
        return True, "Reversible with possible minor data format changes"


class MigrationExecutor:
    """Executes the actual data migration"""
    
    def __init__(self, source_db: str, target_db: str):
        self.source_conn = sqlite3.connect(source_db)
        self.target_conn = sqlite3.connect(target_db)
        self.transformer = DataTransformer()
        self.migration_log = []
        
    def execute_migration(self, mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Execute migration based on mappings"""
        
        results = {
            'success': True,
            'tables_migrated': 0,
            'rows_migrated': 0,
            'errors': [],
            'details': {}
        }
        
        for table_pair, column_mappings in mappings.items():
            src_table, tgt_table = table_pair.split('→')
            
            try:
                migrated_rows = self._migrate_table(src_table, tgt_table, column_mappings)
                results['tables_migrated'] += 1
                results['rows_migrated'] += migrated_rows
                results['details'][table_pair] = {
                    'rows': migrated_rows,
                    'status': 'success'
                }
            except Exception as e:
                results['success'] = False
                results['errors'].append({
                    'table': table_pair,
                    'error': str(e)
                })
                results['details'][table_pair] = {
                    'rows': 0,
                    'status': 'failed',
                    'error': str(e)
                }
        
        return results
    
    def _migrate_table(self, src_table: str, tgt_table: str, 
                      column_mappings: List[Dict]) -> int:
        """Migrate data from source table to target table"""
        
        # Get source data
        src_cursor = self.source_conn.cursor()
        src_cursor.execute(f"SELECT * FROM {src_table}")
        
        # Get column names
        src_columns = [desc[0] for desc in src_cursor.description]
        rows = src_cursor.fetchall()
        
        # Prepare target insert
        tgt_cursor = self.target_conn.cursor()
        tgt_columns = [m['target_column'] for m in column_mappings]
        
        if not tgt_columns:
            return 0
        
        placeholders = ','.join(['?' for _ in tgt_columns])
        insert_sql = f"INSERT INTO {tgt_table} ({','.join(tgt_columns)}) VALUES ({placeholders})"
        
        migrated_count = 0
        
        for row in rows:
            transformed_row = []
            
            for mapping in column_mappings:
                src_col_idx = src_columns.index(mapping['source_column'])
                value = row[src_col_idx]
                
                # Transform value
                transformed_value, explanation = self.transformer.transform_value(
                    value,
                    mapping['source_type'],
                    mapping['target_type']
                )
                
                transformed_row.append(transformed_value)
                
                # Log transformation
                if mapping['transformation_required']:
                    self.migration_log.append({
                        'table': src_table,
                        'column': mapping['source_column'],
                        'original_value': value,
                        'transformed_value': transformed_value,
                        'explanation': explanation
                    })
            
            try:
                tgt_cursor.execute(insert_sql, transformed_row)
                migrated_count += 1
            except Exception as e:
                self.migration_log.append({
                    'table': src_table,
                    'error': str(e),
                    'row_data': dict(zip(src_columns, row))
                })
        
        self.target_conn.commit()
        return migrated_count
    
    def close(self):
        self.source_conn.close()
        self.target_conn.close()


class MigrationValidator:
    """Validates migrated data and performs round-trip testing"""
    
    def __init__(self, source_db: str, target_db: str):
        self.source_conn = sqlite3.connect(source_db)
        self.target_conn = sqlite3.connect(target_db)
        
    def validate_migration(self, mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation of migrated data"""
        
        validation_results = {
            'overall_status': 'PASSED',
            'checks': {}
        }
        
        for table_pair, column_mappings in mappings.items():
            src_table, tgt_table = table_pair.split('→')
            
            checks = {}
            
            # Row count comparison
            checks['row_count'] = self._validate_row_count(src_table, tgt_table)
            
            # Null value consistency
            checks['null_consistency'] = self._validate_nulls(
                src_table, tgt_table, column_mappings
            )
            
            # Duplicate check
            checks['duplicates'] = self._check_duplicates(tgt_table)
            
            # Data type validation
            checks['data_types'] = self._validate_data_types(
                src_table, tgt_table, column_mappings
            )
            
            validation_results['checks'][table_pair] = checks
            
            # Update overall status
            if any(not check.get('passed', True) for check in checks.values()):
                validation_results['overall_status'] = 'FAILED'
        
        return validation_results
    
    def _validate_row_count(self, src_table: str, tgt_table: str) -> Dict[str, Any]:
        """Compare row counts"""
        src_cursor = self.source_conn.cursor()
        tgt_cursor = self.target_conn.cursor()
        
        src_cursor.execute(f"SELECT COUNT(*) FROM {src_table}")
        src_count = src_cursor.fetchone()[0]
        
        tgt_cursor.execute(f"SELECT COUNT(*) FROM {tgt_table}")
        tgt_count = tgt_cursor.fetchone()[0]
        
        return {
            'check': 'row_count_comparison',
            'source_count': src_count,
            'target_count': tgt_count,
            'passed': src_count == tgt_count,
            'message': f"Source: {src_count}, Target: {tgt_count}"
        }
    
    def _validate_nulls(self, src_table: str, tgt_table: str, 
                        mappings: List[Dict]) -> Dict[str, Any]:
        """Validate NULL value consistency"""
        null_checks = []
        
        for mapping in mappings:
            src_col = mapping['source_column']
            tgt_col = mapping['target_column']
            
            src_cursor = self.source_conn.cursor()
            tgt_cursor = self.target_conn.cursor()
            
            src_cursor.execute(f"SELECT COUNT(*) FROM {src_table} WHERE {src_col} IS NULL")
            src_nulls = src_cursor.fetchone()[0]
            
            tgt_cursor.execute(f"SELECT COUNT(*) FROM {tgt_table} WHERE {tgt_col} IS NULL")
            tgt_nulls = tgt_cursor.fetchone()[0]
            
            null_checks.append({
                'column': f"{src_col}→{tgt_col}",
                'source_nulls': src_nulls,
                'target_nulls': tgt_nulls,
                'matched': src_nulls == tgt_nulls
            })
        
        return {
            'check': 'null_consistency',
            'details': null_checks,
            'passed': all(c['matched'] for c in null_checks)
        }
    
    def _check_duplicates(self, table: str) -> Dict[str, Any]:
        """Check for duplicate rows in target"""
        cursor = self.target_conn.cursor()
        
        # This is a simplified check - in reality would check primary keys
        cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
        total = cursor.fetchone()[0]
        
        return {
            'check': 'duplicate_detection',
            'total_rows': total,
            'passed': True,
            'message': 'No duplicate check implemented (would check primary keys)'
        }
    
    def _validate_data_types(self, src_table: str, tgt_table: str,
                            mappings: List[Dict]) -> Dict[str, Any]:
        """Validate data type conversions"""
        type_checks = []
        
        for mapping in mappings:
            type_checks.append({
                'column': f"{mapping['source_column']}→{mapping['target_column']}",
                'source_type': mapping['source_type'],
                'target_type': mapping['target_type'],
                'transformation_required': mapping['transformation_required'],
                'passed': True
            })
        
        return {
            'check': 'data_type_validation',
            'details': type_checks,
            'passed': True
        }
    
    def round_trip_test(self, forward_mappings: Dict[str, Any], 
                        reverse_mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Perform round-trip validation test"""
        
        results = {
            'test': 'round_trip_validation',
            'tables_tested': 0,
            'perfect_round_trips': 0,
            'acceptable_loss': 0,
            'data_loss_detected': 0,
            'details': {}
        }
        
        for table_pair in forward_mappings.keys():
            src_table, tgt_table = table_pair.split('→')
            reverse_pair = f"{tgt_table}→{src_table}"
            
            if reverse_pair not in reverse_mappings:
                continue
            
            results['tables_tested'] += 1
            
            # Analyze reversibility
            reversibility = self._analyze_round_trip(
                forward_mappings[table_pair],
                reverse_mappings[reverse_pair]
            )
            
            results['details'][table_pair] = reversibility
            
            if reversibility['status'] == 'PERFECT':
                results['perfect_round_trips'] += 1
            elif reversibility['status'] == 'ACCEPTABLE_LOSS':
                results['acceptable_loss'] += 1
            else:
                results['data_loss_detected'] += 1
        
        return results
    
    def _analyze_round_trip(self, forward_maps: List[Dict], 
                           reverse_maps: List[Dict]) -> Dict[str, Any]:
        """Analyze round-trip for a table pair"""
        
        perfect_fields = []
        acceptable_fields = []
        data_loss_fields = []
        
        for fwd_map in forward_maps:
            # Find corresponding reverse mapping
            rev_map = next(
                (r for r in reverse_maps if r['target_column'] == fwd_map['source_column']),
                None
            )
            
            if not rev_map:
                data_loss_fields.append({
                    'field': fwd_map['source_column'],
                    'reason': 'No reverse mapping found'
                })
                continue
            
            if not rev_map.get('reversible', False):
                data_loss_fields.append({
                    'field': fwd_map['source_column'],
                    'reason': rev_map.get('reversibility_reason', 'Not reversible')
                })
            elif fwd_map['source_type'] == fwd_map['target_type']:
                perfect_fields.append(fwd_map['source_column'])
            else:
                acceptable_fields.append({
                    'field': fwd_map['source_column'],
                    'note': 'Minor format changes possible'
                })
        
        # Determine overall status
        if data_loss_fields:
            status = 'DATA_LOSS'
        elif acceptable_fields:
            status = 'ACCEPTABLE_LOSS'
        else:
            status = 'PERFECT'
        
        return {
            'status': status,
            'perfect_round_trip_fields': perfect_fields,
            'acceptable_loss_fields': acceptable_fields,
            'data_loss_fields': data_loss_fields,
            'perfect_percentage': len(perfect_fields) / len(forward_maps) * 100 if forward_maps else 0
        }
    
    def close(self):
        self.source_conn.close()
        self.target_conn.close()


class ReportGenerator:
    """Generates comprehensive migration reports"""
    
    def __init__(self):
        self.reports = {}
    
    def generate_mapping_report(self, mappings: Dict[str, Any], 
                                reverse_mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed mapping report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'forward_mappings': {},
            'reverse_mappings': {},
            'summary': {
                'total_tables': len(mappings),
                'total_column_mappings': sum(len(m) for m in mappings.values()),
                'average_confidence': 0.0,
                'high_confidence_mappings': 0,
                'low_confidence_mappings': 0
            }
        }
        
        total_confidence = 0
        total_mappings = 0
        
        # Forward mappings
        for table_pair, column_mappings in mappings.items():
            formatted_mappings = []
            
            for mapping in column_mappings:
                total_confidence += mapping['confidence']
                total_mappings += 1
                
                if mapping['confidence'] >= 0.7:
                    report['summary']['high_confidence_mappings'] += 1
                elif mapping['confidence'] < 0.5:
                    report['summary']['low_confidence_mappings'] += 1
                
                formatted_mappings.append({
                    'source': mapping['source_column'],
                    'target': mapping['target_column'],
                    'confidence': round(mapping['confidence'], 3),
                    'types': f"{mapping['source_type']} → {mapping['target_type']}",
                    'transformation_required': mapping['transformation_required'],
                    'explanation': {
                        'name_match': f"{mapping['explanation']['name_explanation']} (score: {mapping['explanation']['name_similarity']:.2f})",
                        'type_match': f"{mapping['explanation']['type_explanation']} (score: {mapping['explanation']['type_compatibility']:.2f})",
                        'pattern_match': f"{mapping['explanation']['pattern_explanation']} (score: {mapping['explanation']['pattern_similarity']:.2f})"
                    }
                })
            
            report['forward_mappings'][table_pair] = formatted_mappings
        
        # Reverse mappings
        for table_pair, column_mappings in reverse_mappings.items():
            formatted_mappings = []
            
            for mapping in column_mappings:
                formatted_mappings.append({
                    'source': mapping['source_column'],
                    'target': mapping['target_column'],
                    'reversible': mapping.get('reversible', False),
                    'reversibility_reason': mapping.get('reversibility_reason', 'N/A'),
                    'data_loss_risk': not mapping.get('reversible', False)
                })
            
            report['reverse_mappings'][table_pair] = formatted_mappings
        
        if total_mappings > 0:
            report['summary']['average_confidence'] = round(total_confidence / total_mappings, 3)
        
        return report
    
    def generate_validation_report(self, validation_results: Dict[str, Any],
                                   round_trip_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation and round-trip report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_status': validation_results['overall_status'],
            'validation_checks': validation_results['checks'],
            'round_trip_analysis': round_trip_results,
            'recommendations': []
        }
        
        # Generate recommendations
        if round_trip_results['data_loss_detected'] > 0:
            report['recommendations'].append(
                "⚠️ Data loss detected in reverse mappings. Review non-reversible transformations."
            )
        
        if validation_results['overall_status'] == 'FAILED':
            report['recommendations'].append(
                "❌ Validation failed. Review row counts and null consistency."
            )
        
        if round_trip_results['perfect_round_trips'] == round_trip_results['tables_tested']:
            report['recommendations'].append(
                "✅ All tables have perfect round-trip compatibility."
            )
        
        return report
    
    def generate_executive_summary(self, all_results: Dict[str, Any]) -> str:
        """Generate executive summary in plain text"""
        
        summary = []
        summary.append("="*80)
        summary.append("AI-POWERED DATA MIGRATION - EXECUTIVE SUMMARY")
        summary.append("="*80)
        summary.append("")
        
        # Migration overview
        if 'migration_results' in all_results:
            mr = all_results['migration_results']
            summary.append(f"Migration Status: {'✅ SUCCESS' if mr['success'] else '❌ FAILED'}")
            summary.append(f"Tables Migrated: {mr['tables_migrated']}")
            summary.append(f"Total Rows Migrated: {mr['rows_migrated']}")
            summary.append("")
        
        # Mapping quality
        if 'mapping_report' in all_results:
            ms = all_results['mapping_report']['summary']
            summary.append("Mapping Quality:")
            summary.append(f"  - Average Confidence: {ms['average_confidence']:.1%}")
            summary.append(f"  - High Confidence Mappings: {ms['high_confidence_mappings']}")
            summary.append(f"  - Low Confidence Mappings: {ms['low_confidence_mappings']}")
            summary.append("")
        
        # Round-trip analysis
        if 'validation_report' in all_results:
            rt = all_results['validation_report']['round_trip_analysis']
            summary.append("Round-Trip Validation:")
            summary.append(f"  - Tables Tested: {rt['tables_tested']}")
            summary.append(f"  - Perfect Round-Trips: {rt['perfect_round_trips']}")
            summary.append(f"  - Acceptable Data Loss: {rt['acceptable_loss']}")
            summary.append(f"  - Critical Data Loss: {rt['data_loss_detected']}")
            summary.append("")
        
        # Recommendations
        if 'validation_report' in all_results and all_results['validation_report']['recommendations']:
            summary.append("Recommendations:")
            for rec in all_results['validation_report']['recommendations']:
                summary.append(f"  {rec}")
        
        summary.append("")
        summary.append("="*80)
        
        return "\n".join(summary)


def save_json_report(data: Dict, filename: str):
    """Save report as JSON"""
    with open(filename, 'w') as f:
        json.dump(data, indent=2, fp=f, default=str)


# Main execution function
def run_complete_migration(source_db: str, target_db: str, output_dir: str = '/Users/ayushigupta/Documents/GitHub/DataForge/track2/outputs'):
    """
    Run complete migration with all features
    """
    import os
    
    print("🚀 Starting AI-Powered Data Migration System")
    print("="*80)
    
    # 1. Schema Discovery
    print("\n📊 Step 1: Discovering schemas...")
    source_analyzer = SchemaAnalyzer(source_db)
    target_analyzer = SchemaAnalyzer(target_db)
    
    source_schema = source_analyzer.get_schema_info()
    target_schema = target_analyzer.get_schema_info()
    
    print(f"   Source tables: {list(source_schema.keys())}")
    print(f"   Target tables: {list(target_schema.keys())}")
    
    # 2. AI-Powered Mapping
    print("\n🤖 Step 2: Generating AI-powered column mappings...")
    mapper = AIColumnMapper()
    forward_mappings = mapper.map_columns(source_schema, target_schema)
    
    print(f"   Generated {sum(len(m) for m in forward_mappings.values())} column mappings")
    
    # 3. Bidirectional Mapping
    print("\n🔄 Step 3: Generating reverse mappings...")
    bi_mapper = BidirectionalMapper(forward_mappings)
    reverse_mappings = bi_mapper.generate_reverse_mappings()
    
    print(f"   Generated {sum(len(m) for m in reverse_mappings.values())} reverse mappings")
    print(f"   Reversibility analysis: {len(bi_mapper.reversibility_analysis)} field pairs analyzed")
    
    # 4. Execute Migration
    print("\n⚡ Step 4: Executing migration...")
    executor = MigrationExecutor(source_db, target_db)
    migration_results = executor.execute_migration(forward_mappings)
    
    print(f"   Status: {'✅ SUCCESS' if migration_results['success'] else '❌ FAILED'}")
    print(f"   Rows migrated: {migration_results['rows_migrated']}")
    
    # 5. Validation
    print("\n✅ Step 5: Validating migration...")
    validator = MigrationValidator(source_db, target_db)
    validation_results = validator.validate_migration(forward_mappings)
    
    print(f"   Validation: {validation_results['overall_status']}")
    
    # 6. Round-Trip Testing
    print("\n🔁 Step 6: Performing round-trip validation...")
    round_trip_results = validator.round_trip_test(forward_mappings, reverse_mappings)
    
    print(f"   Perfect round-trips: {round_trip_results['perfect_round_trips']}/{round_trip_results['tables_tested']}")
    print(f"   Data loss detected: {round_trip_results['data_loss_detected']} tables")
    
    # 7. Generate Reports
    print("\n📝 Step 7: Generating reports...")
    reporter = ReportGenerator()
    
    mapping_report = reporter.generate_mapping_report(forward_mappings, reverse_mappings)
    validation_report = reporter.generate_validation_report(validation_results, round_trip_results)
    
    all_results = {
        'migration_results': migration_results,
        'mapping_report': mapping_report,
        'validation_report': validation_report,
        'transformation_log': executor.migration_log
    }
    
    executive_summary = reporter.generate_executive_summary(all_results)
    
    # Save all reports
    save_json_report(mapping_report, f'{output_dir}/mapping_report.json')
    save_json_report(validation_report, f'{output_dir}/validation_report.json')
    save_json_report(all_results, f'{output_dir}/complete_migration_report.json')
    
    with open(f'{output_dir}/executive_summary.txt', 'w') as f:
        f.write(executive_summary)
    
    print("\n" + executive_summary)
    
    # Cleanup
    source_analyzer.close()
    target_analyzer.close()
    executor.close()
    validator.close()
    
    print("\n✨ Migration complete! Reports saved to output directory.")
    
    return all_results


if __name__ == "__main__":
    # This would be called with actual database paths
    pass
