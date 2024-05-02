import pandas as pd
import matplotlib.pyplot as plt

# Define the file names
files = ['prices_round_4_day_1.csv', 'prices_round_4_day_2.csv', 'prices_round_4_day_3.csv']

# Read the files and concatenate into a single DataFrame
frames = []
for i, file in enumerate(files):
    temp_df = pd.read_csv(file, sep=';')
    temp_df['adjusted_timestamp'] = i * 1000000 + temp_df['timestamp']  # Adjust timestamp
    frames.append(temp_df)
df = pd.concat(frames)

# Filter data for COCONUT and COCONUT_COUPON and calculate mid prices
coconut_df = df[df['product'] == 'COCONUT'][['adjusted_timestamp', 'ask_price_1', 'bid_price_1']]
coconut_df['mid_price'] = (coconut_df['ask_price_1'] + coconut_df['bid_price_1']) / 2

coconut_coupon_df = df[df['product'] == 'COCONUT_COUPON'][['adjusted_timestamp', 'ask_price_1', 'bid_price_1']]
coconut_coupon_df['mid_price'] = (coconut_coupon_df['ask_price_1'] + coconut_coupon_df['bid_price_1']) / 2

# Merge the datasets on adjusted_timestamp
merged_df = pd.merge(coconut_df[['adjusted_timestamp', 'mid_price']].rename(columns={'mid_price': 'mid_price_coconut'}),
                     coconut_coupon_df[['adjusted_timestamp', 'mid_price']].rename(columns={'mid_price': 'mid_price_coconut_coupon'}),
                     on='adjusted_timestamp', how='inner')

# Calculate the price spread between the two products
merged_df['price_spread'] = merged_df['mid_price_coconut'] - merged_df['mid_price_coconut_coupon']

# Rolling mean and standard deviation of the price spread
window_size = 50  # Rolling window size
merged_df['rolling_mean'] = merged_df['price_spread'].rolling(window=window_size).mean()
merged_df['rolling_std'] = merged_df['price_spread'].rolling(window=window_size).std()

# Calculate the Z-score based on the rolling statistics
merged_df['rolling_z_score'] = (merged_df['price_spread'] - merged_df['rolling_mean']) / merged_df['rolling_std']

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

# Mid Prices plot with two y-axes
ax1.plot(merged_df['adjusted_timestamp'], merged_df['mid_price_coconut'], label='Mid Price COCONUT', color='blue')
ax1.set_ylabel('Mid Price COCONUT', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_title('Mid Prices of COCONUT and COCONUT_COUPON')
ax1.grid(True)

# Create a second y-axis for COCONUT_COUPON
ax1b = ax1.twinx()
ax1b.plot(merged_df['adjusted_timestamp'], merged_df['mid_price_coconut_coupon'], label='Mid Price COCONUT_COUPON', color='red')
ax1b.set_ylabel('Mid Price COCONUT_COUPON', color='red')
ax1b.tick_params(axis='y', labelcolor='red')

# Plot the rolling Z-score of the price spread over time
ax2.plot(merged_df['adjusted_timestamp'], merged_df['rolling_z_score'], label='Rolling Z-Score of Price Spread', color='tab:orange')
ax2.set_xlabel('Adjusted Timestamp')
ax2.set_ylabel('Rolling Z-Score')
ax2.set_title('Rolling Z-Score of Price Spread Over Time Between COCONUT and COCONUT_COUPON')
ax2.legend()
ax2.grid(True)

plt.show()