import streamlit as st
import altair as alt
alt.data_transformers.enable("vegafusion")
import db
import vega_datasets
import pandas as pd
import json
import base64
import numpy as np
import time
import plotly.graph_objects as go

from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
from io import BytesIO
from PIL import Image
import uuid
from PIL import Image as PILImage

from st_aggrid import AgGrid, GridOptionsBuilder

# ==================== INCREMENTAL PLOTTING HELPER FUNCTIONS ====================

def get_numeric_columns_smart(df):
    """Get numeric columns, excluding ID-like columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    filtered_cols = []
    for col in numeric_cols:
        col_lower = col.lower()
        # Skip ID/code columns  -> not doing this?
        # if any(keyword in col_lower for keyword in ['id', 'code', 'serial', 'number', 'no', 'srl', 'idno']):
        #     continue
        # Skip small integer codes
        if df[col].dtype in ['int64', 'int32']:
            unique_count = df[col].nunique()
            max_val = df[col].max()
            if unique_count < 100 and max_val < 1000:
                continue
        filtered_cols.append(col)
    
    return filtered_cols if filtered_cols else numeric_cols

def aggregate_chunk_properly(chunk, x_col, y_col, agg_func, color_col=None):
    """
    Aggregate chunk with intermediate values for proper re-aggregation
    This prevents the "sum of sums" problem
    """
    group_cols = [x_col]
    if color_col and color_col != 'None' and color_col != x_col:
        group_cols.append(color_col)
    
    if agg_func == 'count' or y_col is None:
        result = chunk.groupby(group_cols, dropna=False).size().reset_index(name='_count')
    else:
        # Store sum, count, min, max for proper re-aggregation
        result = chunk.groupby(group_cols, dropna=False)[y_col].agg(['sum', 'count', 'min', 'max']).reset_index()
        result.columns = group_cols + ['_sum', '_count', '_min', '_max']
    
    return result

def combine_aggregated_chunks(combined_df, x_col, y_col, agg_func, color_col=None):
    """
    Properly combine pre-aggregated chunks
    """
    group_cols = [x_col]
    if color_col and color_col != 'None' and color_col != x_col:
        group_cols.append(color_col)
    
    if agg_func == 'count' or y_col is None:
        final_df = combined_df.groupby(group_cols, dropna=False)['_count'].sum().reset_index()
        final_df.columns = group_cols + [y_col if y_col else 'count']
    elif agg_func == 'sum':
        final_df = combined_df.groupby(group_cols, dropna=False)['_sum'].sum().reset_index()
        final_df.columns = group_cols + [y_col]
    elif agg_func == 'mean':
        # Weighted mean: total_sum / total_count
        temp = combined_df.groupby(group_cols, dropna=False).agg({
            '_sum': 'sum',
            '_count': 'sum'
        }).reset_index()
        temp[y_col] = temp['_sum'] / temp['_count']
        final_df = temp[group_cols + [y_col]]
    elif agg_func == 'min':
        final_df = combined_df.groupby(group_cols, dropna=False)['_min'].min().reset_index()
        final_df.columns = group_cols + [y_col]
    elif agg_func == 'max':
        final_df = combined_df.groupby(group_cols, dropna=False)['_max'].max().reset_index()
        final_df.columns = group_cols + [y_col]
    elif agg_func == 'std':
        # For std, use mean as approximation (true std requires all data)
        temp = combined_df.groupby(group_cols, dropna=False).agg({
            '_sum': 'sum',
            '_count': 'sum'
        }).reset_index()
        temp[y_col] = temp['_sum'] / temp['_count']
        final_df = temp[group_cols + [y_col]]
    else:
        # Default to mean
        temp = combined_df.groupby(group_cols, dropna=False).agg({
            '_sum': 'sum',
            '_count': 'sum'
        }).reset_index()
        temp[y_col] = temp['_sum'] / temp['_count']
        final_df = temp[group_cols + [y_col]]
    
    return final_df.sort_values(x_col)

# def create_incremental_plotly_chart(df, x_col, y_col, chart_type, chart_name,
#                                     color_col=None, agg_func='sum', chunk_size=2000):
#     """
#     Create Plotly chart with incremental loading
#     This is used for large datasets to avoid MaxMessageSize errors
#     """
#     chart_placeholder = st.empty()
#     progress_bar = st.progress(0)
#     status_text = st.empty()
    
