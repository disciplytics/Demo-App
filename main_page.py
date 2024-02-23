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

        **👈 Select a demo from the dropdown on the left** to see some examples
        of what Disciplytics can do!

        ### Want to learn more?

        - Check out [Disciplytics](https://disciplytics.com)!

    """
    )
