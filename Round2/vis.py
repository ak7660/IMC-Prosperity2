import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV data
file_path = 'prices_round_2_day_1.csv'  # Update this to the path of your CSV file
data = pd.read_csv(file_path, delimiter=';')  # Using semicolon as delimiter since the data uses it

# Plotting
plt.figure(figsize=(10, 5))  # Set the figure size (optional)
plt.plot(data['TRANSPORT_FEES'], data['ORCHIDS'], marker='o')  # Plot Orchids against Humidity

plt.title('Orchids vs EXPORT_TARIFF')  # Title of the graph
plt.xlabel('Import_TARIFF')  # X-axis label
plt.ylabel('Orchids (units)')  # Y-axis label
plt.grid(True)  # Enable grid for easier readability

# Show the plot
plt.show()