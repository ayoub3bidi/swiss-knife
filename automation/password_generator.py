#!/usr/bin/env python3

import sys
import argparse
import secrets
import string
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
import math


@dataclass
class PasswordPolicy:
    """Password generation policy."""
    length: int = 16
    min_uppercase: int = 1
    min_lowercase: int = 1
    min_digits: int = 1
    min_special: int = 1
    exclude_ambiguous: bool = True
    exclude_similar: bool = False
    custom_special: Optional[str] = None
    no_repeating: bool = False
    no_sequential: bool = False
    require_all_types: bool = True


@dataclass
class PasswordStrength:
    """Password strength analysis."""
    score: int  # 0-100
    level: str  # weak, fair, good, strong, excellent
    entropy: float
    charset_size: int
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_special: bool
    has_repeating: bool
    has_sequential: bool
    common_patterns: List[str]
    suggestions: List[str]


class PasswordGenerator:
    
    # Character sets
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    
    # Ambiguous characters (easy to confuse)
    AMBIGUOUS = "il1Lo0O"
    
    # Similar looking characters
    SIMILAR = "il1|!I/\\0O"
    
    # Common patterns to detect
    COMMON_PATTERNS = [
        (r'(.)\1{2,}', 'repeated characters'),
        (r'(012|123|234|345|456|567|678|789)', 'sequential numbers'),
        (r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', 'sequential letters'),
        (r'(password|pass|admin|user|root|test|qwerty|azerty)', 'common words')
    ]
    
    def __init__(self, policy: PasswordPolicy = None):
        """
        Args:
            policy: Password generation policy
        """
        self.policy = policy or PasswordPolicy()
    
    def _get_charset(self) -> tuple:
        """Get character sets based on policy."""
        uppercase = self.UPPERCASE
        lowercase = self.LOWERCASE
        digits = self.DIGITS
        special = self.policy.custom_special or self.SPECIAL
        
        # Exclude ambiguous characters
        if self.policy.exclude_ambiguous:
            uppercase = ''.join(c for c in uppercase if c not in self.AMBIGUOUS)
            lowercase = ''.join(c for c in lowercase if c not in self.AMBIGUOUS)
            digits = ''.join(c for c in digits if c not in self.AMBIGUOUS)
        
        # Exclude similar characters
        if self.policy.exclude_similar:
            uppercase = ''.join(c for c in uppercase if c not in self.SIMILAR)
            lowercase = ''.join(c for c in lowercase if c not in self.SIMILAR)
            digits = ''.join(c for c in digits if c not in self.SIMILAR)
            special = ''.join(c for c in special if c not in self.SIMILAR)
        
        return uppercase, lowercase, digits, special
    
    def _has_repeating_chars(self, password: str) -> bool:
        """Check for repeating characters (3+ in a row)."""
        return bool(re.search(r'(.)\1{2,}', password))
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters."""
        password_lower = password.lower()
        
        # Check for sequential numbers
        if re.search(r'(012|123|234|345|456|567|678|789)', password):
            return True
        
        # Check for sequential letters
        for i in range(len(password_lower) - 2):
            if ord(password_lower[i]) + 1 == ord(password_lower[i+1]) and \
               ord(password_lower[i+1]) + 1 == ord(password_lower[i+2]):
                return True
        
        return False
    
    def generate(self) -> str:
        """Generate a password according to policy."""
        max_attempts = 1000
        
        for _ in range(max_attempts):
            password = self._generate_attempt()
            
            if self._validate_password(password):
                return password
        
        raise RuntimeError("Failed to generate password meeting policy requirements")
    
    def _generate_attempt(self) -> str:
        """Generate a single password attempt."""
        uppercase, lowercase, digits, special = self._get_charset()
        
        # Start with required characters
        chars = []
        
        if self.policy.min_uppercase > 0:
            chars.extend(secrets.choice(uppercase) for _ in range(self.policy.min_uppercase))
        
        if self.policy.min_lowercase > 0:
            chars.extend(secrets.choice(lowercase) for _ in range(self.policy.min_lowercase))
        
        if self.policy.min_digits > 0:
            chars.extend(secrets.choice(digits) for _ in range(self.policy.min_digits))
        
        if self.policy.min_special > 0:
            chars.extend(secrets.choice(special) for _ in range(self.policy.min_special))
        
        # Fill remaining length with random characters from all sets
        all_chars = uppercase + lowercase + digits + special
        remaining = self.policy.length - len(chars)
        
        if remaining > 0:
            chars.extend(secrets.choice(all_chars) for _ in range(remaining))
        
        # Shuffle to avoid predictable patterns
        chars_list = list(chars)
        for i in range(len(chars_list) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars_list[i], chars_list[j] = chars_list[j], chars_list[i]
        
        return ''.join(chars_list)
    
    def _validate_password(self, password: str) -> bool:
        """Validate password against policy."""
        # Check repeating characters
        if self.policy.no_repeating and self._has_repeating_chars(password):
            return False
        
        # Check sequential characters
        if self.policy.no_sequential and self._has_sequential_chars(password):
            return False
        
        return True
    
    def generate_batch(self, count: int) -> List[str]:
        """Generate multiple passwords."""
        return [self.generate() for _ in range(count)]
    
    def generate_passphrase(self, words: int = 4, separator: str = '-',
                           capitalize: bool = True, add_number: bool = True) -> str:
        """Generate a memorable passphrase using random words."""
        # Built-in word list (subset of EFF long wordlist)
        wordlist = [
            'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
            'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
            'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
            'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
            'advice', 'aerobic', 'afford', 'afraid', 'again', 'age', 'agent', 'agree',
            'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album', 'alcohol',
            'alert', 'alien', 'all', 'alley', 'allow', 'almost', 'alone', 'alpha',
            'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among', 'amount',
            'amused', 'analyst', 'anchor', 'ancient', 'anger', 'angle', 'angry', 'animal',
            'ankle', 'announce', 'annual', 'another', 'answer', 'antenna', 'antique', 'anxiety',
            'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april', 'arch',
            'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor', 'army',
            'around', 'arrange', 'arrest', 'arrive', 'arrow', 'art', 'artefact', 'artist',
            'artwork', 'ask', 'aspect', 'assault', 'asset', 'assist', 'assume', 'asthma',
            'athlete', 'atom', 'attack', 'attend', 'attitude', 'attract', 'auction', 'audit',
            'august', 'aunt', 'author', 'auto', 'autumn', 'average', 'avocado', 'avoid',
            'awake', 'aware', 'away', 'awesome', 'awful', 'awkward', 'axis', 'baby',
            'bachelor', 'bacon', 'badge', 'bag', 'balance', 'balcony', 'ball', 'bamboo',
            'banana', 'banner', 'bar', 'barely', 'bargain', 'barrel', 'base', 'basic',
            'basket', 'battle', 'beach', 'bean', 'beauty', 'because', 'become', 'beef',
            'before', 'begin', 'behave', 'behind', 'believe', 'below', 'belt', 'bench',
            'benefit', 'best', 'betray', 'better', 'between', 'beyond', 'bicycle', 'bid',
            'bike', 'bind', 'biology', 'bird', 'birth', 'bitter', 'black', 'blade',
            'blame', 'blanket', 'blast', 'bleak', 'bless', 'blind', 'blood', 'blossom',
            'blouse', 'blue', 'blur', 'blush', 'board', 'boat', 'body', 'boil'
        ]
        
        # Select random words
        selected = [secrets.choice(wordlist) for _ in range(words)]
        
        # Capitalize if requested
        if capitalize:
            selected = [word.capitalize() for word in selected]
        
        # Add number if requested
        if add_number:
            selected.append(str(secrets.randbelow(100)))
        
        return separator.join(selected)
    
    def analyze_strength(self, password: str) -> PasswordStrength:
        """Analyze password strength."""
        # Character type detection
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_special = any(c in self.SPECIAL for c in password)
        
        # Calculate charset size
        charset_size = 0
        if has_uppercase:
            charset_size += 26
        if has_lowercase:
            charset_size += 26
        if has_digits:
            charset_size += 10
        if has_special:
            charset_size += len(self.SPECIAL)
        
        # Calculate entropy
        entropy = len(password) * math.log2(charset_size) if charset_size > 0 else 0
        
        # Detect patterns
        common_patterns = []
        for pattern, description in self.COMMON_PATTERNS:
            if re.search(pattern, password.lower()):
                common_patterns.append(description)
        
        has_repeating = self._has_repeating_chars(password)
        has_sequential = self._has_sequential_chars(password)
        
        # Calculate score (0-100)
        score = 0
        
        # Length contribution (0-30)
        score += min(len(password) * 2, 30)
        
        # Character variety (0-40)
        if has_uppercase:
            score += 10
        if has_lowercase:
            score += 10
        if has_digits:
            score += 10
        if has_special:
            score += 10
        
        # Entropy contribution (0-30)
        if entropy >= 80:
            score += 30
        elif entropy >= 60:
            score += 20
        elif entropy >= 40:
            score += 10
        
        # Penalties
        if has_repeating:
            score -= 10
        if has_sequential:
            score -= 10
        if common_patterns:
            score -= 15 * len(common_patterns)
        if len(password) < 8:
            score -= 20
        
        score = max(0, min(100, score))
        
        # Determine level
        if score >= 90:
            level = 'excellent'
        elif score >= 70:
            level = 'strong'
        elif score >= 50:
            level = 'good'
        elif score >= 30:
            level = 'fair'
        else:
            level = 'weak'
        
        # Generate suggestions
        suggestions = []
        if len(password) < 12:
            suggestions.append("Increase length to at least 12 characters")
        if not has_uppercase:
            suggestions.append("Add uppercase letters")
        if not has_lowercase:
            suggestions.append("Add lowercase letters")
        if not has_digits:
            suggestions.append("Add digits")
        if not has_special:
            suggestions.append("Add special characters")
        if has_repeating:
            suggestions.append("Avoid repeating characters")
        if has_sequential:
            suggestions.append("Avoid sequential characters")
        if common_patterns:
            suggestions.append("Avoid common patterns")
        
        return PasswordStrength(
            score=score,
            level=level,
            entropy=entropy,
            charset_size=charset_size,
            has_uppercase=has_uppercase,
            has_lowercase=has_lowercase,
            has_digits=has_digits,
            has_special=has_special,
            has_repeating=has_repeating,
            has_sequential=has_sequential,
            common_patterns=common_patterns,
            suggestions=suggestions
        )
    
    def print_strength_analysis(self, password: str):
        """Print password strength analysis."""
        strength = self.analyze_strength(password)
        
        # Color coding
        level_colors = {
            'weak': '🔴',
            'fair': '🟠',
            'good': '🟡',
            'strong': '🟢',
            'excellent': '🔵'
        }
        
        print(f"\n{'='*60}")
        print("PASSWORD STRENGTH ANALYSIS")
        print(f"{'='*60}")
        print(f"Password: {password}")
        print(f"Length:   {len(password)} characters")
        print(f"\nStrength: {level_colors.get(strength.level, '⚪')} {strength.level.upper()} ({strength.score}/100)")
        print(f"Entropy:  {strength.entropy:.1f} bits")
        print(f"Charset:  {strength.charset_size} characters")
        
        print(f"\nCharacter Types:")
        print(f"  Uppercase: {'✓' if strength.has_uppercase else '✗'}")
        print(f"  Lowercase: {'✓' if strength.has_lowercase else '✗'}")
        print(f"  Digits:    {'✓' if strength.has_digits else '✗'}")
        print(f"  Special:   {'✓' if strength.has_special else '✗'}")
        
        if strength.common_patterns:
            print(f"\n⚠️  Detected Patterns:")
            for pattern in strength.common_patterns:
                print(f"  - {pattern}")
        
        if strength.has_repeating:
            print("  - Repeating characters found")
        
        if strength.has_sequential:
            print("  - Sequential characters found")
        
        if strength.suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in strength.suggestions:
                print(f"  - {suggestion}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate secure passwords with policy enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single password (default 16 chars)
  python password_generator.py
  
  # Generate 20-character password
  python password_generator.py -l 20
  
  # Generate 10 passwords
  python password_generator.py -n 10
  
  # Strict policy (no ambiguous/similar chars, no repeating/sequential)
  python password_generator.py -l 16 --no-ambiguous --no-similar --no-repeating --no-sequential
  
  # Custom requirements
  python password_generator.py -l 20 --min-upper 2 --min-lower 2 --min-digits 3 --min-special 3
  
  # Generate passphrase
  python password_generator.py --passphrase -w 5
  
  # Analyze existing password
  python password_generator.py --analyze "MyP@ssw0rd123"
  
  # Custom special characters
  python password_generator.py --special "!@#$%"
        """
    )
    
    # Generation options
    parser.add_argument('-l', '--length', type=int, default=16,
                       help='Password length (default: 16)')
    parser.add_argument('-n', '--count', type=int, default=1,
                       help='Number of passwords to generate (default: 1)')
    
    # Character requirements
    parser.add_argument('--min-upper', type=int, default=1,
                       help='Minimum uppercase letters (default: 1)')
    parser.add_argument('--min-lower', type=int, default=1,
                       help='Minimum lowercase letters (default: 1)')
    parser.add_argument('--min-digits', type=int, default=1,
                       help='Minimum digits (default: 1)')
    parser.add_argument('--min-special', type=int, default=1,
                       help='Minimum special characters (default: 1)')
    
    # Character exclusions
    parser.add_argument('--no-ambiguous', dest='exclude_ambiguous', action='store_true',
                       help='Exclude ambiguous characters (il1Lo0O)')
    parser.add_argument('--no-similar', dest='exclude_similar', action='store_true',
                       help='Exclude similar characters (il1|!I/\\0O)')
    parser.add_argument('--special', type=str,
                       help='Custom special characters')
    
    # Pattern restrictions
    parser.add_argument('--no-repeating', action='store_true',
                       help='Disallow repeating characters (aaa)')
    parser.add_argument('--no-sequential', action='store_true',
                       help='Disallow sequential characters (abc, 123)')
    
    # Passphrase mode
    parser.add_argument('--passphrase', action='store_true',
                       help='Generate passphrase instead of password')
    parser.add_argument('-w', '--words', type=int, default=4,
                       help='Number of words in passphrase (default: 4)')
    parser.add_argument('--separator', default='-',
                       help='Passphrase word separator (default: -)')
    parser.add_argument('--no-capitalize', dest='capitalize', action='store_false',
                       help='Don\'t capitalize passphrase words')
    parser.add_argument('--no-number', dest='add_number', action='store_false',
                       help='Don\'t add number to passphrase')
    
    # Analysis mode
    parser.add_argument('--analyze', type=str,
                       help='Analyze strength of existing password')
    
    # Output options
    parser.add_argument('--show-strength', action='store_true',
                       help='Show strength analysis for generated passwords')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    # Analysis mode
    if args.analyze:
        generator = PasswordGenerator()
        generator.print_strength_analysis(args.analyze)
        return
    
    # Create policy
    policy = PasswordPolicy(
        length=args.length,
        min_uppercase=args.min_upper,
        min_lowercase=args.min_lower,
        min_digits=args.min_digits,
        min_special=args.min_special,
        exclude_ambiguous=args.exclude_ambiguous,
        exclude_similar=args.exclude_similar,
        custom_special=args.special,
        no_repeating=args.no_repeating,
        no_sequential=args.no_sequential
    )
    
    generator = PasswordGenerator(policy)
    
    # Generate passwords or passphrases
    if args.passphrase:
        passwords = [generator.generate_passphrase(
            words=args.words,
            separator=args.separator,
            capitalize=args.capitalize,
            add_number=args.add_number
        ) for _ in range(args.count)]
    else:
        passwords = generator.generate_batch(args.count)
    
    # Output
    if args.json:
        output = []
        for pwd in passwords:
            strength = generator.analyze_strength(pwd)
            output.append({
                'password': pwd,
                'length': len(pwd),
                'strength': asdict(strength)
            })
        print(json.dumps(output, indent=2))
    else:
        for pwd in passwords:
            print(pwd)
            if args.show_strength:
                generator.print_strength_analysis(pwd)
                print()


if __name__ == '__main__':
    main()
