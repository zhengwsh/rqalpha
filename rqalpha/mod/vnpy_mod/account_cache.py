# encoding: UTF-8
import six

from rqalpha.utils import json as json_utils

# TODO: 实现以下三个类


class PositionCache(object):
    def __init__(self, order_book_id):
        pass

    def __to_dict__(self):
        pass

    def update(self, vnpy_position):
        # TODO: 确定字段对应关系
        pass


class PortfolioCache(object):
    def __init__(self):
        self._positions = {}
        pass

    def __to_dict__(self):
        pass

    def update_position(self, order_book_id, vnpy_position):
        if order_book_id not in self._positions:
            self._positions[order_book_id] = PositionCache(order_book_id)
        self._positions[order_book_id].update(vnpy_position)

    def update(self, vnpy_account):
        pass


class AccountCache(object):
    def __init__(self):
        self.portfolio = PortfolioCache()

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
