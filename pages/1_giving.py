# Giving Demo

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import timedelta
from streamlit_dynamic_filters import DynamicFilters

st.title('Giving Report Demo')
st.write('This app contains synthetic data and is for demo purposes only.')
st.write(' ')



# load analytical dataframe
@st.cache_data
def load_data():

    series_length = 3 * 52

    dims_pc = ['Campus 1', 'Campus 2', 'Campus 3']
    dims_ag = ['Young Adult (18-29)', 'Adult (30-64)', 'Senior (65+)']
    dims_mem = ['Guest', 'Attendee', 'Member']
    dims_fund = ['General Giving', 'Missions', 'Youth Group', 'Music Ministries']
    dims_loc = ["Columbus, OH", "Grove City, OH", "Worthington, OH", "Dublin, OH"]
    
    report_data = pd.DataFrame()
    
    for i in dims_pc:
        if i == 'Campus 1':
            weight_i = .5
        elif i == 'Campus 2':
            weight_i = 0.3
        elif i == 'Campus 3':
            weight_i = 0.2
        for j in dims_ag:
            if j == 'Young Adult (18-29)':
                weight_j = 0.1
            elif j == 'Senior (65+)':
                weight_j = 0.3
            elif j == 'Adult (30-64)':
                weight_j = 0.6
            for k in dims_mem:
                if k == 'Guest':
                    weight_k = 0.1
                elif k == 'Attendee':
                    weight_k = 0.15
                elif k == 'Member':
                    weight_k = 0.75
                for l in dims_fund:
                    if l == 'Missions':
                        weight_l = 0.1
                    elif l == 'Youth Group':
                        weight_l = 0.05
                    elif l == 'Music Ministries':
                        weight_l = 0.1
                    elif l == 'General Giving':
                        weight_l = 0.75
                    for m in dims_loc:
                        if m == 'Columbus, OH':
                            weight_m = 0.1
                        elif m == 'Grove City, OH':
                            weight_m = 0.05
                        elif m == 'Worthington, OH':
                            weight_m = 0.1
                        elif m == 'Dublin, OH':
                            weight_m = 0.75
    
                        weight = weight_k * weight_j * weight_i * weight_l * weight_m

                        if m == 'Columbus, OH':
                            lat = 39.983334
                            long = -82.983330
                        elif m == 'Grove City, OH':
                            lat = 39.8822
                            long = -83.0935
                        elif m == 'Dublin, OH':
                            lat = 40.0992
                            long = -83.1141
                        elif m == 'Worthington, OH':
                            lat = 40.0931
                            long = -83.0180
                        data = pd.DataFrame(
                        {
                            'DONATION_DATE': pd.date_range(end=pd.Timestamp.now().floor('d') , freq='W', periods=series_length),
                            'Donations_': np.random.randint(2000, 6000, size=(series_length)).astype(int),
                            'Weight': weight,
                            'PRIMARY_CAMPUS': i,
                            'AGE_GROUP': j,
                            'MEMBERSHIP': k,
                            'FUND': l,
                            'DONOR_LOCATION': m,
                            'LATITUDE': lat,
                            'LONGITUDE': long,
                        })
            
                        data['DONATION_YEAR'] = data['DONATION_DATE'].dt.year.astype(int)
                        data['DONATION_MONTH'] = data['DONATION_DATE'].dt.month.astype(int)
                        data['DONATION_WEEK'] = data['DONATION_DATE'].dt.isocalendar().week.astype(int)
                        
                        data['DONATION_AMOUNT'] = data['Donations_'] * data['Weight']
            
                        report_data = pd.concat([report_data, data])
    
    def clean_outliers(x):
        median_x = np.median(x)
        std_x = np.std(x)
        ucl_x = median_x + 2*std_x
    
        if x > ucl_x:
            x = median_x
    
        return x
    
    report_data['DONATION_AMOUNT'] = report_data['DONATION_AMOUNT'].apply(clean_outliers)

    return report_data

# Load data
giving_data = load_data()

today = pd.Timestamp.now().floor('d')

# filters


#dynamic_filters = DynamicFilters(giving_data, filters=['DONATION_YEAR', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'DONOR_LOCATION'])

#dynamic_filters.display_filters(location='columns', num_columns=5, gap='small')

#df_selection = dynamic_filters.filter_df()

col1, col2, col3, col4 = st.columns(4)

