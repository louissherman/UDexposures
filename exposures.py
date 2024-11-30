#exposures
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set page to wide mode at the very top of the file
st.set_page_config(layout="wide")

st.title("Underdog Draft Exposures Dashboard")

# Define sport-specific configurations
NFL_POSITIONS = ['QB', 'RB', 'WR', 'TE']
NBA_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']

# File upload
uploaded_file = st.file_uploader("Upload your draft data CSV", type=['csv'])

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
        
        # Initialize filtered_df with the original dataframe
        filtered_df = df.copy()
        
        # Add player search box
        player_search = st.multiselect(
            "Search Players",
            options=sorted(df['Player'].unique()),
            placeholder="Search for players..."
        )
        
        # Apply player filters if any players are selected
        if player_search:
            # Create a mask that checks if each draft contains all selected players
            draft_mask = None
            for player in player_search:
                player_drafts = set(df[df['Player'] == player]['Draft Entry'])
                if draft_mask is None:
                    draft_mask = df['Draft Entry'].isin(player_drafts)
                else:
                    draft_mask &= df['Draft Entry'].isin(player_drafts)
            
            # Filter to only drafts containing all selected players
            filtered_df = filtered_df[draft_mask]

        # Create filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col3:  # Moving Draft Pool Title to first in logical order
            # Get all available draft titles
            available_draft_titles = sorted(df['Draft Pool Title'].unique())
            draft_title_options = ['All'] + available_draft_titles
            selected_draft_title = st.selectbox(
                'Filter by Draft Pool Title',
                options=draft_title_options,
                index=0
            )
            
            # Create initial filter based on draft title
            if selected_draft_title != 'All':
                title_filtered_df = df[df['Draft Pool Title'] == selected_draft_title]
            else:
                title_filtered_df = df
        
        with col1:
            # Get positions based on draft title filter
            available_positions = sorted(title_filtered_df['Position'].unique())
            position_options = ["All"] + available_positions
            selected_position = st.selectbox(
                'Filter by Position',
                options=position_options,
                index=0
            )
            
            # Apply position filter
            if selected_position != "All":
                position_filtered_df = title_filtered_df[title_filtered_df['Position'] == selected_position]
            else:
                position_filtered_df = title_filtered_df
        
        with col2:
            # Get teams based on previous filters
            available_teams = sorted(position_filtered_df['Team'].unique().tolist())
            team_options = ["All"] + available_teams
            selected_team = st.selectbox(
                'Filter by Team',
                options=team_options,
                index=0
            )
            
            # Apply team filter
            if selected_team != "All":
                team_filtered_df = position_filtered_df[position_filtered_df['Team'] == selected_team]
            else:
                team_filtered_df = position_filtered_df
            
        with col4:
            # Get draft entries based on previous filters
            available_drafts = sorted(team_filtered_df['Draft Entry'].unique())
            draft_options = ['All'] + list(available_drafts)
            selected_draft = st.selectbox(
                'Filter by Draft',
                options=draft_options,
                index=0
            )
        
        # Final filtered dataframe based on all selections
        filtered_df = team_filtered_df if selected_draft == 'All' else team_filtered_df[team_filtered_df['Draft Entry'] == selected_draft]
        
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
        
        # Create three columns for table and visualizations with less spacing
        col_table, col_comp, col_breakdown = st.columns([1, 1, 1], gap="small")
        
        with col_table:
            # Calculate exposures
            if selected_draft != 'All':
                # Show only players from the selected draft
                exposures = (
                    df[df['Draft Entry'] == selected_draft]
                    .assign(
                        **{
                            'Total Drafts': 1,
                            'Total Entry Fees': lambda x: x['Draft Pool Entry Fee'],
                            'Exposure %': 100.0
                        }
                    )
                    [['Player', 'Position', 'Team', 'Total Drafts', 'Total Entry Fees', 'Exposure %']]
                )
            elif player_search:
                # Get all draft entries containing the searched players
                relevant_drafts = filtered_df['Draft Entry'].unique()
                
                # Get all players from those drafts
                teammate_exposures = (
                    df[df['Draft Entry'].isin(relevant_drafts)]
                    .groupby('Player')
                    .agg({
                        'Draft Pool': 'count',
                        'Position': 'first',
                        'Team': 'first',
                        'Draft Pool Entry Fee': 'sum'
                    })
                    .reset_index()
                )
                
                # Calculate exposure percentages based on filtered drafts
                teammate_exposures['Exposure %'] = (teammate_exposures['Draft Pool'] / len(relevant_drafts) * 100).round(1)
                teammate_exposures = teammate_exposures.sort_values('Exposure %', ascending=False)
                
                # Remove the searched players from the results if you want to show only teammates
                teammate_exposures = teammate_exposures[~teammate_exposures['Player'].isin(set(player_search))]
                
                # Apply team filter if not "All"
                if selected_team != "All":
                    teammate_exposures = teammate_exposures[teammate_exposures['Team'] == selected_team]
                
                # Rename columns
                teammate_exposures = teammate_exposures.rename(columns={
                    'Draft Pool': 'Total Drafts',
                    'Draft Pool Entry Fee': 'Total Entry Fees'
                })
                
                exposures = teammate_exposures
            else:
                # Original exposure calculation for when no players are searched
                exposures = (
                    filtered_df.groupby('Player')
                    .agg({
                        'Draft Pool': 'count',
                        'Position': 'first',
                        'Team': 'first',
                        'Draft Pool Entry Fee': 'sum'
                    })
                    .reset_index()
                )
                
                # Calculate exposure percentages
                exposures['Exposure %'] = (exposures['Draft Pool'] / total_filtered_drafts * 100).round(1)
                exposures = exposures.sort_values('Exposure %', ascending=False)
                
                # Rename columns
                exposures = exposures.rename(columns={
                    'Draft Pool': 'Total Drafts',
                    'Draft Pool Entry Fee': 'Total Entry Fees'
                })
            
            # Display exposures table
            st.subheader("Player Exposures")
            st.dataframe(
                exposures[['Player', 'Position', 'Team', 'Total Drafts', 'Total Entry Fees', 'Exposure %']],
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
                    # Show position distribution
                    team_comps = filtered_df.groupby('Position').size()
                    position_percentages = (team_comps / len(filtered_df) * 100).round(1)
                    
                    # Display as pie chart
                    fig_comp = px.pie(
                        values=position_percentages.values,
                        names=position_percentages.index,
                        title="Position Distribution"
                    )
                else:
                    # Show team distribution for selected position
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
                
                # Convert Picked At to datetime and convert to Eastern Time
                df['Picked At'] = pd.to_datetime(df['Picked At'])
                
                # Convert to Eastern Time (using tz_convert since data is already tz-aware)
                df['Picked At'] = df['Picked At'].dt.tz_convert('US/Eastern')
                
                df['Day'] = df['Picked At'].dt.day_name()
                df['AM_PM'] = df['Picked At'].dt.strftime('%p')
                
                # Combine day and AM/PM
                df['Draft Time'] = df['Day'] + ' ' + df['AM_PM']
                time_dist = df['Draft Time'].value_counts().sort_index()
                
                # Create pie chart
                fig_time = px.pie(
                    values=time_dist.values,
                    names=time_dist.index,
                    
                )
                # Update title size and legend position
                fig_time.update_layout(
                    title=dict(
                        text="Time Distribution (ET)",
                        font=dict(size=22)
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
