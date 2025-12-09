import db
import ingestion_gui
import insights
import measures_and_dimensions_gui
import charts_gui_v2
# import metric_gui
import time_series
import explain_gui

from typing import List
import streamlit_antd_components as sac
from streamlit_antd_components import TreeItem
import streamlit as st
import os
import pandas as pd
from streamlit_extras.grid import grid

def create_tree_data() -> List[TreeItem]:
    return [
        TreeItem('Ingestion', icon='database'),
        TreeItem('Insights', icon='bar-chart', children=[
            TreeItem('Data Info', icon='info-circle'),
            TreeItem('Numeric Features', icon='calculator'),
            TreeItem('Categorical Features', icon='tags'),
            TreeItem('Show Data', icon='table'),
            TreeItem('Bivariate-Correlation', icon='link'),
            TreeItem('Multivariate-Correlation', icon='share-alt'),
            TreeItem('Clustering', icon='cluster'),
            TreeItem('Knowledge Graph', icon='share-alt')
        ]),
        TreeItem('Storytelling', icon='book', children=[
            TreeItem('Measures and Dimensions', icon='table'),
            TreeItem('Charts', icon='histogram'),
            #TreeItem('Metrics', icon='bar-chart'),
            TreeItem('Time Series', icon='time-circle'),
           # TreeItem('Dashboards', icon='appstore')
        ]),
        TreeItem('Explain', icon='question-circle')
    ]

db.init_db()

logo_path = os.path.join(os.path.dirname(__file__), "IDEAS-TIH.webp")
st.set_page_config(page_title="IDEAS XInsight", layout="wide", page_icon=logo_path, initial_sidebar_state="expanded")


hide_streamlit_style = """
    <style>
    /* 1. Global Background Gradient - REMOVED to restore white background */
    /* .stApp {
        background-color: #8EC5FC;
        background-image: linear-gradient(62deg, #8EC5FC 0%, #E0C3FC 100%);
        font-family: 'Inter', sans-serif;
    } */


    /* 2. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255,255,255,0.5);
        box-shadow: 2px 0 15px rgba(0,0,0,0.05);
    }
    
    /* 3. Header & Text Styling */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* 4. Custom Button Styling */
    
    /* Delete Button (Red) - Targeting Primary Buttons */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(45deg, #ff5252, #f44336) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(244, 67, 54, 0.6) !important;
    }
    
    /* Download Button (Green) - Targeting Download Buttons */
    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(45deg, #43a047, #2e7d32) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(67, 160, 71, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(67, 160, 71, 0.6) !important;
    }
    
    /* General Button Styling */
    button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    /* 5. Container/Card Styling (Optional Polish) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.6);
    }
    
    </style>
    """

#     <style>
    
#     /* ============================================
#        HIDE STREAMLIT BRANDING & TOOLBAR
#        ============================================ */
#     #MainMenu {visibility: hidden !important;}
#     header[data-testid="stHeader"] {visibility: hidden !important;}
#     footer {visibility: hidden !important;}
    
#     [data-testid="stToolbar"] {display: none !important;}
#     [data-testid="stDecoration"] {display: none !important;}
#     [data-testid="stStatusWidget"] {display: none !important;}
#     .stDeployButton {display: none !important;}
#     button[kind="header"][data-testid="baseButton-header"] {display: none !important;}
    
#     /* Hide skeleton loading boxes */
#     [data-testid="stSkeleton"] {
#         display: none !important;
#         visibility: hidden !important;
#         opacity: 0 !important;
#         height: 0 !important;
#     }
    
#     /* ============================================
#        MAIN CONTENT LAYOUT
#        ============================================ */
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 0rem;
#         padding-left: 3rem;
#         padding-right: 3rem;
#         max-width: 100% !important;
#     }
    
#     /* Prevent header from being pushed by sidebar */
#     .main .block-container {
#         max-width: 100% !important;
#         padding-top: 1rem;
#     }
    
#     /* When sidebar is expanded, don't shift main content */
#     [data-testid="stSidebar"][aria-expanded="true"] ~ .main {
#         margin-left: 0 !important;
#     }
    
#     /* Ensure columns in header resize properly */
#     [data-testid="column"] > div {
#         overflow: visible !important;
#         min-width: 0 !important;
#     }
    
#     /* ============================================
#        RESPONSIVE TYPOGRAPHY
#        ============================================ */
#     h1, h2, h3 {
#         white-space: normal !important;
#         word-break: break-word !important;
#         line-height: 1.2 !important;
#     }
    
#     @media (max-width: 1400px) {
#         h1 {font-size: 2rem !important;}
#     }
    
#     @media (max-width: 1200px) {
#         h1 {font-size: 1.5rem !important;}
#     }
    
#     /* Theme-specific text colors */
#     [data-theme="dark"] h1,
#     [data-theme="dark"] h2,
#     [data-theme="dark"] h3 {
#         color: #ffffff !important;
#     }
    
