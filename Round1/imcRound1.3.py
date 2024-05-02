import json
import numpy as np
from datamodel import Order, TradingState, Symbol

class Trader:
    def __init__(self):
        self.amethysts_threshold_buy = 9999.5
        self.amethysts_threshold_sell = 10000.5
        self.starfruit_buy_threshold_pct = 0.99  # Buy if ask price is below 99% of mid price
        self.starfruit_sell_threshold_pct = 1.01  # Sell if bid price is above 101% of mid price
        self.position_limit = 20
        self.order_size = 10
        self.recent_prices_starfruit = []

    def run(self, state: TradingState) -> (dict[Symbol, list[Order]], int, str):
        result = {}
        current_mid_price = self.calculate_vwap_mid_price(state, 'STARFRUIT')
        self.recent_prices_starfruit.append(current_mid_price)

        for product in ['STARFRUIT', 'AMETHYSTS']:
            position = state.position.get(product, 0)
            orders = []
            best_ask = self.best_ask(state, product)
            best_bid = self.best_bid(state, product)

            if product == 'STARFRUIT':
                #buy_threshold = current_mid_price - 1
                #sell_threshold = current_mid_price + 1

                if position + self.order_size <= self.position_limit:
                    buy_order = Order(product, int(current_mid_price - 2), self.order_size)
                    orders.append(buy_order)

                if position - self.order_size >= -self.position_limit:
                    sell_order = Order(product, int(current_mid_price + 2), -self.order_size)
                    orders.append(sell_order)

            if product == 'AMETHYSTS':
                    
                if position + self.order_size <= self.position_limit:
                    buy_order = Order(product, 9998, self.order_size)
                    orders.append(buy_order)
                
                if position - self.order_size >= -self.position_limit:
                    sell_order = Order(product, 10002, -self.order_size)
                    orders.append(sell_order)

            result[product] = orders

        return result, 0, ""


    def best_ask(self, state: TradingState, product: Symbol) -> int:
        order_depth = state.order_depths[product]
        # Return the lowest sell price if available, otherwise 0
        return min(order_depth.sell_orders.keys()) if order_depth.sell_orders else 0

    def best_bid(self, state: TradingState, product: Symbol) -> int:
        order_depth = state.order_depths[product]
        # Return the highest buy price if available, otherwise 0
        return max(order_depth.buy_orders.keys()) if order_depth.buy_orders else 0
    
    
    def calculate_vwap_mid_price(self, state: TradingState, product: Symbol) -> float:
        order_depth = state.order_depths[product]
        total_bid_volume = sum(order_depth.buy_orders.values())
        total_ask_volume = sum(abs(volume) for volume in order_depth.sell_orders.values())  # Convert to positive if negative
        total_bid_value = sum(price * qty for price, qty in order_depth.buy_orders.items())
        total_ask_value = sum(price * abs(qty) for price, qty in order_depth.sell_orders.items())  # Use absolute values for qty

        #print(f"Order Depth for {product}: Bids - {order_depth.buy_orders}, Asks - {order_depth.sell_orders}")
        #print(f"Total Bid Volume: {total_bid_volume}, Total Ask Volume: {total_ask_volume}")
        #print(f"Total Bid Value: {total_bid_value}, Total Ask Value: {total_ask_value}")

        if total_bid_volume > 0 and total_ask_volume > 0:
            vwap_bid = total_bid_value / total_bid_volume
            vwap_ask = total_ask_value / total_ask_volume
            mid_price = (total_bid_value + total_ask_value ) / (total_bid_volume + total_ask_volume)
            print(f"VWAP Bid: {vwap_bid}, VWAP Ask: {vwap_ask}, Mid Price: {mid_price}")
            return mid_price
        else:
            print("Insufficient data to calculate VWAP.")
            return 0
        
        