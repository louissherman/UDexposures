#exposures
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt  # Import Altair for bar charts

# Set page to wide mode at the very top of the file
st.set_page_config(layout="wide")

# Title row with Twitter link and feedback
col_title, col_social, col_feedback = st.columns([5, 1, 1])
with col_title:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <h1>Underdog Daily Draft Exposures Dashboard</h1>
            <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/1f3c8.svg" width="40">
            <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/1f3c0.svg" width="40">
            <img src="https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/1f3d2.svg" width="40">
        </div>
        """, unsafe_allow_html=True)
with col_feedback:
    st.markdown("""
        <a href="https://github.com/louisssherman/UDexposures/issues/new/choose" target="_blank">
            Submit Feedback
        </a>
    """, unsafe_allow_html=True)

# Define sport-specific configurations
NFL_POSITIONS = ['QB', 'RB', 'WR', 'TE']
NBA_POSITIONS = ['PG', 'SG', 'SF', 'PF', 'C']
NHL_POSITIONS = ['C', 'LW', 'RW', 'D', 'G']

# Add this near the top of the file with other constants
NFL_TEAM_LOGOS = {
    'ARI': 'https://raw.githubusercontent.com/path/to/cardinals-logo.png',
    'ATL': 'https://raw.githubusercontent.com/path/to/falcons-logo.png',
    # ... add all NFL team logos
}

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
                position_counts = {pos: 0 for pos in POSITIONS}
                for pos, count in positions.items():
                    position_counts[pos] += count
                return position_counts
            
            def analyze_stacks(group):
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
        elif file_positions.issubset(set(NHL_POSITIONS)):
            sport = "NHL"
            POSITIONS = NHL_POSITIONS
            
            def analyze_team_composition(positions):
                position_counts = {pos: 0 for pos in POSITIONS}
                for pos, count in positions.items():
                    position_counts[pos] += count
                return position_counts
            
            def analyze_stacks(group):
                # Convert LW and RW to just W for stack analysis
                group['Position'] = group['Position'].replace({'LW': 'W', 'RW': 'W'})
                
                # Get positions by team
                team_positions = group.groupby('Team')['Position'].agg(list)
                
                # Analyze each team's stack
                team_stacks = []
                for team, positions in team_positions.items():
                    if 'G' in positions:  # Skip goalies for stack analysis
                        positions.remove('G')
                    
                    pos_count = {
                        'C': positions.count('C'),
                        'W': positions.count('W'),
                        'D': positions.count('D')
                    }
                    
                    # Determine stack type
                    if pos_count['C'] >= 1 and pos_count['W'] >= 1 and pos_count['D'] == 0:
                        team_stacks.append('C-W')
                    elif pos_count['C'] >= 1 and pos_count['W'] >= 1 and pos_count['D'] >= 1:
                        team_stacks.append('C-W-D')
                    elif pos_count['C'] >= 1 and pos_count['D'] >= 1 and pos_count['W'] == 0:
                        team_stacks.append('C-D')
                    elif pos_count['C'] == 0 and pos_count['W'] >= 1 and pos_count['D'] >= 1:
                        team_stacks.append('W-D')
                    elif pos_count['C'] == 0 and pos_count['W'] >= 2 and pos_count['D'] >= 1:
                        team_stacks.append('W-W-D')
                
                # Return the most significant stack type
                if team_stacks:
                    return max(team_stacks, key=len)  # Return the longest stack type
                return 'No Stack'
        else:
            st.error("Error: Invalid position data in CSV")
            st.stop()

        # Combine First Name and Last Name into a single Player column
        df['Player'] = df['First Name'] + ' ' + df['Last Name']
        
        # Group by Draft Pool to check for valid drafts (should be multiples of 6)
        draft_counts = df.groupby('Draft Pool').size()
        valid_drafts = draft_counts[draft_counts % 6 == 0].index
        df = df[df['Draft Pool'].isin(valid_drafts)]
        
        # Start with the original dataframe
        base_df = df.copy()

        # Add player search box
        player_options = sorted(df['Player'].str.strip().unique())
        player_search = st.multiselect(
            "Search Players",
            options=player_options,
            placeholder="Search for players..."
        )

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
                base_df = df[draft_mask]
            else:
                st.warning("No drafts found containing all selected players")
                st.stop()

        # Initialize filtered_df with the base_df
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
        
        # Calculate total number of drafts and percentage
        total_filtered_drafts = len(filtered_df['Draft Entry'].unique())
        total_all_drafts = len(df['Draft Entry'].unique())
        percentage = round((total_filtered_drafts / total_all_drafts * 100), 1)
        
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
            st.metric(
                "Total Number of Drafts",
                f"{total_filtered_drafts} / {total_all_drafts} ({percentage}%)"
            )
        with col_metrics2:
            st.metric("Average Draft Position (first pick)", avg_draft_position)
        
        # Create three columns for table and visualizations
        col_table, col_team, col_pos, col_stack = st.columns([2, 1, 1, 1], gap="small")
        
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

        with col_team:
            if sport in ["NFL", "NBA", "NHL"]:
                # Create team distribution bar chart
                team_dist = filtered_df['Team'].value_counts()
                team_percentages = (team_dist / len(filtered_df) * 100).round(1)
                team_percentages = team_percentages.sort_values(ascending=True)
                
                # Create a color sequence for the bars
                colors = px.colors.qualitative.Set3[:len(team_percentages)]
                
                fig_team = px.bar(
                    y=team_percentages.index,
                    x=team_percentages.values,
                    title="Team Distribution",
                    labels={'x': 'Percentage (%)', 'y': 'Team'},
                    orientation='h',
                    color=team_percentages.index,  # Use team names for colors
                    color_discrete_sequence=colors  # Use our custom color sequence
                )
                
                # Add team logos as images
                if sport == "NFL":
                    for idx, team in enumerate(team_percentages.index):
                        if team in NFL_TEAM_LOGOS:
                            fig_team.add_layout_image(
                                dict(
                                    source=NFL_TEAM_LOGOS[team],
                                    xref="paper",
                                    yref="y",
                                    x=-0.1,  # Position logos to the left of bars
                                    y=idx,
                                    sizex=0.1,
                                    sizey=0.1,
                                    xanchor="right",
                                    yanchor="middle"
                                )
                            )
                
                fig_team.update_layout(
                    title=dict(text="Team Distribution", font=dict(size=24)),
                    showlegend=False,
                    height=600,
                    margin=dict(l=100)  # Add left margin for logos
                )
                st.plotly_chart(fig_team, use_container_width=True)

        with col_pos:
            if sport == "NFL":
                # NFL Position distribution
                draft_compositions = filtered_df.groupby('Draft Entry')['Position'].agg(lambda x: x.value_counts().to_dict()).reset_index()
                
                position_counts = draft_compositions['Position'].apply(lambda x: {
                    'RB': x.get('RB', 0),
                    'WR': x.get('WR', 0),
                    'TE': x.get('TE', 0)
                })
                
                position_df = pd.DataFrame(position_counts.tolist())
                
                distribution_summary = {
                    "2 RB": (position_df['RB'] == 2).sum(),
                    "3 WR": (position_df['WR'] >= 3).sum(),
                    "2 TE": (position_df['TE'] == 2).sum()
                }
                
                # Convert to pandas Series and sort
                dist_series = pd.Series(distribution_summary)
                dist_series = dist_series[dist_series > 0].sort_values(ascending=True)
                
                fig_pos = px.bar(
                    y=dist_series.index,
                    x=dist_series.values,
                    title="Position Distribution",
                    labels={'x': 'Number of Drafts', 'y': 'Build Type'},
                    orientation='h',
                    color=dist_series.index,
                    color_discrete_sequence=px.colors.qualitative.Set3[:len(dist_series)]
                )
                fig_pos.update_layout(
                    title=dict(text="Position Distribution", font=dict(size=24)),
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_pos, use_container_width=True)
            else:
                # NBA/NHL Position distribution
                if selected_position == "All":
                    pos_dist = filtered_df['Position'].value_counts()
                    pos_percentages = (pos_dist / len(filtered_df) * 100).round(1)
                    pos_percentages = pos_percentages.sort_values(ascending=True)
                    
                    fig_pos = px.bar(
                        y=pos_percentages.index,
                        x=pos_percentages.values,
                        title="Position Distribution",
                        labels={'x': 'Percentage (%)', 'y': 'Position'},
                        orientation='h',
                        color=pos_percentages.index,
                        color_discrete_sequence=px.colors.qualitative.Set3[:len(pos_percentages)]
                    )
                    fig_pos.update_layout(
                        title=dict(text="Position Distribution", font=dict(size=24)),
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig_pos, use_container_width=True)

        with col_stack:
            # Stack distribution
            stack_analysis = (
                filtered_df
                .groupby('Draft Entry')
                .apply(analyze_stacks)
            )
            
            stack_counts = stack_analysis.value_counts()
            stack_percentages = (stack_counts / len(stack_analysis) * 100).round(1)
            stack_percentages = stack_percentages.sort_values(ascending=True)
            
            fig_stack = px.bar(
                y=stack_percentages.index,
                x=stack_percentages.values,
                title="Stack Distribution",
                labels={'x': 'Percentage (%)', 'y': 'Stack Type'},
                orientation='h',
                color=stack_percentages.index,
                color_discrete_sequence=px.colors.qualitative.Set3[:len(stack_percentages)]
            )
            fig_stack.update_layout(
                title=dict(text="Stack Distribution", font=dict(size=24)),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_stack, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

# Create a footer Twitter icon
col_footer = st.columns([1, 1])  # Create two columns

with col_footer[1]:  # Right column

    # The Twitter icon will be displayed
     st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="https://x.com/loudogvideo" target="_blank">
                <img src="https://www.iconpacks.net/icons/free-icons-6/free-icon-twitter-logo-blue-square-rounded-20855.png" width="30">
            </a>
            <span>@loudogvideo</span>
        </div>
    """, unsafe_allow_html=True)

