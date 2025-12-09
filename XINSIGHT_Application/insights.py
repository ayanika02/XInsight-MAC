import streamlit as st
from streamlit_ace import st_ace
import re
import uuid
#import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
#import plotly.graph_objects as go
from scipy.stats import f_oneway,chi2_contingency,kruskal,kstest,probplot,kurtosis,skew
import plotly.figure_factory as ff
from sklearn.cluster import KMeans
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder,StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
#import webbrowser as wb

import db
from chart_spec import *
from chart_spec_altair import *
from charts_gui_v3 import *
from kg_gui import *

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

from st_aggrid import AgGrid, GridOptionsBuilder

def generate_pdf(dataframe1, dataframe2, output_filename, df_headings=["Heading 1", "Heading 2"], plt_heading="Plot", altair_heading_1="Plot", altair_heading_2="Plot", altair_heading_3="Plot", plt_chart=None, altair_chart1=None, altair_chart2=None, altair_chart3=None):
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
    if dataframe1 is not None:
        pdf_elements.append(Paragraph(text=df_headings[0], style=styles['Heading2']))
        table_data1 = [dataframe1.columns.tolist()] + dataframe1.values.tolist()
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

    # Handle the second dataframe
    if dataframe2 is not None:
        pdf_elements.append(Paragraph(df_headings[1], styles['Heading2']))
        table_data2 = [dataframe2.columns.tolist()] + dataframe2.values.tolist()
        table2 = Table(table_data2)
        table2.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 2.8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        pdf_elements.append(table2)
        pdf_elements.append(Spacer(1, 12))

    def draw_chart_matplotlib(plt_chart, title):
        if plt_chart is not None:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                plt_chart.savefig(tmpfile.name, format='png')
                chart_image_path = tmpfile.name

            max_chart_width = A4[1] - 2 * 30
            max_chart_height = A4[0] - 2 * 30

            with open(chart_image_path, 'rb') as f:
                img = PILImage.open(f)
                img = img.resize((350, 350))

            img_element = Image(chart_image_path, width=350, height=350)
            return [Paragraph(title, styles['Heading2']), img_element, Spacer(1, 12)]

    def draw_chart_altair(altair_chart, title):
        if altair_chart is not None:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                altair_chart.save(tmpfile.name, format='png')
                chart_image_path = tmpfile.name

            max_chart_width = A4[1] - 2 * 30
            max_chart_height = A4[0] - 2 * 30

            with open(chart_image_path, 'rb') as f:
                img = PILImage.open(f)
                img = img.resize((400, 400))

            img_element = Image(chart_image_path, width=400, height=400)
            return [Paragraph(title, styles['Heading2']), img_element, Spacer(1, 12)]

    if plt_chart is not None or altair_chart1 is not None or altair_chart2 is not None or altair_chart3 is not None:
        if dataframe1 is not None or dataframe2 is not None:
            pdf_elements.append(PageBreak())
        if plt_chart is not None:
            pdf_elements.extend(draw_chart_matplotlib(plt_chart, plt_heading))
        if altair_chart1 is not None:
            pdf_elements.extend(draw_chart_altair(altair_chart1, altair_heading_1))
        if altair_chart2 is not None:
            pdf_elements.extend(draw_chart_altair(altair_chart2, altair_heading_2))
        if altair_chart3 is not None:
            pdf_elements.extend(draw_chart_altair(altair_chart3, altair_heading_3))

    # Define a function to add page numbers
    def add_page_numbers(canvas, doc):
        page_number_text = f"Page {doc.page}"
        canvas.drawRightString(A4[0] - inch, 0.75 * inch, page_number_text)

    # Pass the function to be called after each page is drawn
    pdf.build(pdf_elements, onFirstPage=add_page_numbers, onLaterPages=add_page_numbers)
    buffer.seek(0)
    return buffer

def save_df_to_pdf(filename, dataframe1=None, dataframe2=None, df_headings=["Dataframe 1", "Dataframe 2"], plt_headings="Pyplot Heading", altair_headings=["Altair chart 1", "Altair chart 2", "Altair chart 3"], plt_chart=None, altair_chart1=None, altair_chart2=None, altair_chart3=None):
    buffer = generate_pdf(dataframe1=dataframe1,
                          dataframe2=dataframe2,
                          output_filename=filename,
                          df_headings=df_headings,
                          plt_chart=plt_chart,
                          plt_heading=plt_headings,
                          altair_chart1=altair_chart1,
                          altair_chart2=altair_chart2,
                          altair_chart3=altair_chart3,
                          altair_heading_1=altair_headings[0],
                          altair_heading_2=altair_headings[1],
                          altair_heading_3=altair_headings[2])
    pdf_data = buffer.read()
    st.download_button(label="Download PDF", data=pdf_data, file_name=f"{filename}.pdf", mime="application/pdf")


