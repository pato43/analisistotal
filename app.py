# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

import plotly.express as px
import plotly.graph_objects as go

# ---------- Config base ----------
st.set_page_config(page_title="Dashboard de Cursos — AleteIA / TESSENA", layout="wide")

# ---------- Estilos ----------
CSS = """
<style>
:root{
  --bg:#ffffff; --text:#0f172a; --muted:#64748b; --card:#ffffff;
  --border:#e2e8f0; --primary:#1e88e5; --chipbg:#e8f2ff; --chipfg:#0b57d0;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0b1220; --text:#eaf2ff; --muted:#9eb0cc; --card:#0f1420;
    --border:#1f2638; --primary:#7db3ff; --chipbg:#13223a; --chipfg:#99c2ff;
  }
}
html,body,[data-testid="stApp"]{ background:var(--bg); color:var(--text); }
h1,h2,h3{ letter-spacing:.2px; }
.card{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:14px; }
.badge{ display:inline-block; padding:6px 10px; border-radius:999px; background:var(--chipbg); color:var(--chipfg); border:1px solid var(--border); font-weight:700; font-size:.8rem; }
.kpi{ display:flex; gap:14px; }
.kpi .box{ flex:1; background:var(--card); border:1px solid var(--border); border-radius:14px; padding:14px; }
.kpi h4{ margin:0 0 6px; font-size:0.95rem; color:var(--muted); }
.kpi .val{ font-size:1.6rem; font-weight:800; }
.small{ color:var(--muted); font-size:.92rem; }
hr.sep{ height:1px; border:none; margin:14px 0; background:linear-gradient(90deg,var(--primary),transparent); }
.note-pill{ display:inline-block; padding:6px 10px; border-radius:10px; background:#fffbe6; border:1px solid #fde68a; color:#92400e; }
.stTabs [role="tab"]{ padding:10px 16px; border-radius:12px; }
.stTabs [role="tab"][aria-selected="true"]{ background:var(--card); border:1px solid var(--border); }
.instruction{ background:var(--card); border:1px dashed var(--border); border-radius:12px; padding:10px 12px; color:var(--muted);}
.chips span{ margin-right:6px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Catálogos ----------
PROGRAMAS = [
    ("Data Science", "Curso 6 meses", "MES", 1500, 6, None),
    ("Análisis de Datos", "Taller 8 semanas", "SEM", 700, None, 8),
    ("Desarrollo Web No-Code", "Taller 9 semanas", "SEM", 1400, None, 9),
    ("Excel Básico & Analítica", "Taller 8 semanas", "SEM", 500, None, 8),
    ("MCP Avanzado (AI+MCP)", "Bootcamp 12 semanas", "SEM", 2500, None, 12),
    ("Bootcamp IA/Datos (Intensivo)", "Bootcamp 8 meses", "MES", 3000, 8, None),
]
REGIONES = ["CDMX (MX)","Monterrey (MX)","Guadalajara (MX)","Tijuana (MX)","Bogotá (CO)","Medellín (CO)","Auckland (NZ)","Madrid (ES)"]
CANALES  = ["Influencers (micro)","Referidos","Grupos Facebook","LinkedIn"]
DISCIP   = ["STEM","Derecho","Economía","Sociología","Diseño","Administración","Profesorado"]
MONTHS   = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

# ---------- Utilidades ----------
def k_formatter(x):
    if x >= 1_000_000: return f"{x/1_000_000:.2f}M"
    if x >= 1_000: return f"{x/1_000:.1f}k"
    return f"{int(x)}"

def chips(items):
    return " ".join([f"<span class='badge'>{x}</span>" for x in items])

def px_template(theme_choice: str):
    return "plotly_dark" if theme_choice == "Oscuro" else "plotly_white"

PALETTE = ["#1e88e5","#43a047","#fb8c00","#8e24aa","#00acc1","#ef5350","#3949ab","#00897b"]

def calc_ingresos(row):
    if row.UnidadPrecio == "MES":
        meses = int(row.DuraciónMeses if pd.notna(row.DuraciónMeses) else 6)
        return row.PrecioUnidadMXN * meses * row.Estudiantes
    else:
        sem = int(row.DuraciónSemanas if pd.notna(row.DuraciónSemanas) else 8)
        return row.PrecioUnidadMXN * sem * row.Estudiantes

def dirichlet_pct(alpha=[4,2,3,1]):
    p = np.random.dirichlet(alpha)
    vals = np.round(p * 100, 0).astype(int)
    # Ajuste para asegurar suma=100
    diff = 100 - vals.sum()
    vals[0] += diff
    vals = np.clip(vals, 0, 100)
    return vals.tolist()  # [debito, credito, transferencia, paypal]

# ---------- Datos de ejemplo (más realistas) ----------
def seed_data():
    np.random.seed(42)

    # meses típicos por programa (0-index de MONTHS)
    starts = {
        "Data Science": [1, 7],                # Feb, Ago
        "Análisis de Datos": [2, 8],           # Mar, Sep
        "Desarrollo Web No-Code": [3, 9],      # Abr, Oct
        "Excel Básico & Analítica": [0, 6, 9], # Ene, Jul, Oct
        "MCP Avanzado (AI+MCP)": [4, 8],       # May, Sep
        "Bootcamp IA/Datos (Intensivo)": [0, 6]# Ene, Jul
    }

    # rangos de estudiantes por programa (para no inflar ingresos)
    ranges = {
        "Data Science": (12, 28),
        "Análisis de Datos": (15, 40),
        "Desarrollo Web No-Code": (10, 28),
        "Excel Básico & Analítica": (12, 38),
        "MCP Avanzado (AI+MCP)": (8, 22),
        "Bootcamp IA/Datos (Intensivo)": (8, 18),
    }

    years = [2022, 2023, 2024, 2025]
    rows = []
    prog_map = {p[0]: p for p in PROGRAMAS}

    for y in years:
        # cada año se ofrece un subconjunto aleatorio de programas (1 a 4)
        offered = np.random.choice([p[0] for p in PROGRAMAS], size=np.random.randint(1, 5), replace=False)
        for prog in offered:
            P = prog_map[prog]
            # de los starts posibles, tomar 1 (a veces 2) fechas para ese año
            starts_for_prog = starts[prog]
            n_ed = 1 if np.random.rand() < 0.7 else 2
            chosen_months = np.random.choice(starts_for_prog, size=n_ed, replace=False)
            for m in chosen_months:
                est_min, est_max = ranges[prog]
                n_est = int(np.random.randint(est_min, est_max + 1))
                # pagos aleatorios (centrados en 40/20/30/10 por defectos via Dirichlet)
                pct_deb, pct_cre, pct_tra, pct_pay = dirichlet_pct([8,4,6,2])  # sesgo a 40/20/30/10
                colocados = int(np.random.randint(0, max(1, int(n_est * 0.55))))  # hasta ~55%

                rows.append([
                    date(y, m+1, 1), y, m+1, MONTHS[m],
                    *P, n_est,
                    np.random.choice(CANALES, p=[0.6,0.18,0.12,0.10]),
                    np.random.choice(REGIONES, p=[.55,.09,.07,.05,.09,.05,.03,.07]),
                    np.random.choice(DISCIP, p=[.52,.08,.11,.07,.07,.10,.05]),
                    f"{prog[:3].upper()}-{y}-{m+1}",
                    pct_deb, pct_cre, pct_tra, pct_pay,
                    colocados
                ])

    cols = ["FechaInicio","Año","MesNum","Mes","Programa","Modalidad","UnidadPrecio","PrecioUnidadMXN",
            "DuraciónMeses","DuraciónSemanas","Estudiantes","CanalDominante","Region","Disciplina","Edición",
            "PctDebito","PctCredito","PctTransfer","PctPayPal","Colocados"]
    df = pd.DataFrame(rows, columns=cols)

    # asegurar límites y consistencia
    df[["PctDebito","PctCredito","PctTransfer","PctPayPal"]] = df[["PctDebito","PctCredito","PctTransfer","PctPayPal"]].clip(0,100)
    df["Colocados"] = df[["Colocados","Estudiantes"]].min(axis=1)
    return df

# ---------- Estado ----------
if "df" not in st.session_state:
    st.session_state.df = seed_data()
if "notes" not in st.session_state:
    st.session_state.notes = []

df = st.session_state.df

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    year = st.selectbox("Año", sorted(df["Año"].unique()), index=len(sorted(df["Año"].unique()))-1)
    progs = st.multiselect("Programa", sorted(df["Programa"].unique()), default=sorted(df["Programa"].unique()))
    canales = st.multiselect("Canal", CANALES, default=CANALES)
    regiones = st.multiselect("Región", REGIONES, default=REGIONES)
    st.markdown("<hr/>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        theme_graphs = st.selectbox("Apariencia gráficos", ["Claro","Oscuro"], index=0)
    with col_b:
        modo_externo = st.toggle("Modo externo", value=False, help="Oculta edición y notas para presentar a clientes/aliados.")

# ---------- Encabezado ----------
st.markdown(
    f"<div class='card'><span class='badge'>Dashboard</span> "
    f"<b>Programas de formación · 2022–2025</b> "
    f"{'&nbsp;&nbsp;<span class=\"badge\">Versión para presentación</span>' if modo_externo else ''}"
    f"<br><span class='small'>Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
    f"Filtros activos:</span><div class='chips small'>{chips([str(year)])} {chips(progs[:3]+(['…'] if len(progs)>3 else []))} "
    f"{chips(canales[:2]+(['…'] if len(canales)>2 else []))}</div></div>",
    unsafe_allow_html=True
)

# ---------- Filtros ----------
f = df[(df["Año"]==year) & (df["Programa"].isin(progs)) & (df["CanalDominante"].isin(canales)) & (df["Region"].isin(regiones))].copy()
if f.empty:
    st.warning("No hay datos con los filtros actuales. Ajusta opciones en la barra lateral.")
    st.stop()

# ---------- Derivados ----------
def normalize_row_pcts(row):
    p = np.array([row.PctDebito, row.PctCredito, row.PctTransfer, row.PctPayPal], dtype=float)
    s = p.sum()
    if s <= 0:
        p = np.array([40,20,30,10], dtype=float)
        s = 100
    p = p / s * 100.0
    # redondeo y ajuste final a 100
    r = np.round(p).astype(int)
    r[0] += (100 - r.sum())
    return r

pcts = f.apply(normalize_row_pcts, axis=1, result_type="expand")
pcts.columns = ["PctDebitoN","PctCreditoN","PctTransferN","PctPayPalN"]
f = pd.concat([f.reset_index(drop=True), pcts], axis=1)

# Ingresos
f["IngresosMXN"] = f.apply(calc_ingresos, axis=1)

# Conteo de estudiantes por método de pago
for col, pct_col in [("Debito","PctDebitoN"),("Credito","PctCreditoN"),("Transfer","PctTransferN"),("PayPal","PctPayPalN")]:
    f[f"Est_{col}"] = (f["Estudiantes"] * f[pct_col] / 100.0).round().astype(int)

# ---------- KPIs ----------
tpl = px_template(theme_graphs)
c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    st.markdown("<div class='box kpi'><div><h4>Estudiantes (año)</h4>"
                f"<div class='val'>{int(f['Estudiantes'].sum())}</div></div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='box kpi'><div><h4>Ingresos estimados</h4>"
                f"<div class='val'>${k_formatter(int(f['IngresosMXN'].sum()))} MXN</div></div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='box kpi'><div><h4>Ediciones</h4>"
                f"<div class='val'>{f['Edición'].nunique()}</div></div></div>", unsafe_allow_html=True)
with c4:
    top_prog = f.groupby("Programa")["Estudiantes"].sum().sort_values(ascending=False).index[0]
    st.markdown("<div class='box kpi'><div><h4>Programa líder</h4>"
                f"<div class='val'>{top_prog}</div></div></div>", unsafe_allow_html=True)
with c5:
    coloc_tot = int(f["Colocados"].sum())
    tasa_coloc = (coloc_tot / f["Estudiantes"].sum() * 100) if f["Estudiantes"].sum() > 0 else 0
    st.markdown("<div class='box kpi'><div><h4>Empleabilidad</h4>"
                f"<div class='val'>{tasa_coloc:.1f}%</div><div class='small'>{coloc_tot} colocados</div></div></div>", unsafe_allow_html=True)

st.markdown("<hr class='sep'/>", unsafe_allow_html=True)

# ---------- Tabs ----------
tabs = st.tabs([
    "📊 Overview",
    "👥 Ediciones (editable)",
    "💵 Ingresos",
    "🌍 Regiones & Canales",
    "💳 Pagos & 🎯 Empleabilidad",
    "🧱 Heatmap",
    "📝 Datos & Notas"
])

# ===== Overview =====
with tabs[0]:
    cA, cB = st.columns([1.3, 1], gap="large")

    A = f.groupby(["MesNum","Mes","Programa"], as_index=False)["Estudiantes"].sum().sort_values("MesNum")
    figA = px.bar(A, x="Mes", y="Estudiantes", color="Programa", barmode="group",
                  template=tpl, color_discrete_sequence=PALETTE, text_auto=True,
                  hover_data={"Mes":True,"Programa":True,"Estudiantes":":,"})
    figA.update_layout(height=360, margin=dict(t=40,b=10,l=10,r=10), legend_title_text="Programa")
    cA.markdown("**Estudiantes por mes × programa**")
    cA.plotly_chart(figA, use_container_width=True)
    cA.caption("Volumen mensual por programa, considerando los filtros.")

    B = f.groupby(["MesNum","Mes"], as_index=False)["Estudiantes"].sum().sort_values("MesNum")
    figB = px.line(B, x="Mes", y="Estudiantes", markers=True, template=tpl)
    figB.update_traces(hovertemplate="Mes: %{x}<br>Estudiantes: %{y:,}")
    figB.update_layout(height=360, margin=dict(t=40,b=10,l=10,r=10))
    cB.markdown("**Tendencia mensual de estudiantes**")
    cB.plotly_chart(figB, use_container_width=True)
    cB.caption("Evolución de estudiantes durante el año seleccionado.")

    # Conclusiones rápidas
    st.markdown("### 📌 Conclusiones")
    total_est = int(f["Estudiantes"].sum())
    total_ing = int(f["IngresosMXN"].sum())
    top_region = f.groupby("Region")["Estudiantes"].sum().sort_values(ascending=False).index[0]
    top_canal = f.groupby("CanalDominante")["Estudiantes"].sum().sort_values(ascending=False).index[0]
    st.markdown(f"""
