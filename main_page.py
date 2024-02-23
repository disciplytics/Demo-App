import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    
)

st.write("# Disciplytics Demo App")
st.sidebar.success("Select a demo above.")

st.markdown(
        """
        Disciplytics provides analytics as a service to churches. 
        
        This app is a taste of what we can offer to your church!

        **👈 Select a demo in the sidebar on the left** to see some examples
        of what Disciplytics can do!

        ### Want to learn more?

        - Check out [Disciplytics](https://disciplytics.com)!

        ### How Do We Calculate Metrics?

        - Year-to-Date (YTD) is the sum of data, i.e. giving, checkins, headcounts, etc, of the current year since the last sunday.

        - Last Year-to-Date (LYTD) is the sum of data, i.e. giving, checkins, headcounts, etc, of the previous year since the last sunday's week number. 
            Example: If we are in the third week of the current year, then LYTD would be the sum of giving at the 3 week of last year.

        - Year over Year is the percent difference between LYTD and YTD

    """
    )
