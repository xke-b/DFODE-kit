import importlib
from collections import OrderedDict


_COMMAND_SPECS = {
    'augment': {
        'module': 'dfode_kit.cli.commands.augment',
        'help': 'Perform data augmentation.',
    },
    'h52npy': {
        'module': 'dfode_kit.cli.commands.h52npy',
        'help': 'Convert HDF5 scalar fields to NumPy array.',
    },
    'init': {
        'module': 'dfode_kit.cli.commands.init',
        'help': 'Initialize canonical cases from explicit presets.',
    },
    'config': {
        'module': 'dfode_kit.cli.commands.config',
        'help': 'Manage persistent runtime configuration.',
    },
    'label': {
        'module': 'dfode_kit.cli.commands.label',
        'help': 'Label data.',
    },
    'run-case': {
        'module': 'dfode_kit.cli.commands.run_case',
        'help': 'Run a DeepFlame/OpenFOAM case using stored configuration.',
    },
    'sample': {
        'module': 'dfode_kit.cli.commands.sample',
        'help': 'Perform sampling.',
    },
    'train': {
        'module': 'dfode_kit.cli.commands.train',
        'help': 'Train the model.',
    },
}


def load_command_specs():
    return OrderedDict(sorted(_COMMAND_SPECS.items(), key=lambda item: item[0]))


def load_command(command_name, command_specs=None):
    command_specs = command_specs or load_command_specs()
    if command_name not in command_specs:
        raise KeyError(command_name)

    module_name = command_specs[command_name]['module']
    return importlib.import_module(module_name)
