import backtrader as bt      # For backtesting
import pandas as pd          # For data loading and manipulation
import os                    # For file and directory operations
from datetime import datetime
import numpy as np           # For numerical operations (if needed)

# -------------------------------
# 1. Define the SMA Crossover Strategy with Target/Stop-Loss
# -------------------------------

class SmaTargetStopStrategy(bt.Strategy):
    """
    SMA Target-Stop Strategy:
    
    This strategy uses a simple moving average (SMA) crossover to determine entry signals.
    
    - Long Entry: When the short SMA crosses above the long SMA.
    - Short Entry: When the short SMA crosses below the long SMA.
    
    Once in a position, instead of waiting for the opposite SMA signal, the strategy will
    exit when either:
      - For a long position: the price rises to a target (entry * (1 + target)) OR falls to a stop-loss (entry * (1 - stop_loss)).
      - For a short position: the price falls to a target (entry * (1 - target)) OR rises to a stop-loss (entry * (1 + stop_loss)).
    
    Parameters:
      target (float): Profit target as a fraction (e.g., 0.003 for 0.3% profit)
      stop_loss (float): Stop loss as a fraction (e.g., 0.001 for 0.1% loss)
      short_window (int): Window for the short-term moving average.
      long_window (int): Window for the long-term moving average.
    """
    params = (
        ('target', 0.003),       # 0.3% profit target
        ('stop_loss', 0.001),    # 0.1% stop loss
        ('short_window', 10),
        ('long_window', 50),
    )

    def __init__(self):
        # Create moving average indicators on the closing price.
        self.short_sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_window)
        self.long_sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_window)
        # Create a crossover indicator (value > 0 indicates short_sma > long_sma, and vice versa)
        self.crossover = bt.indicators.CrossOver(self.short_sma, self.long_sma)
        
        # Initialize order and entry price variables.
        self.order = None
        self.entry_price = None

    def notify_order(self, order):
        """
        Called when an order's status changes.
        Sets the entry price when an order is completed.
        """
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                self.log(f'BUY executed at {self.entry_price:.2f}')
            elif order.issell():
                self.entry_price = order.executed.price
                self.log(f'SELL executed at {self.entry_price:.2f}')
            # Reset order status
            self.order = None

    def log(self, txt, dt=None):
        """
        Logging function for the strategy.
        """
        dt = dt or self.data.datetime.date(0)
        print(f'{dt} {txt}')

    def next(self):
        """
        Called on each new data bar.
        Implements entry and exit rules:
        - If not in a position, generate an entry based on the SMA crossover.
        - If in a position, check the current price against target and stop-loss levels.
        """
        # Do nothing if there is a pending order.
        if self.order:
            return

        # If not in a position, check for entry signal.
        if not self.position:
            # Long entry: when short SMA > long SMA.
            if self.crossover > 0:
                self.order = self.buy()  # Enter long position
                return
            # Short entry: when short SMA < long SMA.
            elif self.crossover < 0:
                self.order = self.sell()  # Enter short position
                return

        # If in a long position, check exit conditions.
        if self.position.size > 0 and self.entry_price:
            current_price = self.data.close[0]
            # For long: exit if profit target or stop-loss is reached.
            if current_price >= self.entry_price * (1 + self.p.target):
                self.order = self.sell()  # Exit long position for profit
                self.log(f'Long target reached at {current_price:.2f}')
            elif current_price <= self.entry_price * (1 - self.p.stop_loss):
                self.order = self.sell()  # Exit long position for stop loss
                self.log(f'Long stop loss hit at {current_price:.2f}')
        
        # If in a short position, check exit conditions.
        if self.position.size < 0 and self.entry_price:
            current_price = self.data.close[0]
            # For short: profit when price falls; stop loss when price rises.
            if current_price <= self.entry_price * (1 - self.p.target):
                self.order = self.buy()  # Exit short position for profit
                self.log(f'Short target reached at {current_price:.2f}')
            elif current_price >= self.entry_price * (1 + self.p.stop_loss):
                self.order = self.buy()  # Exit short position for stop loss
                self.log(f'Short stop loss hit at {current_price:.2f}')

# -------------------------------
# 2. Data Loading Function
# -------------------------------

def load_data(csv_file):
    """
    Load historical data from a CSV file and prepare it for Backtrader.
    Expects the CSV file to have the columns: Date, Time, Open, High, Low, Close.
    Combines 'Date' and 'Time' into a datetime index.
    Adds a dummy 'volume' column if not present.
    """
    df = pd.read_csv(csv_file)
    # Combine 'Date' and 'Time' columns into a single datetime column.
    df['Date_Time'] = pd.to_datetime(df['Date'] + " " + df['Time'], errors='coerce')
    df.set_index('Date_Time', inplace=True)
    
    # Rename columns to lowercase as expected by Backtrader.
    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close"
    })
    
    # If 'Volume' is missing, add a dummy column.
    if 'Volume' not in df.columns:
        df['volume'] = 0
    else:
        df = df.rename(columns={"Volume": "volume"})
    
    # Return only the columns required by Backtrader.
    return df[["open", "high", "low", "close", "volume"]]

# -------------------------------
# 3. Backtest Setup and Execution
# -------------------------------

if __name__ == '__main__':
    # Initialize the Cerebro engine.
    cerebro = bt.Cerebro()
    
    # Path to your historical CSV file (update this path as needed).
    csv_file = "h_data/NIFTY_ONE_MINUTE_2025-01-01_2025-01-31.csv"
    data = load_data(csv_file)
    
    # Create a Backtrader data feed from the pandas DataFrame.
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    
    # Add the SMA Target-Stop strategy to Cerebro.
    cerebro.addstrategy(SmaTargetStopStrategy, target=0.003, stop_loss=0.001,
                        short_window=10, long_window=50)
    
    # Set the initial portfolio value.
    cerebro.broker.setcash(100000.0)
    
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    
    # -------------------------------
    # Add Trade Analyzer for Summary
    # -------------------------------
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    
    # Run the backtest.
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    print("Final Portfolio Value: %.2f" % final_value)
    
    # Extract trade analysis.
    trade_analyzer = results[0].analyzers.trade_analyzer.get_analysis()
    total_trades = trade_analyzer.get('total', {}).get('closed', 0)
    long_trades = trade_analyzer.get('long', {}).get('total', 0)
    short_trades = trade_analyzer.get('short', {}).get('total', 0)
    winning_trades = trade_analyzer.get('won', {}).get('total', 0)
    losing_trades = trade_analyzer.get('lost', {}).get('total', 0)
    win_probability = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Create a summary table.
    summary_table = f"""
    +----------------------------------------+-----------------+
    | Metric                                 | Value           |
    +----------------------------------------+-----------------+
    | Total Closed Trades                    | {total_trades}              |
    | Long Trades                            | {long_trades}              |
    | Short Trades                           | {short_trades}              |
    | Winning Trades                         | {winning_trades}              |
    | Losing Trades                          | {losing_trades}              |
    | Winning Probability (%)                | {win_probability:.2f}%       |
    +----------------------------------------+-----------------+
    """
    print(summary_table)
    
    # -------------------------------
    # Plot the Backtest Results (Non-blocking)
    # -------------------------------
    cerebro.plot(show=False)
