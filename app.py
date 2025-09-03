import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------
# Google Sheets Setup
# ---------------------------

SHEET_NAME = "restaurant_ratings"  # Your sheet name

# Determine where to get credentials
if "GCP_SERVICE_ACCOUNT" in os.environ:
    # Local dev via environment variable
    service_account_info = json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
else:
    # Streamlit Cloud via secrets
    service_account_info = st.secrets["gcp_service_account"]

# Authenticate
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # first tab

# Load data
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Ensure required columns exist
required_cols = ["restaurant", "rating", "location", "cuisine", "comments"]
for col in required_cols:
    if col not in df.columns:
        df[col] = ""
df = df[required_cols]

# ---------------------------
# Sidebar Navigation
# ---------------------------
page = st.sidebar.radio("Choose a page", ["Add Ratings", "Edit Ratings", "View & Visualize"])

# ---------------------------
# PAGE 1: Add Ratings
# ---------------------------
if page == "Add Ratings":
    st.title("🍴 Add a New Restaurant Rating")
    with st.form("add_rating"):
        restaurant = st.text_input("Restaurant name")
        rating = st.number_input("Rating (0-10)", min_value=0.0, max_value=10.0, step=0.1)
        location = st.text_input("Location")
        cuisine = st.text_input("Cuisine")
        comments = st.text_area("Comments (optional)")
        submitted = st.form_submit_button("Add Rating")
        if submitted and restaurant:
            new_row = [restaurant, rating, location, cuisine, comments]
            sheet.append_row(new_row)
            st.success(f"✅ Added {restaurant} with rating {rating}")

# ---------------------------
# PAGE 2: Edit / Delete Ratings
# ---------------------------
elif page == "Edit Ratings":
    st.title("✏️ Edit or Delete Restaurant Ratings")
    
    if df.empty:
        st.warning("No data available.")
    else:
        restaurant_list = df["restaurant"].unique()
        selected_restaurant = st.selectbox("Select a restaurant", restaurant_list)

        if selected_restaurant:
            restaurant_data = df[df["restaurant"] == selected_restaurant].iloc[0]

            with st.form("edit_form"):
                new_name = st.text_input("Restaurant name", restaurant_data["restaurant"])
                new_rating = st.number_input(
                    "Rating (0-10)", 
                    min_value=0.0, max_value=10.0, 
                    step=0.1, value=float(restaurant_data["rating"])
                )
                new_location = st.text_input("Location", restaurant_data["location"])
                new_cuisine = st.text_input("Cuisine", restaurant_data["cuisine"])
                new_comments = st.text_area("Comments", restaurant_data["comments"])

                col1, col2 = st.columns(2)
                save_btn = col1.form_submit_button("💾 Save Changes")
                delete_btn = col2.form_submit_button("🗑 Delete Restaurant")

                # Find row index in Google Sheet (1-based including header)
                row_index = df.index[df["restaurant"] == selected_restaurant][0] + 2

                if save_btn:
                    sheet.update(
                        f"A{row_index}:E{row_index}", 
                        [[new_name, new_rating, new_location, new_cuisine, new_comments]]
                    )
                    st.success(f"✅ Updated {new_name} successfully!")

                if delete_btn:
                    # Get all rows including header
                    all_rows = sheet.get_all_values()  # returns a list of lists

                    # Find row index (0-based) in the sheet data
                    row_index = df.index[df["restaurant"] == selected_restaurant][0] + 1  # +1 to skip header for Python list

                    # Remove the row from the list
                    all_rows.pop(row_index)

                    # Clear the sheet and write back remaining rows
                    sheet.clear()
                    sheet.update('A1', all_rows)

                    st.success(f"🗑 Deleted {selected_restaurant} successfully!")
                    
# ---------------------------
# PAGE 3: View & Visualize
# ---------------------------
elif page == "View & Visualize":
    st.title("📋 View Ratings & Visualizations")

    if df.empty:
        st.warning("No data available.")
    else:
        # Filter options
        location_filter = st.multiselect("Filter by location", df["location"].unique())
        cuisine_filter = st.multiselect("Filter by cuisine", df["cuisine"].unique())

        filtered_df = df.copy()
        if location_filter:
            filtered_df = filtered_df[filtered_df["location"].isin(location_filter)]
        if cuisine_filter:
            filtered_df = filtered_df[filtered_df["cuisine"].isin(cuisine_filter)]

        # Table view
        st.subheader("Ratings Table")
        st.dataframe(filtered_df)

        # Visualizations
        st.subheader("Ratings Distribution")
        fig = px.histogram(filtered_df, x="rating", nbins=20, title="Distribution of Ratings")
        st.plotly_chart(fig)

        fig2 = px.box(filtered_df, x="cuisine", y="rating", points="all", title="Ratings by Cuisine")
        st.plotly_chart(fig2)
