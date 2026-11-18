import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
# Some test modules import the plugin's files as top-level modules ("import lint"), which only works
# when the plugin directory itself is on sys.path. Without this the older suites fail to collect, which
# hid a real count behind a collection error.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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
