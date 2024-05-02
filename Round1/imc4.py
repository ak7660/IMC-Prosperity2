import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, Dict, List

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()



class Trader:
    def __init__(self):
        self.state_data = None

    def analyze_market(self, order_depth: Dict[Symbol, OrderDepth]) -> Dict[Symbol, float]:
        fair_values = {}
        for symbol, depth in order_depth.items():
            if depth.sell_orders and depth.buy_orders:
                best_ask = min(depth.sell_orders.keys())
                best_bid = max(depth.buy_orders.keys())
                fair_values[symbol] = (best_ask + best_bid) / 2
            else:
                logger.print(f"Insufficient depth for {symbol} to determine fair value")
        return fair_values

    def generate_signals(self, fair_values: Dict[Symbol, float], position: Dict[Symbol, int]) -> Dict[Symbol, str]:
        signals = {}
        for symbol, fair_value in fair_values.items():
            current_position = position.get(symbol, 0)
            if current_position < 0 and fair_value < 0:  # Short and price is below fair value
                signals[symbol] = 'buy_to_cover'
            elif current_position > 0 and fair_value > 0:  # Long and price is above fair value
                signals[symbol] = 'sell'
            elif current_position == 0:
                if fair_value < 0:
                    signals[symbol] = 'buy'
                elif fair_value > 0:
                    signals[symbol] = 'sell'
        return signals

    def execute_orders(self, signals: Dict[Symbol, str], order_depth: Dict[Symbol, OrderDepth]) -> List[Order]:
        orders = []
        for symbol, signal in signals.items():
            depth = order_depth[symbol]
            if signal == 'buy':
                best_ask = min(depth.sell_orders.keys())
                orders.append(Order(symbol, best_ask, 1))
            elif signal == 'sell':
                best_bid = max(depth.buy_orders.keys())
                orders.append(Order(symbol, best_bid, -1))
            elif signal == 'buy_to_cover':
                best_ask = min(depth.sell_orders.keys())
                orders.append(Order(symbol, best_ask, 1))
        return orders

    def manage_state(self, state_data: str) -> str:
        # Serialize state data to be passed on to the next iteration
        return jsonpickle.encode(state_data)

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        fair_values = self.analyze_market(state.order_depths)
        signals = self.generate_signals(fair_values, state.position)
        orders_list = self.execute_orders(signals, state.order_depths)

        orders = {symbol: [] for symbol in state.order_depths.keys()}
        for order in orders_list:
            orders[order.symbol].append(order)

        trader_data = self.manage_state(self.state_data)

        logger.print(f"Generated orders: {orders}")
        logger.flush(state, orders, 0, trader_data)

        return orders, 0, trader_data

# Note: In a real trading environment, you would also need to implement proper error handling and
# possibly more complex trading logic that takes into account trading costs, slippage, and other market factors.