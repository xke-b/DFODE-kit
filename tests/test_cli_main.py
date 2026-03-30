from collections import OrderedDict
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
COMMAND_LOADER_PATH = ROOT / "dfode_kit" / "cli_tools" / "command_loader.py"
MAIN_PATH = ROOT / "dfode_kit" / "cli_tools" / "main.py"


dfode_pkg = sys.modules.setdefault("dfode_kit", types.ModuleType("dfode_kit"))
dfode_pkg.__path__ = [str(ROOT / "dfode_kit")]
cli_pkg = sys.modules.setdefault("dfode_kit.cli_tools", types.ModuleType("dfode_kit.cli_tools"))
cli_pkg.__path__ = [str(ROOT / "dfode_kit" / "cli_tools")]

command_loader_spec = spec_from_file_location("dfode_kit.cli_tools.command_loader", COMMAND_LOADER_PATH)
command_loader = module_from_spec(command_loader_spec)
assert command_loader_spec.loader is not None
sys.modules["dfode_kit.cli_tools.command_loader"] = command_loader
command_loader_spec.loader.exec_module(command_loader)

main_spec = spec_from_file_location("dfode_kit.cli_tools.main", MAIN_PATH)
main = module_from_spec(main_spec)
assert main_spec.loader is not None
sys.modules["dfode_kit.cli_tools.main"] = main
main_spec.loader.exec_module(main)


class DummyCommand:
    def __init__(self):
        self.called_with = None

    def add_command_parser(self, subparsers):
        subparsers.add_parser("dummy", help="dummy command")

    def handle_command(self, args):
        self.called_with = args


def test_load_commands_sorts_discovered_modules(monkeypatch):
    package = SimpleNamespace(__path__=["fake-path"], __name__="fake.commands")
    alpha = SimpleNamespace(add_command_parser=lambda _: None, handle_command=lambda _: None)
    beta = SimpleNamespace(add_command_parser=lambda _: None, handle_command=lambda _: None)

    def fake_import_module(name):
        if name == "fake.commands":
            return package
        if name == "fake.commands.beta":
            return beta
        if name == "fake.commands.alpha":
            return alpha
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(command_loader.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(
        command_loader.pkgutil,
        "walk_packages",
        lambda path, prefix: [
            (None, "fake.commands.beta", False),
            (None, "fake.commands.alpha", False),
        ],
    )

    commands = command_loader.load_commands("fake.commands")

    assert list(commands) == ["alpha", "beta"]


def test_main_lists_commands_in_stable_order(monkeypatch, capsys):
    commands = OrderedDict(
        [
            ("augment", SimpleNamespace(add_command_parser=lambda _: None, handle_command=lambda _: None)),
            ("sample", SimpleNamespace(add_command_parser=lambda _: None, handle_command=lambda _: None)),
        ]
    )
    monkeypatch.setattr(main, "load_commands", lambda: commands)

    exit_code = main.main(["--list-commands"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.splitlines() == ["augment", "sample"]
    assert captured.err == ""


def test_main_dispatches_selected_command(monkeypatch):
    dummy = DummyCommand()
    monkeypatch.setattr(main, "load_commands", lambda: OrderedDict([("dummy", dummy)]))

    exit_code = main.main(["dummy"])

    assert exit_code == 0
    assert dummy.called_with.command == "dummy"


def test_main_returns_two_when_no_command_is_given(monkeypatch, capsys):
    monkeypatch.setattr(main, "load_commands", lambda: OrderedDict())

    exit_code = main.main([])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "usage:" in captured.err


def test_main_returns_one_when_command_handler_fails(monkeypatch, capsys):
    def raise_error(_args):
        raise RuntimeError("boom")

    failing_command = SimpleNamespace(
        add_command_parser=lambda subparsers: subparsers.add_parser("dummy", help="dummy command"),
        handle_command=raise_error,
    )
    monkeypatch.setattr(main, "load_commands", lambda: OrderedDict([("dummy", failing_command)]))

    exit_code = main.main(["dummy"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Command 'dummy' failed: boom" in captured.err


def test_main_returns_two_for_missing_handler(monkeypatch, capsys):
    handlerless = SimpleNamespace(
        add_command_parser=lambda subparsers: subparsers.add_parser("dummy", help="dummy command")
    )
    monkeypatch.setattr(main, "load_commands", lambda: OrderedDict([("dummy", handlerless)]))

    exit_code = main.main(["dummy"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Unknown command: dummy" in captured.err
