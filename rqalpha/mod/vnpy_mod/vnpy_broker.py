# encoding: UTF-8
from time import time

from rqalpha.interface import AbstractBroker
from rqalpha.model.account import BenchmarkAccount, StockAccount, FutureAccount
from rqalpha.const import ACCOUNT_TYPE


def init_accounts(env):
    # FIXME: 从ctp获取获取账户信息，持仓等
    accounts = {}
    config = env.config
    start_date = config.base.start_date
    total_cash = 0
    future_starting_cash = config.base.future_starting_cash
    accounts[ACCOUNT_TYPE.FUTURE] = FutureAccount(env, future_starting_cash, start_date)
    if config.base.benchmark is not None:
        accounts[ACCOUNT_TYPE.BENCHMARK] = BenchmarkAccount(env, total_cash, start_date)

    return accounts


class VNPYBroker(AbstractBroker):
    def __init__(self, env, vnpy_engine):
        self._env = env

        self._accounts = None

        self._engine = vnpy_engine
        self._vnpy_gateway_type = self._env.config.mod.vnpy.gateway_type

        self._account_cache = None

    def _init_account(self):
        self._accounts = {
            ACCOUNT_TYPE.FUTURE: FutureAccount(
                self._env,
                self._env.config.base.start_date,
                self._env.config.base.future_starting_cash
            )}
        self._accounts[ACCOUNT_TYPE.FUTURE].set_state(self._engine.get_account_json())
        self._engine.init_account_timestamp = time()

    def after_trading(self):
        self._vnpy_engine.exit()

    def before_trading(self):
        self._engine.connect()

    def get_accounts(self):
        if self._accounts is None:
            # FIXME: 明确self._init_account 调用时间，必须在缓存完成后才能调用
            self._init_account()
        return self._accounts

    def get_open_orders(self):
        return self._engine.open_orders

    def submit_order(self, order):
        self._engine.send_order(order, self._vnpy_gateway_type)

    def cancel_order(self, order):
        self._engine.cancel_order(order, self._vnpy_gateway_type)

    def update(self, calendar_dt, trading_dt, bar_dict):
        pass