with col1:
    sel1 = st.multiselect(
        "Select Two Donation Years",
        giving_data['DONATION_YEAR'].unique(),
        default = [giving_data['DONATION_YEAR'].max(), giving_data['DONATION_YEAR'].max() - 1])
with col2:
    sel2 = st.multiselect(
        "Select Primary Campus",
        giving_data['PRIMARY_CAMPUS'].unique(),
        default = giving_data['PRIMARY_CAMPUS'].unique())
with col3:
    sel3 = st.multiselect(
        "Select Age Group",
        giving_data['AGE_GROUP'].unique(),
        default = giving_data['AGE_GROUP'].unique())
with col4:
    sel4 = st.multiselect(
        "Select Membership",
        giving_data['MEMBERSHIP'].unique(),
        default = giving_data['MEMBERSHIP'].unique())
    
df_selection = giving_data.query('`DONATION_YEAR`== @sel1').query('`PRIMARY_CAMPUS`== @sel2').query('`AGE_GROUP`== @sel3').query('`MEMBERSHIP`== @sel4')

max_year = df_selection['DONATION_YEAR'].max()
min_year = df_selection['DONATION_YEAR'].min()

ytd_tab, trend_tab = st.tabs(["Year Over Year Report", "Deep Dive"])


# YTD Tab
with ytd_tab:
    st.write('The "Year Over Year Report" defaults to a current year to date versus last year to date comparison. You can compare years ad hoc too.  ')

    ytd_col, growth_col, avg_col = st.columns(3)

    try:
        if df_selection['DONATION_YEAR'].max() != today.year:
            cytd_donations = df_selection[df_selection['DONATION_YEAR'] == max_year]['DONATION_AMOUNT'].sum()
            pytd_donations = df_selection[df_selection['DONATION_YEAR'] == min_year]['DONATION_AMOUNT'].sum()
            yoy = (cytd_donations - pytd_donations) / pytd_donations
            cytd_mean = df_selection[df_selection['DONATION_YEAR'] == max_year]['DONATION_AMOUNT'].mean()
            pytd_mean = df_selection[df_selection['DONATION_YEAR'] == min_year]['DONATION_AMOUNT'].mean()
            
        else:

            cytd_donations_metrics = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]
            pytd_donations_metrics = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()-1) &
                                              (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]
    
            df_selection_metrics = pd.concat([pytd_donations_metrics, cytd_donations_metrics])
            
            cytd_donations = df_selection_metrics[(df_selection_metrics['DONATION_YEAR'] == df_selection_metrics['DONATION_YEAR'].max())]['DONATION_AMOUNT'].sum()
            pytd_donations = df_selection_metrics[(df_selection_metrics['DONATION_YEAR'] == df_selection_metrics['DONATION_YEAR'].max()-1)]['DONATION_AMOUNT'].sum()
            yoy = (cytd_donations - pytd_donations) / pytd_donations
            cytd_mean = df_selection_metrics[(df_selection_metrics['DONATION_YEAR'] == df_selection_metrics['DONATION_YEAR'].max())]['DONATION_AMOUNT'].mean()
            pytd_mean = df_selection_metrics[(df_selection_metrics['DONATION_YEAR'] == df_selection_metrics['DONATION_YEAR'].max()-1)]['DONATION_AMOUNT'].mean()
    except:
        cytd_donations = 0
        pytd_donations = 0
        yoy = 0
        cytd_mean = 0
        pytd_mean = 0
        
    with ytd_col:
        try:
            st.metric(label="Year to Date Donations", 
                      value=f"${format(int(np.round(cytd_donations,0)), ',d')}",
                      delta_color = 'normal',
                      delta = f"{format(int(np.round(cytd_donations - pytd_donations, 0)), ',d')} (+/-) From Prior Year")
        except:
            st.write("No data for current selection. Try selecting more data.")

    with growth_col:
        try:
            st.metric(label="Year Over Year Growth", 
                      value=f"{np.round(100 * yoy,2)} %")
        except:
            st.write("No data for current selection. Try selecting more data.")
    with avg_col:
        try:
            st.metric(label="Year Over Year Average (Mean) Donation", 
                      value=f"${np.round(cytd_mean,2)}",
                      delta_color = 'normal',
                      delta = f"{np.round(cytd_mean - pytd_mean, 2)} (+/-) From Prior Year")
        except:
            st.write("No data for current selection. Try selecting more data.")

    line_tab, bar_tab = st.tabs(['Weekly View', 'Yearly View'])
    
    try:
        if df_selection['DONATION_YEAR'].max() != today.year:
            week_ytd_fig = px.line(
                            df_selection.groupby(['DONATION_WEEK', 'DONATION_YEAR'])['DONATION_AMOUNT'].sum().reset_index(),
                            x="DONATION_WEEK",
                            y="DONATION_AMOUNT",
                            color = 'DONATION_YEAR',
                            title = 'Year Over Year By Weekly Giving',
                            render_mode='svg'
                        ).update_layout(yaxis_title=None, xaxis_title=None)
        else:
            cytd_donations_cy = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]
            pytd_donations_cy = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()-1)]

            df_selection_cy = pd.concat([pytd_donations_cy, cytd_donations_cy])
            week_ytd_fig = px.line(
                            df_selection_cy.groupby(['DONATION_WEEK', 'DONATION_YEAR'])['DONATION_AMOUNT'].sum().reset_index(),
                            x="DONATION_WEEK",
                            y="DONATION_AMOUNT",
                            color = 'DONATION_YEAR',
                            title = 'Year Over Year By Weekly Giving',
                            render_mode='svg'
                        ).update_layout(yaxis_title=None, xaxis_title=None)
            
        line_tab.plotly_chart(week_ytd_fig, theme="streamlit", use_container_width=True)

    except:
        st.write("No data for current selection. Try selecting more data.")

    try:
        cytd_donations_year = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max())]
        pytd_donations_year = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()-1) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]
    
        df_selection_year = pd.concat([pytd_donations_year, cytd_donations_year])
        
        year_bar_fig = px.bar(
                        df_selection_year.groupby(['DONATION_YEAR'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                        y="DONATION_AMOUNT",
                        x="DONATION_YEAR",
                        title = 'Year Over Year Giving By Year',
                    ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
        bar_tab.plotly_chart(year_bar_fig, theme="streamlit", use_container_width=True)
    except:
        st.write("No data for current selection. Try selecting more data.")
    

    camp_col, fund_col = st.columns(2)

    if df_selection['DONATION_YEAR'].max() != today.year: 
        with camp_col:
            try:
            # campus 
                pc_yoy_fig = px.bar(
                            df_selection.groupby(['DONATION_YEAR', 'PRIMARY_CAMPUS'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="PRIMARY_CAMPUS", 
                            barmode="group",
                            title = 'Giving By Primary Campus',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(pc_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")
                
        with fund_col:
            try:
            # fund 
                fund_yoy_fig = px.bar(
                            df_selection.groupby(['DONATION_YEAR', 'FUND'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="FUND", 
                            barmode="group",
                            title = 'Giving By Fund',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(fund_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")

    else:
        cytd_donations_cy_cohort = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]
        pytd_donations_cy_cohort = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()-1) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]

        df_selection_cy_cohort = pd.concat([pytd_donations_cy_cohort, cytd_donations_cy_cohort])
        
        with camp_col:
            try:
            # campus 
                pc_yoy_fig = px.bar(
                            df_selection_cy_cohort.groupby(['DONATION_YEAR', 'PRIMARY_CAMPUS'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="PRIMARY_CAMPUS", 
                            barmode="group",
                            title = 'YTD Vs Last YTD Giving By Primary Campus',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(pc_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")
        with fund_col:
            try:
            # fund 
                fund_yoy_fig = px.bar(
                            df_selection_cy_cohort.groupby(['DONATION_YEAR', 'FUND'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="FUND", 
                            barmode="group",
                            title = 'YTD Vs Last YTD Giving By Fund',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(fund_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")


    ag_col, mem_col = st.columns(2)

    if df_selection['DONATION_YEAR'].max() != today.year: 

        with ag_col:
            try:
            # AGE 
                age_yoy_fig = px.bar(
                            df_selection.groupby(['DONATION_YEAR', 'AGE_GROUP'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="AGE_GROUP", 
                            barmode="group",
                            title = 'Giving By Age Group',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(age_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")
    
        with mem_col:
            try:
            # Membership 
                mem_yoy_fig = px.bar(
                            df_selection.groupby(['DONATION_YEAR', 'MEMBERSHIP'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="MEMBERSHIP", 
                            barmode="group",
                            title = 'Giving By Membership',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(mem_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")

    else:
        cytd_donations_cy_cohort = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]
        pytd_donations_cy_cohort = df_selection[(df_selection['DONATION_YEAR'] == df_selection['DONATION_YEAR'].max()-1) &
                                          (df_selection['DONATION_WEEK'] < today.isocalendar()[1])]

        df_selection_cy_cohort = pd.concat([pytd_donations_cy_cohort, cytd_donations_cy_cohort])

        with ag_col:
            try:
            # AGE 
                age_yoy_fig = px.bar(
                            df_selection_cy_cohort.groupby(['DONATION_YEAR', 'AGE_GROUP'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="AGE_GROUP", 
                            barmode="group",
                            title = 'YTD Vs Last YTD Giving By Age Group',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(age_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")
    
        with mem_col:
            try:
            # Membership 
                mem_yoy_fig = px.bar(
                            df_selection_cy_cohort.groupby(['DONATION_YEAR', 'MEMBERSHIP'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_YEAR'], ascending=True),
                            x="DONATION_YEAR",
                            y="DONATION_AMOUNT",
                            color="MEMBERSHIP", 
                            barmode="group",
                            title = 'YTD Vs Last YTD Giving By Membership',
                        ).update_xaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
                st.plotly_chart(mem_yoy_fig, theme="streamlit", use_container_width=True)
            except:
                st.write("No data for current selection. Try selecting more data.")

#Trend Tab
with trend_tab:
    trend_col, break_col = st.columns([0.6, 0.4])

    with trend_col:
        trend_tab_date, trend_tab_week, trend_tab_month = st.tabs(["Date", "Week", "Month"])

        try:
            # Date
            date_trend_fig = px.line(
                    df_selection.groupby(['DONATION_DATE'])['DONATION_AMOUNT'].sum().reset_index(),
                    x="DONATION_DATE",
                    y="DONATION_AMOUNT",
                    title = 'Giving Trend By Received Date',
                    render_mode='svg'
                ).update_layout(yaxis_title=None, xaxis_title=None)
            trend_tab_date.plotly_chart(date_trend_fig, theme="streamlit", use_container_width=True)

            # Week
            week_trend_fig = px.line(
                    df_selection.groupby(['DONATION_WEEK', 'DONATION_YEAR'])['DONATION_AMOUNT'].sum().reset_index(),
                    x="DONATION_WEEK",
                    y="DONATION_AMOUNT",
                    color = 'DONATION_YEAR',
                    title = 'Giving Trend By Week',
                    render_mode='svg'
                ).update_layout(yaxis_title=None, xaxis_title=None)
            trend_tab_week.plotly_chart(week_trend_fig, theme="streamlit", use_container_width=True)

            # Month
            month_trend_fig = px.line(
                    df_selection.groupby(['DONATION_MONTH', 'DONATION_YEAR'])['DONATION_AMOUNT'].sum().reset_index(),
                    x="DONATION_MONTH",
                    y="DONATION_AMOUNT",
                    color = 'DONATION_YEAR',
                    title = 'Giving Trend By Month',
                    render_mode='svg'
                ).update_layout(yaxis_title=None, xaxis_title=None)
            trend_tab_month.plotly_chart(month_trend_fig, theme="streamlit", use_container_width=True)

        except:
            st.write("No data for current selection. Try selecting more data.")


    with break_col:
        try:
            # DONOR LOCATION
            loc_break_fig = px.bar(
                    df_selection.groupby(['DONOR_LOCATION'])['DONATION_AMOUNT'].sum().reset_index().sort_values(by=['DONATION_AMOUNT'], ascending=True),
                    x="DONATION_AMOUNT",
                    y="DONOR_LOCATION",
                    title = 'Giving By Donor Location',
                ).update_yaxes(type='category').update_layout(yaxis_title=None, xaxis_title=None)
            break_col.plotly_chart(loc_break_fig, theme="streamlit", use_container_width=True)

        except:
            st.write("No data for current selection. Try selecting more data.")

    # Map of Donations
    try: 
        #map_fig = (px.scatter_mapbox(
        #        df_selection.groupby(['LATITUDE', 'LONGITUDE', 'DONOR_LOCATION'])['DONATION_AMOUNT'].sum().reset_index(), 
        #        lat='LATITUDE',
        #        lon='LONGITUDE',
        #        size="DONATION_AMOUNT",
        #        hover_name ='DONOR_LOCATION',
        #        center=dict( lat=df_selection['LATITUDE'].median(), 
        #                     lon=df_selection['LONGITUDE'].median()),
        #        mapbox_style="carto-positron"))
        
        #trend_tab.plotly_chart(map_fig, theme="streamlit", use_container_width=True)

        
        trend_tab.map(df_selection)



    except:
        st.write("No data for current selection. Try selecting more data.")
