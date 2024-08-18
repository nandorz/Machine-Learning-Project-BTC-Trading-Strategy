import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Load your data
# For demonstration, let's use a sample DataFrame. Replace this with your data.
merged_df = pd.read_excel('model_fitting_details_xgb_6.xlsx')
# Ensure 'Date' is set as the index
merged_df['Date'] = pd.to_datetime(merged_df['open_time'])
merged_df.set_index('Date', inplace=True)

# Ensure index is DatetimeIndex
if not isinstance(merged_df.index, pd.DatetimeIndex):
    merged_df.index = pd.to_datetime(merged_df.index)

# Define buy and sell signals
buy_signals = merged_df[merged_df['model_prediction'] == 1]
sell_signals = merged_df[merged_df['model_prediction'] == 0]

# Function to filter consecutive signals
def filter_consecutive_signals(df):
    mask = df.index.to_series().diff().fillna(pd.Timedelta(seconds=1)) != pd.Timedelta(minutes=30)
    return df[mask]

# Apply the function to buy and sell signals
buy_signals_filtered = filter_consecutive_signals(buy_signals)
sell_signals_filtered = filter_consecutive_signals(sell_signals)

# Resampling functions
def resample_data(df, freq):
    resampled_df = df.resample(freq).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
    return resampled_df

def resample_signals(signals_df, freq):
    resampled_signals = signals_df.resample(freq).last()  # Use last to get the signal's position
    return resampled_signals

# Plot function
def plot_candlestick_with_signals(df, start_date, end_date):
    filtered_df = df[start_date:end_date]
    resampled_df = resample_data(filtered_df, '30T')
    
    buy_signals_filtered = filter_consecutive_signals(buy_signals[start_date:end_date])
    sell_signals_filtered = filter_consecutive_signals(sell_signals[start_date:end_date])
    
    buy_signals_resampled = resample_signals(buy_signals_filtered, '30T')
    sell_signals_resampled = resample_signals(sell_signals_filtered, '30T')

    fig = go.Figure()
    
    # Add Candlestick trace
    fig.add_trace(go.Candlestick(
        x=resampled_df.index,
        open=resampled_df['open'],
        high=resampled_df['high'],
        low=resampled_df['low'],
        close=resampled_df['close'],
        name='Candlestick'
    ))

    # Add Buy signals
    fig.add_trace(go.Scatter(
        x=buy_signals_resampled.index,
        y=buy_signals_resampled['close'],
        mode='markers',
        marker=dict(symbol='triangle-up', color='purple', size=10),
        name='Buy Signal'
    ))

    # Add Sell signals
    fig.add_trace(go.Scatter(
        x=sell_signals_resampled.index,
        y=sell_signals_resampled['close'],
        mode='markers',
        marker=dict(symbol='triangle-down', color='pink', size=10),
        name='Sell Signal'
    ))

    fig.update_layout(
        title='Candlestick Chart with Filtered Buy/Sell Signals',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )
    
    return fig

# Streamlit App
st.title('Candlestick Chart with Filtered Buy/Sell Signals')

# Slider for date range
start_date = st.date_input('Start Date', merged_df.index.min())
end_date = st.date_input('End Date', merged_df.index.max())

# Plot
fig = plot_candlestick_with_signals(merged_df, start_date, end_date)
st.plotly_chart(fig)
