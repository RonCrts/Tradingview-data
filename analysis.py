from tradingview_ta import TA_Handler, Interval
import streamlit as st
import pandas as pd
from openpyxl.styles import numbers
from openpyxl import Workbook
import base64
import tempfile
import os
from openpyxl.utils.dataframe import dataframe_to_rows



st.title('Acceso a datos de TradingView')
# haz que el usuario ingrese un símbolo
symbol = st.text_input('Ingrese un símbolo', 'AAPL')

# haz que el usuario seleccione el intervalo
interval_options = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_5_MINUTES, Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_DAY]
interval = st.selectbox('Seleccione un intervalo', interval_options)

# obtener los datos del símbolo
data = TA_Handler(
    symbol=symbol,
    screener="america",
    exchange="NASDAQ",
    interval=interval
)
data_analysis = data.get_analysis()
#haz una barra lateral para mostrar el análisis
st.sidebar.header('Análisis')
st.sidebar.write(data_analysis.summary)  # Fix: Access 'summary' attribute instead of using subscript notation
data = data.get_indicators()

# crear un dataframe
df = pd.DataFrame(data, index=[0])  # Specify index as [0]

# formatear las celdas
formatting = {'General': numbers.FORMAT_GENERAL}
for column in df.columns:
    formatting[column] = numbers.FORMAT_NUMBER_00

# crear un libro de Excel
wb = Workbook()
ws = wb.active

# agregar los datos al libro de Excel
for r in dataframe_to_rows(df, index=False, header=True):
    ws.append(r)

# aplicar el formato a las celdas
for column in ws.columns:
    max_length = 0
    column = [cell for cell in column]
    for i, cell in enumerate(column):
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(cell.value)
        except:
            pass
    adjusted_width = (max_length + 2) * 1.2
    ws.column_dimensions[column[0].column_letter].width = adjusted_width

# guardar el libro de Excel en un archivo temporal
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
wb.save(temp_file.name)
temp_file.close()

# leer el archivo temporal y convertirlo a base64
with open(temp_file.name, 'rb') as file:
    excel_data = file.read()
excel_base64 = base64.b64encode(excel_data).decode()

# crear el enlace de descarga
href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64}" download="data.xlsx">Descargar archivo Excel</a>'
st.markdown(href, unsafe_allow_html=True)

# eliminar el archivo temporal
os.remove(temp_file.name)

