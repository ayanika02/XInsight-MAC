import streamlit as st
import altair as alt
#import streamlit_nested_layout
alt.data_transformers.enable("vegafusion")
import db
import vega_datasets
import pandas as pd
import json
import base64

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import uuid
from PIL import Image as PILImage

from st_aggrid import AgGrid, GridOptionsBuilder


def get_altair_chart(data, chart_type, xValues, yValues = None, aggregate = 'sum', colourValues = None, linepoint = False, height=400, width=200, color_scheme=None):

    chart = alt.Chart(data)

    match chart_type:
        case "Line":
            if data[xValues].dtype == 'datetime64[ns]':
                if colourValues is not None:
                    chart = chart.mark_line(point=linepoint).encode(x=f'{xValues}:T', y=yValues, color=colourValues).properties(height = height, width = width)
                else:
                    chart = chart.mark_line(point=linepoint).encode(x=f'{xValues}:T', y=yValues).properties(height = height, width = width)
            else:
                if colourValues is not None:
                    chart = chart.mark_line(point=linepoint).encode(x=xValues, y=yValues, color=colourValues).properties(height = height, width = width)
                else:
                    chart = chart.mark_line(point=linepoint).encode(x=xValues, y=yValues).properties(height = height, width = width)
        case "Scatter":
            #if colourValues is not None:
            #    chart = chart.mark_circle().encode(x=xValues, y=yValues, color=colourValues).properties(height = height, width = width)
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
                            chart = chart_grp.mark_bar().encode(x=f'{xValues}:T', y = yValues, color=colourValues).properties(height = height, width = width)
                        else:
                            grouped_df = data.groupby(xValues)[yValues].agg(f'{aggregate}').reset_index()
                            grouped_df.columns = [xValues, yValues]
                            chart_grp = alt.Chart(grouped_df)
                            chart = chart_grp.mark_bar().encode(x=f'{xValues}:T', y = yValues).properties(height = height, width = width)
                    else:
                        if colourValues is not None:
                            chart = chart.mark_bar().encode(x=f'{xValues}:T', y = f'count({xValues})', color=colourValues).properties(height = height, width = width)
                        else:
                            chart = chart.mark_bar().encode(x=f'{xValues}:T', y = f'count({xValues})').properties(height = height, width = width)
                else:
                    if yValues is not None:
                        if colourValues is not None:
                            grouped_df = data.groupby([xValues, colourValues])[yValues].agg(f'{aggregate}').reset_index()
                            grouped_df.columns = [xValues, colourValues, yValues]
                            chart_grp = alt.Chart(grouped_df)
                            chart = chart_grp.mark_bar().encode(x=xValues, y = yValues, color=colourValues).properties(height = height, width = width)
                        else:
                            grouped_df = data.groupby(xValues)[yValues].agg(f'{aggregate}').reset_index()
                            grouped_df.columns = [xValues, yValues]
                            chart_grp = alt.Chart(grouped_df)
                            chart = chart_grp.mark_bar().encode(x=xValues, y = yValues).properties(height = height, width = width)
                    else:
                        if colourValues is not None:
                            chart = chart.mark_bar().encode(x=xValues, y = f'count({xValues})', color=colourValues).properties(height = height, width = width)
                        else:
                            chart = chart.mark_bar().encode(x=xValues, y = f'count({xValues})').properties(height = height, width = width)
        case "Pie":                
            chart = chart.mark_arc().encode(theta=xValues, color=yValues).properties(height = height, width = width)

        case "Boxplot":
            if colourValues is not None:
                chart = chart.mark_boxplot(extent = "min-max").encode(x=xValues,y =yValues, color=colourValues).properties(height = height, width = width)
            else:
                chart = chart.mark_boxplot(extent = "min-max").encode(x=xValues,y =yValues).properties(height = height, width = width)
        case "Heatmap":
            chart1 = chart.mark_rect().encode(x=xValues,y =yValues, color=colourValues).properties(height = 500, width = 600).properties(height = height, width = width)
            chart_text = chart1.mark_text(baseline = 'middle',fontSize=10).encode(text = colourValues)
            chart = chart1 + chart_text
        case "Histogram":
            chart1 = chart.mark_bar().encode(x={'field': xValues, 'bin': True}, y = f'{aggregate}({xValues})').properties(height = height, width = width)
            rule = chart1.mark_rule(color='red').encode(x=f'mean({xValues})', size=alt.value(5))
            chart = chart1 + rule

    return chart, chart.to_json(format="vega")
    # return chart, chart.to_json()

