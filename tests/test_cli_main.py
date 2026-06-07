import sys
from unittest.mock import patch

import pytest

import swiss_knife
from swiss_knife.cli.main import main


def test_sk_version_long_flag(capsys):
    with patch.object(sys, "argv", ["sk", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == f"swiss-knife {swiss_knife.__version__}"


def test_sk_version_short_flag(capsys):
    with patch.object(sys, "argv", ["sk", "-V"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == f"swiss-knife {swiss_knife.__version__}"


def test_sk_help_lists_tools(capsys):
    with patch.object(sys, "argv", ["sk", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    for tool in ("sk-duplicates", "sk-csv", "sk-password", "sk-rename"):
        assert tool in captured.out


def test_sk_no_args_prints_help(capsys):
    with patch.object(sys, "argv", ["sk"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "Installed tools:" in captured.out
    assert "sk-duplicates" in captured.out


def test_sk_unknown_argument_exits_nonzero():
    with patch.object(sys, "argv", ["sk", "unknown"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0
