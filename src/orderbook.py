import sys, time

from src.bitmex_websocket import BitMexWs


class OrderBook:
    inited = False
    asks = {}
    bids = {}
    ask_max_price = 0
    bid_min_price = 0

    def __init__(self, ws):
        self.ws = ws
        self.ws.bind('orderBookL2', self.__update)

    def __update(self, action, values):
        if not self.inited and action != "partial":
            return

        if action == "partial":
            self.inited = True

        for v in values:
            ordId = v['id']
            side = v['side']
            orders = self.asks if side == "Buy" else self.bids
            if action == "partial" or \
                    action == "insert":
                orders[ordId] = v
            elif action == "update" and ordId in orders:
                orders[ordId]["size"] = v['size']
            elif action == "delete" and ordId in orders:
                del orders[ordId]

        ask_prices = sorted([v['price'] for v in self.asks.values()])
        bid_prices = sorted([v['price'] for v in self.bids.values()])

        if len(ask_prices) > 0:
            self.ask_max_price = ask_prices[-1]
        if len(bid_prices) > 0:
            self.bid_min_price = bid_prices[0]

    def get_prices(self):
        return self.bid_min_price, self.ask_max_price

if __name__ == '__main__':
    ws = BitMexWs()
    ob = OrderBook(ws)
    while True:
        sys.stdout.write(f"\r{ob.get_prices()}")
        sys.stdout.flush()
