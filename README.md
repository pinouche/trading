# Project for algorithmic trading of (dynamic) delta hedging


## dev:

* `poetry install`
* `pre-commit install`
*
## Run main:

`python3 src/trading/main.py`

## Run tests:

To run test using pytest, simply run:

`pytest -sv`

## Notes:

# Delta Hedging strategy (when selling options)

* If I sell 0DTE, I remove the overnight risk.
* The stocks I am considering are: ["TSLA", "NVDA", "AMD", "ARM"] (maybe add more stocks in the future)
* I first sell an ITM covered call option, and then perform simple dynamic delta-hedging. It outperforms covered and naked.
* It is best to do this on high iv/hist iv


# Delta Hedging strategy (when buying options)

* Think about a strategy here (buy a put, buy shares equivalent)
