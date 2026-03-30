import importlib
import pkgutil


def load_commands(package_name='dfode_kit.cli_tools.commands'):
    commands = {}

    package = importlib.import_module(package_name)
    discovered_modules = sorted(
        pkgutil.walk_packages(package.__path__, package.__name__ + '.'),
        key=lambda item: item[1],
    )

    for _, module_name, _ in discovered_modules:
        module = importlib.import_module(module_name)

        if hasattr(module, 'add_command_parser') and hasattr(module, 'handle_command'):
            commands[module_name.split('.')[-1]] = module

    return commands
