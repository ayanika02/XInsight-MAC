import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import tempfile

import db

def generate_pdf(dataframe, output_filename, df_heading="Heading 1"):
    buffer = tempfile.NamedTemporaryFile(delete=False)
    pdf = SimpleDocTemplate(buffer.name, pagesize=A4)
    pdf_elements = []

    styles = getSampleStyleSheet()

    small_style = ParagraphStyle(
        'small',
        fontSize=6,  # Change font size to 6
        leading=8    # Adjust leading accordingly
    )

    # Handle the first dataframe
    if dataframe is not None:
        pdf_elements.append(Paragraph(text=df_heading, style=styles['Heading2']))
        table_data1 = [dataframe.columns.tolist()] + dataframe.values.tolist()
        table1 = Table(table_data1)
        table1.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 5.2),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        pdf_elements.append(table1)
        pdf_elements.append(Spacer(1, 12))
    # Define a function to add page numbers
    def add_page_numbers(canvas, doc):
        page_number_text = f"Page {doc.page}"
        canvas.drawRightString(A4[0] - inch, 0.75 * inch, page_number_text)

    # Pass the function to be called after each page is drawn
    pdf.build(pdf_elements, onFirstPage=add_page_numbers, onLaterPages=add_page_numbers)
    buffer.seek(0)
    return buffer

def save_df_to_pdf(filename, dataframe=None, df_heading="Dataframe 1"):
    buffer = generate_pdf(dataframe=dataframe,
                          output_filename=filename,
                          df_heading=df_heading)
    pdf_data = buffer.read()
    st.download_button(label="Download PDF", data=pdf_data, file_name=f"{filename}.pdf", mime="application/pdf")



