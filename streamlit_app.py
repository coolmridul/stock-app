import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
from const import *
from dateutil.relativedelta import relativedelta

st.title("NSE Data")

hide_github_icon = """
<style>
#MainMenu {
  visibility: hidden;
}
<style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

baseurl = "https://www.nseindia.com/"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) '
                         'Chrome/80.0.3987.149 Safari/537.36',
           'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}


def call_api(start_date,end_date,symbol):
    link = f"https://www.nseindia.com/api/historical/securityArchives?from="+\
        start_date+"&to="+end_date+"&symbol="+symbol+"&dataType=priceVolumeDeliverable&series=EQ&csv=true"

    session = requests.Session()
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    response = session.get(link, headers=headers, timeout=5, cookies=cookies)

    with open('data.csv', 'wb') as f:
        f.write(response.content)
    
    df = pd.read_csv('data.csv',encoding='unicode_escape')
    df['Total Traded Quantity  '] = df['Total Traded Quantity  '].str.replace(',', '').astype(int)
    df['No. of Trades  '] = df['No. of Trades  '].str.replace(',', '').astype(int)
    df['Deliverable Qty  '] = df['Deliverable Qty  '].str.replace(',', '').astype(int)
    df['Turnover ₹  '] = df['Turnover ₹  '].str.replace(',', '').astype(float)
    # df['VWAP'] = df['Turnover ₹  ']/df['Total Traded Quantity  ']
    df['Avg Quantity Per Trade'] = df['Total Traded Quantity  ']/df['No. of Trades  ']
    df['date_column'] = pd.to_datetime(df['Date  '], format='%d-%b-%Y').dt.strftime('%b-%Y')
    st.dataframe(df)

    df4 = df.groupby(['date_column'],sort=False).agg({'Total Traded Quantity  ': ['sum','mean'],
         'Deliverable Qty  ': ['sum','mean'],
         'Turnover ₹  ': 'sum'
         }).reset_index()
    
    df4.columns = ['_'.join(col).strip() for col in df4.columns.values]
    
    df4.columns = [
    'Date', 
    'Total_Traded_Quantity_Sum', 'Total_Traded_Quantity_Mean',
    'Deliverable_Qty_Sum', 'Deliverable_Qty_Mean',
    'Turnover_Sum']

    df4['VWAP'] = df4['Turnover_Sum']/df4['Total_Traded_Quantity_Sum']
    st.dataframe(df4)

start_date = st.date_input("Start Date", datetime.datetime.today() + relativedelta(years=-1),format="DD-MM-YYYY")
start_date_formatted = start_date.strftime("%d-%m-%Y")

end_date = st.date_input("End Date", datetime.datetime.today(),format="DD-MM-YYYY")
end_date_formatted = end_date.strftime("%d-%m-%Y")

option = st.selectbox(
   "Symbols",
   NIFTYALL,
   index=None,
   placeholder="Select stock from the list..",
)

if st.button("Submit"):

    if option is not None:
        call_api(start_date_formatted,end_date_formatted,option)
    else:
        st.write("Error! Select Stock from the list")

