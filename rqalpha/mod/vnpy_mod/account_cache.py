# encoding: UTF-8
import six
from datetime import date

from rqalpha.utils import json as json_utils
from rqalpha.const import SIDE
from .utils import SIDE_REVERSE

# TODO: 实现以下三个类


class PositionCache(object):
    def __init__(self, order_book_id):
        self._order_book_id = order_book_id
        self._current_date = date.today()

    def __to_dict__(self):
        position_dict = {}
        return position_dict

    def update(self, vnpy_position):
        position = vnpy_position.position
        frozen = vnpy_position.frozen
        price = vnpy_position.price
        pre_position = vnpy_position.ydPosition
        if SIDE_REVERSE[vnpy_position.direction] == SIDE.BUY:
            pass
        if SIDE_REVERSE[vnpy_position.direction] == SIDE.SELL:
            pass


class PortfolioCache(object):
    def __init__(self):
        self._positions = {}

        self._yesterday_portfolio_value = None
        self._cash = None
        self._total_commission = None

    def __to_dict__(self):
        pass

    def update_position(self, order_book_id, vnpy_position):
        if order_book_id not in self._positions:
            self._positions[order_book_id] = PositionCache(order_book_id)
        self._positions[order_book_id].update(vnpy_position)

    def update(self, vnpy_account):
        self._yesterday_portfolio_value = vnpy_account.balance
        self._cash = vnpy_account.available
        self._total_commission = vnpy_account.commission

    def insert_trades(self, trade):
        pass


class AccountCache(object):
    def __init__(self):
        self.portfolio = PortfolioCache()
        self.daily_trades = None
        self.daily_orders = None

    def __to_dict__(self):
        account_dict = {
            "portfolio": self.portfolio.__to_dict__(),
            "daily_orders": {order_id: order.__to_dict__() for order_id, order in six.iteritems(self.daily_orders)},
            "daily_trades": [trade.__to_dict__() for trade in self.daily_trades],
        }
        return account_dict

    def get_state(self):
        return json_utils.convert_dict_to_json(self.__to_dict__()).encode('utf-8')

    def update_position(self, order_book_id, vnpy_position):
        self.portfolio.update_position(order_book_id, vnpy_position)

    def update_portfolio(self, vnpy_account):
        self.portfolio.update(vnpy_account)

    def insert_hist_order(self, vnpy_order):
        pass

    def insert_hist_trade(self, vnpy_trade):
        pass
