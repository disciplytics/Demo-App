# import packages
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

st.title('Headcount Report Demo')
st.subheader("A Weekly Report For Attendance")
st.write('This app contains synthetic data and is for demo purposes only.')
st.write(' ')

@st.cache_data
def load_data():
    series_length = 3 * 52
    
    event_names = ["Campus 1 - Sunday Morning Service", "Campus 2 - Sunday Morning Service", "Campus 3 - Sunday Morning Service"]
    attendance_types = ["Adult", "Volunteer", "Youth"]
    start_at_times = ["10:00", "11:30"]
    
    
    report_data = pd.DataFrame()
    
    for i in event_names:
        if i == "Campus 1 - Sunday Morning Service":
            weight_i = 0.6
        elif i == "Campus 2 - Sunday Morning Service":
            weight_i = 0.3
        elif i == "Campus 3 - Sunday Morning Service":
            weight_i = 0.1
        for k in start_at_times:
            if k == '10:00':
                weight_k = 0.4
            elif k == '11:30':
                weight_k = 0.6
            for j in attendance_types:
                if j == "Adult":
                    weight_j = 0.5
                elif j == "Volunteer":
                    weight_j = 0.1
                elif j == "Youth":
                    weight_j = 0.4
                
    
                weight = weight_k * weight_i * weight_j
                data = pd.DataFrame(
                    {
                        'Event Date': pd.date_range(end=pd.Timestamp.now().floor('d') , freq='W', periods=series_length),
                        'Total Count': np.random.randint(60, 80, size=(series_length)).astype(int),
                        'Weight': weight,
                        'Event Name': i,
                        'Event Time': k,
                        'Attendance Type': j,
                        'Event Day of Week': 'Sunday'
                    })
                    
                data['Total Count'] = np.round(data['Total Count'] * data['Weight'], 0).astype(int)
        
                report_data = pd.concat([report_data, data])

    return report_data
    #df_selection = dynamic_filters.filter_df()

headcount_data = load_data()

today = pd.to_datetime(pd.Timestamp.now().floor('d'), format="ISO8601", utc = True)

for i in ['Total Count']:
    headcount_data[i] = pd.to_numeric(headcount_data[i], downcast="integer")

di = {'0': 'Sunday', '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday', '4': 'Thursday', '5': 'Friday', '6': 'Saturday'}
headcount_data.replace({"Event Day of Week": di}, inplace=True)
headcount_data['Event Year'] = headcount_data['Event Date'].dt.year
headcount_data['Event Month'] = headcount_data['Event Date'].dt.month
headcount_data['Event Week'] =  headcount_data['Event Date'].dt.isocalendar().week
headcount_data['Service'] = headcount_data['Event Name'] + " - " + headcount_data['Event Time']
# get rid of future events
#headcount_data = headcount_data[headcount_data['Event Date'] < pd.to_datetime(today)]
col1, col2, col3, col4 = st.columns(4)

with col1:
    sel1 = st.multiselect(
        "Select Event Year",
        headcount_data['Event Year'].unique(),
        default=[headcount_data['Event Year'].max(), headcount_data['Event Year'].max()-1])

with col2:
    sel2 = st.multiselect(
        "Select Event Name",
        headcount_data['Event Name'].unique(),
        default=headcount_data[headcount_data['Event Day of Week'] == 'Sunday']['Event Name'].unique())
with col3:
    sel3 = st.multiselect(
        "Select Event Time",
        headcount_data['Event Time'].unique(),
        default=headcount_data[headcount_data['Event Day of Week'] == 'Sunday']['Event Time'].unique())
with col4:
    sel4 = st.multiselect(
        "Select Attendance Type",
        headcount_data['Attendance Type'].unique(),
        default=headcount_data['Attendance Type'].unique())
    
df_selection = headcount_data.query('`Event Year`== @sel1').query('`Event Name`== @sel2').query('`Event Time`== @sel3').query('`Attendance Type`== @sel4')

