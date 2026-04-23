from pathlib import Path
from unittest.mock import patch

from src.extensions.run_cpp_profile import compile_cpp


def test_compile_cpp_raises_if_compiler_missing(tmp_path: Path) -> None:
    with patch("src.extensions.run_cpp_profile.shutil.which", return_value=None):
        try:
            compile_cpp(tmp_path / "risk_profile.cpp", tmp_path / "risk_profile")
            assert False, "Expected RuntimeError when g++ is unavailable"
        except RuntimeError as e:
            assert "g++ not found" in str(e)
