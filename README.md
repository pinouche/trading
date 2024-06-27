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

# Delta Hedging strategy

* If I sell 0DTE, I remove the overnight risk.
* The stocks I am considering are: ["TSLA", "NVDA", "AMD", "ARM"].
* I first sell an ITM covered call option, and then perform simple dynamic delta-hedging.
