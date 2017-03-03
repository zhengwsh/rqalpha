# -*- coding: utf-8 -*-
from time import sleep, time

from .vn_trader.ctpGateway.ctpGateway import CtpGateway
from .vn_trader.ctpGateway.ctpGateway import CtpTdApi, CtpMdApi
from .vn_trader.ctpGateway.ctpGateway import directionMapReverse
from .vn_trader.vtGateway import VtBaseData, VtContractData, VtPositionData
from .vn_trader.vtConstant import EMPTY_FLOAT, EMPTY_INT, EMPTY_STRING, EMPTY_UNICODE


# ------------------------------------ 自定义或扩展数据类型 ------------------------------------
class PositionMoreFields(VtBaseData):
    def __init__(self):
        super(PositionMoreFields, self).__init__()
        self.symbol = EMPTY_STRING
        self.direction = EMPTY_STRING

        self.closeProfit = EMPTY_FLOAT
        self.openCost = EMPTY_FLOAT


# ------------------------------------ 扩展CTPApi ------------------------------------
class RQCTPTdApi(CtpTdApi):
    def __init__(self, gateway):
        super(RQCTPTdApi, self).__init__(gateway)
        self.pos_detail_buffer_dict = {}

    def onRspQryInvestorPositionDetail(self, data, error, n, last):
        pos_detail = VtPositionDetailData()
        pos_detail.symbol = data['InstrumentId']

    def onRspQryInstrument(self, data, error, n, last):
        super(RQCTPTdApi, self).onRspQryInstrument(data, error, n, last)
        if last:
            self.gateway.status.contract_success()

    def onRspQryTradingAccount(self, data, error, n, last):
        super(RQCTPTdApi, self).onRspQryTradingAccount(data, error, n, last)
        self.gateway.status.account_success()

    def onRspQryInvestorPosition(self, data, error, n, last):
        super(RQCTPTdApi, self).onRspQryInvestorPosition(data, error, n, last)
        # TODO: 扩展 position 字段, 继承 vnpy 中原有 position 类或另外实现一个其他字段的类
        if last:
            self.gateway.status.position_success()


class RQCTPMdApi(CtpMdApi):
    def __init__(self, gateway):
        super(RQCTPMdApi, self).__init__(gateway)


# ------------------------------------ order生命周期 ------------------------------------
class RQVNCTPGateway(CtpGateway):
    def __init__(self, event_engine, gateway_name):
        super(CtpGateway, self).__init__(event_engine, gateway_name)

        self.mdApi = RQCTPMdApi(self)
        self.tdApi = RQCTPTdApi(self)

        self.mdConnected = False
        self.tdConnected = False

        self.qryEnabled = False

        self.inited = False

        self.status = InitStatus()

    def do_init(self, login_dict):
        self.connect(login_dict)
        self.status.wait_until_contract()
        self.qryAccount()
        self.status.wait_until_account()
        self.qryPosition()
        self.status.wail_until_position()

    def qry_position_detail(self):
        self.tdApi.qry_position_detail()

    def init_complete(self):
        self.inited = True


class InitStatus(object):
    def __init__(self):
        self._login = False
        self._contract = False
        self._account = False
        self._position = False

    def _wait_until(self, which, timeout):
        start_time = time()
        while True:
            which_dict = {
                'login': self._login,
                'contract': self._contract,
                'account': self._account,
                'position': self._position,
            }
            if which_dict[which]:
                break
            else:
                if timeout is not None:
                    if time() - start_time > timeout:
                        break

    def wait_until_login(self, timeout=None):
        self._wait_until('login', timeout)

    def login_success(self):
        self._login = True

    def wait_until_contract(self, timeout=None):
        self._wait_until('contract', timeout)

    def contract_success(self):
        self._contract = True

    def wait_until_account(self, timeout=None):
        self._wait_until('account', timeout)

    def account_success(self):
        self._account = True

    def wait_until_position(self, timeout=None):
        self._wait_until('position', timeout)

    def position_success(self):
        self._position = True
