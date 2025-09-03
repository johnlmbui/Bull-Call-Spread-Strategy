import numpy as np
import scipy.stats as si
import yfinance as yf
import datetime
import matplotlib.pyplot as plt  # Importing Matplotlib for graphing

# Black-Scholes Model
def black_scholes_call(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    return call_price

# Calculate the P&L for a Bull Call Spread
def bull_call_spread_pnl(stock_price, lower_strike, upper_strike, T, r, sigma, lower_call_price, upper_call_price):
    premium_paid = lower_call_price - upper_call_price  # Lower strike bought, upper strike sold
    
    if stock_price <= lower_strike:
        pnl = -premium_paid  # Max loss, if the stock price is below the lower strike
    elif stock_price >= upper_strike:
        pnl = (upper_strike - lower_strike) - premium_paid  # Max profit, if stock price is above upper strike
    else:
        pnl = (stock_price - lower_strike) - premium_paid  # Between the two strikes
    
    return pnl, premium_paid

# Fetch stock and options data
def fetch_data(stock_symbol, expiration_date, lower_strike, upper_strike):
    stock_data = yf.Ticker(stock_symbol)
    stock_price = stock_data.history(period="1d")['Close'].iloc[-1]
    
    options_data = stock_data.option_chain(expiration_date)
    call_data = options_data.calls
    
    lower_call_option = call_data[call_data['strike'] == lower_strike].iloc[0]
    upper_call_option = call_data[call_data['strike'] == upper_strike].iloc[0]
    
    return stock_price, lower_call_option, upper_call_option

# Function to plot two line graphs (one for the lower call price and one for the upper call price)
def plot_line_graphs(expirations, market_lower_call_prices, theoretical_lower_call_prices,
                     market_upper_call_prices, theoretical_upper_call_prices):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))  # Create two subplots (one for lower strike, one for upper strike)
    
    # Plot the graph for Lower Strike Call Prices
    ax1.plot(expirations, theoretical_lower_call_prices, label='Theoretical Lower Call Prices', marker='o', color='blue')
    ax1.plot(expirations, market_lower_call_prices, label='Market Lower Call Prices', marker='x', color='red')
    ax1.set_title('Lower Strike Call Prices: Theoretical vs. Market')
    ax1.set_xlabel('Expiration Date')
    ax1.set_ylabel('Call Price ($)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot the graph for Upper Strike Call Prices
    ax2.plot(expirations, theoretical_upper_call_prices, label='Theoretical Upper Call Prices', marker='o', color='blue')
    ax2.plot(expirations, market_upper_call_prices, label='Market Upper Call Prices', marker='x', color='red')
    ax2.set_title('Upper Strike Call Prices: Theoretical vs. Market')
    ax2.set_xlabel('Expiration Date')
    ax2.set_ylabel('Call Price ($)')
    ax2.legend()
    ax2.grid(True)

    # Adjust layout and show the graphs
    plt.tight_layout()
    plt.show()

# Main Evaluation - now to handle the Bull Call Spread and plotting two line graphs
def evaluate_bull_call_spread(stock_symbol, lower_strike, upper_strike, r=0.01, sigma=0.2):
    stock_data = yf.Ticker(stock_symbol)
    available_expirations = stock_data.options  # Get all available expiration dates
    
    expirations = []
    market_lower_call_prices = []
    theoretical_lower_call_prices = []
    market_upper_call_prices = []
    theoretical_upper_call_prices = []
    
    for expiration_date in available_expirations:
        print(f"Evaluating for expiration date: {expiration_date}")
        
        # Fetch data for the given expiration date and strikes
        stock_price, lower_call_option, upper_call_option = fetch_data(stock_symbol, expiration_date, lower_strike, upper_strike)
        
        # Extract market data for the call options
        market_lower_call_price = lower_call_option['lastPrice']
        market_upper_call_price = upper_call_option['lastPrice']
        
        # Calculate time to expiration (in years)
        expiry_date = datetime.datetime.strptime(expiration_date, '%Y-%m-%d')
        today = datetime.datetime.today()
        T = (expiry_date - today).days / 365.0
        
        # Calculate theoretical call prices using the Black-Scholes model
        theoretical_lower_call_price = black_scholes_call(stock_price, lower_strike, T, r, sigma)
        theoretical_upper_call_price = black_scholes_call(stock_price, upper_strike, T, r, sigma)
        
        # Calculate the Bull Call Spread P&L
        bull_call_pnl, premium_paid = bull_call_spread_pnl(stock_price, lower_strike, upper_strike, T, r, sigma, theoretical_lower_call_price, theoretical_upper_call_price)
        
        # Compare the Bull Call Spread vs. Buying a Single Call
        single_call_pnl = (stock_price - lower_strike) - theoretical_lower_call_price if stock_price > lower_strike else -theoretical_lower_call_price
        
        # Output Results for each expiration
        print(f"Stock Price: {stock_price}")
        print(f"Market Lower Call Price: {market_lower_call_price}, Theoretical Lower Call Price: {theoretical_lower_call_price}")
        print(f"Market Upper Call Price: {market_upper_call_price}, Theoretical Upper Call Price: {theoretical_upper_call_price}")
        print(f"Bull Call Spread P&L (Theoretical): {bull_call_pnl}, Premium Paid for Spread: {premium_paid}")
        print(f"Single Call P&L (Theoretical): {single_call_pnl}")
        
        # Check if Put-Call Parity holds
        parity_difference = (market_lower_call_price - market_upper_call_price) - (stock_price - upper_strike * np.exp(-r * T))
        print(f"Put-Call Parity Difference: {parity_difference}")
        if abs(parity_difference) < 0.01:
            print("Put-Call Parity Holds")
        else:
            print("Put-Call Parity Does NOT Hold")
        
        # Collect data for graphing
        expirations.append(expiration_date)
        market_lower_call_prices.append(market_lower_call_price)
        theoretical_lower_call_prices.append(theoretical_lower_call_price)
        market_upper_call_prices.append(market_upper_call_price)
        theoretical_upper_call_prices.append(theoretical_upper_call_price)
        
        print("\n" + "-"*50 + "\n")  # Just to separate each expiration's output

    # Plot the two line graphs for the lower and upper strike prices
    plot_line_graphs(expirations, market_lower_call_prices, theoretical_lower_call_prices,
                     market_upper_call_prices, theoretical_upper_call_prices)

# Input preferences here
stock_symbol = 'AAPL'  # Example: Apple
lower_strike = 170  # Example: Lower strike price for the long call option
upper_strike = 180  # Example: Upper strike price for the short call option

evaluate_bull_call_spread(stock_symbol, lower_strike, upper_strike)
