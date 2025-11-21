import string

import pytest

from swiss_knife.automation.password_generator import (
    PasswordGenerator,
    generate_password,
)


class TestPasswordGenerator:

    def test_init(self):
        generator = PasswordGenerator()
        assert generator.lowercase == string.ascii_lowercase
        assert generator.uppercase == string.ascii_uppercase
        assert generator.digits == string.digits

    def test_generate_default(self):
        generator = PasswordGenerator()
        password = generator.generate()

        assert len(password) == 12
        assert any(c in string.ascii_lowercase for c in password)
        assert any(c in string.ascii_uppercase for c in password)
        assert any(c in string.digits for c in password)

    def test_generate_custom_length(self):
        generator = PasswordGenerator()

        for length in [8, 16, 32]:
            password = generator.generate(length=length)
            assert len(password) == length

    def test_generate_no_uppercase(self):
        generator = PasswordGenerator()
        password = generator.generate(include_uppercase=False, min_uppercase=0)

        assert not any(c in string.ascii_uppercase for c in password)
        assert any(c in string.ascii_lowercase for c in password)

    def test_generate_no_symbols(self):
        generator = PasswordGenerator()
        password = generator.generate(include_symbols=False, min_symbols=0)

        assert not any(c in generator.symbols for c in password)

    def test_generate_exclude_ambiguous(self):
        generator = PasswordGenerator()
        password = generator.generate(exclude_ambiguous=True, length=50)

        ambiguous = "0O1lI"
        assert not any(c in ambiguous for c in password)

    def test_generate_minimum_requirements(self):
        generator = PasswordGenerator()
        password = generator.generate(
            length=20, min_uppercase=3, min_lowercase=3, min_digits=3, min_symbols=2
        )

        uppercase_count = sum(1 for c in password if c in string.ascii_uppercase)
        lowercase_count = sum(1 for c in password if c in string.ascii_lowercase)
        digit_count = sum(1 for c in password if c in string.digits)
        symbol_count = sum(1 for c in password if c in generator.symbols)

        assert uppercase_count >= 3
        assert lowercase_count >= 3
        assert digit_count >= 3
        assert symbol_count >= 2

    def test_generate_invalid_length(self):
        generator = PasswordGenerator()

        with pytest.raises(ValueError):
            generator.generate(length=0)

        with pytest.raises(ValueError):
            generator.generate(length=-1)

    def test_generate_impossible_requirements(self):
        generator = PasswordGenerator()

        # Requirements exceed length
        with pytest.raises(ValueError):
            generator.generate(length=5, min_uppercase=3, min_lowercase=3, min_digits=3)

    def test_generate_no_character_types(self):
        generator = PasswordGenerator()

        with pytest.raises(ValueError):
            generator.generate(
                include_uppercase=False,
                include_lowercase=False,
                include_digits=False,
                include_symbols=False,
            )

    def test_generate_multiple(self):
        generator = PasswordGenerator()
        passwords = generator.generate_multiple(5, length=10)

        assert len(passwords) == 5
        assert all(len(p) == 10 for p in passwords)
        assert len(set(passwords)) == 5  # All should be unique

    def test_generate_multiple_invalid_count(self):
        generator = PasswordGenerator()

        with pytest.raises(ValueError):
            generator.generate_multiple(0)

        with pytest.raises(ValueError):
            generator.generate_multiple(-1)

    def test_check_strength_empty(self):
        generator = PasswordGenerator()
        result = generator.check_strength("")

        assert result["score"] == 0
        assert result["strength"] == "Very Weak"
        assert "Password is empty" in result["feedback"]

    def test_check_strength_weak(self):
        generator = PasswordGenerator()
        result = generator.check_strength("123")

        assert result["score"] < 40
        assert result["strength"] in ["Very Weak", "Weak"]
        assert result["length"] == 3
        assert not result["has_lowercase"]
        assert not result["has_uppercase"]
        assert result["has_digits"]
        assert not result["has_symbols"]

    def test_check_strength_strong(self):
        generator = PasswordGenerator()
        result = generator.check_strength("MyStr0ng!P@ssw0rd")

        assert result["score"] >= 60
        assert result["strength"] in ["Strong", "Very Strong"]
        assert result["has_lowercase"]
        assert result["has_uppercase"]
        assert result["has_digits"]
        assert result["has_symbols"]

    def test_check_strength_common_password(self):
        generator = PasswordGenerator()
        result = generator.check_strength("password")

        assert result["score"] < 20
        assert "Avoid common passwords" in result["feedback"]

    def test_check_strength_repetitive(self):
        generator = PasswordGenerator()
        result = generator.check_strength("aaaaaaaaaa")

        assert "Reduce repeated characters" in result["feedback"]


def test_generate_password_convenience_function():
    password = generate_password(length=15)

    assert len(password) == 15
    assert any(c in string.ascii_lowercase for c in password)
    assert any(c in string.ascii_uppercase for c in password)
    assert any(c in string.digits for c in password)