def out(df):  #quantile calculations
    
    d=0
    q1= df.quantile(0.25)
    q3= df.quantile(0.75)
    IQR= q3-q1
    ub= q3+1.5*IQR
    lb= q1-1.5*IQR
    for j in df:
            if(j>ub or j<lb):
                d=d+1
    return(d)                             

def check1(uploaded_data):
    if uploaded_data.type=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        val=pd.read_excel(uploaded_data)
    else:
        val=pd.read_csv(uploaded_data) 
    return(val)

@st.cache_data
def load_data(dataset_file_name):
    data = db.load_df_from_parquet(dataset_file_name)
    data1 = db.load_df_from_parquet(dataset_file_name, preprocess=True)
    return data, data1

def tab1_func(data):
    rows=data.shape[0]
    cols= data.shape[1]
    duplicates=data[data.duplicated()]
    no_duplicates= duplicates.shape[0]
    no_missing_val= data[data.isna().any(axis=1)].shape[0]
    st.title("Meta Data")

    dict1={"Description":['Number of Rows','Number of Columns','Number of Duplicate Rows','Number of missing values'],"Values":[rows,cols,no_duplicates,no_missing_val]}
    df= pd.DataFrame(dict1)
        #well adjusted Aggrid height
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(domLayout='autoHeight')
    gridOptions1 = gb.build()
    AgGrid(df, gridOptions=gridOptions1)

    st.title("Column Wise Summary")
    cat_col= data.select_dtypes(include='object').columns.to_list()
    for j in cat_col:
        flag=0
        c=[]
        for i in data[j]:
            test_str = i
            pattern_str_1 = r'^\d{4}(\-|/|.|,)\d{2}(\-|/|.|,)\d{2}$'
            pattern_str_2= r'^\d{2}(\-|/|.|,)\d{2}(\-|/|.|,)\d{4}$'
            pattern_str_3= r'^\d{2}(\-|/|.|,)\d{2}(\-|/|.|,)\d{2}$'
            pattern_str_8=r'^\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|,|-|.)\d{2}(\/|-|,|.)\d{4}$|^\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|,|-|.)\d{2}(\/|-|.|,)\d{2}$|^\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{4}(\/|-|.|,)\d{2}$|^\d{2}(\/|-|.|,)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{4}$|^\d{2}(\/|-|.|,)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{2}$|^\d{4}(\/|-|.|,)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{2}$|^\d{2}(\/|-|.)\b((?:jan(?:uary)?|feb(?:ruary)?|...|dec(?:ember)?)|(?:Jan(?:uary)?|Feb(?:ruary)?|...|Dec(?:ember)?))(\/|-|.|,)\d{2}$'
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
            data[j]=data[j].astype('datetime64[ns]')
    # dictionary={'datatypes':data.dtypes} 
    # show=pd.DataFrame(dictionary)   
    # st.dataframe(show)         
    num_col=data.select_dtypes(include=['number']).columns.to_list()
    datatype=[]
    uni=[]
    miss=[]
    zer=[]
    neg=[]
    mean=[]
    median=[]
    skewness=[]
    kurto=[]
    q_1=[]
    q_3=[]
    minimum=[]
    maximum=[]
    sd=[]
    # inf=[]
    outliers=[]
    for i in data.columns:
        miss.append(data[i].isna().sum())
        uni.append((data[i].nunique()))
        
        # inf.append(data[i].isin([np.inf, -np.inf]).sum())
        if(data.dtypes[i]=="int64"):
            c=0
            datatype.append('Numerical (Integer)')
            zer.append(data[i][data[i]==0].count())
            neg.append(data[i].lt(0).sum())
            q1= data[i].quantile(0.25)
            q3= data[i].quantile(0.75)
            IQR= q3-q1
            ub= q3+1.5*IQR
            lb= q1-1.5*IQR
            for j in data[i]:
                    if(j>ub or j<lb):
                        c=c+1
            outliers.append(c)
            mean.append(round(data[i].mean(),3))
            median.append(round(data[i].median(),3))
            skewness.append(round(data[i].skew(),3))
            kurto.append(round(data[i].kurt(),3))
            sd.append(round(data[i].std(),3))
            minimum.append(data[i].min())
            maximum.append(data[i].max())
            q_1.append(data[i].quantile(0.25))
            q_3.append(data[i].quantile(0.75))
        elif(data.dtypes[i]=='float'):
            c=0
            datatype.append('Numerical (Decimal Point)')
            zer.append(data[i][data[i]==0].count())
            neg.append(data[i].lt(0).sum())
            q1= data[i].quantile(0.25)
            q3= data[i].quantile(0.75)
            IQR= q3-q1
            ub= q3+1.5*IQR
            lb= q1-1.5*IQR
            for j in data[i]:
                if(j>ub or j<lb):
                        c=c+1
            outliers.append(c)
            mean.append(round(data[i].mean(),3))
            median.append(round(data[i].median(),3))
            skewness.append(round(data[i].skew(),3))
            kurto.append(round(data[i].kurt(),3))
            sd.append(round(data[i].std(),3))
            minimum.append(data[i].min())
            maximum.append(data[i].max())
            q_1.append(data[i].quantile(0.25))
            q_3.append(data[i].quantile(0.75))
        elif(data.dtypes[i]=='object'):
            neg.append("Not Applicable")
            datatype.append('Categorical')
            zer.append(0)
            outliers.append("Not Applicable")
            mean.append("Not applicable")
            median.append("Not applicable")
            skewness.append("Not applicable")
            kurto.append("Not applicable")
            q_1.append("Not applicable")
            q_3.append("Not applicable")
            maximum.append("Not Applicable")
            minimum.append("Not Applicable")
            sd.append("Not Applicable")
        elif(data.dtypes[i]=='bool'):
            datatype.append('Boolean')
            zer.append(0)
            neg.append("Not Applicable") 
            outliers.append("Not Applicable")
            mean.append(round(data[i].mean(),3))
            median.append(round(data[i].median(),3))
            skewness.append(round(data[i].skew(),3))
            kurto.append(round(data[i].kurt(),3))
            sd.append(round(data[i].std(),3))
            minimum.append(data[i].min())
            maximum.append(data[i].max())
            q_1.append(data[i].quantile(0.25))
            q_3.append(data[i].quantile(0.75))
        else:
            datatype.append('Date')
            zer.append(0)
            neg.append("Not Applicable") 
            outliers.append("Not Applicable")
            mean.append("Not applicable")
            median.append("Not applicable")
            skewness.append("Not applicable")
            kurto.append("Not applicable")
            q_1.append("Not applicable")
            q_3.append("Not applicable")  
            maximum.append("Not Applicable")
            minimum.append("Not Applicable")
            sd.append("Not Applicable")    
    #st.table({"Column Name":data.columns,"Column Type":datatype,"No. of Unique Values":uni,"No. of Missing Values":miss,"Count of Zero Values":zer,"Count of Outliers":outliers,"No.of negative values":neg,"Mean":mean,"Median":median,"Skewness":skewness,"Kurtosis":kurto,"First Quartile":q_1,"Third Quartile":q_3,"Minimum Value": minimum,"Maximum Value":maximum,"Standard Deviation":sd})
    dict2={"Column Name":data.columns,"Column Type":datatype,"No. of Unique Values":uni,"No. of Missing Values":miss,"Count of Zero Values":zer,"Count of Outliers":outliers,"No.of negative values":neg,"Mean":mean,"Median":median,"Skewness":skewness,"Kurtosis":kurto,"First Quartile":q_1,"Third Quartile":q_3,"Minimum Value": minimum,"Maximum Value":maximum,"Standard Deviation":sd}
    df2= pd.DataFrame(dict2)
    st.table(df2)

    data_melted = data.select_dtypes(include="number").melt(var_name='column', value_name='value')
    chart, chart_spec_json = get_altair_chart(data_melted, chart_type="Boxplot", xValues='column', yValues='value')   
    chart_spec =  chart.to_json(format="vega")
    st.altair_chart(chart, use_container_width=True)
    save_df_to_pdf(filename='DataInfo.pdf', dataframe1=df, dataframe2=df2, altair_chart1=chart, df_headings=["Meta Data", "Summary Statistics"], altair_headings=["Box Plot", None, None])

    # save_df_to_pdf()

