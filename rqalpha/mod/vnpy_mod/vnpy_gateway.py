# -*- coding: utf-8 -*-
from .vn_trader.ctpGateway.ctpGateway import CtpGateway
from .vn_trader.ctpGateway.vnctptd import TdApi
from .vn_trader.ctpGateway.ctpGateway import CtpTdApi, CtpMdApi


class RQCTPTdApi(CtpTdApi):
    def __init__(self, gateway):
        super(RQCTPTdApi, self).__init__(gateway)
        self.pos_detail_buffer_dict = {}

    def onRspQryInvestorPositionDetail(self, data, error, n, last):
        # TODO: 明确字段，缓存数据
        print(data)
        print(last)

    def qry_position_detail(self):
        self.reqID += 1
        req = {
            'BrokerID': self.brokerID,
            'InvestorID': self.userID
        }
        self.reqQryInvestorPositionDetail(req, self.reqID)


class RQCTPMdApi(CtpMdApi):
    def __init__(self, gateway):
        super(RQCTPMdApi, self).__init__(gateway)


class RQVNCTPGateway(CtpGateway):
    def __init__(self, event_engine, gateway_name):
        super(CtpGateway, self).__init__(event_engine, gateway_name)

        self.mdApi = RQCTPMdApi(self)
        self.tdApi = RQCTPTdApi(self)

        self.mdConnected = False
        self.tdConnected = False

        self.qryEnabled = False

    def qry_position_detail(self):
        self.tdApi.qry_position_detail()
