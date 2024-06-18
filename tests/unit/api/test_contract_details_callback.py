from trading.api.ibapi_class import IBapi


def test_options_contract(app: IBapi, options_strikes: list[float]) -> None:

    assert isinstance(options_strikes, list)
    assert isinstance(options_strikes[0], float)

    app.nextorderId += 1  # type: ignore
