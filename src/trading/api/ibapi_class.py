"""Ibapi Class that inherits from both EWrapper and EClient."""

from decimal import Decimal

from dotenv import dotenv_values
from ibapi.client import EClient
from ibapi.common import TickAttrib
from ibapi.contract import Contract, ContractDetails
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper
from loguru import logger

from trading.core.data_models.data_models import StockInfo
from trading.utils import config_load

env_vars = dotenv_values(".env")
config_vars = config_load("./config.yaml")


class IBapi(EWrapper, EClient):
    """Ibapi Class that inherits from both EWrapper and EClient. This is where the logic for handling incoming messages
    through the Ewrapper happens.
    """

    def __init__(self) -> None:
        """Define variables to be assigned returned value from the Ewrapper"""
        EClient.__init__(self, self)

        # orders details dict
        self.order_status: dict = {}

        # next valid order
        self.nextorderId: int | None = None

        self.dic_orderid_to_ticker: dict = {}

        # build a dic for each stock to store price info and market_is_live
        self.stock_price_dic = {}
        for key, values in config_vars["stocks"].items():
            self.stock_price_dic[key] = StockInfo(stock=key)

        # contract details for options
        self.options_strike_price_dict: dict = {}
        # data structure to hold current price requests
        self.stock_current_price_dict: dict = {}

    def nextValidId(self, orderId: int | None) -> None:
        """Callback function to update the next valid order id"""
        self.nextorderId = orderId
        logger.info(f"The next valid order id is: {self.nextorderId}.")

    def contractDetails(self, reqId: int, contractDetails: ContractDetails) -> None:
        """Callback function to receive contract details for option (OPT) type contracts."""
        contract = contractDetails.contract

        if contract.secType == "OPT":
            if contract.symbol not in self.options_strike_price_dict.keys():
                self.options_strike_price_dict[contract.symbol] = []
            self.options_strike_price_dict[contract.symbol].append(contract.strike)

    def orderStatus(self, orderId: int, status: str, filled: Decimal, remaining: Decimal, avgFullPrice: float,
                    permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float) -> None:
        """Overwrite Ewrapper orderStatus callback function."""
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)
        self.order_status[orderId] = {"status": status, "filled": filled, "remaining": remaining}

    def get_open_order_status(self) -> None:
        """Trigger the orderStatus EWrapper callback function."""
        self.order_status = {}  # reset the dictionary
        self.reqOpenOrders()

    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState: OrderState) -> None:
        """Overwrite Ewrapper openOrder callback function."""
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId: int, contract: Contract, execution: Execution) -> None:
        """Overwrite Ewrapper execDetails callback function."""
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)

    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: TickAttrib) -> None:
        """Callback function to obtain tickprice information when calling RqtMktData Eclient function."""
        if reqId not in self.stock_current_price_dict.keys():
            self.stock_current_price_dict[reqId] = []
        if tickType == 1 or tickType == 2:
            self.stock_current_price_dict[reqId].append(price)
            logger.info(f'The current ask price is: {price} for stock.')

    def marketDataType(self, reqId: int, marketDataType: int) -> None:
        """Ewrapper method to receive if market data is live/delayed/frozen from reqMktData()."""
        if marketDataType == 1:
            ticker_symbol = self.dic_orderid_to_ticker[reqId]
            self.stock_price_dic[ticker_symbol].market_is_live = True
            logger.info(
                f'Live data is: {True} for stock {self.stock_price_dic[ticker_symbol].stock}.')
