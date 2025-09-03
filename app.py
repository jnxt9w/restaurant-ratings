import streamlit as st
import pandas as pd
import plotly.express as px

df_path = r'restaurants.csv'

# Load data
try:
    df = pd.read_csv(df_path)
    if "comments" not in df.columns:
        df["comments"] = ""
except FileNotFoundError:
    df = pd.DataFrame(columns=["restaurant", "rating", "location", "cuisine", "comments"])

# --- Sidebar for navigation ---
page = st.sidebar.radio("Choose a page", ["Add Ratings", "Edit Ratings", "View & Visualize"])

# --- PAGE 1: Add Ratings ---
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
            new_row = {"restaurant": restaurant, "rating": rating, 
                       "location": location, "cuisine": cuisine,
                       "comments": comments}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(df_path, index=False)
            st.success(f"✅ Added {restaurant} with rating {rating}")

# --- PAGE 2: Edit Ratings ---
elif page == "Edit Ratings":
    st.title("✏️ Edit Restaurant Ratings")
    if df.empty:
        st.warning("No data available to edit.")
    else:
        restaurant_list = df["restaurant"].unique()
        selected_restaurant = st.selectbox("Select a restaurant to edit", restaurant_list)

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
                submitted = st.form_submit_button("Save Changes")

                if submitted:
                    df.loc[df["restaurant"] == selected_restaurant, ["restaurant", "rating", "location", "cuisine", "comments"]] = \
                        [new_name, new_rating, new_location, new_cuisine, new_comments]
                    df.to_csv(df_path, index=False)
                    st.success(f"✅ Updated {new_name} successfully!")

# --- PAGE 3: View & Visualize ---
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

        # Table view (include comments)
        st.subheader("Ratings Table")
        st.dataframe(filtered_df)

        # Visualizations
        st.subheader("Ratings Distribution")
        fig = px.histogram(filtered_df, x="rating", nbins=20, title="Distribution of Ratings")
        st.plotly_chart(fig)

        fig2 = px.box(filtered_df, x="cuisine", y="rating", points="all", title="Ratings by Cuisine")
        st.plotly_chart(fig2)