def tab2_func(data, data1):
    st.header("Numeric Features to be explored")
    num_col= data.select_dtypes(include="number").columns.to_list()
    selected_col=st.selectbox("What column do you want to choose?",num_col, key='1')
    st.header(f"{selected_col} - Statistics")
    col1= data[selected_col].nunique()
    col2= data[selected_col].isna().sum()
    col3=data[selected_col].eq(0).sum()
    col4=data[selected_col].lt(0).sum()
    col5= data[selected_col].mean()
    col6=data[selected_col].median()
    col7=np.sqrt(data[selected_col].var())
    col8=data[selected_col].min()
    col9=data[selected_col].max()
    col10= skew(data[selected_col],axis=0)
    col11=kurtosis(data[selected_col],axis=0)
    col12=data[selected_col].quantile(0.25)
    col13=data[selected_col].quantile(0.75)
    col14=out(data[selected_col])
    dict={"No.of Unique Values":col1,"No.of Rows with Missing Values": col2,"No.of Rows with 0": col3,"No.of Rows with negative Values": col4,"Average Value": col5,"Median": col6,"Min Value": col8,"Max Value": col9,"Sd":col7,"Skewness":col10,"Kurtosis":col11,"25th Quantile":col12,"75 th Quantile":col13,"outliers_no":col14}
    info_df=pd.DataFrame(list(dict.items()), columns=["description", "Value"])
    AgGrid(info_df)
    st.header("Histogram")
    chart, chart_spec_json = get_altair_chart(data1, chart_type="Histogram", xValues=selected_col) 
    st.altair_chart(chart)
    # save_df_to_pdf(dataframe1=info_df, filename='Numeric_Features.pdf', altair_chart1=chart)
    save_df_to_pdf(filename='Numeric_Features',dataframe1=info_df, altair_chart1=chart, df_headings=[f"{selected_col} - Statistics"], altair_headings=["Histogram", None, None])

