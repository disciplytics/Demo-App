# import packages
#from snowflake.snowpark.context import get_active_session
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
#from streamlit_dynamic_filters import DynamicFilters

#st.set_page_config(page_title="Headcount Analytics",layout="wide")
#st.title('Headcount Analytics')


# Get current session
#session = get_active_session()

# Load ANALYICAL_ATTENDANCE
#headcount_data = session.table(f'{st.secrets["database"]}.{st.secrets["schema"]}.HEADCOUNTS_DATA').to_pandas()
#headcount_data = session.table(f'ANALYICAL_ATTENDANCE').to_pandas().reset_index(drop=True)
#dynamic_filters = DynamicFilters(headcount_data, filters=['Event Name', 'Event Frequency', 'Attendance Time', 'Attendance Year', 'Event Day of Week'])
#dynamic_filters.display_filters(location='columns', num_columns=5, gap='small')

st.title('Headcount Report Demo')
st.subheader("A Weekly Report For Attendance")
st.write('This app contains synthetic data and is for demo purposes only.')
st.write(' ')

@st.cache_data
def load_data():
    series_length = 3 * 52
    
    event_names = ["Sunday Morning Adults", "Sunday Morning Kids", "Online Viewers"]
    event_frequencies = ["Weekly"]
    start_at_times = ["10:00", "11:30"]
    
    
    report_data = pd.DataFrame()
    
    for i in event_names:
        if i == 'Sunday Morning Adults':
            weight_i = 0.6
        elif i == 'Sunday Morning Kids':
            weight_i = 0.2
        elif i == 'Online Viewers':
            weight_i = 0.2
        for k in start_at_times:
            if k == '10:00':
                weight_k = 0.4
            elif k == '11:30':
                weight_k = 0.6
    
            weight = weight_k * weight_i
            data = pd.DataFrame(
                {
                    'Event Date': pd.date_range(end=pd.Timestamp.now().floor('d') , freq='W', periods=series_length),
                    'Total Count': np.random.randint(50, 60, size=(series_length)).astype(int),
                    'Regular Count': np.random.randint(10, 20, size=(series_length)).astype(int),
                    'Guest Count': np.random.randint(10, 15, size=(series_length)).astype(int),
                    'Volunteer Count': np.random.randint(5, 10, size=(series_length)).astype(int),
                    'Weight': weight,
                    'Event Name': i,
                    'Event Time': k,
                    'Event Day of Week': 'Sunday'
                })
                
            data['Total Count'] = (data['Total Count'] * data['Weight']).astype(int)
    
            report_data = pd.concat([report_data, data])
    
    def clean_outliers(x):
        median_x = np.median(x)
        std_x = np.std(x)
        ucl_x = median_x + 2*std_x
    
        if x > ucl_x:
            x = median_x
    
        return x
    
    report_data['Total Count'] = report_data['Total Count'].apply(clean_outliers)

    return report_data
    #df_selection = dynamic_filters.filter_df()

headcount_data = load_data()

today = pd.to_datetime(pd.Timestamp.now().floor('d'), format="ISO8601", utc = True)

for i in ['Total Count', 'Regular Count', 'Guest Count', 'Volunteer Count']:
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
        "Select Event Day of Week",
        headcount_data['Event Day of Week'].unique(),
        default=['Sunday'])
    
df_selection = headcount_data.query('`Event Year`== @sel1').query('`Event Name`== @sel2').query('`Event Time`== @sel3').query('`Event Day of Week`== @sel4')

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
        
# get last sunday metrics
last_week_sunday_attendance = headcount_data[(headcount_data['Event Date']  == headcount_data['Event Date'].max())]['Total Count'].sum()

last_week_sunday_volunteer = headcount_data[(headcount_data['Event Date']  == headcount_data['Event Date'].max())]['Volunteer Count'].sum()

last_week_sunday_regular = headcount_data[(headcount_data['Event Date']  == headcount_data['Event Date'].max())]['Regular Count'].sum()

last_week_sunday_guest = headcount_data[(headcount_data['Event Date']  == headcount_data['Event Date'].max() )]['Guest Count'].sum()
    
    
last_week_sunday_attendance_delta = int(headcount_data[(headcount_data['Event Date']  == two_weeks)]['Total Count'].sum())
last_week_sunday_volunteer_delta = int(headcount_data[(headcount_data['Event Date']  == two_weeks)]['Volunteer Count'].sum())
last_week_sunday_regular_delta = int(headcount_data[(headcount_data['Event Date']  == two_weeks)]['Regular Count'].sum())
last_week_sunday_guest_delta = int(headcount_data[(headcount_data['Event Date']  == two_weeks)]['Guest Count'].sum())