#     [data-theme="light"] h1,
#     [data-theme="light"] h2,
#     [data-theme="light"] h3 {
#         color: #1e1e2e !important;
#     }
    
#     /* ============================================
#        SIDEBAR STYLING
#        ============================================ */
#     [data-testid="stSidebar"] {
#         background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
#         padding-top: 0rem !important;
#     }
    
#     [data-testid="stSidebar"] > div:first-child {
#         padding-top: 0rem;
#     }
    
#     /* Sidebar header */
#     [data-testid="stSidebar"] h1 {
#         color: #ffffff !important;
#         font-size: 1.5rem;
#         font-weight: 700;
#         padding: 1.5rem 1rem 1rem 1rem;
#         margin: 0;
#         border-bottom: 2px solid rgba(255, 255, 255, 0.1);
#         background: rgba(0, 0, 0, 0.2);
#     }
    
#     /* ============================================
#        TREE MENU STYLING
#        ============================================ */
#     [data-testid="stSidebar"] .ant-tree {
#         background: transparent !important;
#         color: #e0e0e0 !important;
#         padding: 0.5rem 0;
#     }
    
#     [data-testid="stSidebar"] .ant-tree-node-content-wrapper {
#         color: #e0e0e0 !important;
#         padding: 8px 12px;
#         border-radius: 6px;
#         transition: all 0.3s ease;        
#     }
    
#     [data-testid="stSidebar"] .ant-tree-node-content-wrapper:hover {
#         background: rgba(255, 75, 75, 0.15) !important;
#         color: #ffffff !important;
#     }
    
#     [data-testid="stSidebar"] .ant-tree-node-selected .ant-tree-node-content-wrapper {
#         background: linear-gradient(90deg, #ff4b4b 0%, #ff6b6b 100%) !important;
#         color: #ffffff !important;
#         font-weight: 600;
#         box-shadow: 0 2px 8px rgba(255, 75, 75, 0.3);
#     }
    
#     /* Tree icons */
#     [data-testid="stSidebar"] .ant-tree-icon {
#         color: #a0a0a0;
#         margin-right: 8px;
#     }
    
#     [data-testid="stSidebar"] .ant-tree-node-selected .ant-tree-icon {
#         color: #ffffff;
#     }
    
#     /* Tree lines */
#     [data-testid="stSidebar"] .ant-tree-indent-unit {
#         border-left: 1px solid rgba(255, 255, 255, 0.1);
#     }
    
#     /* ============================================
#        PERFORMANCE OPTIMIZATION
#        ============================================ */
#     /* Speed up rendering to minimize skeleton flash */
#     * {
#         -webkit-transition: none !important;
#         -moz-transition: none !important;
#         -o-transition: none !important;
#         transition: none !important;
#     }
    
#     /* Re-enable transitions for interactive elements */
#     [data-testid="stSidebar"] .ant-tree-node-content-wrapper,
#     button {
#         transition: all 0.3s ease !important;
#     }
#     </style>
# """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if st.session_state.get('uploaded_file') is None:
    st.session_state['uploaded_file'] = None