- **Total estudiantes {year}:** {total_est:,}
- **Ingresos estimados:** ${total_ing:,.0f} MXN
- **Programa líder:** {top_prog}
- **Región más activa:** {top_region}
- **Canal dominante:** {top_canal}
- **Empleabilidad (colocados/estudiantes):** {tasa_coloc:.1f}%
""")

# ===== Ediciones (editable) =====
with tabs[1]:
    st.markdown("**Ediciones del año** " + ("(solo lectura en modo externo)" if modo_externo else "(editable)"))

    show_cols = [
        "FechaInicio","Año","Mes","Programa","Modalidad","UnidadPrecio","PrecioUnidadMXN",
        "DuraciónMeses","DuraciónSemanas","Estudiantes",
        "PctDebito","PctCredito","PctTransfer","PctPayPal",
        "Colocados",
        "CanalDominante","Region","Edición"
    ]
    base_table = f[show_cols].copy()

    # configs
    cfg = {
        "Estudiantes": st.column_config.NumberColumn(min_value=1, max_value=1000, step=1),
        "PrecioUnidadMXN": st.column_config.NumberColumn(min_value=100, max_value=10000, step=50),
        "PctDebito": st.column_config.NumberColumn(min_value=0, max_value=100, step=1, help="Porcentaje sobre estudiantes"),
        "PctCredito": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
        "PctTransfer": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
        "PctPayPal": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
        "Colocados": st.column_config.NumberColumn(min_value=0, max_value=int(base_table["Estudiantes"].max())),
        "CanalDominante": st.column_config.SelectboxColumn(options=CANALES),
        "Region": st.column_config.SelectboxColumn(options=REGIONES),
    }

    if modo_externo:
        st.dataframe(base_table, use_container_width=True, hide_index=True)
    else:
        edit_df = st.data_editor(base_table, column_config=cfg, hide_index=True, use_container_width=True, num_rows="fixed")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("Aplicar cambios a la base", type="primary"):
                # Fusionar por edición
                base = st.session_state.df
                cols_update = ["Estudiantes","PrecioUnidadMXN","PctDebito","PctCredito","PctTransfer","PctPayPal","Colocados","CanalDominante","Region"]
                merged = base.merge(edit_df[["Edición"]+cols_update], on="Edición", how="left", suffixes=("","_new"))
                for col in cols_update:
                    merged[col] = np.where(merged[col+"_new"].notna(), merged[col+"_new"], merged[col])
                    merged.drop(columns=[col+"_new"], inplace=True)

                # normalizar porcentajes a 100 por edición y clips
                for i, row in merged.iterrows():
                    p = np.array([row["PctDebito"], row["PctCredito"], row["PctTransfer"], row["PctPayPal"]], dtype=float)
                    s = p.sum()
                    if s <= 0: p = np.array([40,20,30,10], dtype=float); s = 100
                    p = p / s * 100.0
                    r = np.round(p).astype(int); r[0] += (100 - r.sum())
                    merged.loc[i, ["PctDebito","PctCredito","PctTransfer","PctPayPal"]] = r
                    merged.loc[i, "Colocados"] = min(int(merged.loc[i, "Colocados"]), int(merged.loc[i, "Estudiantes"]))
                st.session_state.df = merged
                st.toast("Cambios aplicados ✅")
                st.rerun()
        with c2:
            st.info("Los porcentajes de pago se normalizan automáticamente a 100% al aplicar cambios.")

# ===== Ingresos =====
with tabs[2]:
    c1, c2 = st.columns([1.3, 1], gap="large")
    R = f.groupby(["MesNum","Mes","Programa"], as_index=False)["IngresosMXN"].sum().sort_values("MesNum")
    figR = px.area(R, x="Mes", y="IngresosMXN", color="Programa",
                   template=tpl, color_discrete_sequence=PALETTE)
    figR.update_traces(hovertemplate="Mes: %{x}<br>%{legendgroup}: $%{y:,.0f} MXN")
    figR.update_layout(height=360, margin=dict(t=40,b=10,l=10,r=10), yaxis_title="MXN", legend_title_text="Programa")
    c1.markdown("**Ingresos por mes × programa (estimado)**")
    c1.plotly_chart(figR, use_container_width=True)
    c1.caption("Según unidad de cobro (MES/SEM) y duración por programa.")

    tkt = int(f["IngresosMXN"].sum() / f["Estudiantes"].sum()) if f["Estudiantes"].sum() > 0 else 0
    c2.markdown("**Indicadores de monetización**")
    c2.metric("Ticket estimado por estudiante", f"${k_formatter(tkt)} MXN")
    c2.metric("Ingresos totales estimados", f"${k_formatter(int(f['IngresosMXN'].sum()))} MXN")
    c2.caption("Valores aproximados, útiles para planeación y control.")

# ===== Regiones & Canales =====
with tabs[3]:
    left, right = st.columns(2, gap="large")
    G = f.groupby("Region", as_index=False)["Estudiantes"].sum().rename(columns={"Estudiantes":"TotalEstudiantes"}).sort_values("TotalEstudiantes")
    figG = px.bar(G, x="TotalEstudiantes", y="Region", orientation="h",
                  template=tpl, color_discrete_sequence=PALETTE, text="TotalEstudiantes")
    figG.update_traces(texttemplate="%{text:,}", hovertemplate="%{y}<br>Estudiantes: %{x:,}")
    figG.update_layout(height=max(260, 28*len(G)), margin=dict(t=30,b=10,l=10,r=10))
    left.markdown("**Top regiones (por estudiantes)**")
    left.plotly_chart(figG, use_container_width=True)
    left.caption("Suma de estudiantes por región.")

    C = f.groupby("CanalDominante", as_index=False)["Estudiantes"].sum().rename(columns={"Estudiantes":"TotalEstudiantes"})
    figC = px.bar(C, x="CanalDominante", y="TotalEstudiantes",
                  template=tpl, color_discrete_sequence=PALETTE, text="TotalEstudiantes")
    figC.update_traces(texttemplate="%{text:,}", hovertemplate="%{x}<br>Estudiantes: %{y:,}")
    figC.update_layout(height=320, margin=dict(t=30,b=10,l=10,r=10), xaxis_title="Canal", yaxis_title="Estudiantes")
    right.markdown("**Canales de adquisición (por estudiantes)**")
    right.plotly_chart(figC, use_container_width=True)
    right.caption("Principales fuentes de adquisición.")

# ===== Pagos & Empleabilidad =====
with tabs[4]:
    left, right = st.columns([1,1], gap="large")

    # Mezcla de pagos (por estudiantes)
    pagos = pd.DataFrame({
        "Método": ["Débito","Crédito","Transferencia","PayPal"],
        "Estudiantes": [
            f["Est_Debito"].sum(),
            f["Est_Credito"].sum(),
            f["Est_Transfer"].sum(),
            f["Est_PayPal"].sum(),
        ]
    })
    figPie = px.pie(pagos, names="Método", values="Estudiantes", template=tpl, hole=0.45)
    figPie.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{value:,} estudiantes")
    figPie.update_layout(height=360, margin=dict(t=30,b=10,l=10,r=10))
    left.markdown("**Mezcla de métodos de pago (estudiantes)**")
    left.plotly_chart(figPie, use_container_width=True)

    # Colocación por programa
    emp = f.groupby("Programa", as_index=False).agg(Estudiantes=("Estudiantes","sum"), Colocados=("Colocados","sum"))
    emp["Tasa"] = np.where(emp["Estudiantes"]>0, emp["Colocados"]/emp["Estudiantes"]*100, 0)
    figEmp = px.bar(emp.sort_values("Tasa"), x="Tasa", y="Programa", orientation="h",
                    template=tpl, color_discrete_sequence=PALETTE, text=emp["Tasa"].map(lambda x:f"{x:.1f}%"))
    figEmp.update_traces(hovertemplate="%{y}<br>Tasa: %{x:.1f}%<br>Colocados: %{customdata[0]:,} / %{customdata[1]:,}",
                         customdata=np.stack([emp["Colocados"], emp["Estudiantes"]], axis=1))
    figEmp.update_layout(height=max(260, 30*len(emp)), margin=dict(t=30,b=10,l=10,r=10), xaxis_title="Tasa de colocación (%)")
    right.markdown("**Empleabilidad por programa**")
    right.plotly_chart(figEmp, use_container_width=True)
    right.caption("Colocados / Estudiantes por programa (editable por edición).")

# ===== Heatmap =====
with tabs[5]:
    H = f.groupby(["MesNum","Mes","Programa"], as_index=False)["Estudiantes"].sum()
    pivot = H.pivot_table(index="Programa", columns="Mes", values="Estudiantes", aggfunc="sum").reindex(columns=MONTHS).fillna(0)
    heat = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale="Blues", hovertemplate="Programa: %{y}<br>Mes: %{x}<br>Estudiantes: %{z}<extra></extra>",
        colorbar=dict(title="Estudiantes")
    ))
    heat.update_layout(template=tpl, height=max(260, 28*len(pivot.index)), margin=dict(t=40,b=10,l=10,r=10))
    st.markdown("**Heatmap Mes × Programa**")
    st.plotly_chart(heat, use_container_width=True)
    st.caption("Picos y valles por programa y mes.")

# ===== Datos & Notas =====
with tabs[6]:
    t1, t2 = st.tabs(["📄 Datos (filtrados)", "🗒️ Notas del equipo"])
    with t1:
        st.markdown("**Tabla base (con ingresos y pagos normalizados)**")
        show = f.copy()
        show["IngresosMXN"] = show["IngresosMXN"].round(0).astype(int)
        show = show.sort_values(["MesNum","Programa"])
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.download_button("Descargar CSV filtrado", show.to_csv(index=False).encode("utf-8"),
                           file_name=f"cursos_{year}.csv", mime="text/csv")
    with t2:
        if modo_externo:
            st.info("Modo externo activo: las notas internas están ocultas.")
        else:
            with st.form("add_note"):
                nc1, nc2 = st.columns([3,1])
                with nc1:
                    note_text = st.text_area("Escribe una nota (visible para el equipo):", height=120,
                                             placeholder="Ej. Ajustar pauta para crédito; seguimiento empleabilidad en DS…")
                with nc2:
                    note_prog = st.selectbox("Programa", ["(General)"]+sorted(df["Programa"].unique()))
                    note_tag  = st.selectbox("Etiqueta", ["riesgo","idea","tarea","seguimiento","dato"])
                    submitted = st.form_submit_button("Guardar nota", use_container_width=True)
                if submitted and note_text.strip():
                    st.session_state.notes.append({
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "año": year, "programa": note_prog, "tag": note_tag, "nota": note_text.strip()
                    })
                    st.toast("Nota guardada 🗒️")
            if st.session_state.notes:
                notes_df = pd.DataFrame(st.session_state.notes).sort_values("ts", ascending=False)
                st.markdown("**Notas recientes**")
                for _, r in notes_df.iterrows():
                    st.markdown(
                        f"<div class='card'><span class='note-pill'>{r['tag']}</span> "
                        f"<b>{r['programa']}</b> · <span class='small'>{r['ts']}</span><br>{r['nota']}</div>",
                        unsafe_allow_html=True
                    )
                st.download_button("Descargar notas (CSV)", notes_df.to_csv(index=False).encode("utf-8"),
                                   file_name="notas_dashboard.csv", mime="text/csv")
            else:
                st.info("Aún no hay notas. Usa el formulario para registrar hallazgos, tareas o ideas.")

# ---------- Pie ----------
st.markdown("<hr class='sep'/>", unsafe_allow_html=True)
with st.expander("ℹ️ ¿Qué incluye este dashboard?"):
    st.markdown("""
- **KPIs**: estudiantes, ingresos, ediciones, programa líder y **empleabilidad**.
- **Plotly**: barras por mes/programa, línea mensual, áreas de ingresos, barras por región/canal, **mezcla de pagos** y **empleabilidad**, y **heatmap**.
- **Edición por edición**: estudiantes, precios, **porcentajes de pago** (normalizados a 100%) y **colocados**.
- **Modo externo** para presentar sin edición/Notas.
""")
