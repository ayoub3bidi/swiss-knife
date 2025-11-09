#!/usr/bin/env python3

import sys
import argparse
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, asdict

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class DeadCodeItem:
    """Represents a potentially dead code item."""
    name: str
    type: str  # 'function', 'class', 'variable', 'import', 'method'
    filepath: str
    line_number: int
    reason: str
    confidence: str  # 'high', 'medium', 'low'


class PythonDeadCodeDetector:
    """Detect dead code in Python files."""
    
    def __init__(self, exclude_test_files: bool = True,
                 exclude_private: bool = False,
                 exclude_magic: bool = True,
                 min_confidence: str = 'medium'):
        """
        Args:
            exclude_test_files: Exclude test files from analysis
            exclude_private: Exclude private members (starting with _)
            exclude_magic: Exclude magic methods (__init__, etc.)
            min_confidence: Minimum confidence level ('low', 'medium', 'high')
        """
        self.exclude_test_files = exclude_test_files
        self.exclude_private = exclude_private
        self.exclude_magic = exclude_magic
        self.min_confidence = min_confidence
        
        # Track definitions and usages
        self.definitions: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)
        self.usages: Dict[str, int] = defaultdict(int)
        self.imports: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.class_methods: Dict[str, Set[str]] = defaultdict(set)
        
        # Results
        self.dead_code: List[DeadCodeItem] = []
        
        # Statistics
        self.stats = {
            'files_analyzed': 0,
            'total_functions': 0,
            'total_classes': 0,
            'total_imports': 0,
            'dead_functions': 0,
            'dead_classes': 0,
            'dead_imports': 0,
            'dead_variables': 0,
            'parse_errors': 0
        }
    
    def _should_analyze(self, filepath: Path) -> bool:
        """Check if file should be analyzed."""
        if self.exclude_test_files:
            name_lower = filepath.name.lower()
            if name_lower.startswith('test_') or name_lower.endswith('_test.py'):
                return False
            if 'test' in str(filepath.parent).lower():
                return False
        
        return filepath.suffix == '.py'
    
    def _should_include_name(self, name: str, item_type: str) -> bool:
        """Check if name should be included in analysis."""
        if self.exclude_private and name.startswith('_') and not name.startswith('__'):
            return False
        
        if self.exclude_magic and name.startswith('__') and name.endswith('__'):
            return False
        
        # Always include main entry point
        if name == '__main__':
            return False
        
        return True
    
    def _parse_file(self, filepath: Path) -> Optional[ast.AST]:
        """Parse Python file to AST."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            self.stats['parse_errors'] += 1
            return None
        except Exception as e:
            self.stats['parse_errors'] += 1
            return None
    
    def _extract_definitions(self, tree: ast.AST, filepath: str) -> None:
        """Extract function, class, and variable definitions."""
        for node in ast.walk(tree):
            # Functions
            if isinstance(node, ast.FunctionDef):
                if self._should_include_name(node.name, 'function'):
                    self.definitions[node.name].append((filepath, node.lineno, 'function'))
                    self.stats['total_functions'] += 1
            
            # Classes
            elif isinstance(node, ast.ClassDef):
                if self._should_include_name(node.name, 'class'):
                    self.definitions[node.name].append((filepath, node.lineno, 'class'))
                    self.stats['total_classes'] += 1
                    
                    # Track class methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            self.class_methods[node.name].add(item.name)
            
            # Module-level assignments
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if self._should_include_name(target.id, 'variable'):
                            self.definitions[target.id].append((filepath, node.lineno, 'variable'))
            
            # Imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    self.imports[name].append((filepath, node.lineno))
                    self.stats['total_imports'] += 1
            
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == '*':
                        continue
                    name = alias.asname if alias.asname else alias.name
                    self.imports[name].append((filepath, node.lineno))
                    self.stats['total_imports'] += 1
    
    def _extract_usages(self, tree: ast.AST) -> None:
        """Extract name usages (references)."""
        for node in ast.walk(tree):
            # Function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.usages[node.func.id] += 1
                elif isinstance(node.func, ast.Attribute):
                    self.usages[node.func.attr] += 1
            
            # Attribute access
            elif isinstance(node, ast.Attribute):
                self.usages[node.attr] += 1
            
            # Name references
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, (ast.Load, ast.Del)):
                    self.usages[node.id] += 1
    
    def analyze_file(self, filepath: Path) -> None:
        """Analyze a single Python file."""
        if not self._should_analyze(filepath):
            return
        
        tree = self._parse_file(filepath)
        if not tree:
            return
        
        self.stats['files_analyzed'] += 1
        
        # First pass: collect definitions
        self._extract_definitions(tree, str(filepath))
    
    def analyze_usages(self, filepath: Path) -> None:
        """Analyze usages in a file (second pass)."""
        if not self._should_analyze(filepath):
            return
        
        tree = self._parse_file(filepath)
        if not tree:
            return
        
        # Second pass: collect usages
        self._extract_usages(tree)
    
    def _calculate_confidence(self, name: str, item_type: str, 
                             usage_count: int) -> str:
        """Calculate confidence that item is dead code."""
        # High confidence: no usages at all
        if usage_count == 0:
            # Special cases that might be external API
            if name.startswith('test_'):
                return 'low'  # Test functions called by framework
            if item_type == 'class' and name.endswith('Error'):
                return 'medium'  # Exception classes might be caught by type
            return 'high'
        
        # Low usage might still be dead in large projects
        if usage_count == 1 and item_type in ('function', 'class'):
            return 'medium'
        
        return 'low'
    
    def identify_dead_code(self) -> List[DeadCodeItem]:
        """Identify dead code items."""
        self.dead_code = []
        
        # Check functions and classes
        for name, occurrences in self.definitions.items():
            usage_count = self.usages.get(name, 0)
            
            for filepath, line_no, item_type in occurrences:
                # Skip if used elsewhere
                if usage_count > len(occurrences):
                    continue
                
                # Calculate confidence
                confidence = self._calculate_confidence(name, item_type, usage_count)
                
                # Filter by confidence
                confidence_levels = {'low': 0, 'medium': 1, 'high': 2}
                if confidence_levels[confidence] < confidence_levels[self.min_confidence]:
                    continue
                
                reason = f"No references found" if usage_count == 0 else f"Only {usage_count} reference(s)"
                
                item = DeadCodeItem(
                    name=name,
                    type=item_type,
                    filepath=filepath,
                    line_number=line_no,
                    reason=reason,
                    confidence=confidence
                )
                self.dead_code.append(item)
                
                if item_type == 'function':
                    self.stats['dead_functions'] += 1
                elif item_type == 'class':
                    self.stats['dead_classes'] += 1
                elif item_type == 'variable':
                    self.stats['dead_variables'] += 1
        
        # Check imports
        for name, occurrences in self.imports.items():
            usage_count = self.usages.get(name, 0)
            
            # Import used only for import statement itself
            if usage_count <= len(occurrences):
                for filepath, line_no in occurrences:
                    confidence = 'high' if usage_count == 0 else 'medium'
                    
                    confidence_levels = {'low': 0, 'medium': 1, 'high': 2}
                    if confidence_levels[confidence] < confidence_levels[self.min_confidence]:
                        continue
                    
                    item = DeadCodeItem(
                        name=name,
                        type='import',
                        filepath=filepath,
                        line_number=line_no,
                        reason="Imported but never used",
                        confidence=confidence
                    )
                    self.dead_code.append(item)
                    self.stats['dead_imports'] += 1
        
        # Sort by confidence and filepath
        confidence_order = {'high': 0, 'medium': 1, 'low': 2}
        self.dead_code.sort(key=lambda x: (confidence_order[x.confidence], x.filepath, x.line_number))
        
        return self.dead_code
    
    def analyze_directory(self, directory: Path, recursive: bool = True) -> None:
        """Analyze all Python files in directory."""
        pattern = '**/*.py' if recursive else '*.py'
        files = list(directory.glob(pattern))
        
        if not files:
            print(f"No Python files found in {directory}")
            return
        
        print(f"Analyzing {len(files)} Python file(s)...")
        
        # First pass: collect definitions
        iterator = tqdm(files, desc="Pass 1: Definitions", unit="files") if HAS_TQDM else files
        for filepath in iterator:
            self.analyze_file(filepath)
        
        # Second pass: collect usages
        iterator = tqdm(files, desc="Pass 2: Usages", unit="files") if HAS_TQDM else files
        for filepath in iterator:
            self.analyze_usages(filepath)
        
        # Identify dead code
        print("Analyzing for dead code...")
        self.identify_dead_code()
    
    def print_results(self, show_all: bool = False, max_items: int = 50) -> None:
        """Print dead code analysis results."""
        print("\n" + "=" * 80)
        print("DEAD CODE ANALYSIS RESULTS")
        print("=" * 80)
        
        # Statistics
        print("\nStatistics:")
        print(f"  Files analyzed:       {self.stats['files_analyzed']}")
        print(f"  Total functions:      {self.stats['total_functions']}")
        print(f"  Total classes:        {self.stats['total_classes']}")
        print(f"  Total imports:        {self.stats['total_imports']}")
        print(f"  Parse errors:         {self.stats['parse_errors']}")
        
        print(f"\nDead Code Found:")
        print(f"  Dead functions:       {self.stats['dead_functions']}")
        print(f"  Dead classes:         {self.stats['dead_classes']}")
        print(f"  Dead variables:       {self.stats['dead_variables']}")
        print(f"  Unused imports:       {self.stats['dead_imports']}")
        print(f"  Total:                {len(self.dead_code)}")
        
        if not self.dead_code:
            print("\n✓ No dead code found!")
            return
        
        # Group by confidence
        by_confidence = defaultdict(list)
        for item in self.dead_code:
            by_confidence[item.confidence].append(item)
        
        # Display results
        for confidence in ['high', 'medium', 'low']:
            items = by_confidence[confidence]
            if not items:
                continue
            
            confidence_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            print(f"\n{confidence_icon[confidence]} {confidence.upper()} CONFIDENCE ({len(items)} items)")
            print("-" * 80)
            
            display_items = items if show_all else items[:max_items]
            
            for item in display_items:
                filepath = Path(item.filepath).name
                print(f"  {item.type:10s} {item.name:30s} {filepath}:{item.line_number}")
                print(f"             {item.reason}")
            
            if not show_all and len(items) > max_items:
                print(f"\n  ... and {len(items) - max_items} more {confidence} confidence items")
    
    def export_json(self, output_path: Path) -> None:
        """Export results to JSON."""
        data = {
            'statistics': self.stats,
            'dead_code': [asdict(item) for item in self.dead_code],
            'by_type': {
                'functions': [asdict(item) for item in self.dead_code if item.type == 'function'],
                'classes': [asdict(item) for item in self.dead_code if item.type == 'class'],
                'variables': [asdict(item) for item in self.dead_code if item.type == 'variable'],
                'imports': [asdict(item) for item in self.dead_code if item.type == 'import']
            },
            'by_confidence': {
                'high': [asdict(item) for item in self.dead_code if item.confidence == 'high'],
                'medium': [asdict(item) for item in self.dead_code if item.confidence == 'medium'],
                'low': [asdict(item) for item in self.dead_code if item.confidence == 'low']
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults exported to: {output_path}")
    
    def export_csv(self, output_path: Path) -> None:
        """Export results to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Type', 'File', 'Line', 'Reason', 'Confidence'])
            
            for item in self.dead_code:
                writer.writerow([
                    item.name,
                    item.type,
                    item.filepath,
                    item.line_number,
                    item.reason,
                    item.confidence
                ])
        
        print(f"CSV exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect dead code (unused functions, classes, imports) in Python projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  python dead_code_detector.py .
  
  # Analyze with high confidence only
  python dead_code_detector.py src/ --min-confidence high
  
  # Include test files in analysis
  python dead_code_detector.py . --include-tests
  
  # Include private members
  python dead_code_detector.py src/ --include-private
  
  # Export results
  python dead_code_detector.py . --export-json dead_code.json
  
  # Show all results (not just top 50)
  python dead_code_detector.py src/ --show-all
  
  # Non-recursive (current directory only)
  python dead_code_detector.py . --no-recursive

Confidence Levels:
  HIGH   - No references found anywhere
  MEDIUM - Very few references (might be dead)
  LOW    - Has some references (likely used)
        """
    )
    
    parser.add_argument('path', type=Path,
                       help='Directory to analyze')
    
    parser.add_argument('--min-confidence', choices=['low', 'medium', 'high'],
                       default='medium',
                       help='Minimum confidence level to report (default: medium)')
    
    parser.add_argument('--include-tests', dest='exclude_tests', action='store_false',
                       help='Include test files in analysis')
    parser.add_argument('--include-private', dest='exclude_private', action='store_true',
                       help='Include private members (starting with _)')
    parser.add_argument('--include-magic', dest='exclude_magic', action='store_false',
                       help='Include magic methods (__init__, etc.)')
    
    parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                       help='Don\'t analyze subdirectories')
    
    parser.add_argument('--show-all', action='store_true',
                       help='Show all results (not just top 50 per confidence)')
    parser.add_argument('--max-items', type=int, default=50,
                       help='Maximum items to show per confidence level (default: 50)')
    
    parser.add_argument('--export-json', type=Path,
                       help='Export results to JSON file')
    parser.add_argument('--export-csv', type=Path,
                       help='Export results to CSV file')
    
    args = parser.parse_args()
    
    if not args.path.exists():
        print(f"Error: Path not found: {args.path}")
        sys.exit(1)
    
    if not args.path.is_dir():
        print(f"Error: Path must be a directory: {args.path}")
        sys.exit(1)
    
    try:
        detector = PythonDeadCodeDetector(
            exclude_test_files=args.exclude_tests,
            exclude_private=args.exclude_private,
            exclude_magic=args.exclude_magic,
            min_confidence=args.min_confidence
        )
        
        detector.analyze_directory(args.path, recursive=args.recursive)
        
        detector.print_results(
            show_all=args.show_all,
            max_items=args.max_items
        )
        
        if args.export_json:
            detector.export_json(args.export_json)
        
        if args.export_csv:
            detector.export_csv(args.export_csv)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
