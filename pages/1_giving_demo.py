# Giving Demo

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.title('Giving Report Demo')
st.write('This app contains synthetic data and is for demo purposes only.')

series_length = 3 * 52

dims_pc = ['Campus 1', 'Campus 2', 'Campus 3']
dims_ag = ['Young Adult (18-29)', 'Adult (30-64)', 'Senior (65+)']
dims_mem = ['Guest', 'Attendee', 'Member']


report_data = pd.DataFrame()

for i in dims_pc:
    if i == 'Campus 1':
        weight_i = 1
    elif i == 'Campus 2':
        weight_i = 0.7
    elif i == 'Campus 3':
        weight_i = 0.2
    for j in dims_ag:
        if j == 'Young Adult (18-29)':
            weight_j = 0.1
        elif j == 'Senior (65+)':
            weight_j = 0.3
        elif j == 'Adult (30-64)':
            weight_j = 1
        for k in dims_mem:
            if k == 'Guest':
                weight_k = 0.25
            elif k == 'Attendee':
                weight_k = 0.67
            elif k == 'Member':
                weight_k = 1

            weight = weight_k * weight_j * weight_i
            data = pd.DataFrame(
            {
                'Date': pd.date_range(end=pd.Timestamp.now().floor('d') , freq='W', periods=series_length),
                'Donations_': np.random.randint(50, 200, size=(series_length)).astype(int),
                'Weight': weight
                'Primary Campus': i,
                'Age Group': j,
                'Membership': k
            })

            data['Donations'] = data['Donations_'] * data['Weight']

            report_data = pd.concat([report_data, data])

ytd_col, yoy_col, avg_col = st.columns(3)

current_year = pd.Timestamp.now().year
current_month = pd.Timestamp.now().month
current_week = pd.Timestamp.now().isocalendar().week
previous_year = pd.Timestamp.now().year - 1
two_previous_year = pd.Timestamp.now().year - 2

ytd_sum = report_data[report_data['Date'].dt.year == current_year]['Donations'].sum()
pytd_sum = report_data[(report_data['Date'].dt.year == previous_year) &
                       (report_data['Date'].dt.isocalendar().week < current_week)]['Donations'].sum()
twoytd_sum = report_data[(report_data['Date'].dt.year == two_previous_year) &
                       (report_data['Date'].dt.isocalendar().week < current_week)]['Donations'].sum()
yoy = np.round((pytd_sum - ytd_sum)/pytd_sum * 100,2)
pyoy = np.round((twoytd_sum - pytd_sum)/twoytd_sum * 100,2)
ytd_mean = report_data[report_data['Date'].dt.year == current_year]['Donations'].mean()
pytd_mean = report_data[report_data['Date'].dt.year == previous_year]['Donations'].mean()

with ytd_col:
    st.metric(label="Year to Date Giving", value="${:.2f}".format(ytd_sum), delta="${:.2f}".format(ytd_sum - pytd_sum) + ' (+/-) From Last YTD', delta_color="normal")
with yoy_col:
    st.metric(label="Year Over Year Giving", value="{:.2f}%".format(yoy), delta="{:.2f}%".format(yoy - pyoy) + ' (+/-) From Last YTD', delta_color="normal")
with avg_col:
    st.metric(label="Average Donation", value="${:.2f}".format(ytd_mean), delta="${:.2f}".format(ytd_mean - pytd_mean) + ' (+/-) From Last YTD', delta_color="normal")

report_data['Week'] = report_data['Date'].dt.isocalendar().week
report_data['Month'] = report_data['Date'].dt.month
report_data['Year'] = report_data['Date'].dt.year


weekly_tab, monthly_tab, date_tab = st.tabs(['Weekly YoY', 'Monthly YoY', 'Date Trend'])

with weekly_tab:
    weekly_fig = px.line(
        report_data.groupby(['Year', 'Week'])['Donations'].sum().reset_index(),
        x = 'Week',
        y = 'Donations',
        color='Year',
        title='Year Over Year Giving By Week'
    )
    weekly_tab.plotly_chart(weekly_fig, use_container_width=True)

with monthly_tab:
    monthly_fig = px.line(
        report_data.groupby(['Year', 'Month'])['Donations'].sum().reset_index(),
        x = 'Month',
        y = 'Donations',
        color='Year',
        title='Year Over Year Giving By Month'
    )
    monthly_tab.plotly_chart(monthly_fig, use_container_width=True)

with date_tab:
    date_fig = px.line(
        report_data.groupby(['Date'])['Donations'].sum().reset_index(),
        x = 'Date',
        y = 'Donations',
        title='Giving Trend'
    )
    date_tab.plotly_chart(date_fig, use_container_width=True)

camp_col, ag_col, mem_col = st.columns(3)

with camp_col:
    camp_fig = px.bar(
        report_data.groupby(['Primary Campus'])['Donations'].sum().reset_index(),
        y = 'Primary Campus',
        x = 'Donations',
        title='Giving By Primary Campus'
    )
    st.plotly_chart(camp_fig, use_container_width=True)

with ag_col:
    ag_fig = px.bar(
        report_data.groupby(['Age Group'])['Donations'].sum().reset_index(),
        y = 'Age Group',
        x = 'Donations',
        title='Giving By Age Group'
    )
    st.plotly_chart(ag_fig, use_container_width=True)

with mem_col:
    mem_fig = px.bar(
        report_data.groupby(['Membership'])['Donations'].sum().reset_index(),
        y = 'Membership',
        x = 'Donations',
        title='Giving By Membership'
    )
    st.plotly_chart(mem_fig, use_container_width=True)
