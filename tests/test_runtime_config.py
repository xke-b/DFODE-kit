from dfode_kit.runtime import config as runtime_config


def test_runtime_config_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg'))

    path = runtime_config.get_config_path()
    assert path == (tmp_path / 'xdg' / 'dfode-kit' / 'config.json')

    config, saved_path = runtime_config.set_config_value('default_np', '8')
    assert saved_path == path
    assert config['default_np'] == 8

    loaded = runtime_config.load_runtime_config()
    assert loaded['default_np'] == 8

    config, _ = runtime_config.unset_config_value('default_np')
    assert config['default_np'] == runtime_config.DEFAULT_CONFIG['default_np']


def test_validate_config_key_rejects_unknown():
    try:
        runtime_config.validate_config_key('nope')
    except ValueError as exc:
        assert 'Unknown config key' in str(exc)
    else:
        raise AssertionError('expected ValueError')


def test_legacy_runtime_config_shim_matches_new_module():
    from dfode_kit import runtime_config as legacy_runtime_config

    assert legacy_runtime_config.get_config_path is runtime_config.get_config_path
    assert legacy_runtime_config.resolve_runtime_config is runtime_config.resolve_runtime_config
