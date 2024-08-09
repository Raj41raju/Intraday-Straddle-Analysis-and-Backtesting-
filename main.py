import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
import holidays
from modules import index_close, curr_fut_close, curr_monthly_expiry_date, curr_next_weekly_expiry, plot_and_save_straddle_vs_index

data = pd.read_csv('data/NIFTY_01-06-2023.csv')
# print(data.head())

#Converting date into datetime format
data['date'] = pd.to_datetime(data['date'], format="%d-%m-%Y")
data['exp_date'] = pd.to_datetime(data['exp_date'], format="%d-%b-%Y")

#Find current date from dataframe 
curr_date = data['date'].iloc[0]

#find Monthly expiry date
monthly_exp = curr_monthly_expiry_date(curr_date)
#Find Curren and next expiry date
curr_exp, next_exp = curr_next_weekly_expiry(curr_date)
# print(f"Current Date: {curr_date.date()}")

# print(f"Current Expiry: {curr_exp} \nNext Expiry: {next_exp} \nMonthly Expiry: {monthly_exp}")

exp_var = [[curr_exp, monthly_exp, 1, 'Current Straddle Close Vs Index & Fut Close'], \
           [next_exp, monthly_exp, 2, 'Next Straddle Close Vs Index & Fut Close'], \
            [monthly_exp, monthly_exp, 3, 'Monthly Straddle Close Vs Index & Fut Close']]

for lst in exp_var[:]:
    expiry_date = lst[0]
    month_exp = lst[1]
    exp_no = lst[2]
    title = "DT:" + str(curr_date.date()) + " " + lst[3] + " EXP:" + str(expiry_date.date())
    print(title)
    # print(f"Expiry: {expiry} \nExpiry NO.: {exp_no} \nTitle: {title}")

    index_df = index_close(data)
    curr_fut_df = curr_fut_close(data, month_exp)
    # print(index_df.head())
    # print("#"*20)
    # print(curr_fut_df.head())

    #Merget two dataframe based on matching key=Index. merging INDEX AND FUTURE DATAFRAME
    index_fut_df = index_df.join(curr_fut_df, how='left')
    # # Perform a left join on the index
    # result = df1.merge(df2, how='left', left_index=True, right_index=True)
    if exp_no == 1:
        ''' 
        For Current expiry the ATM will be calculated from INDEX CLOSE price
        '''
        index_fut_df['strike_price'] = round(index_fut_df['index_close']/50)*50
    else:
        ''' 
        For Next and Monthly expiry the ATM will be calculated from FUTURE CLOSE price
        '''
        index_fut_df['strike_price'] = round(index_fut_df['curr_fut_close']/50)*50 


    #Filtering call option data for current expiry and only keep required features
    call_opt = data[(data['exp_date']==expiry_date) & (data['option_type'] == 'CE')][['date', 'time', 'strike_price', 'close']]
    call_opt.rename(columns={'close':'ce_close'}, inplace=True)
    #Filtering put option data for current expiry and only keep required features
    put_opt = data[(data['exp_date']==expiry_date) & (data['option_type'] == 'PE')][['date', 'time', 'strike_price', 'close']]
    put_opt.rename(columns={'close':'pe_close'}, inplace=True)
    strdd_df = index_fut_df.merge(call_opt, on=['date', 'time', 'strike_price']).merge(put_opt, on=['date', 'time', 'strike_price'])

    strdd_df['strdd_close'] = strdd_df['ce_close'] + strdd_df['pe_close'] 
    # print(strdd_df.head())
    filename = "Nifty" + "_" + str(curr_date.date()) + "_Strdd_Close_" + str(exp_no) + ".png"
    path = "E:\\Key_Indicator_Stock_Market\\" + filename

    #PLot and Save the image
    plot_and_save_straddle_vs_index(strdd_df, path, title)
    # break
