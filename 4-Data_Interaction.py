# interactive_streamlit_app.py
# pip install streamlit pandas sqlalchemy pymysql seaborn matplotlib plotly statsmodels

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sqlalchemy import create_engine

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="IMDb Movies Dashboard", layout="wide")

# ---------------------- Database Connection ----------------------
user = "2JRRhPHCS6mRsGW.root"
password = "mt2YyedoEbMz4suV"
host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
port = "4000"
database = "imdb"

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    connect_args={"ssl": {"ssl_verify_cert": True, "ssl_verify_identity": True}}
)

# ---------------------- Load Data ----------------------
@st.cache_data
def load_data():
    query = "SELECT * FROM imdb_movies"
    df = pd.read_sql(query, engine)
    return df

df = load_data()

# ---------------------- Page Navigation ----------------------
# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard Overview"
if 'effect_triggered' not in st.session_state:
    st.session_state.effect_triggered = False

# Sidebar navigation
st.sidebar.title("🎬 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard Overview", "Advanced Filtering"], 
                        index=0 if st.session_state.page == "Dashboard Overview" else 1)

# Check if page has changed
if page != st.session_state.page:
    st.session_state.page = page
    st.session_state.effect_triggered = False
    st.rerun()

# Trigger effects when page changes
if not st.session_state.effect_triggered:
    if st.session_state.page == "Dashboard Overview":
        st.balloons()
    else:
        st.snow()
    st.session_state.effect_triggered = True

