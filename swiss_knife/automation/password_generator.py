"""Secure password generation with customizable policies."""

import secrets
import string
from typing import List, Optional, Set


class PasswordGenerator:
    """Generate secure passwords with customizable policies."""
    
    def __init__(self):
        """Initialize password generator."""
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.ambiguous = "0O1lI"
    
    def generate(self, length: int = 12, include_uppercase: bool = True,
                include_lowercase: bool = True, include_digits: bool = True,
                include_symbols: bool = True, exclude_ambiguous: bool = False,
                min_uppercase: int = 1, min_lowercase: int = 1,
                min_digits: int = 1, min_symbols: int = 0) -> str:
        """Generate a secure password.
        
        Args:
            length: Password length
            include_uppercase: Include uppercase letters
            include_lowercase: Include lowercase letters
            include_digits: Include digits
            include_symbols: Include symbols
            exclude_ambiguous: Exclude ambiguous characters (0, O, 1, l, I)
            min_uppercase: Minimum uppercase letters required
            min_lowercase: Minimum lowercase letters required
            min_digits: Minimum digits required
            min_symbols: Minimum symbols required
            
        Returns:
            Generated password string
            
        Raises:
            ValueError: If constraints cannot be satisfied
        """
        if length < 1:
            raise ValueError("Password length must be at least 1")
        
        # Build character sets
        charset = ""
        required_chars = []
        
        if include_lowercase:
            chars = self.lowercase
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous)
            charset += chars
            required_chars.extend([chars] * min_lowercase)
        
        if include_uppercase:
            chars = self.uppercase
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous)
            charset += chars
            required_chars.extend([chars] * min_uppercase)
        
        if include_digits:
            chars = self.digits
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous)
            charset += chars
            required_chars.extend([chars] * min_digits)
        
        if include_symbols:
            charset += self.symbols
            required_chars.extend([self.symbols] * min_symbols)
        
        if not charset:
            raise ValueError("At least one character type must be included")
        
        if len(required_chars) > length:
            raise ValueError("Minimum requirements exceed password length")
        
        # Generate password
        password = []
        
        # Add required characters
        for char_set in required_chars:
            password.append(secrets.choice(char_set))
        
        # Fill remaining length with random characters
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(secrets.choice(charset))
        
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def generate_multiple(self, count: int, **kwargs) -> List[str]:
        """Generate multiple passwords.
        
        Args:
            count: Number of passwords to generate
            **kwargs: Arguments passed to generate()
            
        Returns:
            List of generated passwords
        """
        if count < 1:
            raise ValueError("Count must be at least 1")
        
        return [self.generate(**kwargs) for _ in range(count)]
    
    def check_strength(self, password: str) -> dict:
        """Check password strength.
        
        Args:
            password: Password to check
            
        Returns:
            Dictionary with strength metrics
        """
        if not password:
            return {
                'score': 0,
                'strength': 'Very Weak',
                'feedback': ['Password is empty']
            }
        
        score = 0
        feedback = []
        
        # Length scoring
        length = len(password)
        if length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        elif length >= 6:
            score += 10
        else:
            feedback.append('Password should be at least 8 characters long')
        
        # Character variety scoring
        has_lower = any(c in self.lowercase for c in password)
        has_upper = any(c in self.uppercase for c in password)
        has_digit = any(c in self.digits for c in password)
        has_symbol = any(c in self.symbols for c in password)
        
        variety_count = sum([has_lower, has_upper, has_digit, has_symbol])
        score += variety_count * 15
        
        if not has_lower:
            feedback.append('Add lowercase letters')
        if not has_upper:
            feedback.append('Add uppercase letters')
        if not has_digit:
            feedback.append('Add numbers')
        if not has_symbol:
            feedback.append('Add symbols')
        
        # Repetition penalty
        unique_chars = len(set(password))
        repetition_ratio = unique_chars / length
        if repetition_ratio < 0.7:
            score -= 10
            feedback.append('Reduce repeated characters')
        
        # Common patterns penalty
        if password.lower() in ['password', '123456', 'qwerty', 'admin']:
            score -= 50
            feedback.append('Avoid common passwords')
        
        # Determine strength level
        if score >= 80:
            strength = 'Very Strong'
        elif score >= 60:
            strength = 'Strong'
        elif score >= 40:
            strength = 'Moderate'
        elif score >= 20:
            strength = 'Weak'
        else:
            strength = 'Very Weak'
        
        return {
            'score': max(0, min(100, score)),
            'strength': strength,
            'length': length,
            'has_lowercase': has_lower,
            'has_uppercase': has_upper,
            'has_digits': has_digit,
            'has_symbols': has_symbol,
            'unique_chars': unique_chars,
            'feedback': feedback
        }


def generate_password(length: int = 12, **kwargs) -> str:
    """Generate a secure password (convenience function).
    
    Args:
        length: Password length
        **kwargs: Additional arguments for PasswordGenerator.generate()
        
    Returns:
        Generated password string
    """
    generator = PasswordGenerator()
    return generator.generate(length, **kwargs)
