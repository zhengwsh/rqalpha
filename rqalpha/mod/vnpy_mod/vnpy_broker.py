# encoding: UTF-8

from rqalpha.interface import AbstractBroker
from rqalpha.trader.account import init_accounts

from .vnpy_engine import get_engine


class VNPYBroker(AbstractBroker):
    def __init__(self, env):
        self.env = env

        self._accounts = None

        self._engine = get_engine()
        self._engine.set_broker(self)
        self._vnpy_gateway_name = self.env.config.mod.vnpy.gateway_name

        self._account_cache = None

    def after_trading(self):
        self._vnpy_engine.exit()

    def before_trading(self):
        login_dict = {
            'userID': self.env.config.mod.vnpy.ctp.userID,
            'password': self.env.config.mod.vnpy.ctp.password,
            'brokerID': self.env.config.mod.vnpy.ctp.brokerID,
            'tdAddress': self.env.config.mod.vnpy.ctp.tdAddress,
            'mdAddress': self.env.config.mod.vnpy.ctp.mdAddress,
        }
        self._vnpy_engine.connect(self._vnpy_gateway_name, login_dict)

    def get_accounts(self):
        if self._accounts is None:
            self._accounts = init_accounts()
        return self._accounts

    def get_open_orders(self):
        return self._engine.open_orders

    def submit_order(self, order):
        self._engine.send_order(order, self._vnpy_gateway_name)

    def cancel_order(self, order):
        self._engine.cancel_order(order, self._vnpy_gateway_name)

    def update(self, calendar_dt, trading_dt, bar_dict):
        pass
