import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import exp, sqrt, pi, log
from scipy.stats import norm
from scipy.optimize import newton

def norm_cdf(x):
    """Compute the cumulative distribution function for a standard normal distribution."""
    return norm.cdf(x)

def black_scholes_price(S, K, t, r, sigma):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)
    call_price = S * norm_cdf(d1) - K * np.exp(-r * t) * norm_cdf(d2)
    return call_price
from scipy.optimize import brentq

def implied_volatility(market_price, S, K, t, r, a=0.01, b=1.0, initial_guess=0.2):
    objective_function = lambda sigma: black_scholes_price(S, K, t, r, sigma) - market_price
    try:
        return brentq(objective_function, a, b, args=(), xtol=1e-6, rtol=1e-6, maxiter=100)
    except ValueError:
        return initial_guess

# Define the file names
files = ['prices_round_4_day_1.csv', 'prices_round_4_day_2.csv', 'prices_round_4_day_3.csv']

# Read the files and concatenate into a single DataFrame
frames = []
for i, file in enumerate(files):
    temp_df = pd.read_csv(file, sep=';')
    temp_df['adjusted_timestamp'] = i * 1000000 + temp_df['timestamp']  # Adjust timestamp
    frames.append(temp_df)
df = pd.concat(frames)

# Filter data for COCONUT and calculate mid prices
coconut_df = df[df['product'] == 'COCONUT'][['adjusted_timestamp', 'ask_price_1', 'bid_price_1']]
coconut_df['mid_price'] = (coconut_df['ask_price_1'] + coconut_df['bid_price_1']) / 2

# Reset the index
coconut_df.reset_index(drop=True, inplace=True)

# Filter data for COCONUT_COUPON and calculate mid prices
coconut_coupon_df = df[df['product'] == 'COCONUT_COUPON'][['adjusted_timestamp', 'ask_price_1', 'bid_price_1']]
coconut_coupon_df['mid_price'] = (coconut_coupon_df['ask_price_1'] + coconut_coupon_df['bid_price_1']) / 2

# Reset the index of coconut_coupon_df
coconut_coupon_df.reset_index(drop=True, inplace=True)

# Assume a constant risk-free rate (you can change this assumption if needed)
risk_free_rate = 0.06

# Calculate time to maturity (assuming 250 trading days per year)
total_trading_days = 250
elapsed_trading_days = len(files)
time_to_maturity = (total_trading_days - elapsed_trading_days) / total_trading_days

# Calculate implied volatility for each timestamp
strike_price = 10000
coconut_coupon_df['implied_volatility'] = coconut_coupon_df.apply(lambda row: implied_volatility(row['mid_price'], coconut_df.loc[row.name, 'mid_price'], strike_price, time_to_maturity, risk_free_rate), axis=1)

# Calculate the call price for each timestamp using COCONUT mid-prices as the stock price and implied volatility
coconut_coupon_df['call_price'] = coconut_coupon_df.apply(lambda row: black_scholes_price(coconut_df.loc[row.name, 'mid_price'], strike_price, time_to_maturity, risk_free_rate, row['implied_volatility']), axis=1)

# Calculate 20-day moving averages
coconut_coupon_df['mid_price_ma20'] = coconut_coupon_df['mid_price'].rolling(window=20).mean()
coconut_coupon_df['call_price_ma20'] = coconut_coupon_df['call_price'].rolling(window=20).mean()

# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

# Plot COCONUT_COUPON mid-prices and calculated call prices
ax1.plot(coconut_coupon_df['adjusted_timestamp'], coconut_coupon_df['mid_price'], label='COCONUT_COUPON Mid Price')
ax1.plot(coconut_coupon_df['adjusted_timestamp'], coconut_coupon_df['call_price'], label='Calculated Call Price')
ax1.set_ylabel('Price')
ax1.set_title('COCONUT_COUPON Mid Prices vs Calculated Call Prices')
ax1.legend()
ax1.grid(True)

# Plot 20-day moving averages
ax2.plot(coconut_coupon_df['adjusted_timestamp'], coconut_coupon_df['mid_price_ma20'], label='COCONUT_COUPON Mid Price (MA20)')
ax2.plot(coconut_coupon_df['adjusted_timestamp'], coconut_coupon_df['call_price_ma20'], label='Calculated Call Price (MA20)')
ax2.set_xlabel('Adjusted Timestamp')
ax2.set_ylabel('Price')
ax2.set_title('20-Day Moving Averages')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()