df_selection['Event Year'] = df_selection['Event Year'].astype(str)

max_year = df_selection['Event Year'].max()
min_year = df_selection['Event Year'].min()

two_weeks = headcount_data[(headcount_data['Event Day of Week'] == 'Sunday')] 
two_weeks = pd.to_datetime(two_weeks[(two_weeks['Event Date'] == two_weeks['Event Date'].max())]['Event Date'].reset_index(drop = True)[0]) - timedelta(days = 7)

#BUILD FRONT END



col1, col2, col3, col4 = st.columns(4)

try:
    if df_selection['Event Year'].max() != today.year:
        cytd_total_counts = df_selection[df_selection['Event Year'] == max_year]['Total Count'].sum()
        pytd_total_counts = df_selection[df_selection['Event Year'] == min_year]['Total Count'].sum()
        yoy = (cytd_total_counts - pytd_total_counts) / pytd_total_counts

    else:

        cytd_total_counts_metrics = df_selection[(df_selection['Event Year'] == df_selection['Event Year'].max()) &
                                          (df_selection['Event Week'] < today.isocalendar()[1])]
        pytd_total_counts_metrics = df_selection[(df_selection['Event Year'] == df_selection['Event Year'].max()-1) &
                                              (df_selection['Event Week'] < today.isocalendar()[1])]
    
        df_selection_metrics = pd.concat([pytd_total_counts_metrics, cytd_total_counts_metrics])
            
        cytd_total_counts = df_selection_metrics[(df_selection_metrics['Event Year'] == df_selection_metrics['Event Year'].max())]['Event Year'].sum()
        pytd_total_counts = df_selection_metrics[(df_selection_metrics['Event Year'] == df_selection_metrics['Event Year'].max()-1)]['Event Year'].sum()
        yoy = (cytd_total_counts - pytd_total_counts) / pytd_total_counts
except:
        cytd_total_counts = 0
        pytd_total_counts = 0
        yoy = 0
        

        
trend_df = df_selection.groupby(['Event Date', 'Event Year', 'Event Name', 'Event Time', 'Attendance Type', 'Service'])['Total Count'].sum().reset_index()
trend_time_df = df_selection.groupby(['Event Date', 'Event Year', 'Event Name', 'Event Time'])['Total Count'].sum().reset_index()
trend_at_df = df_selection.groupby(['Event Date', 'Event Year', 'Event Name', 'Event Time'])['Total Count'].sum().reset_index()
wow_df = df_selection.groupby(['Event Week', 'Event Year'])['Total Count'].sum().sort_values(ascending=True).reset_index()

trend_fig = px.line(
    trend_df.groupby(['Event Date'])['Total Count'].sum().reset_index(),
    x="Event Date",
    y="Total Count",
    title = 'Headcount Trends'
)

trend_time_fig = px.line(
    trend_df.groupby(['Event Date', 'Event Time'])['Total Count'].sum().reset_index(),
    x="Event Date",
    y="Total Count",
    color='Event Time',
    title = 'Headcount Trends By Event Time'
)

wow_fig = px.bar(
    wow_df,
    x="Event Week",
    y="Total Count",
    color = 'Event Year',
    title = 'Headcounts Weekly Trends',
    #render_mode='svg'
)




table = df_selection.pivot_table('Total Count', ['Event Date'], 'Service').reset_index().sort_values(by = ['Event Date'], ascending=False)
table['Event Date'] = pd.to_datetime(table['Event Date'], format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')
tab1, tab2, tab3 = st.tabs(["Headcount Trend", "Headcounts Year-Over-Year", "Headcount Trend By Service Time"])
tab1.plotly_chart(trend_fig, theme="streamlit", use_container_width=True)
tab2.plotly_chart(wow_fig, theme="streamlit", use_container_width=True)
tab3.plotly_chart(trend_time_fig, theme="streamlit", use_container_width=True)
st.dataframe(table.fillna(0))
