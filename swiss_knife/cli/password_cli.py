#!/usr/bin/env python3

import argparse

from ..automation.password_generator import PasswordGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate secure passwords with customizable options"
    )
    parser.add_argument(
        "--length",
        "-l",
        type=int,
        default=12,
        help="Password length (default: 12)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of passwords to generate (default: 1)",
    )
    parser.add_argument(
        "--no-uppercase",
        action="store_true",
        help="Exclude uppercase letters",
    )
    parser.add_argument(
        "--no-lowercase",
        action="store_true",
        help="Exclude lowercase letters",
    )
    parser.add_argument(
        "--no-digits",
        action="store_true",
        help="Exclude digits",
    )
    parser.add_argument(
        "--no-symbols",
        action="store_true",
        help="Exclude symbols",
    )
    parser.add_argument(
        "--exclude-ambiguous",
        action="store_true",
        help="Exclude ambiguous characters (0, O, 1, l, I)",
    )
    parser.add_argument(
        "--min-uppercase",
        type=int,
        default=1,
        help="Minimum uppercase letters (default: 1)",
    )
    parser.add_argument(
        "--min-lowercase",
        type=int,
        default=1,
        help="Minimum lowercase letters (default: 1)",
    )
    parser.add_argument(
        "--min-digits",
        type=int,
        default=1,
        help="Minimum digits (default: 1)",
    )
    parser.add_argument(
        "--min-symbols",
        type=int,
        default=0,
        help="Minimum symbols (default: 0)",
    )
    parser.add_argument(
        "--check",
        metavar="PASSWORD",
        help="Check strength of a password instead of generating",
    )

    args = parser.parse_args()

    generator = PasswordGenerator()

    # Check password strength mode
    if args.check:
        result = generator.check_strength(args.check)
        print("\nPassword Strength Analysis:")
        print(f"  Strength: {result['strength']}")
        print(f"  Score: {result['score']}/100")
        print(f"  Length: {result['length']} characters")
        print("\nCharacter Types:")
        print(f"  Lowercase: {'✓' if result['has_lowercase'] else '✗'}")
        print(f"  Uppercase: {'✓' if result['has_uppercase'] else '✗'}")
        print(f"  Digits: {'✓' if result['has_digits'] else '✗'}")
        print(f"  Symbols: {'✓' if result['has_symbols'] else '✗'}")
        print(f"  Unique chars: {result['unique_chars']}")

        if result["feedback"]:
            print("\nRecommendations:")
            for feedback in result["feedback"]:
                print(f"  • {feedback}")
        return

    # Generate password(s)
    try:
        kwargs = {
            "length": args.length,
            "include_uppercase": not args.no_uppercase,
            "include_lowercase": not args.no_lowercase,
            "include_digits": not args.no_digits,
            "include_symbols": not args.no_symbols,
            "exclude_ambiguous": args.exclude_ambiguous,
            "min_uppercase": args.min_uppercase,
            "min_lowercase": args.min_lowercase,
            "min_digits": args.min_digits,
            "min_symbols": args.min_symbols,
        }

        if args.count == 1:
            password = generator.generate(**kwargs)
            print(password)
        else:
            passwords = generator.generate_multiple(args.count, **kwargs)
            for password in passwords:
                print(password)

    except ValueError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
