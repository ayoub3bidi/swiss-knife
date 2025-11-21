#!/usr/bin/env python3

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class WordFrequencyAnalyzer:
    # Common stop words (English)
    DEFAULT_STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "that",
        "the",
        "to",
        "was",
        "will",
        "with",
        "this",
        "but",
        "they",
        "have",
        "had",
        "what",
        "when",
        "where",
        "who",
        "which",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "can",
        "just",
        "should",
        "now",
        "i",
        "you",
        "we",
        "or",
        "been",
        "were",
        "would",
        "there",
        "their",
        "if",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "up",
        "down",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "any",
        "my",
        "our",
        "your",
        "his",
        "her",
        "me",
        "him",
        "them",
        "she",
        "us",
        "do",
        "does",
        "did",
        "doing",
        "am",
    }

    def __init__(
        self,
        min_word_length: int = 1,
        max_word_length: Optional[int] = None,
        case_sensitive: bool = False,
        remove_stop_words: bool = False,
        custom_stop_words: Optional[Set[str]] = None,
        only_alphabetic: bool = False,
        include_numbers: bool = True,
        min_frequency: int = 1,
        encoding: str = "utf-8",
    ):
        """
        Args:
            min_word_length: Minimum word length to include
            max_word_length: Maximum word length to include
            case_sensitive: Preserve word case
            remove_stop_words: Remove common stop words
            custom_stop_words: Additional custom stop words
            only_alphabetic: Only include alphabetic words
            include_numbers: Include numeric tokens
            min_frequency: Minimum frequency threshold
            encoding: File encoding
        """
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.case_sensitive = case_sensitive
        self.remove_stop_words = remove_stop_words
        self.only_alphabetic = only_alphabetic
        self.include_numbers = include_numbers
        self.min_frequency = min_frequency
        self.encoding = encoding

        # Build stop words set
        self.stop_words = set()
        if remove_stop_words:
            self.stop_words = self.DEFAULT_STOP_WORDS.copy()
        if custom_stop_words:
            self.stop_words.update(w.lower() for w in custom_stop_words)

        # Statistics
        self.stats = {
            "total_words": 0,
            "unique_words": 0,
            "total_characters": 0,
            "files_processed": 0,
            "lines_processed": 0,
        }

        self.word_frequencies = Counter()
        self.word_contexts = defaultdict(list)  # Store example sentences
        self.file_frequencies = defaultdict(Counter)  # Per-file frequencies

    def _tokenize(self, text: str) -> List[str]:
        # Split on whitespace and punctuation, but keep apostrophes in words
        if self.only_alphabetic:
            pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b"
        elif self.include_numbers:
            pattern = r"\b\w+(?:'[a-zA-Z]+)?\b"
        else:
            pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b"

        tokens = re.findall(pattern, text)
        return tokens

    def _should_include_word(self, word: str) -> bool:
        # Case handling
        check_word = word if self.case_sensitive else word.lower()

        # Length filters
        if len(word) < self.min_word_length:
            return False
        if self.max_word_length and len(word) > self.max_word_length:
            return False

        # Stop words
        if self.remove_stop_words and check_word in self.stop_words:
            return False

        # Alphabetic only
        if self.only_alphabetic and not word.isalpha():
            return False

        # Numbers
        if not self.include_numbers and word.isdigit():
            return False

        return True

    def _extract_context(self, text: str, word: str, context_words: int = 5) -> str:
        words = text.split()
        for i, w in enumerate(words):
            if word.lower() in w.lower():
                start = max(0, i - context_words)
                end = min(len(words), i + context_words + 1)
                context = " ".join(words[start:end])
                return context[:100] + "..." if len(context) > 100 else context
        return ""

    def analyze_text(self, text: str, store_context: bool = False) -> Counter:
        lines = text.split("\n")
        self.stats["lines_processed"] += len(lines)

        for line in lines:
            tokens = self._tokenize(line)

            for token in tokens:
                if self._should_include_word(token):
                    word = token if self.case_sensitive else token.lower()
                    self.word_frequencies[word] += 1
                    self.stats["total_words"] += 1
                    self.stats["total_characters"] += len(word)

                    # Store context if requested and word frequency is low
                    if store_context and self.word_frequencies[word] <= 3:
                        context = self._extract_context(line, word)
                        if context:
                            self.word_contexts[word].append(context)

        return self.word_frequencies

    def analyze_file(self, filepath: Path, store_context: bool = False) -> Counter:
        try:
            with open(filepath, encoding=self.encoding, errors="replace") as f:
                text = f.read()

            # Store per-file frequencies
            file_counter = Counter()
            tokens = self._tokenize(text)

            for token in tokens:
                if self._should_include_word(token):
                    word = token if self.case_sensitive else token.lower()
                    file_counter[word] += 1

            self.file_frequencies[str(filepath)] = file_counter

            # Analyze full text
            self.analyze_text(text, store_context)
            self.stats["files_processed"] += 1

            return file_counter

        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return Counter()

    def analyze_directory(
        self,
        directory: Path,
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
        store_context: bool = False,
    ) -> None:
        pattern = "**/*" if recursive else "*"
        files = []

        for filepath in directory.glob(pattern):
            if filepath.is_file():
                if extensions:
                    if filepath.suffix.lower().lstrip(".") in extensions:
                        files.append(filepath)
                else:
                    # Try to read as text
                    files.append(filepath)

        if not files:
            print(f"No files found in {directory}")
            return

        print(f"Analyzing {len(files)} file(s)...")
        iterator = tqdm(files, desc="Processing", unit="files") if HAS_TQDM else files

        for filepath in iterator:
            self.analyze_file(filepath, store_context)

    def get_top_words(self, n: int = 20) -> List[Tuple[str, int]]:
        filtered = {
            word: count
            for word, count in self.word_frequencies.items()
            if count >= self.min_frequency
        }
        return Counter(filtered).most_common(n)

    def get_words_by_length(self) -> Dict[int, int]:
        length_counts = defaultdict(int)
        for word, count in self.word_frequencies.items():
            length_counts[len(word)] += count
        return dict(sorted(length_counts.items()))

    def get_words_starting_with(
        self, prefix: str, n: int = 20
    ) -> List[Tuple[str, int]]:
        prefix_lower = prefix.lower()
        matching = {
            word: count
            for word, count in self.word_frequencies.items()
            if word.lower().startswith(prefix_lower)
        }
        return Counter(matching).most_common(n)

    def get_words_ending_with(self, suffix: str, n: int = 20) -> List[Tuple[str, int]]:
        suffix_lower = suffix.lower()
        matching = {
            word: count
            for word, count in self.word_frequencies.items()
            if word.lower().endswith(suffix_lower)
        }
        return Counter(matching).most_common(n)

    def get_words_containing(
        self, substring: str, n: int = 20
    ) -> List[Tuple[str, int]]:
        substring_lower = substring.lower()
        matching = {
            word: count
            for word, count in self.word_frequencies.items()
            if substring_lower in word.lower()
        }
        return Counter(matching).most_common(n)

    def get_word_statistics(self) -> Dict:
        if not self.word_frequencies:
            return {}

        frequencies = list(self.word_frequencies.values())
        words = list(self.word_frequencies.keys())

        self.stats["unique_words"] = len(words)

        return {
            "total_words": self.stats["total_words"],
            "unique_words": self.stats["unique_words"],
            "total_characters": self.stats["total_characters"],
            "avg_word_length": self.stats["total_characters"]
            / self.stats["total_words"],
            "avg_word_frequency": sum(frequencies) / len(frequencies),
            "max_frequency": max(frequencies),
            "min_frequency": min(frequencies),
            "median_frequency": sorted(frequencies)[len(frequencies) // 2],
            "words_appearing_once": sum(1 for f in frequencies if f == 1),
            "longest_word": max(words, key=len),
            "shortest_word": min(words, key=len),
        }

    def print_bar_chart(
        self, data: List[Tuple[str, int]], title: str, max_width: int = 50
    ) -> None:
        if not data:
            return

        print(f"\n{title}")
        print("=" * 80)

        max_count = max(count for _, count in data)

        for word, count in data:
            # Truncate long words
            display_word = word if len(word) <= 20 else word[:17] + "..."

            # Calculate bar length
            bar_length = int((count / max_count) * max_width) if max_count > 0 else 0
            bar = "█" * bar_length

            percentage = (
                (count / self.stats["total_words"] * 100)
                if self.stats["total_words"] > 0
                else 0
            )

            print(
                f"{display_word:<22} {bar:<{max_width}} {count:>8} ({percentage:>5.2f}%)"
            )

    def print_analysis(self, top_n: int = 20, show_contexts: bool = False) -> None:
        print("\n" + "=" * 80)
        print("WORD FREQUENCY ANALYSIS")
        print("=" * 80)

        # Statistics
        stats = self.get_word_statistics()
        print("\nStatistics:")
        print(f"  Total words:          {stats['total_words']:,}")
        print(f"  Unique words:         {stats['unique_words']:,}")
        print(f"  Total characters:     {stats['total_characters']:,}")
        print(f"  Avg word length:      {stats['avg_word_length']:.2f}")
        print(f"  Avg word frequency:   {stats['avg_word_frequency']:.2f}")
        print(f"  Words appearing once: {stats['words_appearing_once']:,}")
        print(
            f"  Longest word:         {stats['longest_word']} ({len(stats['longest_word'])} chars)"
        )
        print(
            f"  Shortest word:        {stats['shortest_word']} ({len(stats['shortest_word'])} chars)"
        )

        # Top words
        top_words = self.get_top_words(top_n)
        self.print_bar_chart(top_words, f"TOP {top_n} MOST FREQUENT WORDS")

        # Word length distribution
        length_dist = self.get_words_by_length()
        if length_dist:
            print("\nWORD LENGTH DISTRIBUTION")
            print("=" * 80)
            for length, count in sorted(length_dist.items())[:15]:
                bar_length = int((count / max(length_dist.values())) * 40)
                bar = "█" * bar_length
                print(f"  {length:2d} chars: {bar:<40} {count:>8}")

        # Contexts
        if show_contexts and self.word_contexts:
            print("\nWORD CONTEXTS (Examples)")
            print("=" * 80)
            for word in list(top_words)[:10]:
                word_str = word[0]
                if word_str in self.word_contexts:
                    contexts = self.word_contexts[word_str][:2]
                    print(f"\n'{word_str}':")
                    for ctx in contexts:
                        print(f"  ... {ctx}")

        # Files breakdown
        if len(self.file_frequencies) > 1:
            print("\nPER-FILE BREAKDOWN")
            print("=" * 80)
            for filepath, counter in sorted(
                self.file_frequencies.items(),
                key=lambda x: sum(x[1].values()),
                reverse=True,
            )[:10]:
                total = sum(counter.values())
                unique = len(counter)
                filename = Path(filepath).name
                print(f"  {filename[:50]:<50} Total: {total:>8}  Unique: {unique:>6}")

    def export_json(self, output_path: Path, include_contexts: bool = False) -> None:
        data = {
            "statistics": self.get_word_statistics(),
            "word_frequencies": dict(self.word_frequencies.most_common()),
            "words_by_length": self.get_words_by_length(),
            "top_50": [{"word": w, "count": c} for w, c in self.get_top_words(50)],
        }

        if include_contexts:
            data["contexts"] = {
                word: contexts[:5] for word, contexts in self.word_contexts.items()
            }

        if len(self.file_frequencies) > 1:
            data["per_file"] = {
                filepath: dict(counter.most_common(20))
                for filepath, counter in self.file_frequencies.items()
            }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Analysis exported to: {output_path}")

    def export_csv(self, output_path: Path) -> None:
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Word", "Frequency", "Percentage", "Length"])

            total = self.stats["total_words"]
            for word, count in self.word_frequencies.most_common():
                percentage = (count / total * 100) if total > 0 else 0
                writer.writerow([word, count, f"{percentage:.4f}", len(word)])

        print(f"CSV exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single file
  python word_frequency.py document.txt

  # Analyze with stop words removed
  python word_frequency.py article.txt --remove-stop-words

  # Analyze directory with specific extensions
  python word_frequency.py docs/ --ext txt,md --recursive

  # Case-sensitive analysis with minimum word length
  python word_frequency.py code/ --case-sensitive --min-length 3 -r

  # Export results to JSON
  python word_frequency.py data.txt --export-json report.json

  # Show word contexts
  python word_frequency.py article.txt --contexts --top 10

  # Find words starting with prefix
  python word_frequency.py text.txt --starts-with "pre"

  # Only alphabetic words, minimum frequency
  python word_frequency.py doc.txt --only-alpha --min-frequency 5
        """,
    )

    parser.add_argument("input", type=Path, help="Input file or directory")

    # Filtering options
    parser.add_argument(
        "--min-length", type=int, default=1, help="Minimum word length (default: 1)"
    )
    parser.add_argument("--max-length", type=int, help="Maximum word length")
    parser.add_argument(
        "--case-sensitive", action="store_true", help="Preserve word case"
    )
    parser.add_argument(
        "--remove-stop-words", action="store_true", help="Remove common stop words"
    )
    parser.add_argument(
        "--stop-words-file",
        type=Path,
        help="File with custom stop words (one per line)",
    )
    parser.add_argument(
        "--only-alpha",
        dest="only_alphabetic",
        action="store_true",
        help="Only include alphabetic words",
    )
    parser.add_argument(
        "--no-numbers",
        dest="include_numbers",
        action="store_false",
        help="Exclude numeric tokens",
    )
    parser.add_argument(
        "--min-frequency",
        type=int,
        default=1,
        help="Minimum frequency threshold (default: 1)",
    )

    # Input options
    parser.add_argument(
        "--ext",
        "--extensions",
        dest="extensions",
        help="File extensions to include (comma-separated)",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process directories recursively"
    )
    parser.add_argument(
        "--encoding", default="utf-8", help="File encoding (default: utf-8)"
    )

    # Output options
    parser.add_argument(
        "--top", type=int, default=20, help="Number of top words to show (default: 20)"
    )
    parser.add_argument(
        "--contexts", action="store_true", help="Show example contexts for top words"
    )

    # Export options
    parser.add_argument("--export-json", type=Path, help="Export results to JSON file")
    parser.add_argument(
        "--export-csv", type=Path, help="Export word frequencies to CSV file"
    )

    # Search options
    parser.add_argument(
        "--starts-with", type=str, help="Show words starting with prefix"
    )
    parser.add_argument("--ends-with", type=str, help="Show words ending with suffix")
    parser.add_argument("--contains", type=str, help="Show words containing substring")

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input not found: {args.input}")
        sys.exit(1)

    # Load custom stop words
    custom_stop_words = None
    if args.stop_words_file:
        try:
            with open(args.stop_words_file, encoding="utf-8") as f:
                custom_stop_words = {line.strip().lower() for line in f if line.strip()}
        except Exception as e:
            print(f"Warning: Could not load stop words file: {e}")

    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip().lstrip(".") for ext in args.extensions.split(",")]

    try:
        # Initialize analyzer
        analyzer = WordFrequencyAnalyzer(
            min_word_length=args.min_length,
            max_word_length=args.max_length,
            case_sensitive=args.case_sensitive,
            remove_stop_words=args.remove_stop_words,
            custom_stop_words=custom_stop_words,
            only_alphabetic=args.only_alphabetic,
            include_numbers=args.include_numbers,
            min_frequency=args.min_frequency,
            encoding=args.encoding,
        )

        # Analyze input
        if args.input.is_file():
            print(f"Analyzing: {args.input}")
            analyzer.analyze_file(args.input, store_context=args.contexts)
        else:
            analyzer.analyze_directory(
                args.input,
                extensions=extensions,
                recursive=args.recursive,
                store_context=args.contexts,
            )

        # Print analysis
        analyzer.print_analysis(top_n=args.top, show_contexts=args.contexts)

        # Search queries
        if args.starts_with:
            results = analyzer.get_words_starting_with(args.starts_with, args.top)
            analyzer.print_bar_chart(
                results, f"WORDS STARTING WITH '{args.starts_with}'"
            )

        if args.ends_with:
            results = analyzer.get_words_ending_with(args.ends_with, args.top)
            analyzer.print_bar_chart(results, f"WORDS ENDING WITH '{args.ends_with}'")

        if args.contains:
            results = analyzer.get_words_containing(args.contains, args.top)
            analyzer.print_bar_chart(results, f"WORDS CONTAINING '{args.contains}'")

        # Export
        if args.export_json:
            analyzer.export_json(args.export_json, include_contexts=args.contexts)

        if args.export_csv:
            analyzer.export_csv(args.export_csv)

        print("\n✓ Analysis complete")

    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
