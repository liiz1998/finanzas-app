# app_dashboard_final.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
import altair as alt

# ---------------------------
# CONFIGURACIÓN DE LA APP
# ---------------------------
st.set_page_config(
    page_title="Finanzas Personales Liz - Dashboard Final",
    page_icon="Liz.jpeg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# TEMA OSCURO STREAMLIT
# ---------------------------
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# LOGO Y TITULO
# ---------------------------
try:
    logo = Image.open("Liz.jpeg")
    st.image(logo, width=80)
except FileNotFoundError:
    st.warning("No se encontró el logo Liz.jpeg en la carpeta.")

st.markdown("## 💼 Finanzas Personales Liz - Dashboard Definitivo")

# ---------------------------
# CONEXIÓN GOOGLE SHEETS
# ---------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["google_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet_id = "1ssM9sq0CmpEOnbAtNIewca7cBDNNH6WDv6_H90Op8UU"
sheet = client.open_by_key(sheet_id).sheet1

# ---------------------------
# CARGAR DATOS
# ---------------------------
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception:
    df = pd.DataFrame(columns=["Fecha", "Categoría", "Tipo", "Monto"])

if not df.empty:
    df["Fecha_dt"] = pd.to_datetime(df["Fecha"], dayfirst=True)
else:
    df["Fecha_dt"] = pd.to_datetime([])

# ---------------------------
# SIDEBAR PARA NUEVOS DATOS
# ---------------------------
st.sidebar.header("➕ Agregar Ingreso/Gasto")
with st.sidebar.form("form_finanzas", clear_on_submit=True):
    fecha = st.date_input("Fecha")
    categoria = st.text_input("Categoría")
    tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"])
    monto = st.number_input("Monto", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Agregar")
    
    if submitted:
        if not categoria.strip():
            st.warning("Ingresa una categoría.")
        else:
            nueva_fila = {
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Categoría": categoria.strip(),
                "Tipo": tipo,
                "Monto": monto
            }
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            df["Fecha_dt"] = pd.to_datetime(df["Fecha"], dayfirst=True)
            try:
                sheet.append_row(list(nueva_fila.values()))
                st.success("✅ Datos agregados correctamente")
            except Exception as e:
                st.error(f"No se pudo guardar: {e}")

# ---------------------------
# FILTROS
# ---------------------------
st.subheader("🔍 Filtrar datos")
if not df.empty:
    fecha_inicio = st.date_input("Fecha inicio", df["Fecha_dt"].min())
    fecha_fin = st.date_input("Fecha fin", df["Fecha_dt"].max())
    categorias = ["Todas"] + sorted(df["Categoría"].unique().tolist())
    filtro_cat = st.selectbox("Filtrar por categoría", categorias)
    
    df_filtrado = df[(df["Fecha_dt"] >= pd.to_datetime(fecha_inicio)) &
                     (df["Fecha_dt"] <= pd.to_datetime(fecha_fin))]
    if filtro_cat != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Categoría"] == filtro_cat]
else:
    df_filtrado = df

# ---------------------------
# KPIs + MINI CHARTS
# ---------------------------
st.subheader("📊 KPIs principales")
if not df_filtrado.empty:
    ingresos = df_filtrado[df_filtrado["Tipo"]=="Ingreso"]["Monto"].sum()
    gastos = df_filtrado[df_filtrado["Tipo"]=="Gasto"]["Monto"].sum()
    balance = ingresos - gastos
    porcentaje_gasto = (gastos / ingresos * 100) if ingresos > 0 else 0

    mini_ingresos = alt.Chart(df_filtrado[df_filtrado["Tipo"]=="Ingreso"]).mark_area(
        line=True, color="#00ff00", opacity=0.3
    ).encode(x="Fecha_dt", y="Monto")
    
    mini_gastos = alt.Chart(df_filtrado[df_filtrado["Tipo"]=="Gasto"]).mark_area(
        line=True, color="#ff4d4d", opacity=0.3
    ).encode(x="Fecha_dt", y="Monto")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ingresos", f"${ingresos:,.2f}")
        st.altair_chart(mini_ingresos, use_container_width=True)
    with col2:
        st.metric("Total Gastos", f"${gastos:,.2f}")
        st.altair_chart(mini_gastos, use_container_width=True)
    with col3:
        st.metric("Balance", f"${balance:,.2f}")
    with col4:
        st.metric("Gasto % sobre ingreso", f"{porcentaje_gasto:.2f}%")
else:
    st.info("No hay datos para mostrar KPIs.")

# ---------------------------
# TABLA + DESCARGA CSV
# ---------------------------
st.subheader("📋 Datos filtrados")
st.dataframe(df_filtrado.drop(columns=["Fecha_dt"], errors='ignore'))

csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar CSV", csv_data, "finanzas_filtradas.csv", "text/csv")

# ---------------------------
# DASHBOARD VISUAL
# ---------------------------
st.subheader("📈 Dashboard visual")
if not df_filtrado.empty:
    chart_tipo = alt.Chart(df_filtrado).mark_bar().encode(
        x='Tipo',
        y='Monto',
        color='Tipo',
        tooltip=['Tipo', 'Monto']
    ).properties(width=300)
    
    chart_cat = alt.Chart(df_filtrado).mark_bar().encode(
        x='Categoría',
        y='Monto',
        color='Tipo',
        tooltip=['Categoría', 'Tipo', 'Monto']
    ).properties(width=600)
    
    chart_line = alt.Chart(df_filtrado).mark_line(point=True).encode(
        x='Fecha_dt',
        y='Monto',
        color='Tipo',
        tooltip=['Fecha', 'Tipo', 'Monto']
    ).properties(width=700)
    
    st.altair_chart(chart_tipo | chart_cat, use_container_width=True)
    st.altair_chart(chart_line, use_container_width=True)
else:
    st.info("No hay datos para graficar.")