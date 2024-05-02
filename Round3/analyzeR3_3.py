import pandas as pd

# Load the data from the CSV file
data = pd.read_csv('prices_round_3_day_0.csv', sep=';')

# Filter rows where the product is 'GIFT_BASKET'
gift_basket_data = data[data['product'] == 'GIFT_BASKET']

# Select only the required columns: 'timestamp', 'ask_price_1' (best ask), 'bid_price_1' (best bid), 'mid_price'
filtered_data = gift_basket_data[['timestamp', 'ask_price_1', 'bid_price_1', 'mid_price']]

# Rename columns to more descriptive names if desired
filtered_data.columns = ['Timestamp', 'Best Ask', 'Best Bid', 'Mid Price']

# Save the filtered data to a new CSV file
filtered_data.to_csv('filtered_gift_basket_data.csv', index=False)

print("Filtered data saved to 'filtered_gift_basket_data.csv'")