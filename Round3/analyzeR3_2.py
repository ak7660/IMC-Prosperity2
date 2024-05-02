import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV
data = pd.read_csv('prices_round_3_day_0.csv', sep=';')

# Filter data for the 'GIFT_BASKET' product
gift_basket_data = data[data['product'] == 'GIFT_BASKET']

# Define the period for Donchian Channels
n = 100 # You can adjust this based on your specific needs

# Calculate Donchian Channel boundaries using the provided mid_price
gift_basket_data['upper_channel'] = gift_basket_data['mid_price'].rolling(window=n).max()
gift_basket_data['lower_channel'] = gift_basket_data['mid_price'].rolling(window=n).min()
gift_basket_data['mid_channel'] = (gift_basket_data['upper_channel'] + gift_basket_data['lower_channel']) / 2

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(gift_basket_data['timestamp'], gift_basket_data['mid_price'], label='Mid Price', color='blue')
plt.plot(gift_basket_data['timestamp'], gift_basket_data['upper_channel'], label='Upper Donchian Channel', linestyle='--', color='red')
plt.plot(gift_basket_data['timestamp'], gift_basket_data['lower_channel'], label='Lower Donchian Channel', linestyle='--', color='green')
plt.plot(gift_basket_data['timestamp'], gift_basket_data['mid_channel'], label='Mid Channel', linestyle=':', color='purple')

# Adding best bid and ask to the plot
#plt.plot(gift_basket_data['timestamp'], gift_basket_data['bid_price_1'], label='Best Bid', color='darkgreen')
#plt.plot(gift_basket_data['timestamp'], gift_basket_data['ask_price_1'], label='Best Ask', color='darkred')

plt.title('Donchian Channels with Best Bid and Ask for GIFT_BASKET')
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.legend()
plt.show()