#     total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
#     aggregated_data = []
    
#     fig = go.Figure()
    
#     for i in range(total_chunks):
#         start_idx = i * chunk_size
#         end_idx = min((i + 1) * chunk_size, len(df))
        
#         chunk = df.iloc[start_idx:end_idx].copy()
        
#         if chart_type.lower() == 'scatter':
#             # For scatter, sample to prevent overcrowding
#             sample_rate = max(1, len(chunk) // 1000)
#             chunk_processed = chunk[::sample_rate].copy()
#             aggregated_data.append(chunk_processed)
            
#             combined_df = pd.concat(aggregated_data, ignore_index=True)
            
#             fig.data = []
            
#             if color_col and color_col != 'None':
#                 # Categorical coloring
#                 for category in combined_df[color_col].unique():
#                     cat_data = combined_df[combined_df[color_col] == category]
#                     fig.add_trace(go.Scatter(
#                         x=cat_data[x_col],
#                         y=cat_data[y_col],
#                         mode='markers',
#                         marker=dict(size=6, opacity=0.6),
#                         name=str(category)
#                     ))
#             else:
#                 fig.add_trace(go.Scatter(
#                     x=combined_df[x_col],
#                     y=combined_df[y_col],
#                     mode='markers',
#                     marker=dict(size=6, opacity=0.6),
#                     name='Data Points'
#                 ))
        
#         else:  # Bar, Line, Pie - need aggregation
#             # Aggregate chunk with intermediate values
#             chunk_agg = aggregate_chunk_properly(chunk, x_col, y_col, agg_func, color_col)
#             aggregated_data.append(chunk_agg)
            
#             # Combine all chunks properly
#             combined_df = pd.concat(aggregated_data, ignore_index=True)
#             final_df = combine_aggregated_chunks(combined_df, x_col, y_col, agg_func, color_col)
            
#             # Update chart
#             fig.data = []
            
#             if chart_type.lower() == 'bar':
#                 if color_col and color_col != 'None':
#                     for category in final_df[color_col].unique():
#                         cat_data = final_df[final_df[color_col] == category]
#                         fig.add_trace(go.Bar(
#                             x=cat_data[x_col],
#                             y=cat_data[y_col if y_col else 'count'],
#                             name=str(category)
#                         ))
#                 else:
#                     fig.add_trace(go.Bar(
#                         x=final_df[x_col],
#                         y=final_df[y_col if y_col else 'count'],
#                         marker_color='lightblue'
#                     ))
            
#             elif chart_type.lower() == 'line':
#                 if color_col and color_col != 'None':
#                     for category in final_df[color_col].unique():
#                         cat_data = final_df[final_df[color_col] == category]
#                         fig.add_trace(go.Scatter(
#                             x=cat_data[x_col],
#                             y=cat_data[y_col if y_col else 'count'],
#                             mode='lines+markers',
#                             name=str(category),
#                             line=dict(width=2),
#                             marker=dict(size=6)
#                         ))
#                 else:
#                     fig.add_trace(go.Scatter(
#                         x=final_df[x_col],
#                         y=final_df[y_col if y_col else 'count'],
#                         mode='lines+markers',
#                         line=dict(width=2, color='blue'),
#                         marker=dict(size=6)
#                     ))
            
#             elif chart_type.lower() == 'pie':
#                 fig.add_trace(go.Pie(
#                     labels=final_df[x_col],
#                     values=final_df[y_col if y_col else 'count']
#                 ))
        
#         # Update layout
#         title_text = f"{chart_name} (Rows: {end_idx:,}/{len(df):,})"
        
#         if chart_type.lower() == 'pie':
#             fig.update_layout(title=title_text, height=500, showlegend=True)
#         else:
#             fig.update_layout(
#                 title=title_text,
#                 xaxis_title=x_col,
#                 yaxis_title=y_col if y_col else 'count',
#                 height=500,
#                 hovermode='closest' if chart_type.lower() == 'scatter' else 'x unified'
#             )
        
#         chart_placeholder.plotly_chart(fig, use_container_width=True)
#         progress_bar.progress((i + 1) / total_chunks)
#         status_text.text(f"Processing: {end_idx:,}/{len(df):,} rows ({((i+1)/total_chunks*100):.1f}%)")
        
#         time.sleep(0.05)
    
