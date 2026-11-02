"""Where the mistakes memory lives when the gateway does not pass KAEASY_DATA_DIR to plugin code."""
import importlib.util
import shutil
from pathlib import Path

from kaeasy import memory

REPO = Path(memory.__file__).resolve().parent


def _install(root: Path) -> Path:
    """A copy of memory.py at <root>/shared-plugins/kaeasy, as on the Hub."""
    plugin = root / "shared-plugins" / "kaeasy"
    plugin.mkdir(parents=True)
    shutil.copy(REPO / "memory.py", plugin / "memory.py")
    return plugin


def _data_dir(plugin: Path) -> Path:
    spec = importlib.util.spec_from_file_location("kaeasy_memory_copy", plugin / "memory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.data_dir()


def test_shared_plugin_uses_the_fleet_dir_without_the_env(tmp_path, monkeypatch):
    monkeypatch.delenv("KAEASY_DATA_DIR", raising=False)
    plugin = _install(tmp_path)
    shared = tmp_path / "shared-knowledge" / "kaeasy"
    shared.mkdir(parents=True)
    assert _data_dir(plugin) == shared


def test_env_still_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("KAEASY_DATA_DIR", str(tmp_path / "elsewhere"))
    plugin = _install(tmp_path)
    (tmp_path / "shared-knowledge" / "kaeasy").mkdir(parents=True)
    assert _data_dir(plugin) == tmp_path / "elsewhere"


def test_no_shared_dir_falls_back(tmp_path, monkeypatch):
    monkeypatch.delenv("KAEASY_DATA_DIR", raising=False)
    plugin = _install(tmp_path)
    assert _data_dir(plugin) != tmp_path / "shared-knowledge" / "kaeasy"
