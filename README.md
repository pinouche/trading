# Project for algorithmic trading of (dynamic) delta hedging


## dev:

* `poetry install`
* `pre-commit install`
## Run main:

`python3 src/trading/main.py`

## Run tests:

To run test using pytest, simply run:

`pytest -sv`

## Setting up TW

First install and login onto the Trader Workstation.

Next you need to change your API settings by:

* Enable ActiveX and Socket Clients.
* Disable the Read-Only, i.e. the API needs to be able to place orders.


## Notes:

# Delta Hedging strategy (when selling options)

* If I sell 0DTE, I remove the overnight risk.
* The stocks I am considering are: ["TSLA", "NVDA", "ARM"] (maybe add more stocks in the future)
* I first sell an ITM covered call option, and then perform simple dynamic delta-hedging. It outperforms covered and naked.
* It is best to do this on high iv/hist iv.

# Important

Before running the program, two things must be done:

1) Change 'todays_date' variable to today's date in yyyymmdd format
2) Make sure that the 'cash_to_trade' variable is larger than 100*stock_price for the most expensive stock in 'stocks' list.
If this is not the case, it will throw an error: 'not enough cash to trade'.
