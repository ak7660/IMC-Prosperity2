import numpy as np
import matplotlib.pyplot as plt

# Constants
number_of_people = 100
sale_price = 1000

# Define the range of x
x_values = range(901, 1000)

# Define the pmf function
def pmf(x):
    return (x - 900) / 5050

# Calculate pmf values for each x
pmf_values = [pmf(x) for x in x_values]


# Calculate the cdf values using numpy's cumulative sum function
cdf_values = np.cumsum(pmf_values)
print(cdf_values*number_of_people)

# Calculate expected profit for each x
expected_profits = [cdf * number_of_people * (sale_price - (x+1)) for x, cdf in zip(x_values, cdf_values)]

# Find the maximum expected profit and its corresponding x value
max_profit = max(expected_profits)
max_profit_index = expected_profits.index(max_profit)
max_profit_x_value = x_values[max_profit_index]
max_profit_coordinates = (max_profit_x_value, max_profit)

# Print all coordinates
for x, profit in zip(x_values, expected_profits):
    print(f"Cost Price: {x}, Expected Profit: {profit}")

# Print the maximum expected profit and its corresponding x value
print(f"\nPeak Expected Profit Coordinate: Cost Price: {max_profit_coordinates[0]}, Expected Profit: {max_profit_coordinates[1]}")

# Set up a figure with three subplots
plt.figure(figsize=(14, 5))

# Plot for PMF
plt.subplot(1, 3, 1)  # 1 row, 3 columns, first plot
plt.bar(x_values, pmf_values, color='blue')
plt.title('Probability Mass Function (PMF)')
plt.xlabel('Cost Price (x)')
plt.ylabel('Probability')

# Plot for CDF
plt.subplot(1, 3, 2)  # 1 row, 3 columns, second plot
plt.plot(x_values, cdf_values, color='orange')
plt.title('Cumulative Distribution Function (CDF)')
plt.xlabel('Cost Price (x)')
plt.ylabel('Cumulative Probability')

# Plot for Expected Profits
plt.subplot(1, 3, 3)  # 1 row, 3 columns, third plot
plt.plot(x_values, expected_profits, marker='o', linestyle='-', color='green')
plt.title('Expected Profit for Different Cost Prices')
plt.xlabel('Cost Price (x)')
plt.ylabel('Expected Profit ($)')

# Annotate the maximum expected profit point
plt.scatter(*max_profit_coordinates, color='red')
plt.annotate(f'Peak: {max_profit_coordinates}',
             xy=max_profit_coordinates, 
             xytext=(max_profit_x_value, max_profit - (max_profit * 0.05)),
             arrowprops=dict(facecolor='black', shrink=0.05),
             ha='center')

plt.grid(True)
plt.tight_layout()  # Adjust subplots to fit into the figure area.
plt.show()