def tab3_func(data):
    st.header("Categorical Features Exploring")  
    cat_fea=data.select_dtypes(include='object').columns.to_list()
    if len(cat_fea) == 0:
        st.warning("⚠️ This dataset has no categorical features to analyze.")
        st.info("💡 Categorical features are text-based columns like names, categories, labels, etc.")
        return 
    selected_cat=st.selectbox("Choose a categorical feature",cat_fea, key='2')
    cat_col={}
    cat_col["No.of unique values"]=data[selected_cat].nunique()  ####
    cat_col["No.of Rows with missing values"]= data[selected_cat].isna().sum()
    cat_col["No.of Empty Rows"]=data[selected_cat].eq("").sum()
    cat_col["No. of Rows with only whitespaces"]=data[selected_cat].str.isspace().sum()
    cat_col["No.of rows with uppercases"]=data[selected_cat].str.isupper().sum()
    cat_col["No. of Rows with Alphabets"]=data[selected_cat].str.isalpha().sum()
    cat_col["No.of Rows with only digits"]=data[selected_cat].str.isdigit().sum()
    cat_df=pd.DataFrame(list(cat_col.items()),columns=["Description","Values"])
    st.table(cat_df)
    st.header("Unique Categories in the selected Column")
    df=pd.DataFrame(list(data[selected_cat].unique()),columns=["Unique Categories"])
    st.table(df)
    chart, chart_spec_json = get_altair_chart(data, chart_type="Bar", xValues=selected_cat, yValues=None, colourValues=None)   
    chart_spec =  chart.to_json(format="vega")
    st.altair_chart(chart, use_container_width=True)
    save_df_to_pdf(filename='Categorical_Features.pdf', dataframe1=cat_df, dataframe2=df, altair_chart1=chart, df_headings=["Categorical Features Exploring", "Unique Categories in the selected Column"], altair_headings=["Bar Chart", None, None])

def tab4_func(data):
    st.header("Data is as follows:")
    st.markdown("""
    <style>
        .ag-theme-alpine {
            height: auto !important;
            max-height: none !important;
        }
    </style>
""", unsafe_allow_html=True)
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_grid_options(domLayout='autoHeight')
    gridOptions2 = gb.build()
    AgGrid(data, gridOptions= gridOptions2)
    num_col=data.select_dtypes(include=['number']).columns.to_list()
    x=st.selectbox("Select a column to check its Distribution",num_col, key='3')
    test_stat= kstest(data[x],"norm",alternative='two-sided')
    # print(test_stat)
    st.write("p value is:",test_stat[1])
    if(round(test_stat[1],3)<=0.05):
        st.write("Datapoints are not Normally Distributed")
    else:
        st.write("Datapoints are Normally Distributed")
    fig = plt.figure(figsize=(5, 4))
    qq= probplot(data[x],dist='norm',plot=plt)
    fig = plt.gcf()
    # st.pyplot(plt.gcf())
    st.pyplot(fig)
    save_df_to_pdf(filename = 'Show_data.pdf', dataframe1=data, df_headings=["Dataset", None], plt_chart=fig, plt_headings="QQ Plot")

