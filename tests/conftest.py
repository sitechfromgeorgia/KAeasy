import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load_plugin():
    # The repo root is the plugin package; load it as "kaeasy" regardless of the checkout folder name.
    spec = importlib.util.spec_from_file_location("kaeasy", ROOT / "__init__.py",
                                                  submodule_search_locations=[str(ROOT)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kaeasy"] = mod
    spec.loader.exec_module(mod)
    return mod


plugin = _load_plugin()


@pytest.fixture
def kaeasy():
    return plugin


@pytest.fixture(autouse=True)
def _data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("KAEASY_DATA_DIR", str(tmp_path / "data"))
