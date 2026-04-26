import pandas as pd
import streamlit as st

# --- 1. DATA LOADING (Unchanged) ---
@st.cache_data
def load_data(pickle_file="josaa_data.pkl"):
    df = pd.read_pickle(pickle_file)
    return df

# --- 2. CORE BACKEND LOGIC (Modified to show Opening Rank) ---
def get_eligible_programs(df, user_exam, my_rank, my_seat_type, my_gender):
    
    # Filter by Exam Qualified
    if user_exam.lower() == 'advanced':
        institute_filter = df['Institute Name'].str.contains('Indian Institute of Technology')
        quota_filter = (df['Quota'] == 'AI')
    elif user_exam.lower() == 'mains':
        institute_filter = ~df['Institute Name'].str.contains('Indian Institute of Technology')
        quota_filter = (df['Quota'].isin(['AI', 'HS']))
    else:
        return pd.DataFrame() 

    filtered_df = df[institute_filter & quota_filter].copy()

    # Apply Personalized Filters
    eligible_programs = filtered_df[
        (filtered_df['Seat Type'] == my_seat_type) &
        (filtered_df['Gender'] == my_gender) &
        (filtered_df['Closing Rank'] >= my_rank)
    ]

    # --- THIS IS THE FIX ---
    # Add 'Opening Rank' to the list of columns to display
    columns_to_show = [
        'Institute Name', 
        'Academic Program Name', 
        'Quota', 
        'Seat Type', 
        'Opening Rank', # Added
        'Closing Rank'
    ]
    
    # Sort and Select Columns
    eligible_programs_final = eligible_programs.sort_values(
        by=['Institute Name', 'Closing Rank']
    )[columns_to_show]
    
    return eligible_programs_final

# --- 3. STREAMLIT APP LAYOUT (Unchanged) ---
st.title("JoSAA College Eligibility Finder 🚀")
st.markdown("Enter your details to find all eligible programs based on last year's closing ranks.")

df = load_data()

seat_types = sorted(df['Seat Type'].unique())
genders = sorted(df['Gender'].unique())

col1, col2 = st.columns(2)
with col1:
    user_exam = st.radio("1. Qualified Exam", ('Advanced', 'Mains'), horizontal=True)
with col2:
    my_rank = st.number_input("2. Your Rank", min_value=1, value=5000)

my_seat_type = st.selectbox("3. Your Seat Type/Reservation Category", options=seat_types)
my_gender = st.selectbox("4. Your Gender Eligibility", options=genders)

st.divider()

if st.button("Find Eligible Programs"):
    results_df = get_eligible_programs(df, user_exam, my_rank, my_seat_type, my_gender)

    if results_df.empty:
        st.warning(f"No programs found for Rank {my_rank} in {my_seat_type} category.")
    else:
        st.success(f"Found {len(results_df)} eligible programs!")
        # The dataframe will now automatically show the Opening Rank
        st.dataframe(results_df, height=600, use_container_width=True)