import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
import holidays


def curr_fut_close(data, monthly_exp):
    #FINDING INDEX CLOSE PRICE
    ''' 
    This Function will Extract Curr Future close price from intraday nifty data,
    which is daily downloaded fron FINWESIYA
    The Out put columns will be ['symbol', 'date', 'time', 'curr_fut_close']
    '''
    #FINDING CURRENT MONTH FUTURE CLOSE PRICE
    temp_fut_df = data[(data['instrument']=='FUTIDX') & (data['exp_date']==monthly_exp) & (data['time'] >= '09:15:00')]\
        [['date', 'time' ,'close']].reset_index(drop=True)

    temp_fut_df['datetime'] = temp_fut_df['date'].astype(str) + ' ' + temp_fut_df['time'].astype(str)
    temp_fut_df.sort_values(by='time', inplace=True, ascending=True)
    temp_fut_df.set_index('datetime', inplace=True)
    temp_fut_df.drop(columns=['date', 'time'], inplace=True)
    temp_fut_df.rename(columns={'close': 'curr_fut_close'}, inplace=True)

    return temp_fut_df


def index_close(data):
    #FINDING INDEX CLOSE PRICE
    ''' 
    This Function will Extract Index close price from intraday nifty data,
    which is daily downloaded fron FINWESIYA
    The Out put columns will be ['symbol', 'date', 'time', 'index_close']
    '''

    temp_index_df = data[(data['instrument']=='INDEX') & (data['time'] >= '09:15:00')] \
        [['symbol', 'date', 'time', 'close']].reset_index(drop=True)

    temp_index_df.sort_values(by='time', inplace=True, ascending=True)
    # Combine 'date' and 'time' columns into a single datetime column
    # strdd_df['datetime'] = pd.to_datetime(strdd_df['date'] + ' ' + strdd_df['time'])
    temp_index_df['datetime'] = temp_index_df['date'].astype(str) + ' ' + temp_index_df['time'].astype(str)

    # Set the new 'datetime' column as the index
    temp_index_df.set_index('datetime', inplace=True)

    #Rename column name
    temp_index_df.rename(columns={'close': 'index_close'}, inplace=True)

    return temp_index_df



def curr_monthly_expiry_date(current_date):

    ''' 
    This function will find the nearest monthlly expiry
    which will be used to find the current month future

    input format: Timestamp('2023-06-01 00:00:00')
    output format: Timestamp('2023-06-29 00:00:00')
    
    '''
    # # Define a list of holidays (you can expand this list based on your requirements)
    # holidays = ['2024-08-29',  # Example holiday on a Thursday
    #             '2024-08-28',  # Example holiday on a Wednesday
    # # Add other holidays in 'YYYY-MM-DD' format
    # ]
    # # Convert current_date to a datetime object if it's not already
    # current_date = pd.to_datetime(current_date)

    #Extract Year from timestamp format
    yr = current_date.year
 
    # Get the last day of the current month
    last_day_of_month = current_date + pd.offsets.MonthEnd(0)
    
    # Find the weekday of the last day of the month (0=Monday, 1=Tuesday, ..., 6=Sunday)
    weekday_last_day = last_day_of_month.weekday()
    
    # Calculate the difference to the last Thursday (3=Thursday)
    days_to_last_thursday = (weekday_last_day - 3) % 7
    
    # Subtract the difference to find the last Thursday of the month
    last_thursday = last_day_of_month - pd.Timedelta(days=days_to_last_thursday)

    # Check if the last Thursday is a holiday and adjust accordingly
    expiry_date = last_thursday

    while expiry_date.strftime('%Y-%m-%d') in holidays.holidays(year=yr):
        expiry_date -= timedelta(days=1)
    
    return expiry_date

def curr_next_weekly_expiry(current_date):
    ''' 
     This Finction will find the 'CURRENT Weekly EXPIRY (Thursday)' and 'NEXT TO NEXT EXPIRY DATE' for Nifty 50
    THe expiry date will occurs on thrusday, if there is holyday on thrusday then expiry date will be 
    the prier to the thrusday
    
    input format: Timestamp('2023-06-01 00:00:00')
    output format: Timestamp('2023-06-01 00:00:00')
    '''
    # Extract the year from the current date
    yr = current_date.year

    # Get the weekday of the current date
    weekday_current_date = current_date.weekday()

#For Current Expiry
    # Calculate the difference to the next Thursday (3=Thursday)
    days_to_next_thursday = (3 - weekday_current_date) % 7
    # Find the nearest Thursday
    next_thursday = current_date + pd.Timedelta(days=days_to_next_thursday)
    # Adjust for holidays: if Thursday is a holiday, shift to the previous day
    curr_expiry_date = next_thursday

    while curr_expiry_date.strftime('%Y-%m-%d') in holidays.holidays(yr):
      curr_expiry_date -= timedelta(days=1)

#For Next Expiry
    days_to_next_next_thursday = 7 + (3 - weekday_current_date) % 7 # 7 added because we have to find the next to next Thrusday
    # Find the next Thursday
    next_to_next_thursday = current_date + pd.Timedelta(days=days_to_next_next_thursday)
    # Adjust for holidays: if Thursday is a holiday, shift to the previous day
    next_expiry_date = next_to_next_thursday

    while next_expiry_date.strftime('%Y-%m-%d') in holidays.holidays(yr):
      next_expiry_date -= timedelta(days=1)

    return curr_expiry_date, next_expiry_date


def plot_and_save_straddle_vs_index(strdd_df, save_path, title):
    # Convert the time column to datetime format
    strdd_df['time'] = pd.to_datetime(strdd_df['time'], format='%H:%M:%S')

    # Filter for times with a 15-minute interval for correct display of time on X-Label
    interval_df = strdd_df[strdd_df['time'].dt.minute % 15 == 0]

    # Filter for 30-minute intervals for vertical lines
    lines_df = strdd_df[strdd_df['time'].dt.minute % 30 == 0]

    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot curr_strdd_close on the first y-axis
    ax1.plot(strdd_df['time'], strdd_df['strdd_close'], color='blue', label='Strdd Close')
    ax1.set_ylabel('Strdd Close Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()
    ax2.plot(strdd_df['time'], strdd_df['index_close'], color='green', label='Index Close')
    ax2.plot(strdd_df['time'], strdd_df['curr_fut_close'], color='orange', label='Curr Fut Close')
    ax2.set_ylabel('Index & Fut Close', color='black')
    ax2.tick_params(axis='y', labelcolor='black')

    # Set x-axis to show only 15-minute intervals
    ax1.set_xticks(interval_df['time'])
    ax1.set_xticklabels(interval_df['time'].dt.strftime('%H:%M'), rotation=45, ha='right')

    # Adding vertical dotted lines every 30 minutes
    for line_time in lines_df['time']:
        ax1.axvline(x=line_time, color='gray', linestyle='--', linewidth=0.75)

    # Adding legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Title and labels
    plt.title(title)
    plt.xlabel('Time')

    # Save the plot to the specified path
    plt.savefig(save_path, bbox_inches='tight')
    # plt.show() if you want to display the image in pop-up window then enable this line

# Example usage:
# plot_and_save_straddle_vs_index(strdd_df, 'path/to/save/plot.png')
