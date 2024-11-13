# Required imports
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
import geopandas as gpd


# Load data
@st.cache_data
def load_data():
    listings_data = pd.read_csv("listings.csv.gz", compression='gzip')
    calendar_data = pd.read_csv("calendar.csv.gz", compression='gzip')
    neighborhoods_data = pd.read_csv("neighbourhoods.csv")
    neighborhoods_geo = gpd.read_file("neighbourhoods.geojson")

    # Clean and preprocess the data
    listings_data['price'] = listings_data['price'].replace('[\\$,]', '', regex=True).astype(float)
    calendar_data['available'] = calendar_data['available'].replace({'t': True, 'f': False})

    return listings_data, calendar_data, neighborhoods_data, neighborhoods_geo


listings_data, calendar_data, neighborhoods_data, neighborhoods_geo = load_data()

# Sidebar for user input
st.sidebar.header("Filter Listings")
min_price, max_price = st.sidebar.slider("Select price range", int(listings_data.price.min()),
                                         int(listings_data.price.max()), (50, 500))
availability = st.sidebar.slider("Select availability (days)", 0, 365, (0, 365))
neighborhood = st.sidebar.selectbox("Select Neighborhood", options=listings_data['neighbourhood'].unique())

# Filter data based on user input
filtered_data = listings_data[(listings_data['price'] >= min_price) &
                              (listings_data['price'] <= max_price) &
                              (listings_data['availability_365'] >= availability[0]) &
                              (listings_data['availability_365'] <= availability[1]) &
                              (listings_data['neighbourhood'] == neighborhood)]

# Title and description
st.title("Boston Airbnb Market Insights")
st.write("Explore trends in pricing, availability, and location for Airbnb listings in Boston.")

# Visualization 1: Price Distribution Histogram
st.subheader("Price Distribution")
fig, ax = plt.subplots()
ax.hist(filtered_data['price'], bins=20, color='skyblue', edgecolor='black')
ax.set_xlabel("Price")
ax.set_ylabel("Frequency")
st.pyplot(fig)

# Visualization 2: Average Price by Neighborhood Bar Chart
st.subheader("Average Price by Neighborhood")
neighborhood_avg_price = listings_data.groupby('neighbourhood')['price'].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))  # Adjusted the size for better visibility
neighborhood_avg_price.plot(kind='bar', ax=ax, color='coral')
ax.set_ylabel("Average Price")
ax.set_xlabel("Neighborhood")
ax.set_title("Average Price by Neighborhood")
ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for readability

st.pyplot(fig)


# Visualization 3: Seasonal Availability Trend
st.subheader("Seasonal Availability Trend")
# Assuming 'date' column exists and in a format like 'YYYY-MM-DD'
calendar_data['month'] = pd.to_datetime(calendar_data['date']).dt.month
availability_by_month = calendar_data.groupby('month')['available'].mean()
fig, ax = plt.subplots()
availability_by_month.plot(kind='line', ax=ax, marker='o', color='green')
ax.set_xlabel("Month")
ax.set_ylabel("Average Availability")
st.pyplot(fig)

# Visualization 4: Interactive Map with PyDeck
st.subheader("Map of Airbnb Listings in Boston")
map_data = filtered_data[['latitude', 'longitude', 'price']]
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=42.3601,
        longitude=-71.0589,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
            pickable=True
        ),
    ],
))

# Additional Insights
st.subheader("Additional Insights")
st.write(f"Total listings in selected range: {filtered_data.shape[0]}")
st.write(filtered_data.describe())

# Documentation String
"""
Name: Christie Xu
Course: CS230, Section 6
Data Source: Boston Airbnb Data
Local URL:  http://localhost:8501 
Network URL: http://141.133.218.220:8501

Description:
This program provides an interactive analysis of Airbnb listings in Boston. It includes visualizations for:
- Price distribution
- Average price by neighborhood
- Seasonal availability trends
- An interactive map of listings

The app allows users to filter listings by price, availability, and neighborhood, providing insights into Boston's Airbnb market.
"""
