import pandas as pd
import duckdb
import streamlit as st
import os


connection = None

def init_db():
    if 'connection' not in st.session_state:
        connection = duckdb.connect("xinsight_db.db")
        st.session_state['connection'] = connection
        connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_dataset_id" START 1')
        connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_dimension_or_mesaure_id" START 1')
        connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_chart_id" START 1')  # New sequence for chart IDs
        connection.execute('CREATE SEQUENCE IF NOT EXISTS "seq_metric_id" START 1')
        connection.execute("CREATE TABLE IF NOT EXISTS datasets (dataset_id integer primary key default nextval('seq_dataset_id'), file_name varchar(1000) unique, mime_type varchar(100), file_size integer, date_created datetime)") #, file blob)")
        connection.execute("CREATE TABLE IF NOT EXISTS measures_and_dimensions (m_or_d_id  integer primary key default nextval('seq_dimension_or_mesaure_id'), column_name varchar(1000), m_or_d_type char(1), dataset_id integer, date_created datetime, FOREIGN KEY (dataset_id) REFERENCES datasets (dataset_id))") #, file blob)")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS charts (
                chart_id INTEGER PRIMARY KEY DEFAULT nextval('seq_chart_id'),
                chart_name VARCHAR(1000),
                x_column VARCHAR(1000),
                y_column VARCHAR(1000),
                color_column VARCHAR(1000),
                chart_type VARCHAR(1000),
                aggregation VARCHAR(100), 
                dataset_id INTEGER, 
                chart_specs JSON, 
                date_created DATETIME, 
                FOREIGN KEY (dataset_id) REFERENCES datasets (dataset_id)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS metric (
                           metric_id INTEGER PRIMARY KEY default nextval('seq_metric_id'),
                           metric_name VARCHAR(1000),
                           metric_measure_name VARCHAR(1000), 
                           metric_dimension_name1 VARCHAR(1000), 
                           metric_dimension_name2 VARCHAR(1000), 
                           metric_dimension_name3 VARCHAR(1000), 
                           m_or_d_id_1 INTEGER, 
                           m_or_d_id_2 INTEGER, 
                           m_or_d_id_3 INTEGER,
                           m_or_d_id_4 INTEGER, 
                           dataset_id INTEGER, 
                           date_created DATETIME, 
                           FOREIGN KEY (m_or_d_id_1) REFERENCES measures_and_dimensions (m_or_d_id),
                           FOREIGN KEY (m_or_d_id_2) REFERENCES measures_and_dimensions (m_or_d_id),
                           FOREIGN KEY (m_or_d_id_3) REFERENCES measures_and_dimensions (m_or_d_id),
                           FOREIGN KEY (m_or_d_id_4) REFERENCES measures_and_dimensions (m_or_d_id),
                           FOREIGN KEY (dataset_id) REFERENCES datasets (dataset_id)
            )
        """)
        
        print(connection.execute("SHOW TABLES").df())

def get_datasets():
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
    return connection.execute("SELECT dataset_id, file_name, mime_type, file_size, date_created from datasets").df()

def delete_dataset(dataset_id):
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
        connection.execute('DELETE FROM metric WHERE dataset_id=?', [dataset_id])
        connection.execute('DELETE FROM charts WHERE dataset_id=?', [dataset_id])
        connection.execute('DELETE FROM measures_and_dimensions where dataset_id=?', [dataset_id])
        return connection.execute('DELETE FROM datasets where dataset_id=?', [dataset_id])
    
    return None

def delete_dataset_file(dataset_file_name):
    dir = "dataset_files"
    current_dir = os.path.dirname(__file__)
    new_folder_path = os.path.join(current_dir, dir)
    path = os.path.join(new_folder_path, dataset_file_name)
    if os.path.exists(path):
        os.remove(path)
    else:
        print("The dataset file does not exist")

def get_dataset_file(dataset_file_name):
    dir = "dataset_files"
    current_dir = os.path.dirname(__file__)
    new_folder_path = os.path.join(current_dir, dir)
    path = os.path.join(new_folder_path, dataset_file_name)
    print(path)
    if os.path.exists(path):
        #os.read("dataset_files/" + dataset_file_name)
        f = open(path, mode="rb")
        data = f.read()
        return data
    else:
        print("The dataset file does not exist")

def insert_dataset(fileName, fileBytes, mime_type, fileSize):
    dir = "dataset_files"
    current_dir = os.path.dirname(__file__)
    new_folder_path = os.path.join(current_dir, dir)
    path = os.path.join(new_folder_path, fileName)
    if not os.path.isfile(new_folder_path):
        os.makedirs(new_folder_path, exist_ok=True)
    with open(path, "wb") as f:
        f.write(fileBytes)
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
    return connection.execute("INSERT INTO datasets VALUES (nextval('seq_dataset_id'), ?, ?, ?, get_current_timestamp())", [fileName, mime_type, fileSize])
    #return connection.execute(f"INSERT INTO datasets VALUES (nextval('seq_dataset_id'), ?, get_current_timestamp()), {fileBytes}::blob" , [fileName])

def load_df_from_parquet(dataset_file_name, preprocess = False):
    dir = "dataset_files"
    current_dir = os.path.dirname(__file__)
    new_folder_path = os.path.join(current_dir, dir)
    path = os.path.join(new_folder_path, dataset_file_name)
    with open(path, "rb") as f:
        df = pd.read_parquet(f)
    #df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.replace(':', '_', regex=True)
    df.columns = df.columns.str.strip()
    if preprocess:
        df = df.dropna().drop_duplicates().reset_index(drop = True)

    return df

# def get_dataset_id_from_dataset_file_name(dataset_file_name):
#     if 'connection' in st.session_state:
#         connection = st.session_state['connection']
#     return connection.execute("SELECT dataset_id from datasets where file_name = ?", [dataset_file_name]).df().iloc[0]["dataset_id"].item()


def get_dataset_id_from_dataset_file_name(dataset_file_name):
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']

    query = 'SELECT dataset_id from datasets WHERE file_name = ?'

    result = connection.execute(query, [str(dataset_file_name)]).fetchone()

    if result:
        dataset_id = result[0]
        return dataset_id
    else:
        return None

def check_m_or_d_already_defined(dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    #print("The variable, dataset_id is of type:", type(dataset_id))
    if 'connection' in st.session_state:
        connection = st.session_state['connection']
        count = connection.execute("SELECT count(*) from measures_and_dimensions where dataset_id =  ?", [dataset_id]).df().iloc[0]["count_star()"].item()
        print("count = ", count)
        if  count> 0:
            return True
        else:
            return False
    
def insert_measures_and_dimensions(dataset_file_name, default_column_selection):
    print(default_column_selection)
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
        for key in default_column_selection:
            connection.execute("INSERT INTO measures_and_dimensions VALUES (nextval('seq_dataset_id'), ?, ?, ?, get_current_timestamp())", 
                               [key, default_column_selection[key], dataset_id])

def get_measures_and_dimensions(dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
        df = connection.execute("SELECT column_name, m_or_d_type, date_created from measures_and_dimensions where dataset_id = ?", [dataset_id]).df()
        
        return df
    
def save_measures_and_dimensions_in_db(modified_measures_and_dimensions_df, dataset_file_name):
    print(modified_measures_and_dimensions_df)
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
        for index, row in modified_measures_and_dimensions_df.iterrows():
            print(row["m_or_d_type"], row["column_name"], dataset_id)
            connection.execute("UPDATE measures_and_dimensions SET m_or_d_type = ?, date_created = get_current_timestamp() WHERE column_name = ? and dataset_id = ?", [row["m_or_d_type"], row["column_name"], dataset_id])
    
def get_measures(dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
        df = connection.execute("SELECT column_name, m_or_d_type, date_created from measures_and_dimensions where m_or_d_type = 'MEASURE' and dataset_id = ?", [dataset_id]).df()
        
        return df
     
def get_dimensions(dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' in st.session_state:
        connection = st.session_state['connection'] 
        df = connection.execute("SELECT column_name, m_or_d_type, date_created from measures_and_dimensions where m_or_d_type = 'DIMENSION' and dataset_id = ?", [dataset_id]).df()

        return df
    
def insert_chart_in_db(chart_name, x_column, y_column, color_column, chart_type, aggregation, dataset_file_name, chart_spec_json):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']
        
    # Prepare the base query and parameters
    base_query = "INSERT INTO charts (chart_name, x_column, chart_type, dataset_id, chart_specs, date_created"
    base_values = "?, ?, ?, ?, ?, get_current_timestamp()"
    params = [chart_name, x_column, chart_type, dataset_id, chart_spec_json]
    
    # Conditionally append y_column
    if y_column is not None:
        base_query += ", y_column"
        base_values += ", ?"
        params.append(y_column)
    
    # Conditionally append color_column
    if color_column is not None:
        base_query += ", color_column"
        base_values += ", ?"
        params.append(color_column)
    
    # Conditionally append aggregation
    if aggregation is not None:
        base_query += ", aggregation"
        base_values += ", ?"
        params.append(aggregation)
    
    # Finalize query
    query = f"{base_query}) VALUES ({base_values})"
    
    try:
        connection.execute(query, params)
        print("Success in inserting data in charts table!")
    except Exception as e:
        print(f"Error in inserting data in charts table: {e}")
        

# def insert_chart(chart_name, x_column, y_column, color_column, chart_type, aggregation, dataset_file_name, chart_spec_json):
#     dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
#     if 'connection' in st.session_state:
#         connection = st.session_state['connection']
#         try:
#             connection.execute("INSERT INTO charts VALUES (nextval('seq_chart_id'), ?, ?, ?, ?, ?, ?, ?, ?, get_current_timestamp())", [chart_name, x_column, y_column, color_column, chart_type, aggregation, dataset_id, chart_spec_json])
#             print("Success in inserting data in charts table!")
#         except:
#             print("Error in inserting data in charts table!")


# def get_charts(dataset_file_name):
#     dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
#     if 'connection' in st.session_state:
#         connection = st.session_state['connection']
#         return connection.execute("SELECT chart_id, chart_name, x_column, y_column, color_column, chart_type, date_created FROM charts WHERE dataset_id = ?", [dataset_id]).df()

def update_charts_in_db(updated_df, dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']
    for index, row in updated_df.iterrows():
        chart_name = row['chart_name']
        # x_column = row['X_column']
        # y_column = row['Y_column']
        # color_column = row['Color Column']
        # chart_type = row['Chart Type']
        # aggregation = row['Aggregation']
        # dataset_id = row['Dataset ID']
        chart_id = row['chart_id']
        # connection.execute("UPDATE charts SET chart_name = ?, x_column = ?, y_column = ?, color_column = ?, chart_type = ?, aggregation = ?, dataset_id = ?, date_created = get_current_timestamp() WHERE chart_id = ?",
        #                    [chart_name, x_column, y_column, color_column, chart_type, aggregation, dataset_id, chart_id])
        connection.execute("UPDATE charts SET chart_name = ? WHERE chart_id = ? AND dataset_id = ?",
                [chart_name, chart_id, dataset_id])

def delete_charts_from_db(selected_rows, dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']

    row_ids = connection.execute(f"""
            WITH OrderedCharts AS (
                SELECT chart_id, ROW_NUMBER() OVER (ORDER BY chart_id) AS row_num
                FROM charts
            )
            SELECT chart_id
            FROM OrderedCharts
            WHERE row_num IN {tuple(selected_rows)}
        """).fetchall()
    row_ids = [item[0] for item in row_ids]
    #print(row_ids)
    for chart_id in row_ids:
        connection.execute("DELETE FROM charts WHERE chart_id = ? AND dataset_id = ?", [chart_id, dataset_id])

def show_chart_data(dataset_file_name):
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']

    def truncate_chart_spec(chart_spec, length=100):
        if chart_spec is not None:
            if len(chart_spec) > length:
                return chart_spec[:length] + '...'
            else:
                return chart_spec
            
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    query = 'SELECT * FROM charts WHERE dataset_id = ?'
    results = connection.execute(query, [dataset_id]).fetchall()

    if results:
        columns = [col[0] for col in connection.description]
        df = pd.DataFrame(results, columns=columns)
        df['chart_specs'] = df['chart_specs'].apply(lambda x: truncate_chart_spec(x, 100))
        #data = [dict(zip(columns, row)) for row in results]
        return df
    else:
        return pd.DataFrame()
    

def get_m_or_d_id(col_name):
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']
    query = 'SELECT m_or_d_id FROM measures_and_dimensions WHERE column_name = ?'
    result = connection.execute(query, [str(col_name)]).fetchone()
    if result:
        return result[0]
    else:
        raise ValueError(f"column_name '{col_name}' not found in measures_and_dimensions")
    

def insert_metrics_in_metric_table(dataset_name, metric_name, measure = None, dimension1 = None, dimension2 = None, dimension3 = None):
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_name)
    if metric_name is not None and measure is not None and dimension1 is not None and dimension2 is not None and dimension3 is not None:
        measure_m_or_d_id = get_m_or_d_id(measure.split('--')[0] if measure is not None else measure)
        dimension1_m_or_d_id = get_m_or_d_id(dimension1.split('--')[0] if dimension1 is not None else dimension1)
        dimension2_m_or_d_id = get_m_or_d_id(dimension2.split('--')[0] if dimension2 is not None else dimension2)
        dimension3_m_or_d_id = get_m_or_d_id(dimension3.split('--')[0] if dimension3 is not None else dimension3)
        # Insert the measure into metric_measure
        insert_query = """
            INSERT INTO metric (metric_name, dataset_id, metric_measure_name, metric_dimension_name1, metric_dimension_name2, metric_dimension_name3, m_or_d_id_1, m_or_d_id_2, m_or_d_id_3, m_or_d_id_4, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, get_current_timestamp())
        """
        connection.execute(insert_query, [metric_name, dataset_id, measure, dimension1, dimension2, dimension3, measure_m_or_d_id, dimension1_m_or_d_id, dimension2_m_or_d_id, dimension3_m_or_d_id])
        
    elif metric_name is not None and measure is not None and dimension1 is not None and dimension2 is not None:
        measure_m_or_d_id = get_m_or_d_id(measure.split('--')[0] if measure is not None else measure)
        dimension1_m_or_d_id = get_m_or_d_id(dimension1.split('--')[0] if dimension1 is not None else dimension1)
        dimension2_m_or_d_id = get_m_or_d_id(dimension2.split('--')[0] if dimension2 is not None else dimension2)
        # Insert the measure into metric_measure
        insert_query = """
            INSERT INTO metric (metric_name, dataset_id, metric_measure_name, metric_dimension_name1, metric_dimension_name2, m_or_d_id_1, m_or_d_id_2, m_or_d_id_3, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, get_current_timestamp())
        """
        connection.execute(insert_query, [metric_name, dataset_id, measure, dimension1, dimension2, measure_m_or_d_id, dimension1_m_or_d_id, dimension2_m_or_d_id])
        
    elif metric_name is not None and measure is not None and dimension1 is not None and dimension3 is not None:
        measure_m_or_d_id = get_m_or_d_id(measure.split('--')[0] if measure is not None else measure)
        dimension1_m_or_d_id = get_m_or_d_id(dimension1.split('--')[0] if dimension1 is not None else dimension1)
        dimension3_m_or_d_id = get_m_or_d_id(dimension3.split('--')[0] if dimension3 is not None else dimension2)
        # Insert the measure into metric_measure
        insert_query = """
            INSERT INTO metric (metric_name, dataset_id, metric_measure_name, metric_dimension_name1, metric_dimension_name3, m_or_d_id_1, m_or_d_id_2, m_or_d_id_4, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, get_current_timestamp())
        """
        connection.execute(insert_query, [metric_name, dataset_id, measure, dimension1, dimension3, measure_m_or_d_id, dimension1_m_or_d_id, dimension3_m_or_d_id])

    elif metric_name is not None and measure is not None and dimension1 is not None:
        measure_m_or_d_id = get_m_or_d_id(measure.split('--')[0] if measure is not None else measure)
        dimension1_m_or_d_id = get_m_or_d_id(dimension1.split('--')[0] if dimension1 is not None else dimension1)
        # Insert the measure into metric_measure
        insert_query = """
            INSERT INTO metric (metric_name, dataset_id, metric_measure_name, metric_dimension_name1, m_or_d_id_1, m_or_d_id_2, date_created)
            VALUES (?, ?, ?, ?, ?, ?, get_current_timestamp())
        """
        connection.execute(insert_query, [metric_name, dataset_id, measure, dimension1, measure_m_or_d_id, dimension1_m_or_d_id])

    else:
        pass


def get_metrics_from_metric_table(dataset_file_name):
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    query = "SELECT * FROM metric WHERE dataset_id = ?"
    result = connection.execute(query, [dataset_id]).fetchall()
    
    if result:
        # Get the column names from the query result
        columns = [desc[0] for desc in connection.description]

        # Convert the result into a DataFrame
        metrics_df = pd.DataFrame(result, columns=columns)
        return metrics_df
    else:
        return pd.DataFrame()
    

def save_updated_metrics(edited_metrics_df):
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']
    for index, row in edited_metrics_df.iterrows():
        connection.execute("""
            UPDATE metric SET 
                           metric_name = ?,
                           metric_measure_name = ?,
                           metric_dimension_name1 = ?,
                           metric_dimension_name2 = ?,
                           metric_dimension_name3 = ?,
                           date_created = get_current_timestamp(),
                           WHERE
                           metric_id = ? AND
                           dataset_id = ?
        """, [row["metric_name"], row["metric_measure_name"], row["metric_dimension_name1"], row["metric_dimension_name2"], row["metric_dimension_name3"], row["metric_id"], row["dataset_id"]])


def delete_metrics_from_db(selected_rows, dataset_file_name):
    dataset_id = get_dataset_id_from_dataset_file_name(dataset_file_name)
    if 'connection' not in st.session_state:
        init_db()
    connection = st.session_state['connection']

    metric_ids = connection.execute(f"""
            WITH OrderedMetrics AS (
                SELECT metric_id, ROW_NUMBER() OVER (ORDER BY metric_id) AS row_num
                FROM metric
                WHERE dataset_id = ?
            )
            SELECT metric_id
            FROM OrderedMetrics
            WHERE row_num IN {tuple(selected_rows)}
        """, [dataset_id]).fetchall()
    metric_ids = [item[0] for item in metric_ids]
    
    for metric_id in metric_ids:
        connection.execute("DELETE FROM metric WHERE metric_id = ?", [metric_id])
