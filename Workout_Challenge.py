import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Page config for better UI
st.set_page_config(
    page_title="Workout Challenge Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    .stats-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 10px 0;
        color: black; /* Ensure text is black */
    }
    .metric-card h3, .metric-card h2, .metric-card p {
        color: black; /* Ensure all text inside metric-card is black */
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
if 'members' not in st.session_state:
    st.session_state.members = []
if 'workouts' not in st.session_state:
    st.session_state.workouts = ['Push-ups', 'Pull-ups', 'Squats']
if 'daily_entries' not in st.session_state:
    st.session_state.daily_entries = {}
if 'statistics' not in st.session_state:
    st.session_state.statistics = {}
if 'personal_bests' not in st.session_state:
    st.session_state.personal_bests = {}

def save_data():
    """Save all data to a JSON file"""
    data = {
        'members': st.session_state.members,
        'workouts': st.session_state.workouts,
        'daily_entries': st.session_state.daily_entries,
        'statistics': st.session_state.statistics,
        'personal_bests': st.session_state.personal_bests
    }
    with open('workout_data.json', 'w') as f:
        json.dump(data, f)

def load_data():
    """Load data from JSON file if it exists"""
    if os.path.exists('workout_data.json'):
        with open('workout_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.members = data['members']
            st.session_state.workouts = data['workouts']
            st.session_state.daily_entries = data['daily_entries']
            st.session_state.statistics = data['statistics']
            st.session_state.personal_bests = data.get('personal_bests', {})

def calculate_stats():
    """Calculate comprehensive statistics"""
    stats = {}
    for date in st.session_state.daily_entries:
        daily_data = st.session_state.daily_entries[date]
        daily_totals = {}
        
        for member in daily_data:
            member_total = sum(daily_data[member].values())
            daily_totals[member] = member_total
        
        if daily_totals:
            winner = max(daily_totals.items(), key=lambda x: x[1])[0]
            if winner not in stats:
                stats[winner] = 0
            stats[winner] += 1
    
    return stats

def update_personal_bests(member, workout, count):
    """Update personal best records"""
    if member not in st.session_state.personal_bests:
        st.session_state.personal_bests[member] = {}
    
    if workout not in st.session_state.personal_bests[member]:
        st.session_state.personal_bests[member][workout] = count
    elif count > st.session_state.personal_bests[member][workout]:
        st.session_state.personal_bests[member][workout] = count
        return True
    return False

def main():
    st.title("🏋️ Workout Challenge Tracker")
    
    # Sidebar
    with st.sidebar:
        st.header("Management")
        
        # Member Management
        with st.expander("👥 Member Management", expanded=True):
            new_member = st.text_input("Add new member")
            if st.button("Add Member", key="add_member") and new_member:
                if new_member not in st.session_state.members:
                    st.session_state.members.append(new_member)
                    save_data()
                    st.success(f"Added {new_member}")

            if st.session_state.members:
                member_to_remove = st.selectbox("Select member to remove", st.session_state.members)
                if st.button("Remove Member", key="remove_member"):
                    # Remove member from members list
                    st.session_state.members.remove(member_to_remove)
                    
                    # Remove member from daily_entries
                    for date in list(st.session_state.daily_entries.keys()):
                        if member_to_remove in st.session_state.daily_entries[date]:
                            del st.session_state.daily_entries[date][member_to_remove]
                        # Remove the date entry if no members are left for that date
                        if not st.session_state.daily_entries[date]:
                            del st.session_state.daily_entries[date]
                    
                    # Remove member from statistics
                    if member_to_remove in st.session_state.statistics:
                        del st.session_state.statistics[member_to_remove]
                    
                    # Remove member from personal_bests
                    if member_to_remove in st.session_state.personal_bests:
                        del st.session_state.personal_bests[member_to_remove]
                    
                    save_data()
                    st.success(f"Removed {member_to_remove} and all associated data.")
        
        # Workout Management
        with st.expander("🏋️ Workout Management", expanded=True):
            new_workout = st.text_input("Add new workout")
            if st.button("Add Workout", key="add_workout") and new_workout:
                if new_workout not in st.session_state.workouts:
                    st.session_state.workouts.append(new_workout)
                    save_data()
                    st.success(f"Added {new_workout}")

            if st.session_state.workouts:
                workout_to_remove = st.selectbox("Select workout to remove", st.session_state.workouts)
                if st.button("Remove Workout", key="remove_workout"):
                    # Remove workout from workouts list
                    st.session_state.workouts.remove(workout_to_remove)
                    
                    # Remove workout from daily_entries
                    for date in st.session_state.daily_entries:
                        for member in st.session_state.daily_entries[date]:
                            if workout_to_remove in st.session_state.daily_entries[date][member]:
                                del st.session_state.daily_entries[date][member][workout_to_remove]
                    
                    # Remove workout from personal_bests
                    for member in st.session_state.personal_bests:
                        if workout_to_remove in st.session_state.personal_bests[member]:
                            del st.session_state.personal_bests[member][workout_to_remove]
                    
                    save_data()
                    st.success(f"Removed {workout_to_remove} and all associated data.")

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Daily Entry", "📊 Statistics", "🏆 Leaderboard"])
    
    with tab1:
        st.header("Daily Workout Entry")
        
        if not st.session_state.members or not st.session_state.workouts:
            st.warning("Please add members and workouts to start tracking")
            return
        
        # Entry form with improved layout
        col1, col2, col3 = st.columns([2,2,1])
        
        with col1:
            member = st.selectbox("Select Member", st.session_state.members)
        
        with col2:
            workout = st.selectbox("Select Workout", st.session_state.workouts)
        
        with col3:
            count = st.number_input("Count", min_value=0, value=0)

        if st.button("Submit Entry", type="primary"):
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Initialize data structures
            if today not in st.session_state.daily_entries:
                st.session_state.daily_entries[today] = {}
            if member not in st.session_state.daily_entries[today]:
                st.session_state.daily_entries[today][member] = {}
            
            # Check for personal best
            is_pb = update_personal_bests(member, workout, count)
            
            # Update entry
            st.session_state.daily_entries[today][member][workout] = count
            save_data()
            
            success_message = f"Recorded {count} {workout}s for {member}!"
            if is_pb:
                success_message += " 🎉 New Personal Best!"
            st.success(success_message)

        # Today's Progress
        st.subheader("Today's Progress")
        today = datetime.now().strftime("%Y-%m-%d")

        if today in st.session_state.daily_entries:
            data = []
            for m in st.session_state.members:
                if m in st.session_state.daily_entries[today]:
                    member_entries = st.session_state.daily_entries[today][m]
                    total = sum(member_entries.values())
                    entry = {'Member': m, 'Total': total}
                    for w in st.session_state.workouts:
                        entry[w] = member_entries.get(w, 0)
                    data.append(entry)
            
            if data:
                df = pd.DataFrame(data)
                
                try:
                    # Try to display the styled table with background gradient
                    st.dataframe(
                        df.style.background_gradient(subset=['Total'], cmap='YlOrRd'),
                        use_container_width=True
                    )
                except ImportError:
                    # Fallback to a simple table if matplotlib is not installed
                    st.dataframe(df, use_container_width=True)
                
                # Today's winner card
                winner = max(data, key=lambda x: x['Total'])
                if winner['Total'] > 0:
                    st.markdown(
                        f"""
                        <div class='metric-card'>
                            <h3>🏆 Today's Leader</h3>
                            <h2>{winner['Member']}</h2>
                            <p>Total: {winner['Total']} reps</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    with tab2:
        st.header("Statistics & Progress")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", 
                                     value=datetime.now() - timedelta(days=30),
                                     max_value=datetime.now())
        with col2:
            end_date = st.date_input("End Date", 
                                   value=datetime.now(),
                                   max_value=datetime.now())
        
        # Filter data by date range
        filtered_entries = {
            date: entries for date, entries in st.session_state.daily_entries.items()
            if start_date.strftime("%Y-%m-%d") <= date <= end_date.strftime("%Y-%m-%d")
        }
        
        if filtered_entries:
            # Prepare data for visualization
            progress_data = []
            for date in filtered_entries:
                for member in filtered_entries[date]:
                    total = sum(filtered_entries[date][member].values())
                    progress_data.append({
                        'Date': date,
                        'Member': member,
                        'Total': total
                    })
            
            progress_df = pd.DataFrame(progress_data)
            
            # Progress line chart
            fig = px.line(progress_df, 
                         x='Date', 
                         y='Total', 
                         color='Member',
                         title='Progress Over Time')
            st.plotly_chart(fig, use_container_width=True)
            
            # Workout distribution
            st.subheader("Workout Distribution")
            workout_data = []
            for date in filtered_entries:
                for member in filtered_entries[date]:
                    for workout, count in filtered_entries[date][member].items():
                        workout_data.append({
                            'Member': member,
                            'Workout': workout,
                            'Count': count
                        })
            
            workout_df = pd.DataFrame(workout_data)
            fig = px.bar(workout_df, 
                        x='Member', 
                        y='Count', 
                        color='Workout',
                        title='Workout Distribution by Member',
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🏆 Leaderboard & Achievements")
        
        # Calculate and update statistics
        st.session_state.statistics = calculate_stats()
        save_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("All-Time Winners")
            if st.session_state.statistics:
                stats_df = pd.DataFrame.from_dict(
                    st.session_state.statistics, 
                    orient='index',
                    columns=['Wins']
                ).sort_values('Wins', ascending=False)
                
                # Create styled leaderboard
                for idx, (member, wins) in enumerate(stats_df.iterrows()):
                    medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "👏"
                    st.markdown(
                        f"""
                        <div class='metric-card'>
                            <h3>{medal} {member}</h3>
                            <p>{int(wins['Wins'])} wins</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        with col2:
            st.subheader("Personal Bests")
            if st.session_state.personal_bests:
                for member in st.session_state.personal_bests:
                    with st.expander(f"💪 {member}'s Personal Bests"):
                        for workout, count in st.session_state.personal_bests[member].items():
                            st.markdown(f"**{workout}**: {count} reps")

# Load data and run the app
load_data()
main()
