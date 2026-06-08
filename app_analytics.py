import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(layout="wide", page_title="Dashboard del Museo")

# --- CUSTOM CSS FOR HIGH-TECH AESTHETIC ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        color: #e5e7eb;
        font-family: 'Courier New', Courier, monospace;
    }
    div.stButton > button {
        background-color: #1f2937;
        color: #f97316;
        border: 1px solid #f97316;
    }
    div.stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f97316;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Filtros Globales")
anio = st.sidebar.selectbox("Año Fiscal", [2025, 2026])
mes = st.sidebar.slider("Mes", 1, 12, 1)

# Main content
st.title("Panel de Control - Sistema Central del Museo")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "CONTROL FINANCIERO",
    "TRAZABILIDAD OBRAS",
    "SEGURIDAD LOGS",
    "AUDITORÍA MEMBRESÍAS"
])

# --- PESTAÑA 1: CONTROL FINANCIERO GERENCIAL ---
with tab1:
    st.header("Control Financiero Gerencial")
    
    # Fetch Data
    try:
        facturacion_res = requests.get(f"{API_BASE_URL}/reportes/facturacion", params={"anio": anio, "mes": mes})
        membresias_res = requests.get(f"{API_BASE_URL}/reportes/membresias", params={"anio": anio, "mes": mes})
        
        facturacion_data = facturacion_res.json() if facturacion_res.status_code == 200 else []
        membresias_data = membresias_res.json() if membresias_res.status_code == 200 else []
        
        if not facturacion_data and not membresias_data:
            st.warning("Sin registros para los parámetros consultados.")
        else:
            # Metrics
            df_fact = pd.DataFrame(facturacion_data)
            df_memb = pd.DataFrame(membresias_data)
            
            # Force numeric conversion
            if 'ganancia_museo' in df_fact.columns:
                df_fact['ganancia_museo'] = pd.to_numeric(df_fact['ganancia_museo'], errors='coerce')
            if 'iva_calculado' in df_fact.columns:
                df_fact['iva_calculado'] = pd.to_numeric(df_fact['iva_calculado'], errors='coerce')
            if 'monto_cobrado' in df_memb.columns:
                df_memb['monto_cobrado'] = pd.to_numeric(df_memb['monto_cobrado'], errors='coerce')
            if 'monto_neto' in df_fact.columns:
                df_fact['monto_neto'] = pd.to_numeric(df_fact['monto_neto'], errors='coerce')

            ganancia_neta = df_fact['ganancia_museo'].sum() if 'ganancia_museo' in df_fact.columns else 0
            iva_recaudado = df_fact['iva_calculado'].sum() if 'iva_calculado' in df_fact.columns else 0
            recaudacion_memb = df_memb['monto_cobrado'].sum() if 'monto_cobrado' in df_memb.columns else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Ganancia Neta ($)", f"{ganancia_neta:,.2f}")
            m2.metric("IVA ($)", f"{iva_recaudado:,.2f}")
            m3.metric("Membresías ($)", f"{recaudacion_memb:,.2f}")
            
            # Visualizations
            st.subheader("Análisis de Ingresos")
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("Distribución de Ganancia Neta")
                if 'ganancia_museo' in df_fact.columns and 'id_factura' in df_fact.columns:
                    st.bar_chart(df_fact.set_index('id_factura')['ganancia_museo'])
            
            with col_chart2:
                st.write("Recaudación por Membresía")
                if 'monto_cobrado' in df_memb.columns:
                    st.line_chart(df_memb['monto_cobrado'])

    except Exception as e:
        st.error(f"Error al conectar con el backend: {e}")

# --- PESTAÑA 2: TRAZABILIDAD Y ESTATUS DE OBRAS ---
with tab2:
    st.header("Trazabilidad y Estatus de Obras")
    id_obra = st.number_input("ID de la Obra", min_value=1, step=1)
    
    if id_obra:
        try:
            res = requests.get(f"{API_BASE_URL}/obras/historico/{id_obra}")
            if res.status_code == 200:
                data = res.json()
                df_obras = pd.DataFrame(data)
                
                st.subheader(f"Línea de tiempo - Obra {id_obra}")
                # Visual timeline approach
                for _, row in df_obras.iterrows():
                    with st.expander(f"{row.get('fecha_evento', 'N/A')} : {row.get('estatus_anterior', 'Inicio')} ➔ {row.get('estatus_nuevo', 'N/A')}"):
                        st.write(f"**Usuario:** {row.get('usuario_id')}")
                        st.write(f"**IP:** {row.get('ip_origen')}")
            elif res.status_code == 404:
                st.warning("No se encontraron registros para esa obra.")
            else:
                st.error("Error al obtener el historial.")
        except Exception as e:
            st.error(f"Error al conectar con el backend: {e}")

# --- PESTAÑA 3: SEGURIDAD Y ACCESOS (LOGS) ---
with tab3:
    st.header("Seguridad y Accesos (Logs)")
    usuario = st.text_input("Login de Administrador/Comprador")
    
    if st.button("Consultar Logs"):
        try:
            # Need dates for the API, assuming current month/year for the range
            desde = datetime(anio, mes, 1).isoformat()
            hasta = (datetime(anio, mes, 1) + timedelta(days=30)).isoformat()
            
            res = requests.get(f"{API_BASE_URL}/seguridad/logs", params={"login_usuario": usuario, "desde": desde, "hasta": hasta})
            
            if res.status_code == 200:
                data = res.json()
                if not data:
                    st.info("Sin registros.")
                else:
                    df = pd.DataFrame(data)
                    st.metric("Total de Eventos", len(df))
                    st.dataframe(df)
                    
                    # Highlight issues
                    if 'accion' in df.columns:
                        if df['accion'].str.contains("DENEGADO|SOSPECHOSA").any():
                            st.error("¡Se detectó actividad sospechosa o acceso denegado!")
            else:
                st.error("Error al consultar logs.")
        except Exception as e:
            st.error(f"Error al conectar con el backend: {e}")

# --- PESTAÑA 4: AUDITORÍA DE CÓDIGOS DE MEMBRESÍA ---
with tab4:
    st.header("Auditoría de Códigos de Membresía")
    id_comprador = st.number_input("ID del Comprador", min_value=1, step=1)
    
    if st.button("Buscar Códigos"):
        try:
            res = requests.get(f"{API_BASE_URL}/membresias/codigos", params={"id_comprador": id_comprador})
            if res.status_code == 200:
                data = res.json()
                if not data['datos']:
                    st.info("Sin registros.")
                else:
                    st.dataframe(pd.DataFrame(data['datos']))
            else:
                st.error("Error al consultar códigos.")
        except Exception as e:
            st.error(f"Error al conectar con el backend: {e}")
