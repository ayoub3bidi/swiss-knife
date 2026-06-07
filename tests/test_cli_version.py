import sys
from unittest.mock import patch

import pytest

import swiss_knife
from swiss_knife.cli.csv_cli import main as csv_main
from swiss_knife.cli.duplicate_finder import main as duplicates_main
from swiss_knife.cli.password_cli import main as password_main
from swiss_knife.cli.rename_cli import main as rename_main


@pytest.mark.parametrize(
    ("main_fn", "argv_base", "prog"),
    [
        (duplicates_main, ["sk-duplicates"], "sk-duplicates"),
        (csv_main, ["sk-csv"], "sk-csv"),
        (password_main, ["sk-password"], "sk-password"),
        (rename_main, ["sk-rename"], "sk-rename"),
    ],
)
def test_cli_version_long_flag(main_fn, argv_base, prog, capsys):
    with patch.object(sys, "argv", [*argv_base, "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main_fn()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == f"{prog} {swiss_knife.__version__}"


@pytest.mark.parametrize(
    ("main_fn", "argv_base", "prog"),
    [
        (duplicates_main, ["sk-duplicates"], "sk-duplicates"),
        (password_main, ["sk-password"], "sk-password"),
    ],
)
def test_cli_version_short_flag(main_fn, argv_base, prog, capsys):
    with patch.object(sys, "argv", [*argv_base, "-V"]):
        with pytest.raises(SystemExit) as exc_info:
            main_fn()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == f"{prog} {swiss_knife.__version__}"
