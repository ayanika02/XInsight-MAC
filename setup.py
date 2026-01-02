

from setuptools import setup
import os 
HERE = os.path.abspath(os.path.dirname(__file__))
APP = [os.path.join(HERE, 'XINSIGHT_Application', 'run_app.py')]
ICON_PATH = os.path.join(HERE, 'IDEAS-TIH.icns')

# xinsight_files = []
# xinsight_dir = os.path.join(HERE, 'XINSIGHT_Application')
# for file in os.listdir(xinsight_dir):
#     if file.endswith('.py'):
#         xinsight_files.append(os.path.join(xinsight_dir, file))

streamlit_config_files = []
streamlit_config_path = os.path.join('XINSIGHT_Application', '.streamlit')
if os.path.exists(streamlit_config_path):
    streamlit_config_files = [
        (os.path.join('XINSIGHT_Application', '.streamlit'), [
            os.path.join(streamlit_config_path, f)
            for f in os.listdir(streamlit_config_path)
            if f.endswith('.toml')
        ])
    ]
    print(f"✓ Found Streamlit config files: {os.listdir(streamlit_config_path)}")
else:
    print("WARNING: .streamlit config folder not found")


DATA_FILES = [('', [
        'altair_chart.html', # 'xinsight_small.gif','splash_screen.html', 'requirements.txt',
        'IDEAS-TIH.icns', 'IDEAS-TIH.webp', 'graph.html', 
    ]),
    ('XINSIGHT_Application', [os.path.join('XINSIGHT_Application', f)
                              for f in os.listdir('XINSIGHT_Application')
                              if f.endswith('.py')]),
        *streamlit_config_files,
    ]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': ICON_PATH, # Optional: specify an application icon
    'plist': {
        'CFBundleName': 'XInsight',
        'CFBundleDisplayName': 'XInsight',
        'CFBundleIdentifier': 'com.ideas-tih.xinsight',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 IDEAS-TIH',
    },
    #'packages': ['XINSIGHT_Application'], # If your modules are in a package
    'packages': [ 'XINSIGHT_Application', 'streamlit_antd_components'],
    'includes': ['altair', 'altgraph', 'appnope', 'asttokens', 'attrs', 'beautifulsoup4', 'blinker', 'cachetools', 
        'certifi', 'chardet', 'charset_normalizer', 'circlify', 'click', 'cmdstanpy', 'colorama', 'colour',
        'comm', 'contourpy', 'cycler', 'debugpy', 'decorator', 'distlib', 'dtreeviz', 'duckdb', 'entrypoints', 
        'et_xmlfile', 'executing', 'Faker', 'favicon', 'fonttools', 'fsspec', 'gitdb', 'GitPython', 'graphviz', 
        'holidays', 'htbuilder', 'idna', 'importlib_metadata', 'importlib_resources', 'iniconfig', 'ipykernel', 'ipython', 
        'isodate', 'jedi', 'Jinja2', 'joblib', 'jsonpickle', 'jsonschema', 'jsonschema_specifications', 'jupyter_client', 
        'jupyter_core', 'kiwisolver', 'lightgbm', 'lxml', 'macholib', 'Markdown', 'markdown_it_py', 'markdownlit', 
        'matplotlib', 'matplotlib_inline', 'mdurl', 'modulegraph', 'more_itertools', 'nest_asyncio', 'networkx', 'numpy', 'onnx', 
        'openpyxl', 'packaging', 'pandas', 'parso', 'patsy', 'pefile', 'pexpect', 'pillow', 'platformdirs', 'plotly', 'pluggy', 
        'prometheus_client', 'prompt_toolkit', 'prophet', 'protobuf', 'psutil', 'ptyprocess', 'pure_eval', 'py2app', 'pyarrow', 
        'pydeck', 'Pygments', 'pymdown_extensions', 'pynsist', 'pyparsing', 'pytest', 'python_dateutil', 'python_decouple', 'pytz', 
        'pyvis', 'pywin32_ctypes', 'PyYAML', 'pyzmq', 'rdflib', 'referencing', 'reportlab', 'requests', 'requests_download', 'rich', 
        'rpds_py', 'scikit_learn', 'scipy', 'seaborn', 'six', 'smmap', 'soupsieve', 'st_annotated_text', 'stack_data', 'stanio', 'statsmodels', 
        'streamlit', 'streamlit_ace', 'streamlit_aggrid', 'streamlit_antd_components', 'streamlit_camera_input_live', 'streamlit_card', 
        'streamlit_embedcode', 'streamlit_extras', 'streamlit_faker', 'streamlit_image_oordinates', 'streamlit_keyup', 'streamlit_option_menu', 
        'streamlit_toggle_switch', 'streamlit_vertical_slider', 'tenacity', 'threadpoolctl', 'toml', 'toolz', 'tornado', 'tqdm', 'traitlets', 
        'typing_extensions', 'tzdata', 'tzlocal', 'urllib3', 'validators', 'vega_datasets', 'vegafusion', 'vegafusion_python_embed', 'vl_convert_python', 
        'watchdog', 'wcwidth', 'xgboost', 'yarg', 'zipp'],
        'site_packages': True,
}

