import numpy as np
import matplotlib.pyplot as plt

# Constants
number_of_people = 100
sale_price = 1000
total_outcomes = 100  # Total outcomes in the range 901-1000

# Define the range of x
x_values = range(901, 1001)

# Calculate uniform pmf value (since each outcome is equally likely)
uniform_pmf_value = 1 / total_outcomes

# Calculate cdf values for each x (uniform pmf means the cdf is a linear function)
cdf_values = [(x - 900) / total_outcomes for x in x_values]

# Calculate expected profit for each x using the uniform cdf
expected_profits = [cdf * number_of_people * (sale_price - x) for x, cdf in zip(x_values, cdf_values)]

# Find the maximum expected profit and its corresponding x value
max_profit = max(expected_profits)
max_profit_index = expected_profits.index(max_profit)
max_profit_x_value = x_values[max_profit_index]
max_profit_coordinates = (max_profit_x_value, max_profit)

# Print the maximum expected profit and its corresponding x value
print(f"Peak Expected Profit Coordinate: Cost Price: {max_profit_coordinates[0]}, Expected Profit: {max_profit_coordinates[1]}")
for x, profit in zip(x_values, expected_profits):
    print(f"Cost Price: {x}, Expected Profit: {profit}")
# Plot the expected profits
plt.plot(x_values, expected_profits, marker='o', linestyle='-', color='green')
plt.title('Expected Profit for Uniform PMF')
plt.xlabel('Cost Price (x)')
plt.ylabel('Expected Profit ($)')

# Annotate the maximum expected profit point
plt.scatter(*max_profit_coordinates, color='red')
plt.annotate(f'Peak: {max_profit_coordinates}',
             xy=max_profit_coordinates, 
             xytext=(max_profit_x_value, max_profit - (max_profit * 0.2)),
             arrowprops=dict(facecolor='black', shrink=0.05),
             ha='center')

plt.grid(True)
plt.show()