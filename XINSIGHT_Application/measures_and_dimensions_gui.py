import streamlit as st
from streamlit_extras.grid import grid
import pandas as pd
import db
import re
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

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
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


def show_measures_and_dimensions(dataset_file_name):
                
    m_or_d_already_defined = db.check_m_or_d_already_defined(dataset_file_name)
    if m_or_d_already_defined is not True:
        df = db.load_df_from_parquet(dataset_file_name, preprocess=True)
        ## date type conversion
        cat_col= df.select_dtypes(include='object').columns.to_list()
        for j in cat_col:
            flag=0
            c=[]
            for i in df[j]:
                test_str = i
                pattern_str_1 = r'^\d{4}(\-|/|.|,)\d{2}(\-|/|.|,)\d{2}$'
                pattern_str_2= r'^\d{2}(\-|/|.|,)\d{2}(\-|/|.|,)\d{4}$'
                pattern_str_3= r'^\d{2}(\-|/|.|,)\d{2}(\-|/|.|,)\d{2}$'
                pattern_str_8=r'^\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|,|-|.)\d{2}(\/|-|,.)\d{4}$|^\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|,|-|.)\d{2}(\/|-|.|,)\d{2}$|^\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{4}(\/|-|.|,)\d{2}$|^\d{2}(\/|-|.|,)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{4}$|^\d{2}(\/|-|.|,)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{2}$|^\d{4}(\/|-|.|,)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{2}$|^\d{2}(\/|-|.)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{2}$'
                # pattern_str_4= r'^\b(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{2}(\/|-|.)\d{4}$|^\b(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{2}(\/|-|.)\d{2}$|^\b(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{4}(\/|-|.)\d{2}$'
                # pattern_str_5= r'^\d{2}(\/|-|.)\b
                # (?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{4}$|^\d{2}(\/|-|.)\b(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{2}$'
                # pattern_str_6= r'^\d{4}(\/|-|.)\b(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{2}$|^\d{2}(\/|-|.)\b(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?)(\/|-|.)\d{2}$'
                pattern_str_7=r'^(?:(?:(?:0?[13578]|1[02])(\/|-|\.)31)\1|(?:(?:0?[1,3-9]|1[0-2])(\/|-|\.)(?:29|30)\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:0?2(\/|-|\.)29\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:(?:0?[1-9])|(?:1[0-2]))(\/|-|\.)(?:0?[1-9]|1\d|2[0-8])\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'
                if re.match(pattern_str_1, str(test_str)) or re.match(pattern_str_2, str(test_str)) or re.match(pattern_str_3, str(test_str))  or re.match(pattern_str_7,str(test_str)) or re.match(pattern_str_8,str(test_str)):
                    # print("True")
                    c.append('True')
                else:
                    # print("False")
                    c.append('False')
            # print(type(c))
            for z in c:
                if(z=='True'):
                    flag=flag+1
                else:
                    flag= flag-1  
            if(flag>=1):
                df[j]=df[j].astype('datetime64[ns]')


        column_types = {}

        # Iterate over columns and determine their types
        for column in df.columns:
            if df[column].dtype == 'object' or df[column].dtype == 'datetime64[ns]':
                column_types[column] = "categorical"
            else: 
                column_types[column] = "numerical"

        # Create default column selections
        default_column_selection = {}
        for column in df.columns:
            default_column_selection[column] = "DIMENSION" if column_types[column] == "categorical" else "MEASURE"

        result = db.insert_measures_and_dimensions(dataset_file_name, default_column_selection)

    st.write(f"**Currently defined measure and dimensions for {dataset_file_name} dataset**")  #** for bold
        
    ph = st.empty()
    measures_and_dimensions_df = db.get_measures_and_dimensions(dataset_file_name)
    edited_measures_and_dimensions_df = ph.data_editor(measures_and_dimensions_df, 
                                                height=300,
                                                hide_index=True, 
                                                column_config={ "column_name":"Column Name", 
                                                                "m_or_d_type": st.column_config.SelectboxColumn("Measure or Dimension", options=["MEASURE","DIMENSION"]), 
                                                                "date_created": "Date Created"})
    

    measures_and_dimensions_df = db.get_measures_and_dimensions(dataset_file_name)
    gb = GridOptionsBuilder.from_dataframe(measures_and_dimensions_df)
    gb.configure_default_column(editable=True)
    gb.configure_column("column_name", header_name="Column Name", editable=True)
    gb.configure_column(
        "m_or_d_type",
        header_name="Measure or Dimension",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": ["MEASURE", "DIMENSION"]},
    )
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()
    with ph.container():
        grid_response = AgGrid(
            measures_and_dimensions_df,
            gridOptions=grid_options,
            height=300,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
        )
    edited_measures_and_dimensions_df = grid_response["data"]

    
    message = st.empty()

    if st.button("Save Measures and Dimensions", type="primary"):
        db.save_measures_and_dimensions_in_db(edited_measures_and_dimensions_df, dataset_file_name)
        message.success("Measures and Dimensions saved successfully.")

    save_df_to_pdf(filename="Measures_Dimensions", dataframe=edited_measures_and_dimensions_df, df_heading="Measures & Dimensions:")

