import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Constants
number_of_goldfish = 100000
sale_price = 1000

def sum_of_numbers(n):
    return (n * (n + 1)) / 2

total_sum = sum_of_numbers(100)
x_values = range(901, 1001)

def pmf(x):
    return (x - 900) / total_sum

pmf_values = [pmf(x) for x in x_values]
cdf_values = np.cumsum(pmf_values)

# Prepare data for analysis and plotting
results = []

for i, cdf in enumerate(cdf_values):
    reserve_price = x_values[i]
    expected_profit_bid1 = cdf * number_of_goldfish * (sale_price - (reserve_price + 1))
    goldfish_left = number_of_goldfish - (cdf * number_of_goldfish)
    
    x_values_2 = range(reserve_price + 1, 1001)
    total_sum_2 = sum_of_numbers(1000 - reserve_price)
    
    pmf_values_2 = [(x - reserve_price) / total_sum_2 for x in x_values_2]
    cdf_values_2 = np.cumsum(pmf_values_2)
    
    for j, cdf2 in enumerate(cdf_values_2):
        reserve_price_2 = x_values_2[j]
        expected_profit_bid2 = cdf2 * goldfish_left * (sale_price - (reserve_price_2 + 1))
        total_expected_profit = expected_profit_bid1 + expected_profit_bid2
        
        # Store results
        results.append((reserve_price + 1, reserve_price_2 + 1, total_expected_profit))

# Sort results by expected profit in descending order
results.sort(key=lambda x: x[2], reverse=True)

# Print top three results
print("Top three bid combinations with their expected profits:")
for i in range(3):
    bid1, bid2, profit = results[i]
    print(f"Rank {i+1}: Bid 1 = {bid1}, Bid 2 = {bid2}, Expected Profit = {profit}")

# Optional: Plotting if needed
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
bid_price1, bid_price2, expected_profit = zip(*results)
ax.scatter(bid_price1, bid_price2, expected_profit, c=expected_profit, cmap='viridis', marker='o')
ax.set_xlabel('Bid Price 1')
ax.set_ylabel('Bid Price 2')
ax.set_zlabel('Expected Profit')
plt.show()