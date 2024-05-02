from itertools import product

def print_all_sequences_and_find_max(exchange_rates, start_amount, max_trades):
    # Assign indices to each currency
    pizza_slice = 0
    wasabi_root = 1
    snowball = 2
    sea_shells = 3
    
    # Initialize variables to track the best sequence and its return
    max_return = 0
    best_sequence = []
    
    # Generate all combinations with repetitions of all currencies for four internal trades
    for trade_sequence in product(range(4), repeat=max_trades - 2):
        current_amount = start_amount
        # Start by selling Sea Shells
        current_amount *= exchange_rates[sea_shells][trade_sequence[0]]
        for i in range(len(trade_sequence) - 1):
            current_amount *= exchange_rates[trade_sequence[i]][trade_sequence[i + 1]]
        # End by buying Sea Shells
        current_amount *= exchange_rates[trade_sequence[-1]][sea_shells]
        
        # Calculate profit and profit percentage
        profit = current_amount - start_amount
        profit_percentage = (profit / start_amount) * 100
        
        # Check if the current sequence is the best so far
        if current_amount > max_return:
            max_return = current_amount
            best_sequence = trade_sequence
        
        # Convert indices to currency names for better readability
        readable_sequence = ['Sea Shells'] + [currency_names[index] for index in trade_sequence] + ['Sea Shells']
        print(f"Sequence: {readable_sequence} -> Final Amount: {current_amount} (Profit: {profit:.2f}, Profit Percentage: {profit_percentage:.2f}%)")
    
    # Print the best sequence found
    if best_sequence:
        best_readable_sequence = ['Sea Shells'] + [currency_names[index] for index in best_sequence] + ['Sea Shells']
        best_profit = max_return - start_amount
        best_profit_percentage = (best_profit / start_amount) * 100
        print("\nBest sequence for maximum profit:")
        print(f"Sequence: {best_readable_sequence} -> Maximum Return: {max_return} (Profit: {best_profit:.2f}, Profit Percentage: {best_profit_percentage:.2f}%)")

# Exchange rates matrix
exchange_rates = [
    [1, 0.48, 1.52, 0.71],
    [2.05, 1, 3.26, 1.56],
    [0.64, 0.3, 1, 0.46],
    [1.41, 0.61, 2.08, 1]
]

# Currency names
currency_names = ['Pizza Slice', 'Wasabi Root', 'Snowball', 'Sea Shells']

# Initial amount and maximum number of trades
start_amount = 2000000
max_trades = 7  # This specifies total trades including start and end with Sea Shells

print_all_sequences_and_find_max(exchange_rates, start_amount, max_trades)