setup(
    name = 'XInsight',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# from setuptools import setup
# import os
# import sys
# import importlib.util

# HERE = os.path.abspath(os.path.dirname(__file__))
# # Entry point: run_app.py launches the Streamlit server
# APP = [os.path.join(HERE, 'XINSIGHT_Application', 'run_app.py')]
# ICON_PATH = os.path.join(HERE, 'IDEAS-TIH.icns')

# def get_path(pkg_name):
#     spec = importlib.util.find_spec(pkg_name)
#     return os.path.dirname(spec.origin) if spec else None

# def collect_assets():
#     # 1. Base files
#     data_files = [('', ['altair_chart.html', 'IDEAS-TIH.icns', 'IDEAS-TIH.webp', 'graph.html'])]
    
#     # 2. Your Application Logic
#     app_dir = os.path.join(HERE, 'XINSIGHT_Application')
#     for root, dirs, files in os.walk(app_dir):
#         rel_path = os.path.relpath(root, HERE)
#         file_list = [os.path.join(rel_path, f) for f in files if f.endswith(('.py', '.toml', '.json'))]
#         if file_list:
#             data_files.append((rel_path, file_list))

#     # 3. Streamlit Component Assets (JS/CSS)
#     # These are the ones that cause "RuntimeError" if you try to import them normally
#     components = [
#         'streamlit', 'streamlit_antd_components', 'st_aggrid', 'streamlit_extras',
#         'streamlit_option_menu', 'st_keyup', 'annotated_text', 'streamlit_card'
#     ]
    
#     for pkg in components:
#         root = get_path(pkg)
#         if root:
#             for dirpath, _, filenames in os.walk(root):
#                 # Grab anything in frontend/dist/static folders
#                 if any(x in dirpath for x in ['frontend', 'static', 'dist', 'component']):
#                     rel_path = os.path.relpath(dirpath, os.path.dirname(root))
#                     files = [os.path.join(dirpath, f) for f in filenames if '.' in f]
#                     data_files.append((rel_path, files))
#     return data_files

# OPTIONS = {
#     'argv_emulation': False,
#     'iconfile': ICON_PATH,
#     'packages': [
#         'streamlit', 'streamlit_antd_components', 'st_aggrid', 'streamlit_extras',
#         'streamlit_option_menu', 'st_keyup', 'annotated_text', 'pandas', 'numpy', 
#         'altair', 'prophet', 'xgboost', 'lightgbm', 'reportlab', 'PIL', 'bs4', 
#         'yaml', 'git', 'duckdb', 'watchdog', 'pyarrow'
#     ],
#     'includes': ['sh', 'six', 'python-dateutil', 'pytz'],
#     'plist': {
#         'CFBundleName': 'XInsight',
#         'CFBundleIdentifier': 'com.ideas-tih.xinsight',
#         'LSEnvironment': {'PYTHONPATH': '../Resources/lib/python3.11'},
#     },
# }

# setup(
#     app=APP,
#     data_files=collect_assets(),
#     options={'py2app': OPTIONS},
#     setup_requires=['py2app'],
# )