def tab5_func(data, data1):
    col_except_date= data.select_dtypes(exclude=['datetime','bool']).columns.to_list()
    x=st.selectbox("Select first column",col_except_date,key='4')
    with st.expander("See the type"):
        if(data.dtypes[x]=='int64'):
            st.write("Numerical Integer") 
        elif(data.dtypes[x]=='float'):
            st.write("Numerical Decimal Point")
        elif(data.dtypes[x]=='object'):
                st.write("Categorical")      
    y=st.selectbox("Select Second column",col_except_date,key='5')
    with st.expander("See the type"):
        if(data.dtypes[y]=='int64'):
            st.write("Numerical Integer") 
        elif(data.dtypes[y]=='float'):
            st.write("Numerical Decimal Point")
        elif(data.dtypes[y]=='object'):
                st.write("Categorical")                
    if (st.button("Show the Correlation")==True):
        if((data.dtypes[x]=='float' or data.dtypes[x]=='int64') and (data.dtypes[y]=='float' or data.dtypes[y]=='int64') ):
            # z=st.selectbox("Choose the type of correlation",['Pearson','Kendall','Spearman'])
            correlation_P = data[x].corr(data[y])
            st.write("The Pearson's correlation between x and y is",round(correlation_P,3))
            correlation_K = data[x].corr(data[y],method='kendall')
            st.write("The Kendall's correlation between x and y is",round(correlation_K,3))
            correlation_S = data[x].corr(data[y],method='spearman')
            st.write("The Spearman's correlation between x and y is",round(correlation_S,3))
            if (round(correlation_K,3)> 0.500):
                    st.write("Two columns are positively associated or correlated")
            else:
                    st.write("Two columns are negatively associated or correlated")     
            fig, ax = plt.subplots()
            chart, chart_spec_json = get_altair_chart(data1, chart_type="Scatter", xValues=x, yValues=y)   
            chart_spec =  chart.to_json(format="vega")
            st.altair_chart(chart, use_container_width=True)
            save_df_to_pdf(filename = 'Bivariate_Correlation.pdf', altair_chart1=chart, altair_headings=["Correlation Plot", None, None])

            
        # categorical vs numeric
        if (data.dtypes[x]=='object' and data.dtypes[y]=='float'):
            cat_col= data.groupby(data[x])[y].apply(list)
            # result_1= f_oneway(*cat_col)
            resultk_1=kruskal(*cat_col,nan_policy='omit')
            st.write("pvalue is for Kruskal Wallis test: ",round(resultk_1[1],4))
            if(round(resultk_1[1],4)<0.05):
                    st.write("Two columns are associated or correlated")
            else:
                    st.write("Two columns are not associated or correlated")
            chart, chart_spec_json = get_altair_chart(data1, chart_type="Boxplot", xValues=x, yValues=y)   
            chart_spec =  chart.to_json(format="vega")
            st.altair_chart(chart, use_container_width=True)
            save_df_to_pdf(filename = 'Bivariate_correlation.pdf', altair_chart1=chart, altair_headings=["Box Plot", None, None])


        elif(data.dtypes[x]=='float' and data.dtypes[y]=='object'):
                cat_col= data.groupby(data[y])[x].apply(list)
            #  result_2= f_oneway(*cat_col)
                resultk_2=kruskal(*cat_col,nan_policy='omit')
            #  st.write("pvalue is: ",round(result_2[1],4)) 
                st.write("pvalue is for Kruskal Wallis test: ",round(resultk_2[1],4))
                if(round(resultk_2[1],4)<0.05):
                    st.write("Two columns are associated or correlated")
                else:
                    st.write("Two columns are not associated or correlated")
                chart, chart_spec_json = get_altair_chart(data1, chart_type="Boxplot", xValues=x, yValues=y)   
                chart_spec =  chart.to_json(format="vega")
                st.altair_chart(chart, use_container_width=True)
                save_df_to_pdf(filename = 'Bivariate_Correlation.pdf', altair_chart1=chart, altair_headings=["Box Plot", None, None])
            
        if(data.dtypes[x]=='object' and data.dtypes[y]=='object'):
                chisqr= pd.crosstab(data[x],data[y],margins=True)
                stat,p,df= chi2_contingency(chisqr)[0:3] 
                st.write("P-value is :",p)
                if(p<=0.05):
                    st.write("Two columns are associated or correlated")
                else:
                    st.write("Two columns are not associated or correlated") 

        return chart        #this chart is basically the correlation, and the various plots are dependent on the types of columns    

