import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page config
st.set_page_config(page_title="Incremental Plotting Demo", layout="wide")

# Constants
CHUNK_SIZE = 1000  # Adjust based on your needs

@st.cache_data
def load_data(file_path):
    """Load the full dataset"""
    return pd.read_csv(file_path)

def prepare_line_chart_data(df_chunk):
    """Aggregate data for line chart - Age vs Avg Earnings"""
    df_chunk['age_group'] = (df_chunk['age'] // 10) * 10
    agg_data = df_chunk.groupby('age_group').agg({
        'ern17': 'mean'  # Average earnings
    }).reset_index()
    agg_data.columns = ['age_group', 'avg_earnings']
    return agg_data

def prepare_bar_chart_data(df_chunk):
    """Aggregate data for bar chart - Education vs Count & Earnings"""
    agg_data = df_chunk.groupby('gedu_lvl').agg({
        'idno': 'count',
        'ern17': 'mean'
    }).reset_index()
    agg_data.columns = ['education', 'count', 'avg_earnings']
    return agg_data

def prepare_scatter_data(df_chunk, sample_rate=5):
    """Sample data for scatter plot - Hours vs Earnings"""
    sampled = df_chunk[::sample_rate].copy()
    return sampled[['hr17', 'ern17', 'age']].dropna()

def create_incremental_line_chart(df, chunk_size):
    """Create line chart with incremental data loading"""
    st.subheader("📈 Line Chart: Age Group vs Average Earnings")
    
    chart_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    fig = go.Figure()
    
    total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
    aggregated_data = []
    
    for i in range(total_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(df))
        
        # Get chunk
        chunk = df.iloc[start_idx:end_idx]
        
        # Process chunk
        chunk_agg = prepare_line_chart_data(chunk)
        aggregated_data.append(chunk_agg)
        
        # Combine all processed chunks
        combined_df = pd.concat(aggregated_data, ignore_index=True)
        combined_df = combined_df.groupby('age_group').agg({
            'avg_earnings': 'mean'
        }).reset_index().sort_values('age_group')
        
        # Update plot
        fig.data = []
        fig.add_trace(go.Scatter(
            x=combined_df['age_group'],
            y=combined_df['avg_earnings'],
            mode='lines+markers',
            name='Avg Earnings',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f"Age Group vs Average Earnings (Rows: {end_idx}/{len(df)})",
            xaxis_title="Age Group",
            yaxis_title="Average Earnings (₹)",
            height=500,
            hovermode='x unified'
        )
        
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        progress_bar.progress((i + 1) / total_chunks)
        status_text.text(f"Processing: {end_idx}/{len(df)} rows ({((i+1)/total_chunks*100):.1f}%)")
        
        time.sleep(0.1)  # Small delay for visualization
    
    status_text.success(f"Completed: {len(df)} rows processed")

def create_incremental_bar_chart(df, chunk_size):
    """Create bar chart with incremental data loading"""
    st.subheader("Bar Chart: Education Level Distribution")
    
    chart_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    fig = go.Figure()
    
    total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
    aggregated_data = []
    
    for i in range(total_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(df))
        
        chunk = df.iloc[start_idx:end_idx]
        chunk_agg = prepare_bar_chart_data(chunk)
        aggregated_data.append(chunk_agg)
        
        # Combine and aggregate
        combined_df = pd.concat(aggregated_data, ignore_index=True)
        combined_df = combined_df.groupby('education').agg({
            'count': 'sum',
            'avg_earnings': 'mean'
        }).reset_index().sort_values('education')
        
        # Update plot
        fig.data = []
        fig.add_trace(go.Bar(
            x=combined_df['education'],
            y=combined_df['count'],
            name='Count',
            marker_color='lightblue',
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            x=combined_df['education'],
            y=combined_df['avg_earnings'],
            name='Avg Earnings',
            marker_color='orange',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=f"Education Level Distribution (Rows: {end_idx}/{len(df)})",
            xaxis_title="Education Level",
            yaxis=dict(title="Count", side='left'),
            yaxis2=dict(title="Avg Earnings (₹)", overlaying='y', side='right'),
            barmode='group',
            height=500
        )
        
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        progress_bar.progress((i + 1) / total_chunks)
        status_text.text(f"Processing: {end_idx}/{len(df)} rows ({((i+1)/total_chunks*100):.1f}%)")
        
        time.sleep(0.1)
    
    status_text.success(f"Completed: {len(df)} rows processed")

def create_incremental_scatter_plot(df, chunk_size):
    """Create scatter plot with incremental data loading"""
    st.subheader("🔵 Scatter Plot: Hours Worked vs Earnings")
    
    chart_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    fig = go.Figure()
    
    total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
    all_scatter_data = []
    
    for i in range(total_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(df))
        
        chunk = df.iloc[start_idx:end_idx]
        scatter_chunk = prepare_scatter_data(chunk, sample_rate=10)
        all_scatter_data.append(scatter_chunk)
        
        # Combine all scatter data
        combined_scatter = pd.concat(all_scatter_data, ignore_index=True)
        
        # Update plot
        fig.data = []
        fig.add_trace(go.Scatter(
            x=combined_scatter['hr17'],
            y=combined_scatter['ern17'],
            mode='markers',
            marker=dict(
                size=6,
                color=combined_scatter['age'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Age")
            ),
            text=combined_scatter['age'],
            name='Workers'
        ))
        
        fig.update_layout(
            title=f"Hours Worked vs Earnings (Sampled Points: {len(combined_scatter)})",
            xaxis_title="Hours Worked per Week",
            yaxis_title="Earnings (₹)",
            height=500
        )
        
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        progress_bar.progress((i + 1) / total_chunks)
        status_text.text(f"Processing: {end_idx}/{len(df)} rows ({((i+1)/total_chunks*100):.1f}%)")
        
        time.sleep(0.1)
    
    status_text.success(f"Completed: {len(all_scatter_data)} scatter points")

# Main App
def main():
    st.title("Incremental Data Plotting for Large Datasets")
    st.markdown("### Handling 1.8 Lakh+ Rows Without MaxMessageSize Error")
    
    # File upload or use existing file
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        # Use your existing file
        df = load_data('mospi data short.csv')
    
    st.info(f"Dataset loaded: **{len(df):,}** rows × **{len(df.columns)}** columns")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        chunk_size = st.slider("Chunk Size", 100, 5000, 1000, 100)
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Line Chart", "Bar Chart", "Scatter Plot", "All Charts"]
        )
        
        if st.button("Generate Charts", type="primary"):
            st.session_state.generate = True
    
    # Generate charts
    if st.session_state.get('generate', False):
        if chart_type == "Line Chart":
            create_incremental_line_chart(df, chunk_size)
        elif chart_type == "Bar Chart":
            create_incremental_bar_chart(df, chunk_size)
        elif chart_type == "Scatter Plot":
            create_incremental_scatter_plot(df, chunk_size)
        else:  # All Charts
            create_incremental_line_chart(df, chunk_size)
            st.divider()
            create_incremental_bar_chart(df, chunk_size)
            st.divider()
            create_incremental_scatter_plot(df, chunk_size)

if __name__ == "__main__":
    main()