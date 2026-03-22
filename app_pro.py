# app_pro.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------
st.set_page_config(
    page_title="Finanzas Personales",
    page_icon="💎",
    layout="wide"
)

# ------------------------------------------------
# ESTILOS AVANZADOS (APPLE / STARTUP STYLE)
# ------------------------------------------------
st.markdown("""
<style>

.main {
    background-color: #fafafa;
}

.title {
    font-size:42px;
    font-weight:700;
}

.subtitle {
    color:#6e6e73;
    font-size:18px;
}

/* TARJETAS KPI */
.card {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border-radius:18px;
    padding:25px;
    box-shadow:0 8px 20px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow:0 15px 35px rgba(0,0,0,0.08);
}

/* TARJETAS SECCIÓN */
.section-card {
    background:white;
    padding:25px;
    border-radius:18px;
    box-shadow:0 8px 20px rgba(0,0,0,0.05);
    margin-bottom:20px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color:#ffffff;
}

/* TEXTO KPI */
.kpi-title {
    color:#6e6e73;
    font-size:16px;
}

.kpi-value {
    font-size:30px;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# TÍTULO
# ------------------------------------------------
st.markdown('<div class="title">💰 Dashboard Financiero</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Control inteligente de ingresos y gastos</div>', unsafe_allow_html=True)

st.write("")

# ------------------------------------------------
# DATOS
# ------------------------------------------------
data = {
    "Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"],
    "Ingresos": [5000, 5200, 4800, 5500, 6000, 5800],
    "Gastos": [3000, 3100, 2900, 3300, 3400, 3200]
}

df = pd.DataFrame(data)

categorias = {
    "Categoria": ["Vivienda", "Comida", "Transporte", "Ocio", "Servicios", "Ahorro"],
    "Monto": [350, 250, 150, 100, 75, 50]
}

df_cat = pd.DataFrame(categorias)

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------
st.sidebar.markdown("## ⚙️ Filtros")

mes = st.sidebar.selectbox(
    "Selecciona mes",
    df["Mes"]
)

df_filtrado = df[df["Mes"] == mes]

ingresos = df_filtrado["Ingresos"].values[0]
gastos = df_filtrado["Gastos"].values[0]
ahorro = ingresos - gastos

# ------------------------------------------------
# TARJETAS KPI
# ------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="kpi-title">Ingresos</div>
        <div class="kpi-value">${ingresos:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="kpi-title">Gastos</div>
        <div class="kpi-value">-${gastos:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="kpi-title">Ahorro</div>
        <div class="kpi-value">${ahorro:,}</div>
    </div>
    """, unsafe_allow_html=True)

if gastos > ingresos:
    st.warning("⚠️ Estás gastando más de lo que ingresas")

st.write("")

# ------------------------------------------------
# OBJETIVO DE AHORRO
# ------------------------------------------------
st.markdown("### 🎯 Objetivo de ahorro")

objetivo = 1000
progreso = ahorro / objetivo

st.progress(min(progreso,1.0))
st.write(f"Has ahorrado **${ahorro}** de **${objetivo}**")

st.write("")

# ------------------------------------------------
# GRÁFICOS
# ------------------------------------------------
col1, col2 = st.columns(2)

# DONUT CATEGORÍAS
with col1:

    st.markdown("### 📊 Gastos por categoría")

    fig_cat = px.pie(
        df_cat,
        names="Categoria",
        values="Monto",
        hole=0.65,
        template="simple_white"
    )

    st.plotly_chart(fig_cat, width="stretch")

# BARRAS MENSUALES
with col2:

    st.markdown("### 📉 Gastos mensuales")

    fig_gastos = px.bar(
        df,
        x="Mes",
        y="Gastos",
        color="Gastos",
        template="simple_white"
    )

    st.plotly_chart(fig_gastos, width="stretch")

# ------------------------------------------------
# TABLA
# ------------------------------------------------
st.markdown("### 📄 Datos completos")

st.dataframe(df, width="stretch")