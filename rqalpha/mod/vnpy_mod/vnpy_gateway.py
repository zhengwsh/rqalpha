# -*- coding: utf-8 -*-
from .vn_trader.ctpGateway.ctpGateway import CtpGateway
from .vn_trader.ctpGateway.ctpGateway import CtpTdApi, CtpMdApi


class RQCTPTdApi(CtpTdApi):
    def __init__(self, gateway):
        super(RQCTPTdApi, self).__init__(gateway)
        self.pos_detail_buffer_dict = {}

    def onRspQryInvestorPositionDetail(self, data, error, n, last):
        # TODO: 明确字段，缓存数据
        print(data)
        print(last)

    def onRspQryInstrument(self, data, error, n, last):
        super(RQCTPTdApi, self).onRspQryInstrument(data, error, n, last)
        if last:
            self.gateway.on_contract_update_complete()

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
        self.contract_update_complete = False

    def qry_position_detail(self):
        self.tdApi.qry_position_detail()

    def on_contract_update_complete(self):
        self.contract_update_complete = True