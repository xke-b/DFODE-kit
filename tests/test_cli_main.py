from collections import OrderedDict
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_INIT_PATH = ROOT / "dfode_kit" / "__init__.py"
COMMAND_LOADER_PATH = ROOT / "dfode_kit" / "cli" / "command_loader.py"
MAIN_PATH = ROOT / "dfode_kit" / "cli" / "main.py"


package_spec = spec_from_file_location("dfode_kit", PACKAGE_INIT_PATH)
dfode_pkg = module_from_spec(package_spec)
assert package_spec.loader is not None
sys.modules["dfode_kit"] = dfode_pkg
package_spec.loader.exec_module(dfode_pkg)

cli_pkg = sys.modules.setdefault("dfode_kit.cli", types.ModuleType("dfode_kit.cli"))
cli_pkg.__path__ = [str(ROOT / "dfode_kit" / "cli")]

command_loader_spec = spec_from_file_location("dfode_kit.cli.command_loader", COMMAND_LOADER_PATH)
command_loader = module_from_spec(command_loader_spec)
assert command_loader_spec.loader is not None
sys.modules["dfode_kit.cli.command_loader"] = command_loader
command_loader_spec.loader.exec_module(command_loader)

main_spec = spec_from_file_location("dfode_kit.cli.main", MAIN_PATH)
main = module_from_spec(main_spec)
assert main_spec.loader is not None
sys.modules["dfode_kit.cli.main"] = main
main_spec.loader.exec_module(main)


class DummyCommand:
    def __init__(self):
        self.called_with = None

    def add_command_parser(self, subparsers):
        subparsers.add_parser("dummy", help="dummy command")

    def handle_command(self, args):
        self.called_with = args


def test_load_command_specs_are_sorted():
    specs = command_loader.load_command_specs()
    assert list(specs) == sorted(specs)
    assert 'config' in specs
    assert 'init' in specs
    assert 'run-case' in specs


def test_main_lists_commands_in_stable_order(monkeypatch, capsys):
    specs = OrderedDict(
        [
            ("augment", {"module": "fake.augment", "help": "augment help"}),
            ("sample", {"module": "fake.sample", "help": "sample help"}),
        ]
    )
    monkeypatch.setattr(main, "load_command_specs", lambda: specs)

    exit_code = main.main(["--list-commands"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.splitlines() == ["augment", "sample"]
    assert captured.err == ""


def test_main_list_commands_does_not_import_command_modules(monkeypatch):
    specs = OrderedDict([("dummy", {"module": "fake.dummy", "help": "dummy help"})])
    load_calls = []

    monkeypatch.setattr(main, "load_command_specs", lambda: specs)
    monkeypatch.setattr(main, "load_command", lambda *args, **kwargs: load_calls.append(args))

    exit_code = main.main(["--list-commands"])

    assert exit_code == 0
    assert load_calls == []


def test_main_dispatches_selected_command(monkeypatch):
    dummy = DummyCommand()
    specs = OrderedDict([("dummy", {"module": "fake.dummy", "help": "dummy help"})])
    monkeypatch.setattr(main, "load_command_specs", lambda: specs)
    monkeypatch.setattr(main, "load_command", lambda name, command_specs=None: dummy)

    exit_code = main.main(["dummy"])

    assert exit_code == 0
    assert dummy.called_with.command == "dummy"


def test_main_returns_two_when_no_command_is_given(monkeypatch, capsys):
    monkeypatch.setattr(main, "load_command_specs", lambda: OrderedDict())

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
    specs = OrderedDict([("dummy", {"module": "fake.dummy", "help": "dummy help"})])
    monkeypatch.setattr(main, "load_command_specs", lambda: specs)
    monkeypatch.setattr(main, "load_command", lambda name, command_specs=None: failing_command)

    exit_code = main.main(["dummy"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Command 'dummy' failed: boom" in captured.err


def test_main_returns_two_for_missing_handler(monkeypatch, capsys):
    handlerless = SimpleNamespace(
        add_command_parser=lambda subparsers: subparsers.add_parser("dummy", help="dummy command")
    )
    specs = OrderedDict([("dummy", {"module": "fake.dummy", "help": "dummy help"})])
    monkeypatch.setattr(main, "load_command_specs", lambda: specs)
    monkeypatch.setattr(main, "load_command", lambda name, command_specs=None: handlerless)

    exit_code = main.main(["dummy"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Unknown command: dummy" in captured.err


def test_cli_tools_command_loader_shim_re_exports_cli_symbols():
    shim = import_module("dfode_kit.cli_tools.command_loader")
    direct = import_module("dfode_kit.cli.command_loader")

    assert shim.load_command_specs is direct.load_command_specs
    assert shim.load_command is direct.load_command