if st.session_state.get('uploaded_file_name') is None:
    st.session_state['uploaded_file_name'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Ingestion'

# Header using columns (better than grid for sidebar compatibility)
header_cols = st.columns([1, 10])

with header_cols[0]:
    # script_path = os.path.join(os.path.dirname(__file__), "IDEAS-TIH.webp")
    # if os.path.exists(script_path):
    #     st.image(script_path, width=80)
    # else:
    #     st.markdown("# 🎓")
    st.markdown("")

with header_cols[1]:
    # st.markdown("""
    #     <h1 style="margin: 0; padding-top: 2rem; font-size: 2.5rem; font-weight: 700;">
    #         IDEAS XInsight - Explainable Visual Insights
    #     </h1>
    # """, unsafe_allow_html=True)
    script_path = os.path.join(os.path.dirname(__file__), "IDEAS-TIH.webp")
    st.markdown("""<div style="display: flex; margin-bottom: 20px; justify-content: center; width: 100%;">
    <div style="display:grid; grid-template-columns: auto 1fr; align-items: center; gap: 20px; max-width: 800px;">
        <div>
            <img src="https://static.wixstatic.com/media/5e79ca_dce5c923992f41fa81d8465041fe5163~mv2.png/v1/fill/w_109,h_107,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/IDEAS-TIH%2C%20ISI%2C%20Kolkata.png" width="100" height="100">
        </div>
        <div style="display: flex; flex-direction: column; justify-content: center;">
            <i>
            <p style="margin:0; color: blue; padding:0.5rem 0.75rem; font-size:0.8rem; font-weight:400; background:white; border-radius:15px; display:inline-block; position:relative; box-shadow: 3px 3px 6px #b8b9be, -3px -3px 6px #ffffff; margin-bottom: 5px; max-width: fit-content;">
                <span style="content:''; position:absolute; width:10px; height:10px; background:white; border-radius:50%; left:-10px; bottom:-4px; box-shadow: 3px 3px 6px #b8b9be, -3px -3px 6px #ffffff;"></span>
                <span style="content:''; position:absolute; width:7px; height:7px; background:white; border-radius:50%; left:-18px; bottom:-9px; box-shadow: 3px 3px 6px #b8b9be, -3px -3px 6px #ffffff;"></span>
                Explainable Visual Insights
            </p>
            </i>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;"> IDEAS XInsight </h1>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Create grid for body and footer only
my_grid = grid(1, 1, vertical_align="top")

# Row 1 - Main Content Body
body = my_grid.container(border=True, height=700)
# Sidebar with tree menu
with st.sidebar:
    st.markdown("# Navigation")
    
    selected_page_key = sac.tree(
        items=create_tree_data(),
        label='',
        index=0,
        format_func='title',
        icon='default',
        show_line=False,
        open_all=True,
        checkbox=False,
        return_index=False,
        key='antd_menu_nav'
    )
    
    # Update session state
    if selected_page_key:
        if 'last_tree_selection' not in st.session_state:
            st.session_state['last_tree_selection'] = selected_page_key
            st.session_state['current_page'] = selected_page_key
        elif selected_page_key != st.session_state['last_tree_selection']:
            st.session_state['last_tree_selection'] = selected_page_key
            st.session_state['current_page'] = selected_page_key
    
    # Sidebar footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #a0a0a0; font-size: 0.8rem; padding: 1rem;">
            <p>Click items to navigate</p>
            <p style="margin-top: 0.5rem;">© IDEAS-TIH 2025</p>
        </div>
    """, unsafe_allow_html=True)

INSIGHTS_TABS = ['Data Info', 'Numeric Features', 'Categorical Features', 'Show Data',
                 'Bivariate-Correlation', 'Multivariate-Correlation', 'Clustering', 'Knowledge Graph']

STORYTELLING_TABS = ['Measures and Dimensions', 'Charts', 'Time Series'] #'Metrics','Dashboards']

# Render content inside the grid body container
with body:
    current_page = st.session_state.get('current_page', 'Ingestion')
    
    # Content breadcrumb
    if current_page in INSIGHTS_TABS:
        st.markdown(f"### Insights › {current_page}")
    elif current_page in STORYTELLING_TABS:
        st.markdown(f"### Storytelling › {current_page}")
    elif current_page == 'Ingestion':
        st.markdown("### Data Ingestion")
    elif current_page == 'Explain':
        st.markdown("### Explain")

    st.markdown("---")
    
    # Render content based on selection
    if current_page == 'Ingestion':
        ingestion_gui.ingestion_gui()

    elif current_page in INSIGHTS_TABS or current_page == 'Insights':
        if current_page == 'Insights':
            current_page = 'Data Info'
            st.session_state['current_page'] = current_page
        
        dataset_df = db.get_datasets()
        dataset_file_name = st.selectbox('Select a dataset', dataset_df['file_name'].tolist(),
                                        index=None, placeholder="Select a dataset...")
        
        if dataset_file_name:
            try:
                data, data1 = insights.load_data(dataset_file_name)
                
                if current_page == 'Data Info':
                    insights.tab1_func(data)
                elif current_page == 'Numeric Features':
                    insights.tab2_func(data, data1)
                elif current_page == 'Categorical Features':
                    insights.tab3_func(data)
                elif current_page == 'Show Data':
                    insights.tab4_func(data)
                elif current_page == 'Bivariate-Correlation':
                    insights.tab5_func(data, data1)
                elif current_page == 'Multivariate-Correlation':
                    insights.tab6_func(data)
                elif current_page == 'Clustering':
                    insights.tab7_func(data, data1)
                elif current_page == 'Knowledge Graph':
                    insights.tab8_func(data)
                        
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                with st.expander("See full traceback"):
                    st.exception(e)

    elif current_page in STORYTELLING_TABS or current_page == 'Storytelling':
        if current_page == 'Storytelling':
            current_page = 'Measures and Dimensions'
            st.session_state['current_page'] = current_page
        
        dataset_df = db.get_datasets()
        dataset_file_name = st.selectbox('Select a dataset', dataset_df['file_name'].tolist(),
                                        index=None, placeholder="Select a dataset...")
        
        if dataset_file_name:
            if current_page == 'Measures and Dimensions':
                measures_and_dimensions_gui.show_measures_and_dimensions(dataset_file_name)
            elif current_page == 'Charts':
                charts_gui_v2.show_charts(dataset_file_name)
            # elif current_page == 'Metrics':
            #     metric_gui.show_metrics(dataset_file_name)
            elif current_page == 'Time Series':
                time_series.time_series_forecasting(dataset_file_name)
            # elif current_page == 'Dashboards':
            #     st.write('Dashboard: Work in progress...')

    elif current_page == 'Explain':
        explain_gui.explain_gui()

# Row 2 - Footer
my_grid.markdown("<h3 style='text-align: center; color: #666; padding: 1rem 0;'>©IDEAS-TIH</h3>", unsafe_allow_html=True)