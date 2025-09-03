import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

df_path = r'C:\Users\A1033402\OneDrive - H & M HENNES & MAURITZ GBC AB\Documents\DA\Example data\restaurants.csv'

# Load data (or start empty)
try:
    df = pd.read_csv(df_path)
except FileNotFoundError:
    df = pd.DataFrame(columns=["restaurant", "rating", "location", "cuisine"])

st.title("🍴 My Restaurant Ratings Dashboard")

# --- Add New Rating ---
st.subheader("➕ Add a new restaurant rating")
with st.form("add_rating"):
    restaurant = st.text_input("Restaurant name")
    rating = st.number_input("Rating (0-10)", min_value=0.0, max_value=10.0, step=0.1)
    location = st.text_input("Location")
    cuisine = st.text_input("Cuisine")
    submitted = st.form_submit_button("Add Rating")
    if submitted and restaurant:
        new_row = {"restaurant": restaurant, "rating": rating, 
                   "location": location, "cuisine": cuisine}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(df_path, index=False)
        st.success(f"✅ Added {restaurant} with rating {rating}")

# --- Filter Options ---
st.subheader("🔍 Filter Ratings")
location_filter = st.multiselect("Filter by location", df["location"].unique())
cuisine_filter = st.multiselect("Filter by cuisine", df["cuisine"].unique())

filtered_df = df.copy()
if location_filter:
    filtered_df = filtered_df[filtered_df["location"].isin(location_filter)]
if cuisine_filter:
    filtered_df = filtered_df[filtered_df["cuisine"].isin(cuisine_filter)]

# --- Table View ---
st.subheader("📋 Ratings Table")
st.dataframe(filtered_df)

# --- Visualization ---
st.subheader("📊 Ratings Distribution")
fig = px.histogram(filtered_df, x="rating", nbins=20, title="Distribution of Ratings")
st.plotly_chart(fig)

fig2 = px.box(filtered_df, x="cuisine", y="rating", points="all", title="Ratings by Cuisine")
st.plotly_chart(fig2)