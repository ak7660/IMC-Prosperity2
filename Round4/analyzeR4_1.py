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

# Standardize the price spread (Z-score normalization)
merged_df['spread_z_score'] = (merged_df['price_spread'] - merged_df['price_spread'].mean()) / merged_df['price_spread'].std()

# Plotting the standardized price spread over time
plt.figure(figsize=(14, 7))
plt.plot(merged_df['adjusted_timestamp'], merged_df['spread_z_score'], label='Standardized Price Spread (COCONUT - COCONUT_COUPON)', color='tab:green')
plt.xlabel('Adjusted Timestamp')
plt.ylabel('Standardized Price Spread (Z-score)')
plt.title('Standardized Price Spread Over Time Between COCONUT and COCONUT_COUPON')
plt.legend()
plt.grid(True)
plt.show()