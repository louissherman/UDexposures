#exposures
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set page to wide mode at the very top of the file
st.set_page_config(layout="wide")

# Title row with Twitter link
col_title, col_social = st.columns([6, 1])
with col_title:
    st.title("Underdog Draft Exposures Dashboard")
with col_social:
    st.markdown("""
        <a href="https://x.com/loudogvideo" target="_blank">
            <img src="https://www.iconpacks.net/icons/free-icons-6/free-icon-twitter-logo-blue-square-rounded-20855.png" width="50">
        </a>
    """, unsafe_allow_html=True)

# Define sport-specific configurations
NFL_POSITIONS = ['QB', 'RB', 'WR', 'TE']
NBA_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']

# File upload with tooltip
st.markdown("""
    Upload CSV 
    <span title="You can email an exposure csv to yourself from the Completed Drafts page on Underdog">❔</span>
    """, 
    unsafe_allow_html=True
)
uploaded_file = st.file_uploader("", type=['csv'])

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Detect sport based on positions in the file
        file_positions = set(df['Position'].unique())
        
        if file_positions.issubset(set(NFL_POSITIONS)):
            sport = "NFL"
            POSITIONS = NFL_POSITIONS
            
            def analyze_team_composition(positions):
                if positions.get('QB', 0) != 1:  # Must have exactly 1 QB
                    return 'Invalid'
                elif positions.get('RB', 0) == 2 and positions.get('WR', 0) == 2 and positions.get('TE', 0) == 1:
                    return '2 RB Build'
                elif positions.get('RB', 0) == 1 and positions.get('WR', 0) == 3 and positions.get('TE', 0) == 1:
                    return '3 WR Build'
                elif positions.get('TE', 0) == 2:
                    return '2 TE Build'
                else:
                    return 'Other'
            
            def analyze_stacks(group):
                qb_row = group[group['Position'] == 'QB']
                if len(qb_row) != 1:
                    return 'Invalid'
                
                qb_team = qb_row.iloc[0]['Team']
                stack_count = len(group[
                    (group['Position'] != 'QB') & 
                    (group['Team'] == qb_team)
                ])
                
                if stack_count == 0:
                    return 'Naked QB'
                elif stack_count == 1:
                    return 'Skinny'
                elif stack_count == 2:
                    return 'Double'
                else:
                    return 'Triple+'
                    
        elif file_positions.issubset(set(NBA_POSITIONS)):
            sport = "NBA"
            POSITIONS = NBA_POSITIONS
            
            def analyze_team_composition(positions):
                # Initialize position counts
                position_counts = {pos: 0 for pos in POSITIONS}
                # Add the counts from this team's positions
                for pos, count in positions.items():
                    position_counts[pos] += count
                return position_counts
            
            def analyze_stacks(group):
                # Count players per team
                team_counts = group['Team'].value_counts()
                
                if len(team_counts) == 6:
                    return '6 Unique'
                elif team_counts.iloc[0] == 3:
                    if team_counts.iloc[1] == 3:
                        return '3-3'
                    elif team_counts.iloc[1] == 2:
                        return '3-2-1'
                    else:
                        return '3-1-1-1'
                elif team_counts.iloc[0] == 2:
                    if team_counts.iloc[1] == 2:
                        if team_counts.iloc[2] == 2:
                            return '2-2-2'
                        else:
                            return '2-2-1-1'
                    else:
                        return '2-1-1-1-1'
                else:
                    return 'Other'
        else:
            st.error("Error: Invalid position data in CSV")
            st.stop()
            
        # Continue with the rest of the code...
        # Combine First Name and Last Name into a single Player column
        df['Player'] = df['First Name'] + ' ' + df['Last Name']
        
        # Group by Draft Pool to check for valid drafts (should be multiples of 6)
        draft_counts = df.groupby('Draft Pool').size()
        valid_drafts = draft_counts[draft_counts % 6 == 0].index
        df = df[df['Draft Pool'].isin(valid_drafts)]
        
        # Add player search box with normalized names
        player_options = sorted(df['Player'].str.strip().unique())
        player_search = st.multiselect(
            "Search Players",
            options=player_options,
            placeholder="Search for players..."
        )
        
        # Start with the original dataframe
        base_df = df.copy()
        
        # Apply player filters if any players are selected
        if player_search:
            # Create a mask that checks if each draft contains all selected players
            draft_mask = None
            for player in player_search:
                player_drafts = set(df[df['Player'].str.strip() == player.strip()]['Draft Entry'])
                if draft_mask is None:
                    draft_mask = df['Draft Entry'].isin(player_drafts)
                else:
                    draft_mask &= df['Draft Entry'].isin(player_drafts)
            
            if draft_mask is not None:
                # Filter the base dataframe
                base_df = df[draft_mask]
            else:
                st.warning("No drafts found containing all selected players")
                st.stop()
        
        # Initialize filtered_df with the base_df (which now includes player search filter)
        filtered_df = base_df.copy()
        
        # Create filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col3:
            available_draft_titles = sorted(base_df['Draft Pool Title'].unique())
            draft_title_options = ['All'] + available_draft_titles
            selected_draft_title = st.selectbox(
                'Filter by Draft Pool Title',
                options=draft_title_options,
                index=0
            )
            
            if selected_draft_title != 'All':
                filtered_df = filtered_df[filtered_df['Draft Pool Title'] == selected_draft_title]
        
        with col1:
            available_positions = sorted(filtered_df['Position'].unique())
            position_options = ["All"] + available_positions
            selected_position = st.selectbox(
                'Filter by Position',
                options=position_options,
                index=0
            )
            
            if selected_position != "All":
                filtered_df = filtered_df[filtered_df['Position'] == selected_position]
        
        with col2:
            available_teams = sorted(filtered_df['Team'].unique())
            team_options = ["All"] + available_teams
            selected_team = st.selectbox(
                'Filter by Team',
                options=team_options,
                index=0
            )
            
            if selected_team != "All":
                filtered_df = filtered_df[filtered_df['Team'] == selected_team]
        
        with col4:
            available_drafts = sorted(filtered_df['Draft Entry'].unique())
            draft_options = ['All'] + list(available_drafts)
            selected_draft = st.selectbox(
                'Filter by Draft',
                options=draft_options,
                index=0
            )
            
            if selected_draft != 'All':
                filtered_df = filtered_df[filtered_df['Draft Entry'] == selected_draft]
        
        # Calculate total number of drafts based on unique Draft Entries
        total_filtered_drafts = len(filtered_df['Draft Entry'].unique())
        
        # Calculate Draft Position for each entry
        draft_positions = (
            filtered_df.groupby('Draft Entry')['Pick Number']
            .min()
            .reset_index()
            .rename(columns={'Pick Number': 'Draft Position'})
        )
        
        # Calculate average Draft Position
        avg_draft_position = draft_positions['Draft Position'].mean().round(1)
        
        # Display metrics
        col_metrics1, col_metrics2 = st.columns(2)
        with col_metrics1:
            st.metric("Total Number of Drafts", total_filtered_drafts)
        with col_metrics2:
            st.metric("Average Draft Position (first pick)", avg_draft_position)
        
        # Create three columns for table and visualizations
        col_table, col_comp, col_breakdown = st.columns([1, 1, 1], gap="small")
        
        with col_table:
            # Calculate exposures
            if selected_draft != 'All':
                exposures = (
                    filtered_df
                    .assign(
                        **{
                            'Total Drafts': 1,
                            'Total Entry Fees': lambda x: x['Draft Pool Entry Fee'],
                            'Exposure %': 100.0
                        }
                    )
                    [['Player', 'Position', 'Team', 'Total Drafts', 'Total Entry Fees', 'Exposure %']]
                )
            else:
                exposures = (
                    filtered_df.groupby(['Player', 'Position', 'Team'])
                    .agg({
                        'Draft Entry': 'count',
                        'Draft Pool Entry Fee': 'sum'
                    })
                    .reset_index()
                    .rename(columns={
                        'Draft Entry': 'Total Drafts',
                        'Draft Pool Entry Fee': 'Total Entry Fees'
                    })
                )
                
                # Calculate exposure percentages
                exposures['Exposure %'] = (exposures['Total Drafts'] / total_filtered_drafts * 100).round(1)
                exposures = exposures.sort_values('Exposure %', ascending=False)
            
            # Display exposures table
            st.subheader("Player Exposures")
            st.dataframe(
                exposures,
                hide_index=True,
                column_config={
                    'Exposure %': st.column_config.NumberColumn(format="%.1f%%"),
                    'Total Entry Fees': st.column_config.NumberColumn(format="%.0f")
                }
            )
        
        with col_comp:
            col_pos, col_time = st.columns(2)
            
            with col_pos:
                if selected_position == "All":
                    # Show position distribution using filtered_df
                    team_comps = filtered_df.groupby('Position').size()
                    position_percentages = (team_comps / len(filtered_df) * 100).round(1)
                    
                    # Display as pie chart
                    fig_comp = px.pie(
                        values=position_percentages.values,
                        names=position_percentages.index,
                        title="Position Distribution"
                    )
                else:
                    # Show team distribution using filtered_df
                    team_comps = filtered_df.groupby('Team').size()
                    team_percentages = (team_comps / len(filtered_df) * 100).round(1)
                    
                    # Display as pie chart
                    fig_comp = px.pie(
                        values=team_percentages.values,
                        names=team_percentages.index,
                        title=f"{selected_position} Team Distribution"
                    )
                
                # Update title size and legend position
                fig_comp.update_layout(
                    title=dict(
                        text="Position Distribution" if selected_position == "All" else f"{selected_position} Team Distribution",
                        font=dict(size=24)
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig_comp, use_container_width=True)
            
            with col_time:
                try:
                    # Create time distribution using filtered_df
                    filtered_df['Picked At'] = pd.to_datetime(filtered_df['Picked At'], utc=True)
                    
                    # Extract day and hour information
                    filtered_df['Day'] = filtered_df['Picked At'].dt.day_name()
                    filtered_df['Hour'] = filtered_df['Picked At'].dt.hour
                    
                    # Define AM/PM
                    filtered_df['AM_PM'] = filtered_df['Hour'].apply(lambda x: 'AM' if x < 12 else 'PM')
                    
                    # Combine day and AM/PM for filtered_df
                    filtered_df['Draft Time'] = filtered_df['Day'] + ' ' + filtered_df['AM_PM']
                    
                    # Get distribution for filtered drafts only
                    time_dist = filtered_df['Draft Time'].value_counts().sort_index()
                    
                    # Create pie chart
                    fig_time = px.pie(
                        values=time_dist.values,
                        names=time_dist.index,
                    )
                    # Update title size and legend position
                    fig_time.update_layout(
                        title=dict(
                            text="Time Distribution (UTC)",
                            font=dict(size=24)
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.5,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
                except Exception as e:
                    st.error(f"Error in time distribution: {str(e)}")
        
        with col_breakdown:
            # Get all draft entries from filtered_df
            filtered_draft_entries = filtered_df['Draft Entry'].unique()
            
            # Use original df to analyze stacks, but only for the filtered draft entries
            stack_analysis = (
                df[df['Draft Entry'].isin(filtered_draft_entries)]
                .groupby('Draft Entry')
                .apply(analyze_stacks)
            )
            
            stack_counts = stack_analysis.value_counts()
            stack_percentages = (stack_counts / len(stack_analysis) * 100).round(1)
            
            # Display as pie chart
            fig_stack = px.pie(
                values=stack_percentages.values,
                names=stack_percentages.index,
                title="Stack Distribution"
            )
            # Update title size and legend position
            fig_stack.update_layout(
                title=dict(
                    text="Stack Distribution",
                    font=dict(size=24)
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig_stack, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
