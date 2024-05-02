import json
import jsonpickle
from datamodel import TradingState, Order

class Trader:

    def __init__(self):
        self.state_data = None

    def analyze_market(self, order_depth):
        # Analyze the market and determine the fair value for each product
        fair_values = {}
        for product, depth in order_depth.items():
            # This is a very simple example where we just take the average of the best bid and ask
            best_bid, best_bid_qty = max(depth.buy_orders.items())
            best_ask, best_ask_qty = min(depth.sell_orders.items())
            fair_values[product] = (best_bid + best_ask) / 2
        return fair_values

    def generate_signals(self, fair_values, position):
        # Generate signals based on the fair value and your current position
        signals = {}
        for product, fair_value in fair_values.items():
            current_position = position.get(product, 0)
            if current_position < 0:  # If we are short, look to cover if the price is below fair value
                if fair_value < 0:
                    signals[product] = 'buy_to_cover'
            elif current_position > 0:  # If we are long, look to sell if the price is above fair value
                if fair_value > 0:
                    signals[product] = 'sell'
            else:  # If we are flat, look to take a position if there's a strong signal
                if fair_value < 0:
                    signals[product] = 'buy'
                elif fair_value > 0:
                    signals[product] = 'sell'
        return signals

    def execute_orders(self, signals, order_depth):
        # Execute orders based on the signals
        orders = []
        for product, signal in signals.items():
            depth = order_depth[product]
            if signal == 'buy':
                # Find the best ask and place a buy order
                best_ask, _ = min(depth.sell_orders.items())
                orders.append(Order(product, best_ask, 1))  # quantity is set to 1 for simplicity
            elif signal == 'sell':
                # Find the best bid and place a sell order
                best_bid, _ = max(depth.buy_orders.items())
                orders.append(Order(product, best_bid, -1))  # negative quantity for sell order
            elif signal == 'buy_to_cover':
                best_ask, _ = min(depth.sell_orders.items())
                orders.append(Order(product, best_ask, 1))  # covering a short position
        return orders

    def manage_state(self, state_data):
        # Serialize state data to be passed on to the next iteration
        return jsonpickle.encode(state_data)

    def run(self, state: TradingState):
        # Main trading logic
        fair_values = self.analyze_market(state.order_depths)
        signals = self.generate_signals(fair_values, state.position)
        orders = self.execute_orders(signals, state.order_depths)
        trader_data = self.manage_state(self.state_data)

        # Prepare the result dictionary
        result = {product: order_list for product, order_list in zip(state.order_depths.keys(), orders)}

        # You might want to handle conversions based on your trading strategy
        conversions = 0

        return result, conversions, trader_data