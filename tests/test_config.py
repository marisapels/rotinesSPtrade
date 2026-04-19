from spy_trader import config


def test_defaults_match_strategy_md():
    assert config.RISK_FRACTION == 0.02
    assert config.HEAT_CAP == 0.06
    assert config.MONTHLY_BREAKER == 0.06
    assert config.BUY_STOP_EXPIRY_DAYS == 3
    assert config.TIME_STOP_BARS == 10
    assert config.CHANNEL_WIDTH_PCT == 0.027
    assert config.SAFEZONE_LOOKBACK == 10
    assert config.SAFEZONE_MULT == 2.0
    assert config.EMA_WEEKLY == 26
    assert config.EMA_IMPULSE == 13
    assert config.EMA_CHANNEL == 22
    assert config.STOCHASTIC == (5, 3, 3)
    assert config.MACD == (12, 26, 9)
    assert config.FORCE_INDEX_EMA == 2


def test_risk_fraction_can_be_overridden_by_env(monkeypatch):
    monkeypatch.setenv("RISK_FRACTION", "0.01")
    import importlib

    from spy_trader import config as cfg

    importlib.reload(cfg)
    assert cfg.RISK_FRACTION == 0.01
