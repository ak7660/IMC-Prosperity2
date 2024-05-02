import json
from datamodel import Order, TradingState, Symbol

class Trader:
    def __init__(self):
        # Initialize thresholds for buying and selling
        self.starfruit_threshold_buy = 4900
        self.starfruit_threshold_sell = 5100
        self.amethysts_threshold_buy = 9999.5
        self.amethysts_threshold_sell = 10000.5
        # Position limits for the products
        self.position_limit = 20
        self.order_size = 10
        

    def run(self, state: TradingState) -> (dict[Symbol, list[Order]], int, str):
        result = {}
        # Iterate over the products and determine orders based on the current state
        print(f"TraderData: {state.traderData}")
        print(f"Timestamp: {state.timestamp}")
        print(f"Positions: {state.position}")
        print(f"own_trade {state.own_trades}")
        print(f"market_trade {state.market_trades}")
        for product in ['STARFRUIT', 'AMETHYSTS']:
            position = state.position.get(product, 0)
            orders = []

            # Determine the best bid and ask prices from the order book
            best_ask = self.best_ask(state, product)
            best_bid = self.best_bid(state, product)

            # Define strategy for STARFRUIT
            if product == 'STARFRUIT':
                if best_ask < self.starfruit_threshold_buy and position + self.order_size <= self.position_limit:
                    buy_order = Order(product, best_ask, self.order_size)
                    orders.append(buy_order)
                if best_bid > self.starfruit_threshold_sell and position - self.order_size >= -self.position_limit:
                    sell_order = Order(product, best_bid, -self.order_size)
                    orders.append(sell_order)

            # Define strategy for AMETHYSTS based on the given price ranges
            elif product == 'AMETHYSTS':
                if 9998 <= best_ask < 9999 or 10001 < best_ask <= 10002:
                    order_size = 10
                elif best_ask < 9998 or best_ask > 10002:
                    order_size = self.position_limit - abs(position)  # Buy/sell up to the position limit
                else:  # Price is between 9999 - 10000 or 10000 - 10001
                    order_size = 5

                # Place buy and sell orders based on the strategy
                if best_ask < self.amethysts_threshold_buy and position + order_size <= self.position_limit:
                    buy_order = Order(product, best_ask, order_size)
                    orders.append(buy_order)
                if best_bid > self.amethysts_threshold_sell and position - order_size >= -self.position_limit:
                    sell_order = Order(product, best_bid, -order_size)
                    orders.append(sell_order)

            result[product] = orders

        # Assume no conversion requests and no trader data to persist
        return result, 0, ""

    def best_ask(self, state: TradingState, product: Symbol) -> int:
        order_depth = state.order_depths[product]
        # Return the lowest sell price if available, otherwise 0
        return min(order_depth.sell_orders.keys()) if order_depth.sell_orders else 0

    def best_bid(self, state: TradingState, product: Symbol) -> int:
        order_depth = state.order_depths[product]
        # Return the highest buy price if available, otherwise 0
        return max(order_depth.buy_orders.keys()) if order_depth.buy_orders else 0