def tab6_func(data):
    mul_corr_p= data.corr(numeric_only=True)
    st.write("Pearson's Correlation Coefficients")
    heatmap_p = px.imshow(mul_corr_p,text_auto=True,
                          aspect="auto",color_continuous_scale='RdBu_r')
    heatmap_p.update_layout(
    # Enable modebar buttons including fullscreen
    modebar=dict(
        orientation='v',
        bgcolor='rgba(0,0,0,0)',
    )
)
# Update traces for better text visibility
    heatmap_p.update_traces(
        texttemplate='%{z:.2f}'  # Format correlation values to 2 decimal places
    ) 
    
    st.plotly_chart(heatmap_p,
                        use_container_width=True,
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['toggleSpikelines'],
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': 'pearson_correlation',
                                'height': 1000,
                                'width': 1000,
                                'scale': 2
                            }
                        })
    
    st.write("Kendall's Correlation Coefficients")
    mul_corr_k= data.corr(method='kendall',numeric_only=True)
    heatmap_k= px.imshow(mul_corr_k,text_auto=True, 
                         aspect="auto",color_continuous_scale='RdBu_r') 
    heatmap_k.update_layout(
    # Enable modebar buttons including fullscreen
    modebar=dict(
        orientation='v',
        bgcolor='rgba(0,0,0,0)',
    )
)
# Update traces for better text visibility
    heatmap_k.update_traces(
        texttemplate='%{z:.2f}'  # Format correlation values to 2 decimal places
    ) 
    
    st.plotly_chart(heatmap_k) 

    st.write("Spearman's Correlation Coefficients")
    mul_corr_s= data.corr(method='spearman',numeric_only=True)
    heatmap_s= px.imshow(mul_corr_s,text_auto=True, aspect="auto",color_continuous_scale='RdBu_r') 
    heatmap_s.update_layout(
    # Enable modebar buttons including fullscreen
    modebar=dict(
        orientation='v',
        bgcolor='rgba(0,0,0,0)',
    )
)
# Update traces for better text visibility
    heatmap_s.update_traces(
        texttemplate='%{z:.2f}'  # Format correlation values to 2 decimal places
    ) 
    
    st.plotly_chart(heatmap_s) 
    st.write(type(mul_corr_p).__name__)
    st.write(mul_corr_p)
    mul_corr_p_melted = mul_corr_p.reset_index().melt(id_vars='index')
    mul_corr_p_melted.columns = ['x', 'y', 'Correlation']
    mul_corr_p_melted['Correlation'] = mul_corr_p_melted['Correlation'].round(7)

