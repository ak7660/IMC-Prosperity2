import pandas as pd
import matplotlib.pyplot as plt

# Set the variables for the trader's name and product name
trader_name = 'Rhianna'
product_name = 'COCONUT'

# Function to load and preprocess price data
def load_price_data(file_name, day_offset):
    df = pd.read_csv(file_name, delimiter=';')
    df = df[(df['product'] == product_name) & (df['timestamp'] >= 100) & (df['timestamp'] <= 1000000)]
    df['timestamp'] += day_offset  # Adjust timestamp for each day
    return df

# Load price data for three days
price_df_day_0 = load_price_data('prices_round_4_day_1.csv', 0)
price_df_day_1 = load_price_data('prices_round_4_day_2.csv', 1000000)
price_df_day_2 = load_price_data('prices_round_4_day_3.csv', 2000000)

# Concatenate the data from all days
all_price_data = pd.concat([price_df_day_0, price_df_day_1, price_df_day_2])

# Calculate the moving average for smoothing
window_size = 50
all_price_data['smoothed_mid_price'] = all_price_data['mid_price'].rolling(window=window_size, min_periods=1).mean()

# Load and prepare the trade data for each day (similar to price data)
def load_trade_data(file_name, day_offset):
    df = pd.read_csv(file_name, delimiter=';')
    df = df[(df['symbol'] == product_name) & ((df['buyer'] == trader_name) | (df['seller'] == trader_name))]
    df['timestamp'] += day_offset  # Adjust timestamp for each day
    return df

trades_df_day_0 = load_trade_data('trades_round_4_day_1_wn.csv', 0)
trades_df_day_1 = load_trade_data('trades_round_4_day_2_wn.csv', 1000000)
trades_df_day_2 = load_trade_data('trades_round_4_day_3_wn.csv', 2000000)

# Concatenate trade data
all_trades_data = pd.concat([trades_df_day_0, trades_df_day_1, trades_df_day_2])
trader_buys = all_trades_data[all_trades_data['buyer'] == trader_name]
trader_sells = all_trades_data[all_trades_data['seller'] == trader_name]

# Plotting the data
plt.figure(figsize=(12, 6))
plt.plot(all_price_data['timestamp'], all_price_data['mid_price'], marker='', linestyle='-', color='lightgray', label='Original')
plt.plot(all_price_data['timestamp'], all_price_data['smoothed_mid_price'], marker='', linestyle='-', color='blue', label='Smoothed')

# Plot transactions
plt.scatter(trader_buys['timestamp'], trader_buys['price'], color='green', s=50, marker='o', label=f'{trader_name} Buys')
plt.scatter(trader_sells['timestamp'], trader_sells['price'], color='red', s=50, marker='o', label=f'{trader_name} Sells')

plt.title(f'Timestamp vs Mid Price for {product_name} (Smoothed) with {trader_name} Transactions Over 3 Days')
plt.xlabel('Timestamp')
plt.ylabel('Mid Price')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()