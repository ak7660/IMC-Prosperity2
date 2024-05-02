import json
from datamodel import Order, TradingState, Symbol

class Trader:
    def __init__(self):
        # Initialize thresholds for buying and selling
        self.starfruit_threshold_buy = 4900
        self.starfruit_threshold_sell = 5100
        self.amethysts_threshold_buy = 9999
        self.amethysts_threshold_sell = 10001
        # Position limits and order size for the products
        self.position_limit = 20
        self.order_size = 10
        # Spread is not used in the provided strategy, but can be included if needed
        self.spread = 2

    def run(self, state: TradingState) -> (dict[Symbol, list[Order]], int, str):
        result = {}
        # Iterate over the products and determine orders based on the current state
        for product in ['STARFRUIT', 'AMETHYSTS']:
            position = state.position.get(product, 0)
            orders = []

            # Determine the best bid and ask prices from the order book
            best_ask = self.best_ask(state, product)
            best_bid = self.best_bid(state, product)

            # Check if we should place a buy order for STARFRUIT
            if product == 'STARFRUIT' and best_ask < self.starfruit_threshold_buy and position + self.order_size <= self.position_limit:
                buy_order = Order(product, best_ask, self.order_size)
                orders.append(buy_order)
            
            # Check if we should place a sell order for STARFRUIT
            if product == 'STARFRUIT' and best_bid > self.starfruit_threshold_sell and position - self.order_size >= -self.position_limit:
                sell_order = Order(product, best_bid, -self.order_size)
                orders.append(sell_order)

            # Check if we should place a buy order for AMETHYSTS
            if product == 'AMETHYSTS' and best_ask < self.amethysts_threshold_buy and position + self.order_size <= self.position_limit:
                buy_order = Order(product, best_ask, self.order_size)
                orders.append(buy_order)
            
            # Check if we should place a sell order for AMETHYSTS
            if product == 'AMETHYSTS' and best_bid > self.amethysts_threshold_sell and position - self.order_size >= -self.position_limit:
                sell_order = Order(product, best_bid, -self.order_size)
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