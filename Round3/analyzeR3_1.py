import pandas as pd
import matplotlib.pyplot as plt

# Define the file names
files = ['prices_round_3_day_0.csv', 'prices_round_3_day_1.csv', 'prices_round_3_day_2.csv']

# Read the files and concatenate into a single DataFrame
frames = []
for file in files:
    temp_df = pd.read_csv(file, sep=';')
    frames.append(temp_df)
df = pd.concat(frames)

# Filter the data for strawberries
strawberries_df = df[df['product'] == 'STRAWBERRIES']

# Adjust the timestamp to reflect continuous time across multiple days
# Assuming there are 1,000,000 timestamps for each day
strawberries_df['adjusted_timestamp'] = strawberries_df['day'] * 1000000 + strawberries_df['timestamp']

# Sort by the new adjusted timestamp
strawberries_df = strawberries_df.sort_values(by='adjusted_timestamp')

# Calculate the 20-period moving average of the mid_price
strawberries_df['MA20'] = strawberries_df['mid_price'].rolling(window=50).mean()

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(strawberries_df['adjusted_timestamp'], strawberries_df['mid_price'], label='Mid Price', color='red')
plt.plot(strawberries_df['adjusted_timestamp'], strawberries_df['MA20'], label='20-Period MA', color='blue', linestyle='--')
plt.title('Strawberries Prices with 20-Period Moving Average')
plt.xlabel('Adjusted Timestamp')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()