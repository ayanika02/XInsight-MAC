
def generate_chart_spec(data, x_field, y_field, col_field=None, mark_type = 'point'):
    if x_field not in [None] + list(data.columns) or y_field not in [None] + list(data.columns) or col_field not in [None] + list(data.columns):
        raise ValueError("Column(s) not found !!")
    '''
    if mark_type in ['scatter', 'line']:
        if data[x_field].dtype not in ['int64', 'float64'] or data[y_field].dtype not in ['int64', 'float64'] or data[col_field].dtype != 'object':
            raise ValueError("For 'Scatter', and 'Line' charts -- X and Y axes must be 'Quantitative', Color column must be 'Categorical' !!")
    elif mark_type == 'bar':
        if data[x_field].dtype != 'object' or data[col_field].dtype != 'object':
            raise ValueError("For 'Bar' chart -- X axis and Color column must be 'Categorical' !!")
        y_field = None
    '''
    if mark_type == 'bar':
        if col_field == None:
            chart_spec = {
                "mark": "bar",
                "encoding": {
                    "x": {"field": x_field, "type": "nominal"},
                    "y": {"aggregate": "count", "type": "quantitative"}
                },
                "width": 500,
                "height": 300
            }
        else:
            chart_spec = {
                "mark": "bar",
                "encoding": {
                    "x": {"field": x_field, "type": "nominal"},
                    "y": {"aggregate": "count", "type": "quantitative"},
                    "color": {"field": col_field, "type": "nominal"}
                },
                "width": 500,
                "height": 300
            }

    elif mark_type == 'scatter':
        if col_field == None:
            chart_spec = {
                "mark": "point",
                "encoding": {
                    "x": {"field": x_field, "type": "quantitative"},
                    "y": {"field": y_field, "type": "quantitative"}
                },
                "width": 500,
                "height": 300
            }
        else:
            chart_spec = {
                "mark": "point",
                "encoding": {
                    "x": {"field": x_field, "type": "quantitative"},
                    "y": {"field": y_field, "type": "quantitative"},
                    "color": {"field": col_field, "type": "nominal"}
                },
                "width": 500,
                "height": 300
            }

    elif mark_type == 'line':
        if col_field == None:
            chart_spec = {
                "mark": "line",
                "encoding": {
                    "x": {"field": x_field, "type": "quantitative"},
                    "y": {"field": y_field, "type": "quantitative"}
                },
                "width": 500,
                "height": 300
            }
        else:
            chart_spec = {
                "mark": "line",
                "encoding": {
                    "x": {"field": x_field, "type": "quantitative"},
                    "y": {"field": y_field, "type": "quantitative"},
                    "color": {"field": col_field, "type": "nominal"}
                },
                "width": 500,
                "height": 300
            }
    else:
        raise ValueError("Unsupported `mark_type` !!")
   
    return chart_spec