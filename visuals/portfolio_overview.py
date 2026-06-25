# visuals/portfolio_overview.py

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_utils import safe_numeric, fmt_short_eur

def render_general_tab(df):
    st.markdown("####  Distribución de Oportunidad por Familia de Precio")
    
    # Agregación controlada
    agg_dict = {"uplift_abs": "sum", "revenue_total": "sum"}
    if "q_total" in df.columns:
        agg_dict["q_total"] = "sum"

    df_family = df.groupby("price_family", as_index=False).agg(agg_dict).round(2)
    df_family = df_family.sort_values("uplift_abs", ascending=False)
    
    # Para el tamaño del Treemap necesitamos magnitudes absolutas
    df_family["uplift_abs_size"] = df_family["uplift_abs"].abs()
    
    # SOLUCIÓN CRÍTICA PARA EL BUG DEL NaN:
    # Creamos una etiqueta de texto pre-formateada en el DataFrame. 
    # Así Plotly solo tiene que leer el string sin calcular dinámicamente el %{color}.
    df_family["label_custom"] = df_family.apply(
        lambda r: f"<b>{r['price_family']}</b><br>€{r['uplift_abs']:,.0f}", axis=1
    )
    
    # 1. TREEMAP PRINCIPAL CON GRADACIÓN BICOLOR Y ETIQUETA PRE-FORMATEADA
    fig = px.treemap(
        df_family,
        path=['label_custom'], # Usamos la etiqueta pre-formateada como el nodo del path
        values='uplift_abs_size',
        color='uplift_abs',
        color_continuous_scale='RdYlGn', 
        color_continuous_midpoint=0,      
        title="Distribución de Oportunidad por Familia de Precio",
        hover_data={'uplift_abs': ':,.0f', 'revenue_total': ':,.0f'}
    )
    fig.update_layout(height=480, margin=dict(t=50, l=15, r=15, b=15))
    
    # Cambiamos %{color} por %{label}, que ahora contiene el nombre de la familia y el valor limpio
    fig.update_traces(texttemplate="%{label}", textposition="middle center")
    st.plotly_chart(fig, use_container_width=True)
    
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.subheader("Top 10 Price Families por Oportunidad")
        dftop10 = df_family.head(10).copy()
        
        # 2. BARPLOT CON GRADACIÓN ROJO-VERDE Y CIFRAS INTERNAS CONSERVADAS
        figbar = px.bar(
            dftop10, 
            x="uplift_abs", 
            y="price_family", 
            orientation="h",
            color="uplift_abs", 
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0
        )
        figbar.update_layout(
            height=420,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=20, l=10, r=10, b=20),
            xaxis=dict(title="Uplift Acumulado (€)"),
            yaxis=dict(title=None, categoryorder='total ascending')
        )
        # Conservamos las cifras dentro de las barras de manera limpia
        figbar.update_traces(
            texttemplate="€%{x:,.0f}", 
            textposition="inside", 
            insidetextanchor="end"
        )
        st.plotly_chart(figbar, use_container_width=True)
    
    with col_der:
        # 3. SE QUEDA EL TREEMAP DE ROLES (Para acostumbrar al usuario al código de color)
        st.subheader("Arquitectura Estratégica por Rol Comercial")
        df_role = df.groupby("role_b2b", as_index=False).agg({"uplift_abs": "sum"})
        df_role["uplift_abs_size"] = df_role["uplift_abs"].abs()
        
        total_uplift_roles = df_role["uplift_abs"].sum()
        df_role["pct"] = (df_role["uplift_abs"] / total_uplift_roles * 100).round(1) if total_uplift_roles > 0 else 0
        
        df_role["customlabel"] = df_role.apply(
            lambda r: f"<b>{r['role_b2b'].upper()}</b><br>€{r['uplift_abs']:,.0f}<br>({r['pct']:.1f}%)", axis=1
        )
        
        colormap = {
            "traffic driver": "#1f77b4", "competitive fighter": "#ff7f0e",
            "kvi": "#2ca02c", "premium leader": "#d62728", "unknown": "#7f7f7f"
        }
        
        figtreerole = px.treemap(
            df_role, path=["customlabel"], values="uplift_abs_size",
            color="role_b2b", color_discrete_map=colormap, custom_data=["role_b2b"]  
        )
        figtreerole.update_layout(height=420, margin=dict(t=20, l=10, r=10, b=20), showlegend=False)
        figtreerole.update_traces(texttemplate="%{label}", textposition="middle center")
        st.plotly_chart(figtreerole, use_container_width=True)


