import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV data into a pandas DataFrame
df = pd.read_csv('d14a4e1b-a9e1-47ad-b5c8-9e19139c19fb.csv', delimiter=';')

# Convert the timestamp to a more readable format if necessary
# df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Separate the data for each product
df_starfruit = df[df['product'] == 'STARFRUIT']
df_amethysts = df[df['product'] == 'AMETHYSTS']

# Plot the mid-price for each product over time
plt.figure(figsize=(14, 7))

# Plot for STARFRUIT
plt.subplot(2, 1, 1)
plt.plot(df_starfruit['timestamp'], df_starfruit['mid_price'], label='STARFRUIT Mid Price', color='blue')
plt.xlabel('Timestamp')
plt.ylabel('Mid Price')
plt.title('STARFRUIT Mid Price Over Time')
plt.legend()

# Plot for AMETHYSTS
plt.subplot(2, 1, 2)
plt.plot(df_amethysts['timestamp'], df_amethysts['mid_price'], label='AMETHYSTS Mid Price', color='orange')
plt.xlabel('Timestamp')
plt.ylabel('Mid Price')
plt.title('AMETHYSTS Mid Price Over Time')
plt.legend()

plt.tight_layout()
plt.show()

# Plot the profit and loss over time
plt.figure(figsize=(14, 7))
plt.plot(df['timestamp'], df['profit_and_loss'], label='Profit and Loss', color='green')
plt.xlabel('Timestamp')
plt.ylabel('Profit and Loss')
plt.title('Profit and Loss Over Time')
plt.legend()
plt.show()