def show_metrics(dataset_name):
    
    measures_df = db.get_measures(dataset_name)
    dimensions_df = db.get_dimensions(dataset_name)
    df = db.get_metrics_from_metric_table(dataset_name)
    if not df.empty:
        df.index = df.index + 1
        metrics_df_mod = df.drop(columns=['m_or_d_id_1', 'm_or_d_id_2', 'm_or_d_id_3', 'm_or_d_id_4'])
        metrics_df_mod['Selections'] = False
    else:
        st.warning("No metric found in the database.")
        metrics_df_mod = pd.DataFrame({
            "metric_id": [None],
            "dataset_id": [None],
            "metric_name": [None],
            "metric_measure_name": [None], 
            "metric_dimension_name1": [None],
            "metric_dimension_name2": [None],
            "metric_dimension_name3": [None],
            "date_created": [None],
            "Selections": False
        })
    measure_col_config_list = [None]+(measures_df['column_name']+"--"+measures_df['m_or_d_type'].astype(str)).tolist()
    dimension_config_list = [None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist()
    ph = st.empty()
    edited_metrics_df = ph.data_editor(metrics_df_mod,
                                                height=300,
                                                hide_index=True,
                                                column_config={ "metric_id":"Metric_Id", 
                                                                "dataset_id":"Dataset ID",
                                                                "metric_name":"Metric_Name",
                                                                "metric_measure_name":st.column_config.SelectboxColumn("Measure", options=measure_col_config_list), 
                                                                "metric_dimension_name1":st.column_config.SelectboxColumn("Dimension 1", options=dimension_config_list),
                                                                "metric_dimension_name2":st.column_config.SelectboxColumn("Dimension 2", options=dimension_config_list),
                                                                "metric_dimension_name3":st.column_config.SelectboxColumn("Dimension 3", options=dimension_config_list),
                                                                "date_created": "Date Created",
                                                                "Selections": "Selections"})
    
    if st.button("Save Edited Metrics", type="primary"):
        db.save_updated_metrics(edited_metrics_df)
        st.rerun()
        
    if st.button('Delete Selected'):
            rows_to_delete = edited_metrics_df[edited_metrics_df['Selections']].index.tolist()
            if rows_to_delete:
                df = df.drop(rows_to_delete)
                #st.write(rows_to_delete)
                #print(rows_to_delete)
                db.delete_metrics_from_db(rows_to_delete, dataset_name)
                st.rerun()



    with st.form("show-metric", clear_on_submit=True):

        metric_name = st.text_input("Enter Name for the Metric: ", value = "")
        measure_name = st.selectbox(
                'Select measure column',[None]+(measures_df['column_name']+"--"+measures_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select measure column...")
        
        dimension_name1 = st.selectbox(
                'Select dimension 1 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 1...")
        
        dimension_name2 = st.selectbox(
                'Select dimension 2 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 2...")
        
        dimension_name3 = st.selectbox(
                'Select dimension 3 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 3...")
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Check if at least one dimension is of date type
            selected_dimensions = [dimension_name1, dimension_name2, dimension_name3]
            date_dimension_selected = any("date" in dimension.lower() for dimension in selected_dimensions if dimension)

            if date_dimension_selected:
                db.insert_metrics_in_metric_table(dataset_name, metric_name, measure_name, dimension_name1, dimension_name2, dimension_name3)
                st.rerun()
            else:
                st.error("At least one dimension must be of date type. Please select a date type dimension.")



    # def save_df_to_pdf(dataframe, filename):
    #     buffer = BytesIO()
    #     c = canvas.Canvas(buffer, pagesize=landscape(A4))
    #     width, height = landscape(A4)
    #     c.setFont("Helvetica-Bold", 12)
    #     c.drawString(30, height - 30, "Metrics:")

    #     # Adjusted column widths to fit content better
    #     col_widths = [50, 65, 105, 115, 115, 115, 58, 100, 55]  # Customize based on your DataFrame
    #     row_height = 25  # Slightly increased row height

    #     # Draw headers with grid lines
    #     c.setFont("Helvetica-Bold", 9)
    #     y_position = height - 65
    #     for i, col in enumerate(dataframe.columns):
    #         x_position = 30 + sum(col_widths[:i])
    #         c.drawString(x_position + 2, y_position, col)

    #     # Draw rows with grid lines
    #     c.setFont("Helvetica", 9)
    #     y_position -= row_height
    #     for row_num, row in enumerate(dataframe.values):
    #         for col_num, cell in enumerate(row):
    #             x_position = 30 + sum(col_widths[:col_num])
    #             c.drawString(x_position + 2, y_position, str(cell))
    #         y_position -= row_height

    #     # Draw final horizontal and vertical grid lines
    #     for i in range(len(dataframe.columns) + 1):
    #         x_position = 30 + sum(col_widths[:i])
    #         c.line(x_position, height - 50, x_position, y_position + row_height-10)
    #     for j in range(len(dataframe) + 2):
    #         y_position = height - 50 - j * row_height
    #         c.line(30, y_position, 30 + sum(col_widths), y_position)

    #     c.save()
    #     buffer.seek(0)
    #     st.download_button(label="Download PDF", data=buffer, file_name=filename, mime="application/pdf")

# Assuming edited_metrics_df is your DataFrame and this is in a Streamlit app context
    save_df_to_pdf(filename="metrics.pdf", dataframe= edited_metrics_df, df_heading="Metrics")


'''
import streamlit as st
import pandas as pd


import db
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def show_metrics_table(dataset_name):
    df = db.get_metrics_from_metric_table(dataset_name)
    df.index = df.index + 1
    if not df.empty:
        df['Selections'] = False
        # st.write("## Metrics in the database")
        # st.table(df)
        pass
    else:
        st.write("No metric found in the database.")

def show_metrics(dataset_file_name):
    show_metrics_table(dataset_file_name)
    measures_df = db.get_measures(dataset_file_name)
    dimensions_df = db.get_dimensions(dataset_file_name)

    ph = st.empty()
    metrics_df = db.get_metrics_from_metric_table(dataset_file_name)
    if metrics_df.empty:
        metrics_df_mod = pd.DataFrame({
            "metric_id": [None],
            "dataset_id": [None],
            "metric_name": [None],
            "metric_measure_name": [None], 
            "metric_dimension_name1": [None],
            "metric_dimension_name2": [None],
            "metric_dimension_name3": [None],
            "date_created": [None]
        })
    else:
        metrics_df_mod = metrics_df.drop(columns=['m_or_d_id_1', 'm_or_d_id_2', 'm_or_d_id_3', 'm_or_d_id_4'])
        metrics_df_mod.index = metrics_df_mod.index + 1
    #st.dataframe(metrics_df_mod)
    measure_col_config_list = [None]+(measures_df['column_name']+"--"+measures_df['m_or_d_type'].astype(str)).tolist()
    dimension_config_list = [None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist()
    
    edited_metrics_df = ph.data_editor(metrics_df_mod,
                                                height=300,
                                                hide_index=True,
                                                column_config={ "metric_id":"Metric_Id", 
                                                                "dataset_id":"Dataset ID",
                                                                "metric_name":"Metric_Name",
                                                                "metric_measure_name":st.column_config.SelectboxColumn("Measure", options=measure_col_config_list), 
                                                                "metric_dimension_name1":st.column_config.SelectboxColumn("Dimension 1", options=dimension_config_list),
                                                                "metric_dimension_name2":st.column_config.SelectboxColumn("Dimension 2", options=dimension_config_list),
                                                                "metric_dimension_name3":st.column_config.SelectboxColumn("Dimension 3", options=dimension_config_list),
                                                                "date_created": "Date Created"})

    #st.dataframe(edited_metrics_df)
    if st.button('Delete Selected'):
            rows_to_delete = edited_metrics_df[edited_metrics_df['Selections']].index.tolist()
            if rows_to_delete:
                df = df.drop(rows_to_delete)
                #st.write(rows_to_delete)
                #print(rows_to_delete)
                db.delete_metrics_from_db(rows_to_delete, dataset_file_name)
                #st.success('Charts deleted!')
                #st.rerun()
    if st.button("Save Edited Metrics", type="primary"):
        db.save_updated_metrics(edited_metrics_df)
        st.rerun()

    with st.form("show-metric", clear_on_submit=True):

        metric_name = st.text_input("Enter Name for the Metric: ", value = "")
        measure_name = st.selectbox(
                'Select measure column',[None]+(measures_df['column_name']+"--"+measures_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select measure column...")
        
        dimension_name1 = st.selectbox(
                'Select dimension 1 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 1...")
        
        dimension_name2 = st.selectbox(
                'Select dimension 2 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 2...")
        
        dimension_name3 = st.selectbox(
                'Select dimension 3 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 3...")
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Check if at least one dimension is of date type
            selected_dimensions = [dimension_name1, dimension_name2, dimension_name3]
            date_dimension_selected = any("date" in dimension.lower() for dimension in selected_dimensions if dimension)

            if date_dimension_selected:
                db.insert_metrics_in_metric_table(dataset_file_name, metric_name, measure_name, dimension_name1, dimension_name2, dimension_name3)
                st.rerun()
            else:
                st.error("At least one dimension must be of date type. Please select a date type dimension.")



    def save_df_to_pdf(dataframe, filename):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.drawString(30, height - 30, f"Measures and Dimensions for {filename}")

        # Adjusted column widths to fit content better
        col_widths = [36, 48, 80, 90, 90, 90, 40, 85]  # Customize based on your DataFrame
        row_height = 25  # Slightly increased row height

        # Draw headers with grid lines
        c.setFont("Helvetica-Bold", 7)
        y_position = height - 65
        for i, col in enumerate(dataframe.columns):
            x_position = 30 + sum(col_widths[:i])
            c.drawString(x_position + 2, y_position, col)

        # Draw rows with grid lines
        c.setFont("Helvetica", 7)
        y_position -= row_height
        for row_num, row in enumerate(dataframe.values):
            for col_num, cell in enumerate(row):
                x_position = 30 + sum(col_widths[:col_num])
                c.drawString(x_position + 2, y_position, str(cell))
            y_position -= row_height

        # Draw final horizontal and vertical grid lines
        for i in range(len(dataframe.columns) + 1):
            x_position = 30 + sum(col_widths[:i])
            c.line(x_position, height - 50, x_position, y_position + row_height-10)
        for j in range(len(dataframe) + 2):
            y_position = height - 50 - j * row_height
            c.line(30, y_position, 30 + sum(col_widths), y_position)

        c.save()
        buffer.seek(0)
        st.download_button(label="Download PDF", data=buffer, file_name=filename, mime="application/pdf")

# Assuming edited_metrics_df is your DataFrame and this is in a Streamlit app context
    save_df_to_pdf(edited_metrics_df, "metrics.pdf")

'''









# import streamlit as st
# import pandas as pd


# import db


# def show_metrics_table(dataset_name):
#     df = db.get_metrics_from_metric_table(dataset_name)
#     df.index = df.index + 1
#     if not df.empty:
#         st.write("## Metrics in the database")
#         st.table(df)
#     else:
#         st.write("No metric found in the database.")

# def show_metrics(dataset_file_name):
#     show_metrics_table(dataset_file_name)
#     measures_df = db.get_measures(dataset_file_name)
#     dimensions_df = db.get_dimensions(dataset_file_name)

#     ph = st.empty()
#     metrics_df = db.get_metrics_from_metric_table(dataset_file_name)
#     if metrics_df.empty:
#         metrics_df_mod = pd.DataFrame({
#             "metric_id": [None],
#             "dataset_id": [None],
#             "metric_name": [None],
#             "metric_measure_name": [None], 
#             "metric_dimension_name1": [None],
#             "metric_dimension_name2": [None],
#             "metric_dimension_name3": [None],
#             "date_created": [None]
#         })
#     else:
#         metrics_df_mod = metrics_df.drop(columns=['m_or_d_id_1', 'm_or_d_id_2', 'm_or_d_id_3', 'm_or_d_id_4'])
#         metrics_df_mod.index = metrics_df_mod.index + 1
#     #st.dataframe(metrics_df_mod)
#     measure_col_config_list = [None]+(measures_df['column_name']+"--"+measures_df['m_or_d_type'].astype(str)).tolist()
#     dimension_config_list = [None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist()
    
#     edited_metrics_df = ph.data_editor(metrics_df_mod,
#                                                 height=300,
#                                                 hide_index=True,
#                                                 column_config={ "metric_id":"Metric_Id", 
#                                                                 "dataset_id":"Dataset ID",
#                                                                 "metric_name":"Metric_Name",
#                                                                 "metric_measure_name":st.column_config.SelectboxColumn("Measure", options=measure_col_config_list), 
#                                                                 "metric_dimension_name1":st.column_config.SelectboxColumn("Dimension 1", options=dimension_config_list),
#                                                                 "metric_dimension_name2":st.column_config.SelectboxColumn("Dimension 2", options=dimension_config_list),
#                                                                 "metric_dimension_name3":st.column_config.SelectboxColumn("Dimension 3", options=dimension_config_list),
#                                                                 "date_created": "Date Created"})

#     #st.dataframe(edited_metrics_df)
#     if st.button("Save Edited Metrics", type="primary"):
#         db.save_updated_metrics(edited_metrics_df)
#         st.rerun()

#     with st.form("show-metric", clear_on_submit=True):

#         metric_name = st.text_input("Enter Name for the Metric: ", value = "")
#         measure_name = st.selectbox(
#                 'Select measure column',[None]+(measures_df['column_name']+"--"+measures_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select measure column...")
        
#         dimension_name1 = st.selectbox(
#                 'Select dimension 1 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 1...")
        
#         dimension_name2 = st.selectbox(
#                 'Select dimension 2 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 2...")
        
#         dimension_name3 = st.selectbox(
#                 'Select dimension 3 column',[None]+(dimensions_df['column_name']+"--"+dimensions_df['m_or_d_type'].astype(str)).tolist(), index=0, placeholder="Select dimension column 3...")
        
#         submitted = st.form_submit_button("Submit")
#         if submitted:
#             # Check if at least one dimension is of date type
#             selected_dimensions = [dimension_name1, dimension_name2, dimension_name3]
#             date_dimension_selected = any("date" in dimension.lower() for dimension in selected_dimensions if dimension)

#             if date_dimension_selected:
#                 db.insert_metrics_in_metric_table(dataset_file_name, metric_name, measure_name, dimension_name1, dimension_name2, dimension_name3)
#                 st.rerun()
#             else:
#                 st.error("At least one dimension must be of date type. Please select a date type dimension.")