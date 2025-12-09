import streamlit as st
import pandas as pd
from prophet import Prophet
import altair as alt

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
import matplotlib.pyplot as plt

import db


def save_df_to_pdf(filename, altair_chart, plt_chart):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 30

    def draw_chart(c, chart, title, y_position, is_altair):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            if is_altair:
                chart.save(tmpfile.name, format='png')
            else:
                chart.savefig(tmpfile.name, format='png', bbox_inches='tight')
                plt.close(chart)
            chart_image_path = tmpfile.name

        max_chart_width = width - 2 * margin
        max_chart_height = (height - 3 * margin) / 2
        chart_aspect_ratio = max_chart_width / max_chart_height

        with Image.open(chart_image_path) as img:
            img_width, img_height = img.size

        if img_width / img_height > chart_aspect_ratio:
            scaled_width = max_chart_width
            scaled_height = scaled_width * img_height / img_width
        else:
            scaled_height = max_chart_height
            scaled_width = scaled_height * img_width / img_height

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position + scaled_height + 10, title)
        c.drawImage(chart_image_path, margin, y_position, width=scaled_width, height=scaled_height)

    if altair_chart is not None:
        draw_chart(c, altair_chart, "Original and forecasted data", height - margin - (height - 3 * margin) / 2, True)

    if plt_chart is not None:
        draw_chart(c, plt_chart, "Model components", margin, False)

    c.setFont("Helvetica", 10)
    c.drawString(width - margin - 50, margin / 2, f"Page 1")

    c.save()
    buffer.seek(0)
    unique_key = str(uuid.uuid4())
    st.download_button(label="Download PDF", data=buffer, file_name=filename, mime="application/pdf", key=unique_key)


def time_series_forecasting(dataset_file_name):
    # data = pd.read_csv(data)
    data = db.load_df_from_parquet(dataset_file_name)
    # Step 2: User selects date and measure columns
    date_column = st.selectbox("Select the Date Column", data.columns, index=None)
    measure_column = st.selectbox("Select the Measure Column", data.columns, index=None)
    # additional_regressor_options = [regressor for regressor in data.columns if regressor not in [date_column, measure_column]]
    # regressors = st.multiselect("Select othe dimensions column", additional_regressor_options)
    if date_column and measure_column:
        # Ensure the selected columns are valid
        # data[date_column] = pd.to_datetime(data[date_column],
        #                                     format="%Y-%m-%d"
        #                                     )
        data[date_column] = pd.to_datetime(data[date_column], dayfirst=True, errors='coerce')
        data = data.sort_values(by=date_column)
        # all_except_date_col = [col for col in data.columns if col not in [date_column]]
        # data_summarized = data
        # duplicate_rows = data[data[date_column].duplicated()]
        # st.write(duplicate_rows)
        data_summarized = data.groupby(date_column)[measure_column].sum().reset_index()
        data_summarized = data_summarized.sort_values(by=date_column)
        data_summarized = data_summarized[[date_column, measure_column]].dropna()
        data_summarized.columns = ["ds", "y"]  # Prophet requires columns to be named 'ds' and 'y'
        st.write(f'This dataset contains {data_summarized.shape[0], data.shape[0]} data points.')
        # Step 4: Option to choose confidence interval
        confidence_interval = st.slider("Choose confidence interval:", 0.01, 0.99, 0.80)

        # Step 3: User chooses forecasting parameters
        forecasting_period = st.number_input("Enter forecasting period:", min_value=1, max_value=365*5)
        forecasting_period_unit = st.selectbox("Select period unit:", ("days", "weeks", "months"))
        
        if forecasting_period_unit == "days":
            # forecasting_period *= 30
            forecasting_freq = 'D'
        elif forecasting_period_unit == "weeks":
            # forecasting_period *= 7
            forecasting_freq = 'W'
        elif forecasting_period_unit == "months":
            # forecasting_period *= 30
            forecasting_freq = 'M'
        # elif forecasting_period_unit == "years":
        #     # forecasting_period *= 365
        #     forecasting_freq = 'Y'
        ignore_last = st.number_input("Ignore the last:", min_value=0, max_value=data_summarized.shape[0]-1, value=0)

        model_option = st.radio("Choose model type:", ['Default', 'Flexible'])
        if model_option == 'Default':
                model = Prophet(interval_width=confidence_interval)
        elif model_option == 'Flexible':
            st.write("Choose model properties:")
            # growth = st.selectbox("Select trend mode:", ['linear','logistic','flat'])
            # User inputs for seasonalities and changepoints
            yearly_seasonality = st.checkbox("Add yearly seasonality", value=True)
            # if yearly_seasonality:
            #     yearly_seasonality_period = st.number_input("Yearly Seasonality period:", min_value=1)
            weekly_seasonality = st.checkbox("Add weekly seasonality", value=True)
            # if weekly_seasonality:
            #     weekly_seasonality_period = st.number_input("Weekly Seasonality period:", min_value=1)
            daily_seasonality = st.checkbox("Add daily seasonality", value=False)
            # if daily_seasonality:
            #     daily_seasonality_period = st.number_input("Daily Seasonality period:", min_value=1)
            seasonality_mode = st.selectbox("Select seasonality mode:", ['additive', 'multiplicative'])
            changepoint_prior_scale = st.slider("Changepoint prior scale", 0.001, 0.5, 0.05)
            model = Prophet(
                # growth=growth,
                interval_width=confidence_interval,
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                daily_seasonality=daily_seasonality,
                seasonality_mode=seasonality_mode,
                changepoint_prior_scale=changepoint_prior_scale
            )

        if st.button("Forecast"):
            st.write("Performing forecasting...")
            # Use the entire data for training

            # if regressors:
            #     for regressor in regressors:
            #         model.add_regressor(regressor)
            # st.write(data_summarized.columns)
            if ignore_last == 0:
                model.fit(data_summarized)
            else:
                model.fit(data_summarized.head(data_summarized.shape[0]-ignore_last))

            # Make forecast
            future_dates = model.make_future_dataframe(periods=forecasting_period, freq=forecasting_freq)
            forecast = model.predict(future_dates)

            # Merge original and forecasted data for visualization
            forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[-forecasting_period:]

            st.write("Forecasted Values")
            forecast_display = forecast_data.copy()
            forecast_display.columns = ['Date', 'Predicted Value', 'Lower Bound', 'Upper Bound']
            forecast_display['Date'] = forecast_display['Date'].dt.strftime('%Y-%m-%d')
            st.dataframe(forecast_display, use_container_width=True)
            # Plotting original data and forecasted data
            st.write("Plotting original data and forecasted data...")
            base = alt.Chart(data_summarized).encode(x='ds:T')

            original = base.mark_line(color='#8AC0F9').encode(y='y:Q').properties(title="Original and Forecasted Data")
            forecast_line = alt.Chart(forecast_data).mark_line(color='#F88107').encode(x='ds:T', y='yhat:Q')
            forecast_band = alt.Chart(forecast_data).mark_area(opacity=0.2, color='#FBD1A6').encode(x='ds:T', y='yhat_lower:Q', y2='yhat_upper:Q')

            combined_chart = alt.layer(original, forecast_line, forecast_band).interactive()
            st.altair_chart(combined_chart, use_container_width=True)
            # save_df_to_pdf_altair('Charts.pdf', combined_chart)

            # Plot model components
            st.write("Plotting model components...")
            fig = model.plot_components(forecast)
            st.pyplot(fig)
            # save_df_to_pdf_matplotlib('Charts.pdf', fig)
            save_df_to_pdf('Charts.pdf', combined_chart, fig)
            
            