def show_charts(dataset_file_name):
    alt.data_transformers.enable("vegafusion")
    # measures_df = db.get_measures(dataset_file_name)
    dimensions_df = db.get_dimensions(dataset_file_name)
    measures_and_dimensions_df = db.get_measures_and_dimensions(dataset_file_name)

    st.write("**Generated Charts**")
    
    df = db.show_chart_data(dataset_file_name)
    
    if not df.empty:
        df = df.drop(['chart_specs'], axis=1)
        df.index = df.index+1
        # st.table(df)
        # Add a selection column for row deletion
        df['Selections'] = False
        # df_cols = ['Delete'] + df.columns.tolist().remove('Delete')
        # df = df[df_cols]
        non_editable_columns = [column for column in df.columns.tolist() if column not in ['Selections', 'chart_name']]
        #st.write(non_editable_columns)
        # edited_df = st.data_editor(
        #     df,
        #     column_config={
        #     },
        #     disabled=non_editable_columns,
        #     hide_index=True,
        # ) 
        
        
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_grid_options(domLayout='autoHeight')
        gridOptions = gb.build()
        edited_df = AgGrid(df, gridOptions=gridOptions)

        # Optional: Save the edited data back to DuckDB
        if st.button('Save Changes'):
            db.update_charts_in_db(edited_df, dataset_file_name)
            st.rerun()
        
        if st.button('Delete Selected Rows'):
            rows_to_delete = edited_df[edited_df['Selections']].index.tolist()
            if rows_to_delete:
                df = df.drop(rows_to_delete)
                #st.write(rows_to_delete)
                #print(rows_to_delete)
                db.delete_charts_from_db(rows_to_delete, dataset_file_name)
                #st.success('Charts deleted!')
                st.rerun()

    #st.success('Changes saved successfully!')
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
            "Selections": [None]}
        )
        
        st.warning("No charts in database yet!")
        st.data_editor(empty_df, hide_index=True)

    with st.form("show-chart", clear_on_submit=True):
        Xcolumn = st.selectbox(
            'Select X axis column', [None] + (measures_and_dimensions_df['column_name'] + "--" + measures_and_dimensions_df['m_or_d_type'].astype(str)).tolist(), index=None, placeholder="Select X column...")
        Ycolumn = st.selectbox(
            'Select Y axis column', [None] + (measures_and_dimensions_df['column_name'] + "--" + measures_and_dimensions_df['m_or_d_type'].astype(str)).tolist(), index=None, placeholder="Select Y column...")
        Colourcolumn = st.selectbox(
            'Select Colour column', [None] + (dimensions_df['column_name'] + "--" + dimensions_df['m_or_d_type'].astype(str)).tolist(), index=None, placeholder="Select Colour column...")
    
        aggregation = st.selectbox("Aggregation: ", [None] + ["sum", "mean", "std"], index=1)
        aggregation_dimension = st.selectbox("Aggregation for dimension: ", [None] + ["X", "Y"], index=None)
        chart_type = st.selectbox("Chart-type: ", ["Line", "Scatter", "Bar", "Pie"], index=None)
    
        data = db.load_df_from_parquet(dataset_file_name)
    
        xValues = Xcolumn.split("--", 1)[0] if Xcolumn else None
        yValues = Ycolumn.split("--", 1)[0] if Ycolumn else None
        colourValues = Colourcolumn.split("--", 1)[0] if Colourcolumn else None
    
        chart_name = st.text_input("Enter a name for the chart", value="My Chart", key="chart_name")
    
        submitted = st.form_submit_button("Save and Show Chart")
    
    if submitted and chart_type:
        altair_chart, chart_data = get_altair_chart(data, chart_type=chart_type, xValues=xValues, yValues=yValues, aggregate=aggregation, colourValues=colourValues)
        st.altair_chart(altair_chart, use_container_width=True)
        
        db.insert_chart_in_db(chart_name, xValues, yValues, colourValues, chart_type, aggregation, dataset_file_name, chart_data)

        def save_df_to_pdf(filename, altair_chart):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            margin = 30
            page_number = 1  # Initialize page number

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

                    # Add page number
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
            st.download_button(label="Download PDF", data=buffer, file_name=filename, mime="application/pdf", key=unique_key)

# Example usage:
        save_df_to_pdf('Charts.pdf', altair_chart)
    
    