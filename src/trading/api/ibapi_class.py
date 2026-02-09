"""Ibapi Class that inherits from both EWrapper and EClient."""

import threading
from decimal import Decimal
from loguru import logger

from ibapi.client import EClient
from ibapi.common import TickAttrib, SetOfString, SetOfFloat
from ibapi.contract import Contract, ContractDetails
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper

from trading.core.data_models.config_data_models import StockInfo
from trading.core.data_models.option_chains import OptionsChain


class IBapi(EWrapper, EClient):
    """Ibapi Class that inherits from both EWrapper and EClient. This is where the logic for handling incoming messages
    through the Ewrapper happens.
    """

    def __init__(self) -> None:
        """Define variables to be assigned returned value from the Ewrapper"""
        EClient.__init__(self, self)

        # orders details dict
        self.order_status: dict = {}
        # order execution details
        self.execution_details: dict = {}

        # next valid order
        self.nextorderId: int | None = None
        self._lock = threading.Lock()

        # contract details for options and stocks
        self.options_chain_dict = {}
        self.options_contract_details_dict: dict = {}
        self.stocks_contract_details_dict: dict = {}

        # data structure to hold current requests from reqMktData
        self.list_ask_bid_dict: dict = {}
        self.current_asset_price_dict: dict[int, StockInfo] = {}
        self.current_option_iv_dict: dict = {}

        # data from scanner
        self.scanner_data: dict = {}

    def nextValidId(self, orderId: int | None) -> None:
        """Callback function to update the next valid order id"""
        with self._lock:
            self.nextorderId = orderId
        logger.info(f"The next valid order id is: {self.nextorderId}.")

    def get_next_req_id(self) -> int:
        """Get the next valid order id and increment it in a thread-safe way."""
        with self._lock:
            if self.nextorderId is None:
                raise ValueError("nextorderId is None. Is the app connected?")
            res = self.nextorderId
            self.nextorderId += 1
            return res

    def contractDetails(self, reqId: int, contract_details: ContractDetails) -> None:
        """Callback function to receive contract details for option (OPT) type contracts."""

        # we use a different dict to store options and stocks data
        if contract_details.contract.secType == "OPT":
            if reqId not in self.options_contract_details_dict:
                self.options_contract_details_dict[reqId] = []
            self.options_contract_details_dict[reqId].append(contract_details)

        elif contract_details.contract.secType == "STK":
            self.stocks_contract_details_dict[reqId] = [contract_details]


    def securityDefinitionOptionParameter(self,
                                          reqId: int,
                                          exchange: str,
                                          underlyingConId: int,
                                          tradingClass: str,
                                          multiplier: int,
                                          expirations: SetOfString,
                                          strikes: SetOfFloat) -> None:
        """Callback function to receive available strikes and expirations for an underlying."""

        print(f"Received securityDefinitionOptionParameter for reqId {reqId}.")

        self.options_chain_dict[reqId] = OptionsChain(
            exchange=exchange,
            underlyingConId=underlyingConId,
            tradingClass=tradingClass,
            multiplier=multiplier,
            expirations=sorted(list(expirations)),
            strikes=sorted(list(strikes)),
        )

    def securityDefinitionOptionParameterEnd(self, reqId: int) -> None:
        """Called once all option chain data has been received for this reqId."""
        print(f"Option chain request {reqId} completed. "
              f"Found {len(self.options_chain_dict[reqId]['strikes'])} strikes "
              f"and {len(self.options_chain_dict[reqId]['expirations'])} expirations.")

    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState: OrderState) -> None:
        """Overwrite Ewrapper openOrder callback function."""
        logger.info(f'''openOrder id:, {orderId}, {contract.symbol}, {contract.secType}, @, {contract.exchange}, ':',
                    {order.action}, {order.orderType}, {order.totalQuantity}, {orderState.status}.''')

    def execDetails(self, reqId: int, contract: Contract, execution: Execution) -> None:
        """Overwrite Ewrapper execDetails callback function."""
        logger.info(
            f'''Order Executed: {reqId}, {contract.symbol}, {contract.secType}, {contract.currency}, {execution.execId},
        {execution.orderId}, {execution.shares}, {execution.lastLiquidity}.''')
        self.execution_details[execution.orderId] = {"contract": contract, "execution": execution}

    def orderStatus(self, orderId: int, status: str, filled: Decimal, remaining: Decimal, avgFullPrice: float,
                    permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str,
                    mktCapPrice: float) -> None:
        """Overwrite Ewrapper orderStatus callback function."""
        logger.info(f'''orderStatus - orderid: {orderId}, status:, {status}, filled, {filled}, remaining, {remaining},
                    lastFillPrice, {lastFillPrice}''')
        self.order_status[orderId] = {"status": status, "filled": filled, "remaining": remaining}
        logger.info(f"We print order status dict {self.order_status}.")

    def tickOptionComputation(self, reqId: int, tickType: int, tickAttrib: int, impliedVol: float,
                              delta: float, optPrice: float, pvDividend: float, gamma: float, vega: float, theta: float,
                              undPrice: float) -> None:
        """Gather data from the requestMktdata for options contract"""
        logger.info(
            f'''TickOptionComputation. TickerId: {reqId}, TickType: {tickType}, TickAttrib: {tickAttrib},
                ImpliedVolatility: {impliedVol}, Delta: {delta}, OptionPrice: {optPrice}, pvDividend: {pvDividend},
                Gamma: {gamma} Vega: {vega} Theta: {theta} UnderlyingPrice: {undPrice}.''')

        if tickType == 12:  # this is the ticker corresponding to last
            self.current_option_iv_dict[reqId] = impliedVol

    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: TickAttrib) -> None:
        """Callback function to obtain tickprice information when calling RqtMktData Eclient function."""
        if reqId not in self.current_asset_price_dict:
            self.current_asset_price_dict[reqId] = StockInfo()
        if reqId not in self.list_ask_bid_dict:
            self.list_ask_bid_dict[reqId] = []

        if tickType == 1 or tickType == 2:

            # Append the new price to the list
            self.list_ask_bid_dict[reqId].append(price)

            spread_side = "bid"
            if tickType == 2:
                spread_side = "ask"
            logger.info(f'The current {spread_side} price is: {price} for reqId {reqId}.')

        if len(self.list_ask_bid_dict[reqId]) == 2:
            self.current_asset_price_dict[reqId].price.append(self.list_ask_bid_dict[reqId])
            self.list_ask_bid_dict[reqId] = []  # reset the entry

    def marketDataType(self, reqId: int, marketDataType: int) -> None:
        """Ewrapper method to receive if market data is live/delayed/frozen from reqMktData()."""
        if reqId not in self.current_asset_price_dict:
            self.current_asset_price_dict[reqId] = StockInfo()
        if reqId not in self.list_ask_bid_dict:
            self.list_ask_bid_dict[reqId] = []

        if marketDataType == 1:
            # Append the new price to the list
            self.current_asset_price_dict[reqId].market_is_live = True

            logger.info(
                f'Live data is: {True} for reqId {reqId}.')

    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails,
                    distance: str, benchmark: str, projection: str, legsStr: str) -> None:
        """Ewrapper method to receive scanner data."""
        logger.info(
            f"scannerData. reqId: {reqId}, rank: {rank}, contractDetails: {contractDetails}, "
            f"distance: {distance}, benchmark: {benchmark}, projection: {projection}, legsStr: {legsStr}.")
        self.scanner_data[rank] = [contractDetails, distance, benchmark, projection, legsStr]

    def scannerDataEnd(self, reqId: int) -> None:
        """EWrapper methods to close the scanner."""
        logger.info("ScannerDataEnd!")
        # end the scanner
        self.cancelScannerSubscription(reqId)
