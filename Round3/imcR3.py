import json
import numpy as np
import pandas as pd
import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any
from collections import defaultdict
from typing import List, Dict

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

class RollingWindow:
    def __init__(self, size):
        self.size = size
        self.values = []
    
    def push(self, value):
        """Add a new value to the window, and remove the oldest if the window is full."""
        if len(self.values) >= self.size:
            self.values.pop(0)
        self.values.append(value)
    
    def get_zscore(self):
        """Calculate the z-score of the last value in the window."""
        if not self.values:
            return 0  # Can't compute z-score without data
        
        mean = sum(self.values) / len(self.values)
        std_dev = (sum((x - mean) ** 2 for x in self.values) / len(self.values)) ** 0.5
        
        if std_dev == 0:
            return 0  # Prevent division by zero; z-score is undefined if std_dev is zero
        
        latest_value = self.values[-1]
        z_score = (latest_value - mean) / std_dev
        return z_score

class Trader:
    def __init__(self):
        self.amethysts_threshold_buy = 9999.5
        self.amethysts_threshold_sell = 10000.5
        self.starfruit_buy_threshold_pct = 0.99  # Buy if ask price is below 99% of mid price
        self.starfruit_sell_threshold_pct = 1.01  # Sell if bid price is above 101% of mid price
        self.position_limit = 20
        self.order_size = 20
        self.Orhid_pricelong = []
        self.Orhid_priceshort = []
        self.best_internal_bid = 0
        self.best_internal_ask = 0
        self.arbit_limit = 100
        self.recent_prices_starfruit = []
        self.position_limit_Dic = {'STARFRUIT' : 20, 'AMETHYSTS' : 20, 'CHOCOLATE' : 250, 'STRAWBERRIES' : 350, 'ROSES' : 60, 'ORCHIDS' : 100, 'GIFT_BASKET' : 60}
        self.order_size_Dic = {'STARFRUIT' : 20, 'AMETHYSTS' : 20, 'CHOCOLATE' : 250, 'STRAWBERRIES' : 350, 'ROSES' : 60, 'ORCHIDS' : 100, 'GIFT_BASKET' : 60}
        self.recent_prices = {product: [] for product in self.position_limit_Dic.keys()}
        self.window_size = 10
        self.opened_last_position = 0
        self.premium_window = RollingWindow(50)
        
    def run(self, state: TradingState) -> (dict[Symbol, list[Order]], int, str):
        result = {}
        conversions = 0
        
        trader_data = ""
        #current_mid_price_amethysts = self.calculate_vwap_mid_price(state, 'AMETHYSTS')\
        #current_mid_price = self.calculate_vwap_mid_price(state, 'STARFRUIT')
        #self.recent_prices_starfruit.append(current_mid_price)

        for product in ['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET', 'STARFRUIT', 'AMETHYSTS', 'ORCHIDS']:
            position1 = state.position.get('ORCHIDS', 0)
            position = state.position.get(product, 0)
            if position1 >= -100 and position1 < 0:
                conversions = -position1
           
            current_mid_price = self.calculate_vwap_mid_price(state, product)
            self.recent_prices[product].append(current_mid_price)
            orders = []
            best_ask = self.best_ask(state, product)
            best_bid = self.best_bid(state, product)
            latest_own_trade_price = self.get_latest_own_trade_price(state, product)
            etf = 'GIFT_BASKET'
            constituents = ['STRAWBERRIES', 'CHOCOLATE', 'ROSES']
            weights = [6, 4, 1]
            pos = state.position.get(etf,0)
            lim = self.position_limit_Dic
            psell, vsell = {}, {}
            pbuy, vbuy = {}, {}
            mid_price = {}
                
            for p in constituents + [etf]:
                psell[p], vsell[p] = zip(*sorted(state.order_depths[p].sell_orders.items()))
                pbuy[p], vbuy[p] = zip(*sorted(state.order_depths[p].buy_orders.items(), reverse=True))
                mid_price[p] = (psell[p][0] + pbuy[p][0]) / 2

            combined = sum([w * mid_price[p] for w, p in zip(weights, constituents)])
            premium = mid_price[etf] - combined
            self.premium_window.push(premium)
            zscore = self.premium_window.get_zscore()
            
            if product == 'GIFT_BASKET':
                print('zscore', zscore)
                if zscore < -0.8:  # Buy etf
                    vol = lim[etf] - pos
                    buy_order = Order(etf, int(current_mid_price), int(vol))
                    orders.append(buy_order)
                elif zscore > 0.8:  # Sell etf
                    vol = -lim[etf] - pos
                    sell_order = Order(etf, int(current_mid_price), int(vol))
                    orders.append(sell_order)
                else:
                    vol = 0  
                    
            if product == 'CHOCOLATE':
                    # Calculate moving averages
                    ma100 = self.moving_average(self.recent_prices[product], 50)
                    ma200 = self.moving_average(self.recent_prices[product], 100)

                    # Trading signals based on moving averages
                    if ma100 > ma200 and position + self.order_size_Dic[product] <= self.position_limit_Dic[product] and position >= 0:
                        buy_order = Order(product, int(current_mid_price), self.order_size_Dic[product])
                        orders.append(buy_order)
                    elif ma100 > ma200 and position < self.position_limit_Dic[product]:
                        buy_order = Order(product, int(current_mid_price), self.position_limit_Dic[product] - position)
                        orders.append(buy_order)
                        
                        
                    if ma100 < ma200 and position - self.order_size_Dic[product] >= -self.position_limit_Dic[product] and position <= 0:
                        sell_order = Order(product, int(current_mid_price), -self.order_size_Dic[product] - position)
                        orders.append(sell_order)
                    elif ma100 < ma200 and position > -self.position_limit_Dic[product]:
                        sell_order = Order(product, int(current_mid_price), -self.position_limit_Dic[product] - position)
                        orders.append(sell_order)

                    print(f'CHOCOLATE MA100: {ma100}, MA200: {ma200}')
                    
            
            if product == 'STRAWBERRIES':
                # Calculate moving averages
                    #roc = self.calculate_roc(self.recent_prices[product], window=500)
                    if  position + self.order_size_Dic[product] <= self.position_limit_Dic[product] and position >= 0:
                        buy_order = Order(product, int(current_mid_price - 1), self.order_size_Dic[product])
                        orders.append(buy_order)
                    elif position < self.position_limit_Dic[product]:
                        buy_order = Order(product, int(current_mid_price - 1), self.position_limit_Dic[product] - position)
                        orders.append(buy_order)

                    if position - self.order_size_Dic[product] >= -self.position_limit and position <= 0:
                        sell_order = Order(product, int(current_mid_price + 1), -self.order_size_Dic[product])
                        orders.append(sell_order)
                    elif position > -self.position_limit_Dic[product]:
                        sell_order = Order(product, int(current_mid_price + 1), -self.position_limit_Dic[product] - position)
                        orders.append(sell_order)

                
            
            if product == 'ROSES':
                # Calculate ROC
                # Calculate Donchian Channels
                window = 10
                upper_channel, lower_channel = self.calculate_donchian_channels(self.recent_prices[product], window)

                # Determine trading signals based on the Donchian Channels
                best_ask = self.best_ask(state, product)
                best_bid = self.best_bid(state, product)
                if current_mid_price <= lower_channel and position + self.order_size_Dic[product] <= self.position_limit_Dic[product] and position >= 0:
                    buy_order = Order(product, int(current_mid_price), self.order_size_Dic[product])
                    orders.append(buy_order)
                elif current_mid_price <= lower_channel and position < self.position_limit_Dic[product]:
                    buy_order = Order(product, int(current_mid_price), self.position_limit_Dic[product] - position)
                    orders.append(buy_order)
                        
                        
                if current_mid_price >= upper_channel and position - self.order_size_Dic[product] >= -self.position_limit_Dic[product] and position <= 0:
                    sell_order = Order(product, int(current_mid_price), -self.order_size_Dic[product] - position)
                    orders.append(sell_order)
                elif current_mid_price >= upper_channel and position > -self.position_limit_Dic[product]:
                    sell_order = Order(product, int(current_mid_price), -self.position_limit_Dic[product] - position)
                    orders.append(sell_order)    
                    
            
                       
                    

                    
            
            
            
                    

                    

                
            
            if product == 'ORCHIDS':
                #buy_threshold = current_mid_price - 1
                #sell_threshold = current_mid_price + 1
                self.Orhid_priceshort.append(self.best_internal_ask)
                self.Orhid_pricelong.append(self.best_internal_bid)
                observation = state.observations.conversionObservations[product]
                
                SI_bid_price = observation.bidPrice
                SI_ask_price = observation.askPrice
                transport_fees = observation.transportFees
                export_tariff = observation.exportTariff
                import_tariff = observation.importTariff
                sunlight = observation.sunlight
                humidity = observation.humidity
                print('ORCHIDS Observation', SI_bid_price, SI_ask_price, transport_fees, export_tariff, import_tariff, sunlight, humidity)
                orderbook = self.get_order_book(state, product)
                total_cost_price = SI_ask_price + transport_fees + import_tariff
                total_sale_price = SI_bid_price - export_tariff - transport_fees
                #print('Total Cost Price', total_cost_price)
                print(self.Orhid_priceshort)
                #print('Total Sale Price', total_sale_price)
                print(self.Orhid_pricelong)
                
                #if max(self.Orhid_priceshort) > total_cost_price and total_cost_price > 0:
                         #conversions = -position
                         #self.Orhid_priceshort.clear()
                #print('Conversions', conversions)

                # Arbitrage Buy (Buy externally, sell internally)
                self.best_internal_bid = best_ask
                self.best_internal_ask = best_bid

                if position >= -self.arbit_limit and position <= 0 and import_tariff <= -3:
                    sell_order = Order(product, int(current_mid_price-1), -self.arbit_limit)
                    orders.append(sell_order)
                elif position >= -self.arbit_limit and import_tariff <= -3:
                    sell_order = Order(product, int(current_mid_price-1), -self.arbit_limit)
                    orders.append(sell_order)
                
                    
                
                        
                print('ORCHIDS Position', position)
            

            if product == 'STARFRUIT':
                #buy_threshold = current_mid_price - 1
                #sell_threshold = current_mid_price + 1

                if  position + self.order_size <= self.position_limit and position >= 0:
                    buy_order = Order(product, int(current_mid_price - 2), self.order_size)
                    orders.append(buy_order)
                elif position < self.position_limit:
                    buy_order = Order(product, int(current_mid_price - 2), self.position_limit - position)
                    orders.append(buy_order)

                if position - self.order_size >= -self.position_limit and position <= 0:
                    sell_order = Order(product, int(current_mid_price + 2), -self.order_size)
                    orders.append(sell_order)
                elif position > -self.position_limit:
                    sell_order = Order(product, int(current_mid_price + 2), -self.position_limit - position)
                    orders.append(sell_order)
                    
                print('StarFruit Position', position)

            if product == 'AMETHYSTS':
                    
                if position + self.order_size <= self.position_limit and position >= 0:
                    buy_order = Order(product, 9998, self.order_size)
                    orders.append(buy_order)
                elif position < self.position_limit:
                    buy_order = Order(product, 9998, self.position_limit - position)
                    orders.append(buy_order)
                
                if position - self.order_size >= -self.position_limit and position <= 0:
                    sell_order = Order(product, 10002, -self.order_size)
                    orders.append(sell_order)
                elif position > -self.position_limit:
                    sell_order = Order(product, 10002, -self.position_limit - position)
                    orders.append(sell_order)
                
                print('Amethysts Position', position)

            result[product] = orders
            
        
        logger.flush(state, result, conversions, trader_data)

        return result, conversions, trader_data
        


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
            #vwap_bid = total_bid_value / total_bid_volume
            #vwap_ask = total_ask_value / total_ask_volume
            mid_price = (total_bid_value + total_ask_value ) / (total_bid_volume + total_ask_volume)
            #print(f"VWAP Bid: {vwap_bid}, VWAP Ask: {vwap_ask}, Mid Price: {mid_price}")
            return mid_price
        else:
            print("Insufficient data to calculate VWAP.")
            return 0
        
    def get_order_book(self, state: TradingState, product: str) -> dict:
        order_depth = state.order_depths.get(product, OrderDepth())  # Get the OrderDepth or an empty one if not found
        
        # Retrieve bids and asks
        bids = {price: qty for price, qty in order_depth.buy_orders.items()}
        asks = {price: qty for price, qty in order_depth.sell_orders.items()}
        
        # Return the order book
        return {
            'bids': bids,
            'asks': asks
        }
        
    def rolling_regression(self, x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
        n = len(x)
        n = len(x)
        x_windows = np.lib.stride_tricks.sliding_window_view(x, window_shape=window)
        y_windows = np.lib.stride_tricks.sliding_window_view(y, window_shape=window)

        x_means = np.mean(x_windows, axis=1)
        y_means = np.mean(y_windows, axis=1)

        x_diffs = x_windows - x_means[:, np.newaxis]
        y_diffs = y_windows - y_means[:, np.newaxis]

        numerator = np.sum(x_diffs * y_diffs, axis=1)
        denominator = np.sum(x_diffs ** 2, axis=1)

        slopes = np.zeros(n)
        slopes[window-1:] = numerator / denominator

        return slopes
    
    def moving_average(self, prices: list, window: int) -> float:
        if len(prices) < window:
            return 0  # Not enough data to calculate moving average
        return sum(prices[-window:]) / window
    
    def get_latest_own_trade_price(self, state: TradingState, product: Symbol) -> int:
        """Retrieve the latest trade price for a given product from own trades."""
        trades = state.own_trades.get(product)
        if trades and len(trades) > 0:
            return trades[-1].price  # Return the price of the last trade
        return 0  # Return 0 if there are no trades for the product
    
    def calculate_roc(self, prices, window=50) -> pd.Series:
        """Calculate the Rate of Change (ROC) for a given window.
        
        Args:
            prices (list or pd.Series): List of prices or a Pandas Series of prices.
            window (int): The period over which to calculate the ROC.
        
        Returns:
            pd.Series: A Pandas Series containing the ROC values.
        """
        # Convert list to a Pandas Series if it's not already one
        if isinstance(prices, list):
            prices = pd.Series(prices)
        
        # Calculate ROC if there are enough data points
        if len(prices) >= window:
            roc = ((prices - prices.shift(window)) / prices.shift(window)) * 100
        else:
            roc = pd.Series([0] * len(prices))  # Not enough data to compute ROC
        
        return roc
    
    def calculate_donchian_channels(self, prices, window):
        """Calculate Donchian Channels for a given list of prices."""
        if len(prices) >= window:
            upper_channel = max(prices[-self.window_size:])
            lower_channel = min(prices[-self.window_size:])
        else:
            upper_channel = prices[-1] if prices else 0
            lower_channel = prices[-1] if prices else 0
        return upper_channel, lower_channel
    

    

            
        