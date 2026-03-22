# app_pro.py
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------
# CONFIGURACIÓN PÁGINA
# ---------------------------
st.set_page_config(
    page_title="Finanzas Personales",
    page_icon="liz.jpeg",
    layout="wide"
)

# ---------------------------
# CONEXIÓN GOOGLE SHEETS
# ---------------------------
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
client = gspread.authorize(creds)

# Reemplaza con tu Sheet ID
sheet_id = "1ssM9sq0CmpEOnbAtNIewca7cBDNNH6WDv6_H90Op8UU"
sheet = client.open_by_key(sheet_id).worksheet("Datos")

# ---------------------------
# ESTILOS APP
# ---------------------------
st.markdown("""
<style>
/* Tus estilos Apple / Startup y modo oscuro */
body { transition: background-color 0.3s, color 0.3s; }
@media (prefers-color-scheme: dark) { body { background-color: #1c1c1e; color: #f2f2f7; } }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# TÍTULO
# ---------------------------
st.markdown('<h1 style="font-size:42px;">💰 Dashboard Financiero</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="color:#6e6e73;">Control inteligente de ingresos y gastos</h3>', unsafe_allow_html=True)
st.write("")

# ---------------------------
# SIDEBAR: MES + INPUTS
# ---------------------------
st.sidebar.markdown("## ⚙️ Selecciona mes e ingresa tus datos")
mes = st.sidebar.selectbox("Mes", [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
])

# Inputs vacíos
ingresos = st.sidebar.number_input("Ingresos del mes", min_value=0, value=0, step=100)
gastos = st.sidebar.number_input("Gastos del mes", min_value=0, value=0, step=100)
ahorro = ingresos - gastos

# ---------------------------
# GUARDAR EN GOOGLE SHEETS
# ---------------------------
records = sheet.get_all_records()
df_sheet = pd.DataFrame(records)

if mes in df_sheet["Mes"].values:
    row_idx = df_sheet[df_sheet["Mes"] == mes].index[0] + 2
    sheet.update_cell(row_idx, 2, ingresos)
    sheet.update_cell(row_idx, 3, gastos)
    sheet.update_cell(row_idx, 4, ahorro)
else:
    sheet.append_row([mes, ingresos, gastos, ahorro])

# ---------------------------
# ACTUALIZAR DATAFRAME PARA GRAFICOS
# ---------------------------
records = sheet.get_all_records()
df = pd.DataFrame(records)

df_cat = pd.DataFrame({
    "Categoria": ["Vivienda","Comida","Transporte","Ocio","Servicios","Ahorro"],
    "Monto": [0.35*ahorro, 0.25*ahorro, 0.15*ahorro, 0.10*ahorro, 0.075*ahorro, 0.05*ahorro]
})

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3 = st.columns(3)
with col1: st.metric("Ingresos", f"${ingresos:,}")
with col2: st.metric("Gastos", f"-${gastos:,}")
with col3: st.metric("Ahorro", f"${ahorro:,}")

if gastos > ingresos:
    st.warning("⚠️ Estás gastando más de lo que ingresas")

# ---------------------------
# Objetivo de ahorro
# ---------------------------
objetivo = 1000
progreso = ahorro/objetivo
st.progress(min(progreso,1.0))
st.write(f"Has ahorrado **${ahorro}** de **${objetivo}**")

# ---------------------------
# Gráficos
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gastos por categoría")
    fig_cat = px.pie(df_cat, names="Categoria", values="Monto", hole=0.65, template="simple_white")
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    st.subheader("Gastos mensuales")
    fig_gastos = px.bar(df, x="Mes", y="Gastos", color="Gastos", template="simple_white")
    st.plotly_chart(fig_gastos, use_container_width=True)

# ---------------------------
# Tabla de datos completos
# ---------------------------
st.subheader("Datos completos")
st.dataframe(df, use_container_width=True)