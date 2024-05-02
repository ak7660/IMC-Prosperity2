import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a pandas DataFrame
# Make sure to replace 'data.csv' with the actual path to your CSV file
df = pd.read_csv('prices_round_1_day_0.csv', delimiter=';')

# Filter the DataFrame to only include rows where the 'product' is 'STARFRUIT'
starfruit_df = df[df['product'] == 'STARFRUIT']

# Plotting the mid-price against timestamp for STARFRUIT
plt.figure(figsize=(10, 5))  # Set the figure size (optional)
plt.plot(starfruit_df['timestamp'], starfruit_df['mid_price'], marker='o')

# Adding title and labels
plt.title('Mid-Price of STARFRUIT Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Mid-Price')

# Show a grid
plt.grid(True)

# Show the plot
plt.show()