#     status_text.success(f"Chart completed: {len(df):,} rows processed")
#     progress_bar.empty()
    
#     return fig

def create_incremental_plotly_chart(df, x_col, y_col, chart_type, chart_name,
                                    color_col=None, agg_func='sum', chunk_size=2000):
    """
    Create Plotly chart with incremental loading
    This is used for large datasets to avoid MaxMessageSize errors
    """
    import streamlit.components.v1 as components
    
    chart_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
    aggregated_data = []
    
    fig = go.Figure()
    
    for i in range(total_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(df))
        
        chunk = df.iloc[start_idx:end_idx].copy()
        
        if chart_type.lower() == 'scatter':
            # For scatter, sample to prevent overcrowding
            sample_rate = max(1, len(chunk) // 1000)
            chunk_processed = chunk[::sample_rate].copy()
            aggregated_data.append(chunk_processed)
            
            combined_df = pd.concat(aggregated_data, ignore_index=True)
            
            fig.data = []
            
            if color_col and color_col != 'None':
                # Categorical coloring
                for category in combined_df[color_col].unique():
                    cat_data = combined_df[combined_df[color_col] == category]
                    fig.add_trace(go.Scatter(
                        x=cat_data[x_col],
                        y=cat_data[y_col],
                        mode='markers',
                        marker=dict(size=6, opacity=0.6),
                        name=str(category)
                    ))
            else:
                fig.add_trace(go.Scatter(
                    x=combined_df[x_col],
                    y=combined_df[y_col],
                    mode='markers',
                    marker=dict(size=6, opacity=0.6),
                    name='Data Points'
                ))
        
        else:  # Bar, Line, Pie - need aggregation
            # Aggregate chunk with intermediate values
            chunk_agg = aggregate_chunk_properly(chunk, x_col, y_col, agg_func, color_col)
            aggregated_data.append(chunk_agg)
            
            # Combine all chunks properly
            combined_df = pd.concat(aggregated_data, ignore_index=True)
            final_df = combine_aggregated_chunks(combined_df, x_col, y_col, agg_func, color_col)
            
            # Update chart
            fig.data = []
            
            if chart_type.lower() == 'bar':
                if color_col and color_col != 'None':
                    for category in final_df[color_col].unique():
                        cat_data = final_df[final_df[color_col] == category]
                        fig.add_trace(go.Bar(
                            x=cat_data[x_col],
                            y=cat_data[y_col if y_col else 'count'],
                            name=str(category)
                        ))
                else:
                    fig.add_trace(go.Bar(
                        x=final_df[x_col],
                        y=final_df[y_col if y_col else 'count'],
                        marker_color='lightblue'
                    ))
            
            elif chart_type.lower() == 'line':
                if color_col and color_col != 'None':
                    for category in final_df[color_col].unique():
                        cat_data = final_df[final_df[color_col] == category]
                        fig.add_trace(go.Scatter(
                            x=cat_data[x_col],
                            y=cat_data[y_col if y_col else 'count'],
                            mode='lines+markers',
                            name=str(category),
                            line=dict(width=2),
                            marker=dict(size=6)
                        ))
                else:
                    fig.add_trace(go.Scatter(
                        x=final_df[x_col],
                        y=final_df[y_col if y_col else 'count'],
                        mode='lines+markers',
                        line=dict(width=2, color='blue'),
                        marker=dict(size=6)
                    ))
            
            elif chart_type.lower() == 'pie':
                fig.add_trace(go.Pie(
                    labels=final_df[x_col],
                    values=final_df[y_col if y_col else 'count']
                ))
        
        # Update layout
        title_text = f"{chart_name} (Rows: {end_idx:,}/{len(df):,})"
        
        if chart_type.lower() == 'pie':
            fig.update_layout(title=title_text, height=500, showlegend=True)
        else:
            fig.update_layout(
                title=title_text,
                xaxis_title=x_col,
                yaxis_title=y_col if y_col else 'count',
                height=500,
                hovermode='closest' if chart_type.lower() == 'scatter' else 'x unified'
            )
        
        # Force immediate update using container rewriting
        with chart_placeholder.container():
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
        
        progress_bar.progress((i + 1) / total_chunks)
        status_text.text(f"Processing: {end_idx:,}/{len(df):,} rows ({((i+1)/total_chunks*100):.1f}%)")
        
        time.sleep(0.1)  # Small delay to see the animation
    
    status_text.success(f"Chart completed: {len(df):,} rows processed")
    progress_bar.empty()
    
    return fig

# ==================== ORIGINAL ALTAIR CHART FUNCTION ====================

def get_altair_chart(data, chart_type, xValues, yValues=None, aggregate='sum', colourValues=None, linepoint=False, height=400, width=200, color_scheme=None):

    chart = alt.Chart(data)

    match chart_type:
        case "Line":
            if data[xValues].dtype == 'datetime64[ns]':
                if colourValues is not None:
                    chart = chart.mark_line(point=linepoint).encode(x=f'{xValues}:T', y=yValues, color=colourValues).properties(height=height, width=width)
                else:
                    chart = chart.mark_line(point=linepoint).encode(x=f'{xValues}:T', y=yValues).properties(height=height, width=width)
            else:
                if colourValues is not None:
                    chart = chart.mark_line(point=linepoint).encode(x=xValues, y=yValues, color=colourValues).properties(height=height, width=width)
                else:
                    chart = chart.mark_line(point=linepoint).encode(x=xValues, y=yValues).properties(height=height, width=width)
        case "Scatter":
            base = chart.mark_circle().encode(
                x=xValues,
                y=yValues
            ).properties(height=height, width=width)
            
            if colourValues is not None:
                color_encoding = alt.Color(colourValues)
                if color_scheme:
                    color_encoding = color_encoding.scale(scheme=color_scheme)
                chart = base.encode(color=color_encoding)
            else:
                chart = base
        case "Bar":
            if data[xValues].dtype == 'datetime64[ns]':
                if yValues is not None:
                    if colourValues is not None:
                        grouped_df = data.groupby([xValues, colourValues])[yValues].agg(f'{aggregate}').reset_index()
                        grouped_df.columns = [xValues, colourValues, yValues]
                        chart_grp = alt.Chart(grouped_df)
                        chart = chart_grp.mark_bar().encode(x=f'{xValues}:T', y=yValues, color=colourValues).properties(height=height, width=width)
                    else:
                        grouped_df = data.groupby(xValues)[yValues].agg(f'{aggregate}').reset_index()
                        grouped_df.columns = [xValues, yValues]
                        chart_grp = alt.Chart(grouped_df)
                        chart = chart_grp.mark_bar().encode(x=f'{xValues}:T', y=yValues).properties(height=height, width=width)
                else:
                    if colourValues is not None:
                        chart = chart.mark_bar().encode(x=f'{xValues}:T', y=f'count({xValues})', color=colourValues).properties(height=height, width=width)
                    else:
                        chart = chart.mark_bar().encode(x=f'{xValues}:T', y=f'count({xValues})').properties(height=height, width=width)
            else:
                if yValues is not None:
                    if colourValues is not None:
                        grouped_df = data.groupby([xValues, colourValues])[yValues].agg(f'{aggregate}').reset_index()
                        grouped_df.columns = [xValues, colourValues, yValues]
                        chart_grp = alt.Chart(grouped_df)
                        chart = chart_grp.mark_bar().encode(x=xValues, y=yValues, color=colourValues).properties(height=height, width=width)
                    else:
                        grouped_df = data.groupby(xValues)[yValues].agg(f'{aggregate}').reset_index()
                        grouped_df.columns = [xValues, yValues]
                        chart_grp = alt.Chart(grouped_df)
                        chart = chart_grp.mark_bar().encode(x=xValues, y=yValues).properties(height=height, width=width)
                else:
                    if colourValues is not None:
                        chart = chart.mark_bar().encode(x=xValues, y=f'count({xValues})', color=colourValues).properties(height=height, width=width)
                    else:
                        chart = chart.mark_bar().encode(x=xValues, y=f'count({xValues})').properties(height=height, width=width)
        case "Pie":
            chart = chart.mark_arc().encode(theta=xValues, color=yValues).properties(height=height, width=width)

        case "Boxplot":
            if colourValues is not None:
                chart = chart.mark_boxplot(extent="min-max").encode(x=xValues, y=yValues, color=colourValues).properties(height=height, width=width)
            else:
                chart = chart.mark_boxplot(extent="min-max").encode(x=xValues, y=yValues).properties(height=height, width=width)
        case "Heatmap":
            chart1 = chart.mark_rect().encode(x=xValues, y=yValues, color=colourValues).properties(height=500, width=600).properties(height=height, width=width)
            chart_text = chart1.mark_text(baseline='middle', fontSize=10).encode(text=colourValues)
            chart = chart1 + chart_text
        case "Histogram":
            chart1 = chart.mark_bar().encode(x={'field': xValues, 'bin': True}, y=f'{aggregate}({xValues})').properties(height=height, width=width)
            rule = chart1.mark_rule(color='red').encode(x=f'mean({xValues})', size=alt.value(5))
            chart = chart1 + rule

    return chart, chart.to_json(format="vega")

# ==================== MAIN SHOW_CHARTS FUNCTION ====================

def show_charts(dataset_file_name):
    alt.data_transformers.enable("vegafusion")
    dimensions_df = db.get_dimensions(dataset_file_name)
    measures_and_dimensions_df = db.get_measures_and_dimensions(dataset_file_name)

    st.write("**Generated Charts**")
    
    df_charts = db.show_chart_data(dataset_file_name)
    
    if not df_charts.empty:
        df_charts = df_charts.drop(['chart_specs'], axis=1)
        df_charts.index = df_charts.index + 1
        df_charts['Selections'] = True
        non_editable_columns = [column for column in df_charts.columns.tolist() if column not in ['Selections', 'chart_name']]
        
        gb = GridOptionsBuilder.from_dataframe(df_charts)
        gb.configure_grid_options(domLayout='autoHeight', editable=True)
        gridOptions = gb.build()
        edited_df = AgGrid(df_charts, gridOptions=gridOptions)

        if st.button('Save Changes'):
            db.update_charts_in_db(edited_df, dataset_file_name)
            st.rerun()
        
        if st.button('Delete Selected Rows'):
            rows_to_delete = edited_df[edited_df['Selections']].index.tolist()
            if rows_to_delete:
                df_charts = df_charts.drop(rows_to_delete)
                db.delete_charts_from_db(rows_to_delete, dataset_file_name)
                st.rerun()
    else:
        empty_df = pd.DataFrame({
            "chart_id": [None],
            "chart_name": [None],
            "x_column": [None],
            "y_column": [None],
            "color_column": [None],
            "chart_type": [None],
            "aggregation": [None],
            "dataset_id": [None],
            "date_created": [None],
            "Selections": [None]
        })
        
        st.warning("No charts in database yet!")
        st.data_editor(empty_df, hide_index=True)

    # Chart creation form
    st.divider()
    st.subheader("📊 Create New Chart")
    
    # Load data once
    data = db.load_df_from_parquet(dataset_file_name)
    
    # Check dataset size
    dataset_size = len(data)
    use_incremental = dataset_size > 10000  # Auto-enable for large datasets
    
    if dataset_size > 10000:
        st.info(f"📊 Large dataset detected ({dataset_size:,} rows). Incremental plotting will be used automatically.")
    
    with st.form("show-chart", clear_on_submit=True):
        # Column selections
        Xcolumn = st.selectbox(
            'Select X axis column',
            [None] + (measures_and_dimensions_df['column_name'] + "--" + measures_and_dimensions_df['m_or_d_type'].astype(str)).tolist(),
            index=None,
            placeholder="Select X column..."
        )
        Ycolumn = st.selectbox(
            'Select Y axis column',
            [None] + (measures_and_dimensions_df['column_name'] + "--" + measures_and_dimensions_df['m_or_d_type'].astype(str)).tolist(),
            index=None,
            placeholder="Select Y column..."
        )
        Colourcolumn = st.selectbox(
            'Select Colour column',
            [None] + (dimensions_df['column_name'] + "--" + dimensions_df['m_or_d_type'].astype(str)).tolist(),
            index=None,
            placeholder="Select Colour column..."
        )
    
        aggregation = st.selectbox("Aggregation: ", [None, "sum", "mean", "std", "count"], index=1)
        aggregation_dimension = st.selectbox("Aggregation for dimension: ", [None, "X", "Y"], index=None)
        chart_type = st.selectbox("Chart-type: ", ["Line", "Scatter", "Bar", "Pie"], index=None)
        
        # Extract column names
        xValues = Xcolumn.split("--", 1)[0] if Xcolumn else None
        yValues = Ycolumn.split("--", 1)[0] if Ycolumn else None
        colourValues = Colourcolumn.split("--", 1)[0] if Colourcolumn else None
        
        # Show warning for suspicious Y columns
        if yValues and yValues in data.columns:
            y_unique = data[yValues].nunique()
            y_max = data[yValues].max()
            if y_unique < 50 and y_max < 100:
                st.warning(f"⚠️ '{yValues}' has only {y_unique} unique values (max: {y_max}). This looks like a category/code, not a measurement. Consider using it as X-axis instead.")
        
        chart_name = st.text_input("Enter a name for the chart", value="My Chart", key="chart_name")
        
        # Chunk size for incremental (only shown if needed)
        if use_incremental:
            chunk_size = st.slider(
                "Chunk Size (for large datasets)",
                min_value=100,
                max_value=10000,
                value=3000,
                step=100,
                help="Number of rows to process per update"
            )
        else:
            chunk_size = 2000
        
        submitted = st.form_submit_button("Save and Show Chart", type="primary")
    
    if submitted and chart_type:
        try:
            if use_incremental and chart_type in ["Line", "Bar", "Scatter", "Pie"]:
                # Use incremental Plotly charting for large datasets
                st.info(f"🔄 Using incremental rendering for {dataset_size:,} rows...")
                
                create_incremental_plotly_chart(
                    df=data,
                    x_col=xValues,
                    y_col=yValues,
                    chart_type=chart_type,
                    chart_name=chart_name,
                    color_col=colourValues,
                    agg_func=aggregation if aggregation else 'sum',
                    chunk_size=chunk_size
                )
                
                # Note: For incremental charts, we don't save to DB with Vega specs
                st.success("✅ Chart generated successfully! (Incremental charts are not saved to database)")
                
            else:
                # Use original Altair charting for small datasets
                altair_chart, chart_data = get_altair_chart(
                    data,
                    chart_type=chart_type,
                    xValues=xValues,
                    yValues=yValues,
                    aggregate=aggregation if aggregation else 'sum',
                    colourValues=colourValues
                )
                st.altair_chart(altair_chart, use_container_width=True)
                
                # Save to database
                db.insert_chart_in_db(
                    chart_name,
                    xValues,
                    yValues,
                    colourValues,
                    chart_type,
                    aggregation,
                    dataset_file_name,
                    chart_data
                )
                
                # PDF download
                def save_df_to_pdf(filename, altair_chart):
                    buffer = BytesIO()
                    c = canvas.Canvas(buffer, pagesize=A4)
                    width, height = A4
                    margin = 30
                    page_number = 1

                    def draw_chart(c, altair_chart, title):
                        nonlocal page_number
                        if altair_chart is not None:
                            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                                altair_chart.save(tmpfile.name, format='png')
                                chart_image_path = tmpfile.name

                            max_chart_width = width - 2 * margin
                            max_chart_height = height - 2 * margin
                            chart_aspect_ratio = max_chart_width / max_chart_height

                            with open(chart_image_path, 'rb') as f:
                                img = PILImage.open(f)
                                img_width, img_height = img.size

                            if img_width > max_chart_width:
                                scaled_width = max_chart_width
                                scaled_height = scaled_width / chart_aspect_ratio
                            elif img_height > max_chart_height:
                                scaled_height = max_chart_height
                                scaled_width = scaled_height * chart_aspect_ratio
                            else:
                                scaled_width = img_width
                                scaled_height = img_height

                            c.setFont("Helvetica-Bold", 12)
                            c.drawString(margin, height - margin, title)
                            c.drawImage(ImageReader(chart_image_path), margin, margin, width=scaled_width, height=scaled_height)

                            page_number_text = f"Page {page_number}"
                            c.drawRightString(width - margin, margin, page_number_text)
                            page_number += 1

                    if altair_chart is not None:
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(margin, height - margin, "Chart 1")
                        draw_chart(c, altair_chart, "Chart 1")

                    c.save()
                    buffer.seek(0)

                    unique_key = str(uuid.uuid4())
                    st.download_button(
                        label="Download PDF",
                        data=buffer,
                        file_name=filename,
                        mime="application/pdf",
                        key=unique_key
                    )

                save_df_to_pdf('Charts.pdf', altair_chart)
                
        except Exception as e:
            st.error(f"Error generating chart: {str(e)}")
            st.exception(e)