with col1:
    try:
        st.metric(label="Last Event Total Total", 
             value=f"{format(int(round(last_week_sunday_attendance,0)), ',d')}",
             delta_color = 'normal',
             delta = f"{last_week_sunday_attendance - last_week_sunday_attendance_delta} From Prior Week")
    except:
        st.metric(label="Last Event Total Total", 
             value=0)

with col2:
    try:
        st.metric(label="Last Event Regular Total", 
             value=f"{format(int(round(last_week_sunday_regular,0)), ',d')}",
             delta_color = 'normal',
             delta = f"{last_week_sunday_regular -last_week_sunday_regular_delta} From Prior Week")
    except:
        st.metric(label="Last Event Regular Total", 
             value=0)
with col3:
    try:
        st.metric(label="Last Event Guest Total", 
             value=f"{format(int(round(last_week_sunday_guest,0)), ',d')}",
             delta_color = 'normal',
             delta = f"{last_week_sunday_guest -last_week_sunday_guest_delta} From Prior Week")
    except:
        st.metric(label="Last Event Guest Total", 
             value=0)
with col4:
    try:
        st.metric(label="Last Event Volunteer Total", 
             value=f"{format(int(round(last_week_sunday_volunteer,0)), ',d')}",
             delta_color = 'normal',
             delta = f"{last_week_sunday_volunteer -last_week_sunday_volunteer_delta} From Prior Week")
    except:
        st.metric(label="Last Event Volunteer Total", 
             value=0)
        
        
trend_df = df_selection.groupby(['Event Date', 'Event Year', 'Event Name', 'Event Time', 'Event Day of Week', 'Service'])['Total Count'].sum().reset_index()#.sort_values(ascending=True).reset_index()
wow_df = df_selection.groupby(['Event Week', 'Event Year'])['Total Count'].sum().sort_values(ascending=True).reset_index()

trend_fig = px.line(
    trend_df.groupby(['Event Date'])['Total Count'].sum().reset_index(),
    x="Event Date",
    y="Total Count",
    title = 'Headcount Trends'
)

wow_fig = px.bar(
    wow_df,
    x="Event Week",
    y="Total Count",
    color = 'Event Year',
    title = 'Headcounts Weekly Trends',
    #render_mode='svg'
).update_layout(yaxis_title=None, xaxis_title=None)


wow_v_df = df_selection.drop(columns = ['Regular Count', 'Guest Count','Total Count'])

wow_v_df = wow_v_df.groupby(['Event Year', 'Event Week'])['Volunteer Count'].sum().reset_index()

wow_v_fig = px.bar(
    wow_v_df,
    x="Event Week",
    y="Volunteer Count",
    color = 'Event Year',
    title = 'Volunteer Weekly Trends',
    #render_mode='svg'
).update_layout(yaxis_title=None, xaxis_title=None)


wow_r_df = df_selection.drop(columns = ['Volunteer Count', 'Guest Count','Total Count'])

wow_r_df = wow_r_df.groupby(['Event Year', 'Event Week'])['Regular Count'].sum().reset_index()

wow_r_fig = px.bar(
    wow_r_df,
    x="Event Week",
    y="Regular Count",
    color = 'Event Year',
    title = 'Regular Weekly Trends',
    #render_mode='svg'
).update_layout(yaxis_title=None, xaxis_title=None)

wow_g_df = df_selection.drop(columns = ['Volunteer Count', 'Regular Count','Total Count'])

wow_g_df = wow_g_df.groupby(['Event Year', 'Event Week'])['Guest Count'].sum().reset_index()

wow_g_fig = px.bar(
    wow_g_df,
    x="Event Week",
    y="Guest Count",
    color = 'Event Year',
    title = 'Regular Weekly Trends',
    #render_mode='svg'
).update_layout(yaxis_title=None, xaxis_title=None)

table = df_selection.pivot_table('Total Count', ['Event Date'], 'Service').reset_index().sort_values(by = ['Event Date'], ascending=False)
table['Event Date'] = pd.to_datetime(table['Event Date'], format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Headcount Trend", 'Headcounts Weekly Trend', 'Volunteer Weekly Trend', 'Regular Weekly Trend', 'Guest Weekly Trend', 'Headcount Table'])
tab1.plotly_chart(trend_fig, theme="streamlit", use_container_width=True)
tab2.plotly_chart(wow_fig, theme="streamlit", use_container_width=True)
tab3.plotly_chart(wow_v_fig, theme="streamlit", use_container_width=True)
tab4.plotly_chart(wow_r_fig, theme="streamlit", use_container_width=True)
tab5.plotly_chart(wow_g_fig, theme="streamlit", use_container_width=True)
tab6.dataframe(table.fillna(0))
