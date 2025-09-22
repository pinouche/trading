import numpy as np
import pytest

from trading.core.strategy.get_strike_and_stock import pick_strikes_for_strategy


@pytest.fixture
def strikes():
    # Uniform strikes every 5
    return np.array([80, 85, 90, 95, 100, 105, 110, 115, 120], dtype=float)


@pytest.fixture
def spot():
    # Spot that sits between 100 and 105
    return 103.0


def test_put_basic(strikes, spot):
    # nearest OTM put is 100 (below 103)
    res = pick_strikes_for_strategy(strikes, spot, strategy="put", distance_n_strikes=0)
    assert res == {"put_short": 100.0}


def test_call_basic(strikes, spot):
    # nearest OTM call is 105 (above 103)
    res = pick_strikes_for_strategy(strikes, spot, strategy="call", distance_n_strikes=0)
    assert res == {"call_short": 105.0}


def test_put_with_distance(strikes, spot):
    # one strike further OTM on put side: 95
    res = pick_strikes_for_strategy(strikes, spot, strategy="put", distance_n_strikes=1)
    assert res == {"put_short": 95.0}


def test_call_with_distance(strikes, spot):
    # one strike further OTM on call side: 110
    res = pick_strikes_for_strategy(strikes, spot, strategy="call", distance_n_strikes=1)
    assert res == {"call_short": 110.0}


def test_strangle_basic(strikes, spot):
    res = pick_strikes_for_strategy(strikes, spot, strategy="strangle", distance_n_strikes=0)
    assert res == {"put_short": 100.0, "call_short": 105.0}


def test_strangle_with_distance(strikes, spot):
    res = pick_strikes_for_strategy(strikes, spot, strategy="strangle", distance_n_strikes=2)
    # put: 100 -> 2 further OTM = 90; call: 105 -> 2 further OTM = 115
    assert res == {"put_short": 90.0, "call_short": 115.0}


def test_iron_condor_basic(strikes, spot):
    res = pick_strikes_for_strategy(
        strikes,
        spot,
        strategy="iron_condor",
        distance_n_strikes=0,
        wing_width_n_strikes=1,
    )
    # short put/call: 100/105, long wings 1 strike further OTM: 95/110
    assert res == {
        "put_short": 100.0,
        "put_long": 95.0,
        "call_short": 105.0,
        "call_long": 110.0,
    }


def test_iron_condor_with_distance_and_wing(strikes, spot):
    res = pick_strikes_for_strategy(
        strikes,
        spot,
        strategy="iron_condor",
        distance_n_strikes=1,
        wing_width_n_strikes=2,
    )
    # short put: 100 -> 95; long put: 95 -> 2 further OTM = 85
    # short call: 105 -> 110; long call: 110 -> 2 further OTM = 120
    assert res == {
        "put_short": 95.0,
        "put_long": 85.0,
        "call_short": 110.0,
        "call_long": 120.0,
    }


def test_negative_distance_raises(strikes, spot):
    with pytest.raises(ValueError, match="distance_n_strikes must be >= 0"):
        pick_strikes_for_strategy(strikes, spot, strategy="put", distance_n_strikes=-1)


def test_iron_condor_requires_positive_wing(strikes, spot):
    with pytest.raises(ValueError, match="wing_width_n_strikes must be > 0"):
        pick_strikes_for_strategy(
            strikes, spot, strategy="iron_condor", distance_n_strikes=0, wing_width_n_strikes=0
        )


def test_empty_strikes_raises(spot):
    with pytest.raises(ValueError, match="No strikes available"):
        pick_strikes_for_strategy(np.array([], dtype=float), spot, strategy="put")


def test_out_of_range_indices_raise_on_large_distance(strikes, spot):
    # below_idx for spot 103 is strike 100 at index 4; distance 10 -> negative index -> error
    with pytest.raises(ValueError, match="out of range"):
        pick_strikes_for_strategy(strikes, spot, strategy="put", distance_n_strikes=10)
    # above_idx for spot 103 is strike 105 at index 5; distance 10 -> index beyond n -> error
    with pytest.raises(ValueError, match="out of range"):
        pick_strikes_for_strategy(strikes, spot, strategy="call", distance_n_strikes=10)


def test_spot_exactly_on_strike_edges():
    strikes = np.array([90.0, 100.0, 110.0], dtype=float)
    spot = 100.0
    # below should be 90, above should be 110
    assert pick_strikes_for_strategy(strikes, spot, "put") == {"put_short": 90.0}
    assert pick_strikes_for_strategy(strikes, spot, "call") == {"call_short": 110.0}
    assert pick_strikes_for_strategy(strikes, spot, "strangle") == {
        "put_short": 90.0,
        "call_short": 110.0,
    }


def test_spot_below_all_strikes_raises():
    strikes = np.array([80.0, 90.0, 100.0], dtype=float)
    spot = 70.0
    with pytest.raises(ValueError, match="out of range"):
        pick_strikes_for_strategy(strikes, spot, "put")
    with pytest.raises(ValueError, match="out of range"):
        pick_strikes_for_strategy(strikes, spot, "strangle")


def test_spot_above_all_strikes_raises():
    strikes = np.array([80.0, 90.0, 100.0], dtype=float)
    spot = 130.0
    with pytest.raises(ValueError, match="out of range"):
        pick_strikes_for_strategy(strikes, spot, "call")
    with pytest.raises(ValueError, match="out of range"):
        pick_strikes_for_strategy(strikes, spot, "strangle")