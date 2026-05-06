"""
Name: Rihen Shah
CS230: Section XXX
Data: LEGO Stores USA & Canada (CSV)

Description:
This app analyzes LEGO store locations and identifies underserved areas
based on store counts. Users can explore store distribution and discover
which states may be good candidates for expansion.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# -----------------------------
# [PY3] Error handling
# -----------------------------
try:
    df = pd.read_csv("LegoUSACanada.csv")
except:
    st.error("CSV file not found.")
    st.stop()

# -----------------------------
# [DA1] Clean data
# -----------------------------
df.columns = df.columns.str.strip()

df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# -----------------------------
# Sidebar [ST1][ST2][ST3][ST4]
# -----------------------------
st.sidebar.title("Filters")

countries = df['Country'].dropna().unique().tolist()  # [PY4]
selected_country = st.sidebar.selectbox("Country", countries)

states = df[df['Country'] == selected_country]['State'].dropna().unique().tolist()
selected_state = st.sidebar.selectbox("State", ["All"] + states)

threshold = st.sidebar.slider("Max stores for 'Underserved'", 1, 10, 3)

# -----------------------------
# [PY1] Function with default param
# -----------------------------
def filter_data(country, state="All"):
    if state == "All":
        return df[df['Country'] == country]
    else:
        return df[(df['Country'] == country) & (df['State'] == state)]

filtered_df = filter_data(selected_country, selected_state)
_ = filter_data(selected_country)

# -----------------------------
# Title
# -----------------------------
st.title("🧱 LEGO Expansion Analyzer")
st.write("Find underserved regions where LEGO could open new stores.")

# -----------------------------
# [PY2] Function returning multiple values
# -----------------------------
def get_stats(data):
    return len(data), data['State'].nunique()

total_stores, total_states = get_stats(filtered_df)

st.metric("Total Stores", total_stores)
st.metric("States Covered", total_states)

# -----------------------------
# [DA2] Sorting
# -----------------------------
sorted_df = filtered_df.sort_values(by='State')

# -----------------------------
# [DA3] Top values
# -----------------------------
state_counts = filtered_df['State'].value_counts()

# -----------------------------
# [PY5] Dictionary
# -----------------------------
state_dict = dict(state_counts)

# -----------------------------
# [DA6] Pivot table
# -----------------------------
pivot = pd.pivot_table(filtered_df, index='State', values='City', aggfunc='count')

# -----------------------------
# Underserved logic
# -----------------------------
low_states = state_counts[state_counts <= threshold]

# -----------------------------
# 📊 VIZ 1: Bar Chart
# -----------------------------
st.subheader("Stores by State")

fig, ax = plt.subplots()
state_counts.head(10).plot(kind='bar', ax=ax)
ax.set_title("Top States by Store Count")
ax.set_xlabel("State")
ax.set_ylabel("Number of Stores")

st.pyplot(fig)

# -----------------------------
# 🥧 VIZ 2: Pie Chart
# -----------------------------
st.subheader("Store Distribution")

fig2, ax2 = plt.subplots()
state_counts.head(5).plot(kind='pie', autopct='%1.1f%%', ax=ax2)
ax2.set_ylabel("")

st.pyplot(fig2)

# -----------------------------
# 📋 VIZ 3: Table
# -----------------------------
st.subheader("Store Data Table")
st.dataframe(sorted_df)

# -----------------------------
# 📊 VIZ 4: Underserved States Table
# -----------------------------
st.subheader("Underserved States (Expansion Targets)")
st.write(low_states)

# -----------------------------
# 🗺️ MAP
# -----------------------------
st.subheader("Store Map")

# Color logic
filtered_df['color'] = filtered_df['State'].apply(
    lambda x: [255, 0, 0] if x in state_counts.head(5).index else [0, 0, 255]
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_df,
    get_position='[Longitude, Latitude]',
    get_color='color',
    get_radius=40000,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=filtered_df['Latitude'].mean(),
    longitude=filtered_df['Longitude'].mean(),
    zoom=3
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{Store Name} - {City}, {State}"}
))

# -----------------------------
# Insights
# -----------------------------
st.subheader("Insights")

if len(state_counts) > 0:
    st.write(f"State with most stores: **{state_counts.idxmax()}**")
    st.write(f"Best expansion targets (few stores):")
    st.write(low_states.index.tolist())