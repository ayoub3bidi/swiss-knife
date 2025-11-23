import sys
from unittest.mock import patch

import pytest

from swiss_knife.cli.password_cli import main


class TestPasswordCLI:

    def test_generate_default_password(self, capsys):
        with patch.object(sys, "argv", ["sk-password"]):
            main()

        captured = capsys.readouterr()
        password = captured.out.strip()
        assert len(password) == 12  # Default length
        assert password  # Not empty

    def test_generate_custom_length(self, capsys):
        with patch.object(sys, "argv", ["sk-password", "--length", "20"]):
            main()

        captured = capsys.readouterr()
        password = captured.out.strip()
        assert len(password) == 20

    def test_generate_multiple_passwords(self, capsys):
        with patch.object(sys, "argv", ["sk-password", "--count", "3", "--length", "10"]):
            main()

        captured = capsys.readouterr()
        passwords = captured.out.strip().split("\n")
        assert len(passwords) == 3
        assert all(len(p) == 10 for p in passwords)
        # Verify they're all different
        assert len(set(passwords)) == 3

    def test_generate_no_symbols(self, capsys):
        with patch.object(sys, "argv", ["sk-password", "--length", "16", "--no-symbols"]):
            main()

        captured = capsys.readouterr()
        password = captured.out.strip()
        # Verify no symbols present
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        assert not any(s in password for s in symbols)

    def test_generate_exclude_ambiguous(self, capsys):
        with patch.object(
            sys, "argv", ["sk-password", "--length", "20", "--exclude-ambiguous"]
        ):
            main()

        captured = capsys.readouterr()
        password = captured.out.strip()
        ambiguous = "0O1lI"
        assert not any(c in password for c in ambiguous)

    def test_check_password_strength_strong(self, capsys):
        test_password = "MyStr0ng!Pass@2024"
        with patch.object(sys, "argv", ["sk-password", "--check", test_password]):
            main()

        captured = capsys.readouterr()
        output = captured.out
        assert "Password Strength Analysis" in output
        assert "Strength:" in output
        assert "Score:" in output

    def test_check_password_strength_weak(self, capsys):
        test_password = "123"
        with patch.object(sys, "argv", ["sk-password", "--check", test_password]):
            main()

        captured = capsys.readouterr()
        output = captured.out
        assert "Password Strength Analysis" in output
        assert "Recommendations:" in output

    def test_generate_with_minimums(self, capsys):
        with patch.object(
            sys,
            "argv",
            [
                "sk-password",
                "--length",
                "16",
                "--min-uppercase",
                "3",
                "--min-lowercase",
                "3",
                "--min-digits",
                "3",
                "--min-symbols",
                "2",
            ],
        ):
            main()

        captured = capsys.readouterr()
        password = captured.out.strip()
        assert len(password) == 16

        # Count character types
        uppercase = sum(1 for c in password if c.isupper())
        lowercase = sum(1 for c in password if c.islower())
        digits = sum(1 for c in password if c.isdigit())

        assert uppercase >= 3
        assert lowercase >= 3
        assert digits >= 3

    def test_invalid_length_error(self, capsys):
        with patch.object(sys, "argv", ["sk-password", "--length", "0"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_impossible_constraints_error(self, capsys):
        with patch.object(
            sys,
            "argv",
            [
                "sk-password",
                "--length",
                "5",
                "--min-uppercase",
                "10",  # Impossible: more than total length
            ],
        ):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "Error:" in captured.out

    def test_help(self):
        with patch.object(sys, "argv", ["sk-password", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
