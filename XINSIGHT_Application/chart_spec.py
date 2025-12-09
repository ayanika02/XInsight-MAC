import json
from jinja2 import Template

# To define a function for generating the chart specifications
def generate_chart_specs(dataframe, x_field, y_field=None, mark_type="point", color_field=None, shape_field=None, size_field=None, height=400, width=600, hist_mean_line=True):
    if x_field not in [None] + list(dataframe.columns) or y_field not in [None] + list(dataframe.columns) or color_field not in [None] + list(dataframe.columns) or shape_field not in [None] + list(dataframe.columns) or size_field not in [None] + list(dataframe.columns):
        raise ValueError("Column(s) not found !!")

    if mark_type == "bar":
        chart_specs_template = """
        {
            "data": {"values": {{ chart_data | tojson }}},
            "mark": "{{ mark_type }}",
            "encoding": {
                "x": {"field": "{{ x_field }}", "type": "nominal"},
                "y": {"aggregate": "count", "type": "quantitative"}
                {% if color_field %},
                "color": {"field": "{{ color_field }}", "type": "nominal"}
                {% endif %}
            },
            "height": {{ height }},
            "width": {{ width }}
        }
        """
    elif mark_type == "histogram":
        chart_specs_template = """
        {
            "data": {"values": {{ chart_data | tojson }}},
            "layer": [
                {
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "{{ x_field }}", "type": "quantitative", "bin": true},
                        "y": {"aggregate": "count", "type": "quantitative"}
                    }
                }
                {% if hist_mean_line %},
                {
                    "mark": "rule",
                    "encoding": {
                        "x": {"aggregate": "mean", "field": "{{ x_field }}"},
                        "color": {"value": "red"},
                        "size": {"value": 5}
                    }
                }
                {% endif %}
            ],
            "height": {{ height }},
            "width": {{ width }}
        }
        """
    elif mark_type == "boxplot":
        chart_specs_template = """
        {
            "data": {"values": {{ chart_data | tojson }}},
            "mark": {"type": "{{ mark_type }}", "extent": "min-max"},
            "encoding": {
                "x": {"field": "{{ x_field }}", "type": "nominal"},
                "y": {"field": "{{ y_field }}", "type": "quantitative", "scale": {"zero": false}}
                {% if color_field %},
                "color": {"field": "{{ color_field }}", "type": "nominal"}
                {% endif %}
            },
            "height": {{ height }},
            "width": {{ width }}
        }
        """
    elif mark_type == "line":
        chart_specs_template = """
        {
            "data": {"values": {{ chart_data | tojson }}},
            "mark": {"type": "{{ mark_type }}", "point": true},
            "encoding": {
                "x": {"field": "{{ x_field }}", "type": "quantitative"},
                "y": {"field": "{{ y_field }}", "type": "quantitative"}
                {% if color_field %},
                "color": {"field": "{{ color_field }}", "type": "nominal"}
                {% endif %}
            },
            "height": {{ height }},
            "width": {{ width }}
        }
        """
    elif mark_type == "point":
        chart_specs_template = """
        {
            "data": {"values": {{ chart_data | tojson }}},
            "mark": "{{ mark_type }}",
            "encoding": {
                "x": {"field": "{{ x_field }}", "type": "quantitative"},
                "y": {"field": "{{ y_field }}", "type": "quantitative"}
                {% if color_field %},
                "color": {"field": "{{ color_field }}", "type": "nominal"}
                {% endif %}
                {% if shape_field %},
                "shape": {"field": "{{ shape_field }}", "type": "nominal"}
                {% endif %}
                {% if size_field %},
                "size": {"field": "{{ size_field }}", "type": "quantitative"}
                {% endif %},
                "tooltip": [
                    {"field": "{{ x_field }}", "type": "quantitative"},
                    {"field": "{{ y_field }}", "type": "quantitative"}
                ]
            },
            "height": {{ height }},
            "width": {{ width }}
        }
        """

    try:
        chart_specs = Template(chart_specs_template).render(
            chart_data=dataframe.to_dict('records'),
            x_field=x_field,
            y_field=y_field,
            mark_type=mark_type,
            color_field=color_field,
            shape_field=shape_field,
            size_field=size_field,
            height=height,
            width=width,
            hist_mean_line=hist_mean_line
        )
    except Exception as e:
        raise ValueError("Failed to render !!") from e

    if not chart_specs:
        raise ValueError("Empty chart specifications !!")

    return json.loads(chart_specs)
#returns json