def tab7_func(data, data1):
    tab71,tab72,tab73=st.tabs(["Basic Clusters","PCA Clusters","Cluster Using 2 Feature"])
    le = LabelEncoder()
    num_col=data.select_dtypes(include="number").columns.to_list()
    num_col_df=data.select_dtypes(include=['number','object'])
    for i in num_col_df.columns:
            for j in num_col:
                if(j==i):
                    num_col_df[i]=num_col_df[i].fillna(num_col_df[i].mean())
            if((num_col_df[i].nunique())<=10):
                num_col_df[i]=le.fit_transform(num_col_df[i])
    num_col_df=num_col_df.select_dtypes(include='number')
            
    with tab71:
        st.title("Basic Clustering") 
        # #  elbow method determining k
        data_norm= preprocessing.normalize(num_col_df)
        wcss_list=[]
        silhouette_avg=[]
        max_sil=-2
        num_clusters=0

        for k in range(2,11):
            cluster_model=KMeans(n_clusters=k,init='k-means++',random_state=42)
            cluster_model.fit_predict(data_norm)
            wcss_list.append(cluster_model.inertia_)
            silhouette_avg.append(silhouette_score(data_norm,cluster_model.labels_))
            for i in range(0,len(silhouette_avg)):
                if(silhouette_avg[i]>max_sil):
                    max_sil=silhouette_avg[i]
                    num_clusters=k
        #scatter_cluster=px.line(x=range(2,11),y=wcss_list,markers=True,title='Elbow Method')
        #st.plotly_chart(scatter_cluster)
        df_wccs = pd.DataFrame({
             'x': [i for i in range(2, 11)],
             'y': wcss_list
             })
        df_silhouette = pd.DataFrame({
                'x': [i for i in range(2, 11)],
                'y': silhouette_avg
                })
        st.write("WCSS vs Number of clusters")
        chart1, chart_spec_json = get_altair_chart(df_wccs, chart_type="Line", xValues='x', yValues='y', linepoint=True)   
        chart_spec =  chart1.to_json(format="vega")
        st.altair_chart(chart1, use_container_width=True)
        st.write("Silhouette Score vs Number of clusters")
        chart2, chart_spec_json = get_altair_chart(df_silhouette, chart_type="Line", xValues='x', yValues='y', linepoint=True)   
        chart_spec =  chart2.to_json(format="vega")
        st.altair_chart(chart2, use_container_width=True)
        
        st.write("Our suggested value of optimal number of clusters is",num_clusters)
        val_k=st.selectbox("Choose the number of clusters to be formed",range(num_clusters,11),key='6')
        fin_cluster_model=KMeans(n_clusters=val_k,init='k-means++',random_state=42)
        fin_fit=fin_cluster_model.fit_predict(data_norm)
        num_col_df['Clusters']=fin_cluster_model.labels_
        num_col_df['Clusters']=num_col_df['Clusters'].astype(str)
        st.subheader(f"Count of Samples in each of {val_k} clusters")
        chart3, chart_spec_json = get_altair_chart(num_col_df, chart_type="Bar", xValues='Clusters', colourValues='Clusters')   
        chart_spec =  chart3.to_json(format="vega")
        st.altair_chart(chart3, use_container_width=True)

        sil=silhouette_score(data_norm,fin_cluster_model.labels_)
        see_3=st.button("See the Silhouette Score without PCA")
        if (see_3==True):
            st.write("The  Silhoutte score is ",round(sil,3))
        save_df_to_pdf(filename = 'Basic_Clusters.pdf', altair_chart1=chart1, altair_chart2=chart2, altair_chart3=chart3, altair_headings=["Chart1", "Chart2", "Count of Samples in each of 2 clusters"])
        
    with tab72:
        st.title("PCA Clusters")
        standardized_data=StandardScaler().fit_transform(num_col_df)
        pca= PCA()
        pca.fit(standardized_data)
        pca=PCA(n_components=2)
        pca.fit(standardized_data)
        reduced_data=pca.transform(standardized_data)
        silhouette_avg_pca=[]
        max_sil_pca=-2
        num_clusters_pca=0
        wcss_list_pca=[]
        for k_pca in range(2,11):
    #   max_sil.append(-2)
            cluster_model_pca=KMeans(n_clusters=k_pca,init='k-means++',random_state=42)
            cluster_model_pca.fit_predict(reduced_data)
            wcss_list_pca.append(cluster_model_pca.inertia_)
            silhouette_avg_pca.append(silhouette_score(reduced_data,cluster_model_pca.labels_))
        #   print(silhouette_avg)
        for i in range(0,len(silhouette_avg_pca)):
            if(silhouette_avg_pca[i]>max_sil_pca):
                max_sil_pca=silhouette_avg_pca[i]
                num_clusters_pca=k_pca

        df_cluster_pca = pd.DataFrame(
                {
                    'x': [i for i in range(2, 11)],
                    'y': wcss_list_pca
                }
        )
        df_silhouette_avg_pca = pd.DataFrame(
                {
                    'x': [i for i in range(2, 11)],
                    'y': silhouette_avg_pca
                }
        )

        chart1, chart_spec_json = get_altair_chart(df_cluster_pca, chart_type="Line", xValues='x', yValues='y', linepoint=True)   
        chart_spec =  chart1.to_json(format="vega")
        st.altair_chart(chart1, use_container_width=True)

        chart2, chart_spec_json = get_altair_chart(df_silhouette_avg_pca, chart_type="Line", xValues='x', yValues='y', linepoint=True)   
        chart_spec =  chart2.to_json(format="vega")
        st.altair_chart(chart2, use_container_width=True)
        
        st.write("Our suggested value of optimal number of clusters is ",num_clusters_pca)
        val_k_pca=st.selectbox("Choose the number of clusters to be formed",range(num_clusters_pca,11),key='7')
        fin_cluster_model_pca=KMeans(n_clusters=val_k_pca,init='k-means++',random_state=42)
        fin_cluster_model_pca.fit_predict(reduced_data)
        num_col_df['Cluster_pca']=fin_cluster_model_pca.labels_
        pca_kmeans_dataframe=pd.concat([num_col_df.reset_index(drop=True),pd.DataFrame(reduced_data)],axis=1)
        pca_kmeans_dataframe.columns.values[-2:]=['Component 1','Component 2']
        st.write(pca_kmeans_dataframe.drop(['Clusters'],axis=1))
        chart3, chart_spec_json = get_altair_chart(pca_kmeans_dataframe, chart_type="Scatter", xValues='Component 1', yValues='Component 2',colourValues='Cluster_pca', color_scheme='viridis')   
        chart_spec =  chart3.to_json(format="vega")
        st.altair_chart(chart3, use_container_width=True)

        fin_silhouette_avg= silhouette_score(reduced_data,fin_cluster_model_pca.labels_)
        see=st.button("See the Silhouette Score with PCA")
        if (see==True):
            st.write("The  Silhoutte score is ",round(fin_silhouette_avg,3))

        save_df_to_pdf(filename = 'PCA_Clusters.pdf', dataframe1 = pca_kmeans_dataframe,altair_chart1=chart1, altair_chart2=chart2, altair_chart3=chart3, altair_headings=["Chart1", "Chart2", "Scatter Plot"])
        
    with tab73:
        Feature_1=st.selectbox("Choose any column",num_col_df.drop(['Clusters','Cluster_pca'],axis=1).columns, key='8')
        Feature_2=st.selectbox("Choose any column",num_col_df.drop(['Clusters','Cluster_pca',Feature_1],axis=1).columns, key='9')
        data_2_fea=pd.DataFrame({f"{Feature_1}": num_col_df[Feature_1],f"{Feature_2} ":num_col_df[Feature_2]})
    #  st.dataframe(data_2_fea)
        norm_data_2_fea=StandardScaler().fit_transform(data_2_fea)
        wcss_2=[]
        silhouette_avg_2=[]
        max_sil_2=-2
        num_clusters_2=0
        for i in range(2,11):
            model_2_fea=KMeans(n_clusters=i,init='k-means++',random_state=42)
            model_2_fea.fit_predict(norm_data_2_fea)
            wcss_2.append(model_2_fea.inertia_)
            silhouette_avg_2.append(silhouette_score(norm_data_2_fea, model_2_fea.labels_))
    #   print(silhouette_avg)
            for j in range(0,len(silhouette_avg_2)):
                if(silhouette_avg_2[j]>max_sil_2):
                    max_sil_2=silhouette_avg_2[j]
                    num_clusters_2=i
        
        df_cluster2 = pd.DataFrame(
                {
                    'x': [i for i in range(2, 11)],
                    'y': wcss_2
                }
        )
        df_silhouette_k2 = pd.DataFrame(
                {
                    'x': [i for i in range(2, 11)],
                    'y': silhouette_avg_2
                }
        )

        chart1, chart_spec_json = get_altair_chart(df_cluster2, chart_type="Line", xValues='x', yValues='y', linepoint=True)   
        chart_spec =  chart1.to_json(format="vega")
        st.altair_chart(chart1, use_container_width=True)

        chart2, chart_spec_json = get_altair_chart(df_silhouette_k2, chart_type="Line", xValues='x', yValues='y', linepoint=True)   
        chart_spec =  chart2.to_json(format="vega")
        st.altair_chart(chart2, use_container_width=True)


        st.write("Our suggested value of optimal number of clusters is ",num_clusters_2)
        val_k_2=st.selectbox("Choose number of clusters",range(num_clusters_2,11),key='10')
        model_2_fea=KMeans(n_clusters=val_k_2,init='k-means++',random_state=42)
        model_2_fea.fit_predict(norm_data_2_fea)
        sil_2=silhouette_score(norm_data_2_fea,model_2_fea.labels_)
        num_col_df['model2_feature_labels'] = model_2_fea.labels_
        chart3, chart_spec_json = get_altair_chart(num_col_df, chart_type="Scatter", xValues=Feature_1, yValues=Feature_2,colourValues='model2_feature_labels', color_scheme='viridis')   
        chart_spec =  chart3.to_json(format="vega")
        st.altair_chart(chart3, use_container_width=True)

        see_2=st.button("See the Silhouette Score For 2 feature clustering")
        if (see_2==True):
            st.write("The  Silhoutte score is ",round(sil_2,3))  
        save_df_to_pdf(filename = 'Cluster_2_Features.pdf', altair_chart1=chart1, altair_chart2=chart2, altair_chart3=chart3)

    