def render_community_decision_map_tab(df, data):
    st.markdown("### Sistema de Gobierno y Decisión por Unidad de Negocio")
   
    if "final_summary" not in data:
        st.error("🚨 Error: La tabla maestra 'final_summary' no está disponible.")
        return
        
    df_summary = data["final_summary"].copy()
    communities = sorted(df_summary["community"].dropna().astype(str).unique())
    
    colsel1, colsel2 = st.columns([2, 1.5])
    with colsel1:
        selected_community = st.selectbox("Seleccionar Unidad de Negocio", communities, key="comm_sel_tab2")
    with colsel2:
        metricmap = {
            "Revenue Total (€)": "revenue_total", 
            "Uplift Potencial (€)": "uplift_abs", 
            "Margen Bruto Proyectado (€)": "margin_abs"
        }
        selectedmetriclabel = st.selectbox("Métrica de Control Visual", list(metricmap.keys()), key="metric_sel_tab2")
        selectedmetric = metricmap[selectedmetriclabel]

    # FILTRADO SEGURO (Previene fallos de asimetría)
    df_filtered = df[df["community"].astype(str) == selected_community].copy()
    df_summary_filtered = df_summary[df_summary["community"].astype(str) == selected_community]

    if df_summary_filtered.empty:
        st.error(f"🚨 Error: No se encuentran metadatos para la unidad '{selected_community}' en el resumen de control.")
        return

    # BUG SOLUCIONADO: Captura segura tras validar que el dataframe no venga vacío
    comm_row = df_summary_filtered.iloc[0]

    # Captura de datos segura
    quadrant = str(comm_row.get("quadrant", "No Definido"))
    canib_pct = comm_row.get("canib_internal_pct", 0)
    canib_flag = str(comm_row.get("canib_flag", "NORMAL"))
    uplift_real = df_filtered["uplift_abs"].sum()

    # Bloques de Alerta Ejecutiva
    if comm_row.get("alta_fragilidad_dec") or comm_row.get("alta_fragilidad_val"):
        st.error(f"### 🔴 FRAGILIDAD CRÍTICA ({quadrant})\n* **Diagnóstico:** Concentración de riesgo en el core.\n* **Mandato:** CONGELAR incrementos indexados de inmediato.")
    elif "ALTA" in canib_flag.upper() or float(canib_pct) > 15.0:
        st.warning(f"### 🟡 RIESGO DE CANIBALIZACIÓN ({canib_flag})\n* **Diagnóstico:** Riesgo de fuga interna del {float(canib_pct):.1f}%.\n* **Mandato:** Rebalancear markups differentials por rol estratégico.")
    else:
        st.success(f"### 🟢 DESPLIEGUE AUTORIZADO ({quadrant})\n* **Diagnóstico:** Estructura saludable y diversificada.\n* **Mandato:** Autorizar la actualización de tarifas en el maestro de precios.")

    # KPIs Principales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Volumen Gestionado", fmt_short_eur(df_filtered["revenue_total"].sum()), f"{df_filtered['sku'].nunique()} SKUs")
    c2.metric("Oportunidad Cautiva", fmt_short_eur(uplift_real), "Uplift mensual")
    c3.metric("Índice Concentración (CDI)", f"{comm_row.get('cdi_mean', 0):.2f}", "Estructura Core")
    c4.metric("Tasa Canibalización", f"{float(canib_pct):.1f}%", f"Estatus: {canib_flag}")

    # 4. PAGINA 2 SE QUEDA COMO ESTÁ PERO CON TRATAMIENTO DE DATOS PROTEGIDO
    plotdf = df_filtered.copy()
    
    if selectedmetric == "uplift_abs":
        plotdf["v_plot"] = plotdf["uplift_abs"].abs()
    else:
        plotdf["v_plot"] = safe_numeric(plotdf[selectedmetric])
        
    # BUG SOLUCIONADO: Evitamos forzar el dato real a 0.1 de manera destructiva en el DF. 
    # Solo aplicamos la máscara de renderizado visual si Plotly va a fallar con tamaños <= 0.
    plotdf["v_plot_render"] = plotdf["v_plot"].apply(lambda x: x if x > 0 else 0.001)

    colormaptab2 = {"traffic driver": "#1f77b4", "competitive fighter": "#ff7f0e", "kvi": "#2ca02c", "premium leader": "#d62728", "unknown": "#7f7f7f"}

    st.markdown("#### Desglose Jerárquico: Familia de Precio ➔ SKUs")
    
    figmain = px.treemap(
        plotdf, 
        path=["price_family", "sku"], 
        values="v_plot_render", # Usamos la columna de renderizado seguro para la geometría
        color="role_b2b", 
        color_discrete_map=colormaptab2, 
        height=500
    )
    
    # Mostramos el valor real (%{customdata[0]}) o calculamos según el mapeo para no mentir en la etiqueta
    figmain.update_traces(
        texttemplate="<b>%{label}</b><br>€%{value:,.0f}", 
        textposition="middle center",
        maxdepth=2 
    )
    figmain.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(figmain, use_container_width=True)

    st.markdown("---")
    coldownleft, coldownright = st.columns([5.5, 4.5])

    with coldownleft:
        st.markdown("#### Concentración de Oportunidad por Rol")
        roledf = df_filtered.groupby("role_b2b", as_index=False).agg({"revenue_total": "sum", "uplift_abs": "sum", "margin_abs": "sum"})
        roledf["v_role_plot"] = roledf["uplift_abs"].abs() if selectedmetric == "uplift_abs" else safe_numeric(roledf[selectedmetric])
        roledf["v_role_plot_render"] = roledf["v_role_plot"].apply(lambda x: x if x > 0 else 0.001)
        
        figroles = px.treemap(roledf, path=["role_b2b"], values="v_role_plot_render", color="role_b2b", color_discrete_map=colormaptab2, height=250)
        figroles.update_traces(texttemplate="<b>%{label}</b><br>€%{value:,.0f}", textposition="middle center")
        figroles.update_layout(margin=dict(t=10, l=10, r=10, b=10), showlegend=False)
        st.plotly_chart(figroles, use_container_width=True)

    with coldownright:
        st.markdown("#### Perfil Avanzado de Estructura")
        intensity_pct = float(comm_row.get('structure_intensity', 0)) * (100 if float(comm_row.get('structure_intensity', 0)) <= 1.0 else 1)
        st.markdown(f"""
        * **Elasticidad Comercial Dominante**: `{quadrant}`
        * **Índice de Salud de Ejecución**: **`{comm_row.get('executive_score', 0):.2f}`** `(Rank #{int(comm_row.get('exec_rank', 0)) if pd.notna(comm_row.get('exec_rank')) else 0})`
        * **Intensidad de Cobertura Core**: **`{intensity_pct:.1f}%`**
        """)
