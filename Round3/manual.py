import itertools

# Define the base treasure and expedition costs
base_treasure = 7500
second_exped_cost = 25000
third_exped_cost = 75000

# Define the spots with their respective multipliers and hunters
spots = {
    'G26': (24, 2), 'G27': (70, 4), 'G28': (41, 3), 'G29': (21, 2), 'G30': (60, 4),
    'H31': (47, 3), 'H32': (82, 5), 'H33': (87, 5), 'H34': (80, 5), 'H35': (35, 3),
    'I36': (73, 4), 'I37': (89, 5), 'I38': (100, 8), 'I39': (90, 7), 'I40': (17, 2),
    'J41': (77, 5), 'J42': (83, 5), 'J43': (85, 5), 'J44': (79, 5), 'J45': (55, 4),
    'K46': (12, 2), 'K47': (27, 3), 'K48': (52, 4), 'K49': (15, 2), 'K50': (30, 3)
}

# Calculate the profit for a single spot
def calculate_profit(multiplier, hunters, expeditions_percentage, expedition_cost=0):
    total_treasure = base_treasure * multiplier
    split_factor = hunters + expeditions_percentage
    profit = total_treasure / split_factor - expedition_cost
    return profit

# Generate all possible combinations of expeditions
all_combinations = []
for r in range(1, len(spots) + 1):  # From 1 to all spots
    all_combinations.extend(itertools.combinations(spots.keys(), r))

# Expeditions percentages to consider
expedition_percentages = [0.00, 0.01, 0.02]

# Calculate the profit for all combinations and percentages
results = []
for combination in all_combinations:
    for percent in expedition_percentages:
        # Calculate the total profit for the current combination and expedition percentage
        profit_sum = sum(calculate_profit(spots[spot][0], spots[spot][1], percent) for spot in combination)
        
        # Subtract the costs for additional expeditions
        if len(combination) > 1:
            profit_sum -= second_exped_cost
        if len(combination) > 2:
            profit_sum -= third_exped_cost
        
        results.append((combination, percent, profit_sum))

# Sort results by profit
results.sort(key=lambda x: x[2], reverse=True)

# Print the top results
for result in results[:10]:  # Change the slice to see more or fewer results
    print(f"Combination: {result[0]}, Percentage: {result[1] * 100}%, Profit: {result[2]}")