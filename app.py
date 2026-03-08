import mysql.connector          # pip install mysql-connector-python
import streamlit as st    
import numpy as np
import pandas as pd
import plotly.express as px


import warnings
warnings.filterwarnings("ignore", category=UserWarning)
# connection

import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Iphone6+',
    database='project_1'
)

mycursor = mydb.cursor()


# --------------------------------------------------------------------------------------------------------------

                                                # sidebar
st.sidebar.header('Filters')


# City- Multi-select
cities = pd.read_sql("SELECT DISTINCT City FROM listing", mydb)
# print(cities['City'].tolist())
selected_cities = st.sidebar.multiselect("Select City", cities['City'].tolist())


# Property type Dropdown
property_types = pd.read_sql("SELECT DISTINCT Property_Type FROM listing", mydb)
# print(property_types['Property_Type'].tolist())
selected_property = st.sidebar.selectbox("Property Type", ['All'] + property_types['Property_Type'].tolist())


# Price Range Slider
price_range = st.sidebar.slider("Price Range", 100000, 5000000, (100000, 1000000), step=100000)


# Agent - searchable dropdown
agents = pd.read_sql("SELECT DISTINCT Agent_ID FROM listing", mydb)
# print(agents['Agent_ID'].tolist())
selected_agent = st.sidebar.selectbox("Agent", ["All"] + agents['Agent_ID'].tolist())


# --------------------------------------------------------------------------------------------------------------

                                            # Dataframe of sidebar
query = """
        SELECT l.*, a.Name
        FROM listing l
        LEFT JOIN agents a 
            ON l.Agent_ID = a.Agent_ID
        WHERE 1=1
    """

params = []

# Cities
if selected_cities:
    placeholder = ",".join(["%s"] * len(selected_cities))
    query += f" AND l.City IN ({placeholder})"
    params.extend(selected_cities)

# Property Type
if selected_property != "All":
    query += " AND l.Property_Type = %s"
    params.append(selected_property)

# Price Range
query += " AND l.Price BETWEEN %s AND %s"
params.extend(price_range)

# Agent
if selected_agent != "All":
    query += " AND l.Agent_ID = %s"
    params.append(selected_agent)

print(params)

# debug
# st.write(query)
# st.write(params)

df = pd.read_sql(query, mydb, params = params)
st.dataframe(df)




# --------------------------------------------------------------------------------------------------------------

                                        # Interactive Map
st.subheader("Property Map")

fig_map = px.scatter_mapbox(df, 
                            lat='Latitude', 
                            lon='Longitude', 
                            hover_name='City', 
                            hover_data=['Price', 'Property_Type'], 
                            zoom=4, 
                            height=500, 
                            mapbox_style='open-street-map')
st.plotly_chart(fig_map, use_container_width=True)



# --------------------------------------------------------------------------------------------------------------


                                    # Listing by City (Bar Chart)
st.subheader("Listing by City")

city_count = df.groupby("City")['Listing_ID'].count().reset_index()

print(city_count)

fig_bar = px.bar(city_count,
                 x='City',
                 y='Listing_ID')
                #  title="Number of Listings")

st.plotly_chart(fig_bar, use_container_width=True)


                                    # Average Price by City (Bar Chart)
st.subheader("Avg Price of City")

avg_price = df.groupby("City")['Price'].mean().reset_index()

print(avg_price)

fig_bar = px.bar(avg_price,
                 x='City',
                 y='Price')

st.plotly_chart(fig_bar, use_container_width=True)


# --------------------------------------------------------------------------------------------------------------


                                    # Property Distribution (Pie chart)
st.subheader("Property Type Distribution")

property_dist = df['Property_Type'].value_counts().reset_index()
# print(property_dist)

fig_pie = px.pie(property_dist,
                 names=property_dist["Property_Type"],
                 values=property_dist['count']
)

st.plotly_chart(fig_pie, use_container_width=True)



# --------------------------------------------------------------------------------------------------------------


                                    # Monthly Trend (line chart)

st.subheader("Monthly Listing Trend")

st.subheader("Monthly Listings Trend")

df['Date_Listed'] = pd.to_datetime(df['Date_Listed'])
monthly = df.groupby(df['Date_Listed'].dt.to_period("M")).size()
monthly = monthly.reset_index(name='Count')
monthly['Date_Listed'] = monthly['Date_Listed'].astype(str)

fig_line = px.line(
    monthly,
    x="Date_Listed",
    y="Count"
)

st.plotly_chart(fig_line, use_container_width=True)