# ---------------------- Page Content ----------------------
if st.session_state.page == "Dashboard Overview":
    # ---------------------- Compact Layout ----------------------
    st.title("🎬 IMDb Movies Dashboard")

    # ---------------------- Sidebar Filters ----------------------
    with st.sidebar:
        st.header("🔍 Filters")
        genres = st.multiselect(
            "Select Genres",
            options=df['genre'].unique(),
            default=df['genre'].unique()
        )

        rating_range = st.slider(
            "Rating Range",
            float(df['rating'].min()),
            float(df['rating'].max()),
            (float(df['rating'].min()), float(df['rating'].max()))
        )

        votes_range = st.slider(
            "Votes Range",
            int(df['voters'].min()),
            int(df['voters'].max()),
            (int(df['voters'].min()), int(df['voters'].max()))
        )

        duration_range = st.slider(
            "Duration Range (min)",
            int(df['duration'].min()),
            int(df['duration'].max()),
            (int(df['duration'].min()), int(df['duration'].max()))
        )
        
        # Summary stats in sidebar
        st.header("📊 Summary")
        filtered_df = df[
            (df['genre'].isin(genres)) &
            (df['rating'].between(*rating_range)) &
            (df['voters'].between(*votes_range)) &
            (df['duration'].between(*duration_range))
        ]
        
        st.metric("Movies", f"{len(filtered_df):,}")
        st.metric("Avg Rating", f"{filtered_df['rating'].mean():.2f}")
        st.metric("Total Votes", f"{filtered_df['voters'].sum():,}")

    # Apply filters
    filtered_df = df[
        (df['genre'].isin(genres)) &
        (df['rating'].between(*rating_range)) &
        (df['voters'].between(*votes_range)) &
        (df['duration'].between(*duration_range))
    ]

    # ---------------------- Top Row: Key Metrics ----------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌟 Avg Rating", f"{filtered_df['rating'].mean():.2f}")
    with col2:
        st.metric("🗳️ Total Votes", f"{filtered_df['voters'].sum():,}")
    with col3:
        st.metric("⏱️ Avg Duration", f"{filtered_df['duration'].mean():.0f} min")
    with col4:
        st.metric("🎭 Genres", filtered_df['genre'].nunique())

    # ---------------------- Second Row: Distribution Charts ----------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Genre Distribution")
        genre_counts = filtered_df['genre'].value_counts()
        fig1 = px.bar(
            x=genre_counts.index,
            y=genre_counts.values,
            labels={'x': 'Genre', 'y': 'Count'},
            title="",
            text=[f"{count:,}" for count in genre_counts.values],
            color=genre_counts.values,
            color_continuous_scale='viridis'
        )
        fig1.update_traces(textposition='outside')
        fig1.update_layout(
            xaxis_tickangle=-45,
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("⭐ Rating Distribution")
        fig2 = px.histogram(
            filtered_df, 
            x='rating', 
            nbins=20, 
            title="",
            labels={'rating': 'Rating', 'count': 'Count'},
            opacity=0.7
        )
        fig2.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------------- Third Row: Comparative Analysis ----------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⏱ Avg Duration by Genre")
        avg_duration = filtered_df.groupby('genre')['duration'].mean().sort_values().round(2)
        fig3 = px.bar(
            x=avg_duration.values,
            y=avg_duration.index,
            orientation='h',
            labels={'x': 'Minutes', 'y': 'Genre'},
            title="",
            text=[f"{dur:.0f} min" for dur in avg_duration.values],
            color=avg_duration.values,
            color_continuous_scale='blues'
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("📈 Avg Votes by Genre")
        avg_votes = filtered_df.groupby('genre')['voters'].mean().sort_values(ascending=False).round(2)
        fig4 = px.bar(
            x=avg_votes.index,
            y=avg_votes.values,
            labels={'x': 'Genre', 'y': 'Votes'},
            title="",
            text=[f"{votes:,.0f}" for votes in avg_votes.values],
            color=avg_votes.values,
            color_continuous_scale='greens'
        )
        fig4.update_traces(textposition='outside')
        fig4.update_layout(
            xaxis_tickangle=-45,
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ---------------------- Fourth Row: Top Movies & Leaders ----------------------
    tab1, tab2 = st.tabs(["🏆 Top Movies", "🎯 Genre Leaders"])

    with tab1:
        top10 = filtered_df.sort_values(by=['voters', 'rating'], ascending=[False, False]).head(10)
        top10_display = top10[['title', 'genre', 'rating', 'voters', 'duration']].copy()
        top10_display['rating'] = top10_display['rating'].round(2)
        top10_display['voters'] = top10_display['voters'].apply(lambda x: f"{x:,.0f}")
        top10_display['duration'] = top10_display['duration'].apply(lambda x: f"{x:.0f} min")
        st.dataframe(top10_display, use_container_width=True, height=300)

    with tab2:
        leaders = filtered_df.loc[filtered_df.groupby('genre')['rating'].idxmax()]
        leaders_display = leaders[['genre', 'title', 'rating', 'voters']].copy()
        leaders_display['rating'] = leaders_display['rating'].round(2)
        leaders_display['voters'] = leaders_display['voters'].apply(lambda x: f"{x:,.0f}")
        leaders_display = leaders_display.sort_values('rating', ascending=False)
        st.dataframe(leaders_display, use_container_width=True, height=300)

    # ---------------------- Fifth Row: Heatmap & Correlation ----------------------
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("🔥 Ratings Heatmap")
        ratings_pivot = filtered_df.pivot_table(index='genre', values='rating', aggfunc='mean').round(2)
        fig5 = px.imshow(
            ratings_pivot,
            labels=dict(x="", y="Genre", color="Rating"),
            title="",
            aspect="auto",
            color_continuous_scale='YlGnBu',
            text_auto=True
        )
        fig5.update_xaxes(showticklabels=False)
        fig5.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("🔗 Correlation Analysis")
        fig6 = px.scatter(
            filtered_df,
            x='rating',
            y='voters',
            hover_data=['title', 'genre'],
            trendline="ols",
            title="",
            labels={'rating': 'Rating', 'voters': 'Votes'},
            log_y=True
        )
        
        correlation = filtered_df['rating'].corr(np.log(filtered_df['voters'] + 1))
        fig6.add_annotation(
            x=0.05, y=0.95,
            xref="paper", yref="paper",
            text=f"Correlation: {correlation:.3f}",
            showarrow=False,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        
        fig6.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig6, use_container_width=True)

    # ---------------------- Sixth Row: Extremes & Pie Chart ----------------------
    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        st.subheader("🎬 Shortest Movies")
        shortest = filtered_df.nsmallest(5, 'duration')[['title', 'duration']].copy()
        shortest['duration'] = shortest['duration'].apply(lambda x: f"{x:.0f} min")
        st.dataframe(shortest, use_container_width=True, height=200)

    with col2:
        st.subheader("🎥 Longest Movies")
        longest = filtered_df.nlargest(5, 'duration')[['title', 'duration']].copy()
        longest['duration'] = longest['duration'].apply(lambda x: f"{x:.0f} min")
        st.dataframe(longest, use_container_width=True, height=200)

    with col3:
        st.subheader("🥇 Votes by Genre")
        votes_by_genre = filtered_df.groupby('genre')['voters'].sum().sort_values(ascending=False)
        fig7 = px.pie(
            values=votes_by_genre.values,
            names=votes_by_genre.index,
            title="",
            hole=0.4
        )
        fig7.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Votes: %{value:,.0f}'
        )
        fig7.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
        st.plotly_chart(fig7, use_container_width=True)

    # ---------------------- Footer ----------------------
    st.markdown("---")
    st.caption("🎬 IMDb Movies Dashboard | Built with Streamlit")

else:
    # ---------------------- Page 2: Advanced Filtering ----------------------
    st.title("🎬 Advanced Movie Filtering")
    
    st.markdown("Use the filters below to find movies that match your specific criteria.")
    
    # ---------------------- Advanced Filters ----------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Duration Filter")
        duration_option = st.radio(
            "Select duration range:",
            ["All", "Short (< 2 hrs)", "Medium (2-3 hrs)", "Long (> 3 hrs)"],
            index=0
        )
        
        st.subheader("Rating Filter")
        min_rating = st.slider(
            "Minimum Rating:",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1
        )
    
    with col2:
        st.subheader("Votes Filter")
        min_votes = st.slider(
            "Minimum Votes:",
            min_value=0,
            max_value=int(df['voters'].max()),
            value=0,
            step=1000
        )
        
        st.subheader("Genre Filter")
        selected_genres = st.multiselect(
            "Select genres:",
            options=df['genre'].unique(),
            default=df['genre'].unique()
        )
    
    # Apply filters based on user selection
    filtered_data = df.copy()
    
    # Apply genre filter
    filtered_data = filtered_data[filtered_data['genre'].isin(selected_genres)]
    
    # Apply rating filter
    filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
    
    # Apply votes filter
    filtered_data = filtered_data[filtered_data['voters'] >= min_votes]
    
    # Apply duration filter
    if duration_option == "Short (< 2 hrs)":
        filtered_data = filtered_data[filtered_data['duration'] < 120]
    elif duration_option == "Medium (2-3 hrs)":
        filtered_data = filtered_data[(filtered_data['duration'] >= 120) & (filtered_data['duration'] <= 180)]
    elif duration_option == "Long (> 3 hrs)":
        filtered_data = filtered_data[filtered_data['duration'] > 180]
    
    # Display filter summary
    st.subheader("Filter Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Movies Found", len(filtered_data))
    with col2:
        st.metric("Avg Rating", f"{filtered_data['rating'].mean():.2f}")
    with col3:
        st.metric("Total Votes", f"{filtered_data['voters'].sum():,}")
    with col4:
        st.metric("Avg Duration", f"{filtered_data['duration'].mean():.0f} min")
    
    # Display filtered results
    st.subheader("Filtered Movies")
    
    if len(filtered_data) > 0:
        # Format the data for display
        display_data = filtered_data[['title', 'genre', 'rating', 'voters', 'duration']].copy()
        display_data['rating'] = display_data['rating'].round(2)
        display_data['voters'] = display_data['voters'].apply(lambda x: f"{x:,.0f}")
        display_data['duration'] = display_data['duration'].apply(lambda x: f"{x:.0f} min")
        
        # Add sorting capability
        sort_option = st.selectbox(
            "Sort by:",
            ["Rating (High to Low)", "Votes (High to Low)", "Duration (Long to Short)", "Title (A-Z)"]
        )
        
        if sort_option == "Rating (High to Low)":
            display_data = display_data.sort_values('rating', ascending=False)
        elif sort_option == "Votes (High to Low)":
            # Remove commas for sorting, then add back
            display_data['voters_num'] = filtered_data['voters']
            display_data = display_data.sort_values('voters_num', ascending=False)
            display_data = display_data.drop('voters_num', axis=1)
        elif sort_option == "Duration (Long to Short)":
            display_data = display_data.sort_values('duration', ascending=False)
        elif sort_option == "Title (A-Z)":
            display_data = display_data.sort_values('title')
        
        # Display the data
        st.dataframe(display_data, use_container_width=True, height=400)
        
        # Add download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="filtered_movies.csv",
            mime="text/csv",
        )
        
        # Visualization of filtered results
        st.subheader("Filter Results Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Genre distribution of filtered results
            genre_counts = filtered_data['genre'].value_counts()
            fig = px.pie(
                values=genre_counts.values,
                names=genre_counts.index,
                title="Genre Distribution in Filtered Results"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating distribution of filtered results
            fig = px.histogram(
                filtered_data, 
                x='rating', 
                nbins=20, 
                title="Rating Distribution in Filtered Results"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No movies match your filter criteria. Please try different filters.")
    
    # Example use cases
    st.subheader("Example Use Cases")
    
    with st.expander("See example filter combinations"):
        st.markdown("""
        **Popular Action Movies:**
        - Genre: Action
        - Minimum Rating: 7.0
        - Minimum Votes: 100,000
        - Duration: All
        
        **Highly Rated Short Films:**
        - Genre: All
        - Minimum Rating: 8.0
        - Minimum Votes: 10,000
        - Duration: Short (< 2 hrs)
        
        **Blockbuster Long Movies:**
        - Genre: All
        - Minimum Rating: 7.5
        - Minimum Votes: 500,000
        - Duration: Long (> 3 hrs)
        """)
    
    # ---------------------- Footer ----------------------
    st.markdown("---")
    st.caption("🎬 IMDb Movies Advanced Filtering | Built with Streamlit")