def tab8_func(data):
    if isinstance(data, pd.DataFrame):
        uploaded_file = data
    else:
        # If data is a filename string
        uploaded_file = db.load_df_from_parquet(data)    
    if uploaded_file is not None:
        # Display head of the CSV file
        st.subheader("CSV File Preview")
        df_preview = uploaded_file
        st.write(df_preview.head())
        values = st.slider("Select a range of row indeces", 0, df_preview.shape[0]+1, (25, 75))

        df = df_preview.copy().iloc[values[0]:values[1]]
        df = preprocess_columns(df)  # Preprocess column names

        # Select the main column for the knowledge graph
        st.subheader("Select the main column for the knowledge graph")
        main_column = st.radio("Main Column", df.columns)

        # Generate Turtle data
        ttl_data = convert_to_ttl(df, main_column)

        button1 = st.button("Download .ttl File")
        button2 = st.button("Visualize Graph")
                
        if button1:
            st.markdown(get_binary_file_downloader_html(ttl_data.serialize(format="turtle"), 'output.ttl'), unsafe_allow_html=True)
        elif button2:
            st.write("Use your mouse to interact with the graph")
            vis_graph(ttl_data, df.columns, main_column)
        else:
            st.warning("Please select a button!")
        st.subheader("Run SPARQL Query")
        query_input = st_ace(
            language="sparql",
            theme="monokai",
            height="300px",
            key="sparql_query_input",
        )
        if st.button("Run Query"):
            if query_input:
                try:
                    results = run_query(ttl_data, query_input)
                    st.subheader("Query Results")
                    st.markdown(get_binary_file_downloader_html(results, 'query_results.txt'), unsafe_allow_html=True)
                    st.write(results)
                except Exception as e:
                    st.error(f"Error executing the query: {e}")
            else:
                st.warning("Please enter a valid SPARQL query.")         