# -*- coding: utf-8 -*-
from dateutil.parser import parse
from datetime import timedelta

from rqalpha.model.order import Order
from rqalpha.model.trade import Trade
from rqalpha.model.account.future_account import FutureAccount
from rqalpha.model.portfolio.future_portfolio import FuturePortfolio
from rqalpha.model.position.future_position import FuturePosition
from rqalpha.const import ORDER_STATUS, ORDER_TYPE, POSITION_EFFECT, ACCOUNT_TYPE
from .vn_trader.vtConstant import EXCHANGE_SHFE, OFFSET_CLOSE, OFFSET_OPEN, OFFSET_CLOSETODAY
from .utils import SIDE_MAPPING, POSITION_EFFECT_MAPPING, ORDER_TYPE_MAPPING


def _trading_dt(calendar_dt):
    if calendar_dt.hour > 20:
        return calendar_dt + timedelta(days=1)
    return calendar_dt


def _order_book_id(symbol):
    if len(symbol) < 4:
        return None
    if symbol[-4] not in '0123456789':
        order_book_id = symbol[:2] + '1' + symbol[-3:]
    else:
        order_book_id = symbol
    return order_book_id.upper()


class RQVNOrder(Order):
    def __init__(self, vnpy_order, contract):
        super(RQVNOrder, self).__init__()
        self._order_id = next(self.order_id_gen)
        self._calendar_dt = parse(vnpy_order.orderTime)
        self._trading_dt = _trading_dt(self._calendar_dt)
        self._quantity = vnpy_order.totalVolume
        self._order_book_id = _order_book_id(vnpy_order.symbol)
        self._side = SIDE_MAPPING[vnpy_order.direction]

        if contract.exchange == EXCHANGE_SHFE:
            if vnpy_order.offset == OFFSET_OPEN:
                self._position_effect = POSITION_EFFECT.OPEN
            elif vnpy_order.offset == OFFSET_CLOSETODAY:
                self._position_effect = POSITION_EFFECT.CLOSE_TODAY
            else:
                self._position_effect = POSITION_EFFECT.CLOSE
        else:
            if vnpy_order.offset == OFFSET_OPEN:
                self._position_effect = POSITION_EFFECT.OPEN
            else:
                self._position_effect = POSITION_EFFECT.CLOSE

        self._message = ""
        self._filled_quantity = vnpy_order.tradedVolume
        self._status = ORDER_STATUS.PENDING_NEW
        # hard code VNPY 封装的报单类型中省掉了 type 字段
        self._type = ORDER_TYPE.LIMIT
        self._frozen_price = vnpy_order.price
        self._type = ORDER_TYPE.LIMIT
        self._avg_price = 0
        self._transaction_cost = 0

    @classmethod
    def create_from_vnpy_trade__(cls, vnpy_trade, contract):
        order = cls()
        order._order_id = next(order.order_id_gen)
        order._calendar_dt = parse(vnpy_trade.tradeTime)
        order._trading_dt = _trading_dt(order._calendar_dt)
        order._order_book_id = _order_book_id(vnpy_trade.symbol)
        order._quantity = vnpy_trade.volume
        order._side = SIDE_MAPPING[vnpy_trade.direction]

        if contract.exchange == EXCHANGE_SHFE:
            if vnpy_trade.offset == OFFSET_OPEN:
                order._position_effect = POSITION_EFFECT.OPEN
            elif vnpy_trade.offset == OFFSET_CLOSETODAY:
                order._position_effect = POSITION_EFFECT.CLOSE_TODAY
            else:
                order._position_effect = POSITION_EFFECT.CLOSE
        else:
            if vnpy_trade.offset == OFFSET_OPEN:
                order._position_effect = POSITION_EFFECT.OPEN
            else:
                order._position_effect = POSITION_EFFECT.CLOSE

        order._message = ""
        order._filled_quantity = vnpy_trade.volume
        order._status = ORDER_STATUS.FILLED
        order._type = ORDER_TYPE.LIMIT
        order._avg_price = vnpy_trade.price
        order._transaction_cost = 0


class RQVNTrade(Trade):
    def __init__(self, vnpy_trade, order):
        super(RQVNTrade, self).__init__()
        self._calendar_dt = parse(vnpy_trade.tradeTime)
        self._trading_dt = _trading_dt(self._calendar_dt)
        self._price = vnpy_trade.price
        self._amount = vnpy_trade.volume
        self._order = order
        self._commission = 0.
        self._tax = 0.
        self._trade_id = next(self.trade_id_gen)
        self._close_today_amount = 0.


class VNPYFuturePosition(FuturePosition):
    def __init__(self, order_book_id):
        super(VNPYFuturePosition, self).__init__(order_book_id)

    def update_with_vnpy_position(self, vnpy_position):
        pass

    def update_with_vnpy_position_detail(self, vnpy_position_ditail):
        pass

    def update_with_hist_trade(self, trade):
        pass

    def update_with_hist_order(self, order):
        inc_order_quantity = order.quantity
        inc_order_value = order._frozen_price * created_quantity * self._contract_multiplier
        if order.side == SIDE.BUY:
            if order.position_effect == POSITION_EFFECT.OPEN:
                self._buy_open_order_quantity += inc_order_quantity
                self._buy_open_order_value += inc_order_value
            else:
                self._buy_close_order_quantity += inc_order_quantity
                self._buy_close_order_value += inc_order_value
        else:
            if order.position_effect == POSITION_EFFECT.OPEN:
                self._sell_open_order_quantity += inc_order_quantity
                self._sell_open_order_value += inc_order_value
            else:
                self._sell_close_order_quantity += inc_order_quantity
                self._sell_close_order_value += inc_order_value


class RQVNPortfolio(FuturePortfolio):
    def __init__(self, vnpy_account, start_date):
        super(RQVNPortfolio, self).__init__(0, start_date, ACCOUNT_TYPE.FUTURE)
        pass


class RQVNCount(FutureAccount):
    def __init__(self, env, start_date):
        super(RQVNCount, self).__init__(env, 0, start_date)
        self._hist_order_cache = []
        self._hist_trade_cache = []
        self._position_cache = {}
        self._vnpy_account_cache = None
        self.inited = False

    def put_hist_order(self, order):
        self._hist_order_cache.append(order)

    def put_hist_trade(self, trade):
        self._hist_trade_cache.append(trade)

    def put_vnpy_position(self, vnpy_position):
        order_book_id = _order_book_id(vnpy_position.symbol)
        if order_book_id not in self._position_cache:
            self._position_cache[order_book_id] = VNPYFuturePosition(order_book_id)
        self._position_cache[order_book_id].update_with_vnpy_position(vnpy_position)

    def put_vnpy_account(self, vnpy_account):
        self._vnpy_account_cache = vnpy_account
