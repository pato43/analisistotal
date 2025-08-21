# app.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, date

# ---------- Config base ----------
st.set_page_config(page_title="Dashboard de Cursos — AleteIA / TESSENA", layout="wide")

# ---------- Estilos (auto claro/oscuro) ----------
CSS = """
<style>
:root{
  --bg: #ffffff; --text:#0f172a; --muted:#64748b; --card:#ffffff;
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
.chat{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:12px; }
.msg{ border-radius:12px; padding:10px 12px; margin:8px 0; max-width:92%; }
.msg.agent{ background:rgba(30,136,229,.12); border:1px solid rgba(30,136,229,.2); }
.msg.user{ background:rgba(148,163,184,.12); border:1px solid rgba(148,163,184,.2); margin-left:auto; }
.note-pill{ display:inline-block; padding:6px 10px; border-radius:10px; background:#fffbe6; border:1px solid #fde68a; color:#92400e; }
.stTabs [role="tab"]{ padding:10px 16px; border-radius:12px; }
.stTabs [role="tab"][aria-selected="true"]{ background:var(--card); border:1px solid var(--border); }
.instruction{ background:var(--card); border:1px dashed var(--border); border-radius:12px; padding:10px 12px; color:var(--muted);}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Estado / datos iniciales ----------
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

def seed_data():
    np.random.seed(11)
    rows = []
    bands = {2022:(20,30), 2023:(40,80), 2024:(80,160), 2025:(100,200)}
    def ri(a,b): return int(np.random.randint(a,b+1))
    def pick(arr, p=None):
        if p is None: return np.random.choice(arr)
        return np.random.choice(arr, p=p)

    prog_map = {p[0]:p for p in PROGRAMAS}
    for y in [2022,2023,2024,2025]:
        if y==2022:
            for (prog, m) in [("Data Science",4), ("Excel Básico & Analítica",10)]:
                P = prog_map[prog]; n = ri(*bands[y])
                rows.append([date(y, m+1, 1), y, m+1, MONTHS[m], *P, n, pick(CANALES, [0.7,0.12,0.1,0.08]),
                             pick(REGIONES,[.66,.07,.06,.04,.06,.03,.02,.06]), pick(DISCIP, [.55,.08,.1,.07,.07,.08,.05]),
                             f"{prog[:3].upper()}-{y}-1"])
        if y==2023:
            for (prog, m) in [("Data Science",2),("Análisis de Datos",7),("Desarrollo Web No-Code",9)]:
                P = prog_map[prog]; n = ri(*bands[y])
                rows.append([date(y, m+1, 1), y, m+1, MONTHS[m], *P, n, pick(CANALES, [0.7,0.12,0.1,0.08]),
                             pick(REGIONES,[.66,.07,.06,.04,.06,.03,.02,.06]), pick(DISCIP, [.55,.08,.1,.07,.07,.08,.05]),
                             f"{prog[:3].upper()}-{y}-1"])
        if y==2024:
            for (prog, m) in [("Bootcamp IA/Datos (Intensivo)",0),("MCP Avanzado (AI+MCP)",4),
                              ("Excel Básico & Analítica",6),("Desarrollo Web No-Code",9)]:
                P = prog_map[prog]; n = ri(*bands[y])
                rows.append([date(y, m+1, 1), y, m+1, MONTHS[m], *P, n, pick(CANALES, [0.7,0.12,0.1,0.08]),
                             pick(REGIONES,[.66,.07,.06,.04,.06,.03,.02,.06]), pick(DISCIP, [.55,.08,.1,.07,.07,.08,.05]),
                             f"{prog[:3].upper()}-{y}-1"])
        if y==2025:
            for (prog, m) in [("Bootcamp IA/Datos (Intensivo)",0),("Análisis de Datos",3),
                              ("MCP Avanzado (AI+MCP)",5),("Excel Básico & Analítica",7),("Data Science",9)]:
                P = prog_map[prog]; n = ri(*bands[y])
                rows.append([date(y, m+1, 1), y, m+1, MONTHS[m], *P, n, pick(CANALES, [0.7,0.12,0.1,0.08]),
                             pick(REGIONES,[.66,.07,.06,.04,.06,.03,.02,.06]), pick(DISCIP, [.55,.08,.1,.07,.07,.08,.05]),
                             f"{prog[:3].upper()}-{y}-1"])
    cols = ["FechaInicio","Año","MesNum","Mes","Programa","Modalidad","UnidadPrecio","PrecioUnidadMXN",
            "DuraciónMeses","DuraciónSemanas","Estudiantes","CanalDominante","Region","Disciplina","Edición"]
    return pd.DataFrame(rows, columns=cols)

if "df" not in st.session_state:
    st.session_state.df = seed_data()
if "notes" not in st.session_state:
    st.session_state.notes = []  # list of dicts

df = st.session_state.df

# ---------- Funciones ----------
def calc_ingresos(row):
    if row.UnidadPrecio == "MES":
        meses = int(row.DuraciónMeses if pd.notna(row.DuraciónMeses) else 6)
        return row.PrecioUnidadMXN * meses * row.Estudiantes
    else:
        sem = int(row.DuraciónSemanas if pd.notna(row.DuraciónSemanas) else 8)
        return row.PrecioUnidadMXN * sem * row.Estudiantes

def k_formatter(x):  # 1234000 -> 1.23M
    if x >= 1_000_000: return f"{x/1_000_000:.2f}M"
    if x >= 1_000: return f"{x/1_000:.1f}k"
    return f"{int(x)}"

def chips(items):
    return " ".join([f"<span class='badge'>{x}</span>" for x in items])

# ---------- Sidebar filtros ----------
with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    year = st.selectbox("Año", sorted(df["Año"].unique()), index=len(sorted(df["Año"].unique()))-1)
    progs = st.multiselect("Programa", sorted(df["Programa"].unique()), default=sorted(df["Programa"].unique()))
    canales = st.multiselect("Canal", CANALES, default=CANALES)
    regiones = st.multiselect("Región", REGIONES, default=REGIONES)
    st.markdown("<hr/>", unsafe_allow_html=True)
    with st.expander("➕ Agregar edición rápidamente"):
        c1,c2 = st.columns(2)
        with c1:
            y_new = st.selectbox("Año nuevo", sorted(df["Año"].unique()), key="y_new")
            prog_new = st.selectbox("Programa nuevo", [p[0] for p in PROGRAMAS], key="prog_new")
            mes_new = st.selectbox("Mes", MONTHS, key="mes_new")
            est_new = st.number_input("Estudiantes", 5, 500, 120, key="est_new")
        with c2:
            canal_new = st.selectbox("Canal", CANALES, key="canal_new")
            region_new = st.selectbox("Región", REGIONES, key="reg_new")
            disc_new = st.selectbox("Disciplina", DISCIP, key="disc_new")
            fecha_new = date(y_new, MONTHS.index(mes_new)+1, 1)
        if st.button("Agregar edición", use_container_width=True):
            P = {p[0]:p for p in PROGRAMAS}[prog_new]
            new_row = {
                "FechaInicio": fecha_new, "Año": y_new, "MesNum": MONTHS.index(mes_new)+1, "Mes": mes_new,
                "Programa": P[0], "Modalidad": P[1], "UnidadPrecio": P[2], "PrecioUnidadMXN": P[3],
                "DuraciónMeses": P[4], "DuraciónSemanas": P[5], "Estudiantes": est_new,
                "CanalDominante": canal_new, "Region": region_new, "Disciplina": disc_new,
                "Edición": f"{prog_new[:3].upper()}-{y_new}-{mes_new}"
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.toast("Edición agregada ✅")

# ---------- Encabezado ----------
st.markdown(f"<div class='card'><span class='badge'>Dashboard</span> "
            f"<b>Programas de formación · 2022–2025</b><br>"
            f"<span class='small'>Filtros activos: {chips([str(year)])} {chips(progs[:3]+(['…'] if len(progs)>3 else []))} "
            f"{chips(canales[:2]+(['…'] if len(canales)>2 else []))}</span></div>", unsafe_allow_html=True)

# ---------- Dataset filtrado ----------
f = df[(df["Año"]==year) & (df["Programa"].isin(progs)) & (df["CanalDominante"].isin(canales)) & (df["Region"].isin(regiones))].copy()
if f.empty:
    st.warning("No hay datos con los filtros actuales. Ajusta opciones en la barra lateral.")
    st.stop()

f["IngresosMXN"] = f.apply(calc_ingresos, axis=1)

# ---------- KPIs ----------
c1,c2,c3,c4 = st.columns(4)
with c1:
    st.markdown("<div class='box kpi'><div><h4>Estudiantes (año)</h4>"
                f"<div class='val'>{int(f['Estudiantes'].sum())}</div></div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='box kpi'><div><h4>Ingresos estimados</h4>"
                f"<div class='val'>${k_formatter(f['IngresosMXN'].sum())} MXN</div></div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='box kpi'><div><h4>Ediciones</h4>"
                f"<div class='val'>{f['Edición'].nunique()}</div></div></div>", unsafe_allow_html=True)
with c4:
    top_prog = f.groupby("Programa")["Estudiantes"].sum().sort_values(ascending=False).index[0]
    st.markdown("<div class='box kpi'><div><h4>Programa líder</h4>"
                f"<div class='val'>{top_prog}</div></div></div>", unsafe_allow_html=True)

st.markdown("<hr class='sep'/>", unsafe_allow_html=True)

# ---------- Tabs principales ----------
tabs = st.tabs(["📊 Overview", "👥 Estudiantes", "💵 Ingresos", "🌍 Regiones & Canales", "🧱 Heatmap", "📝 Datos & Notas"])

# ===== Overview =====
with tabs[0]:
    cA, cB = st.columns([1.3, 1], gap="large")

    # A) Estudiantes por mes x programa
    A = (f.groupby(["MesNum","Mes","Programa"], as_index=False)["Estudiantes"].sum())
    chartA = alt.Chart(A).mark_bar().encode(
        x=alt.X('Mes:N', sort=MONTHS, title="Mes"),
        y=alt.Y('Estudiantes:Q', title='Estudiantes'),
        color=alt.Color('Programa:N', legend=alt.Legend(title="Programa")),
        tooltip=['Programa','Mes','Estudiantes']
    ).properties(height=320)
    cA.markdown("**A) Estudiantes por mes x programa**")
    cA.altair_chart(chartA, use_container_width=True)
    cA.caption("Volumen mensual por programa, considerando los filtros.")

    # B) Tendencia mensual (línea)
    B = f.groupby(["MesNum","Mes"], as_index=False)["Estudiantes"].sum()
    chartB = alt.Chart(B).mark_line(point=True).encode(
        x=alt.X('Mes:N', sort=MONTHS),
        y=alt.Y('Estudiantes:Q'),
        tooltip=['Mes','Estudiantes']
    ).properties(height=320)
    cB.markdown("**B) Tendencia mensual de estudiantes**")
    cB.altair_chart(chartB, use_container_width=True)
    cB.caption("Evolución de estudiantes por mes durante el año seleccionado.")

# ===== Estudiantes =====
with tabs[1]:
    left, right = st.columns([1.2, 1], gap="large")

    # Tabla editable de ediciones (algunas columnas editables)
    editable_cols = {
        "Estudiantes": st.column_config.NumberColumn(min_value=1, max_value=1000, step=1),
        "PrecioUnidadMXN": st.column_config.NumberColumn(min_value=100, max_value=10000, step=50),
        "CanalDominante": st.column_config.SelectboxColumn(options=CANALES),
        "Region": st.column_config.SelectboxColumn(options=REGIONES),
        "Nota": st.column_config.TextColumn(help="Comentarios por edición")
    }
    show_cols = ["FechaInicio","Año","Mes","Programa","Modalidad","UnidadPrecio","PrecioUnidadMXN",
                 "DuraciónMeses","DuraciónSemanas","Estudiantes","CanalDominante","Region","Edición"]
    left.markdown("**Ediciones (editable)**")
    edit_df = st.data_editor(f.assign(Nota=""), column_config=editable_cols, hide_index=True, use_container_width=True)
    left.caption("Edita estudiantes/precio/canal/región por edición. Los KPIs y gráficos se recalculan si presionas “Aplicar cambios”.")

    if left.button("Aplicar cambios a la base", type="primary"):
        # Reconciliar cambios por clave Edición+Año+Programa
        key_cols = ["Edición","Año","Programa","Mes","UnidadPrecio"]
        base = st.session_state.df
        merged = base.merge(edit_df[["Edición","Estudiantes","PrecioUnidadMXN","CanalDominante","Region"]],
                            on="Edición", how="left", suffixes=("","_new"))
        for col in ["Estudiantes","PrecioUnidadMXN","CanalDominante","Region"]:
            merged[col] = np.where(merged[col+"_new"].notna(), merged[col+"_new"], merged[col])
            merged.drop(columns=[col+"_new"], inplace=True)
        st.session_state.df = merged
        st.toast("Cambios aplicados ✅")
        st.experimental_rerun()

    # Distribución por programa (barra horizontal)
    right.markdown("**Distribución por programa**")
    P = f.groupby("Programa", as_index=False)["Estudiantes"].sum().sort_values("Estudiantes")
    chartP = alt.Chart(P).mark_bar().encode(
        x=alt.X('Estudiantes:Q'),
        y=alt.Y('Programa:N', sort=None),
        tooltip=['Programa','Estudiantes']
    ).properties(height=max(240, 30*len(P)))
    right.altair_chart(chartP, use_container_width=True)
    right.caption("Acumulado de estudiantes por programa con filtros activos.")

# ===== Ingresos =====
with tabs[2]:
    c1, c2 = st.columns([1.3, 1], gap="large")

    # Ingresos por mes y programa (área apilada)
    R = f.groupby(["MesNum","Mes","Programa"], as_index=False)["IngresosMXN"].sum()
    chartR = alt.Chart(R).mark_area(opacity=0.85).encode(
        x=alt.X('Mes:N', sort=MONTHS),
        y=alt.Y('IngresosMXN:Q', title="MXN"),
        color=alt.Color('Programa:N'),
        tooltip=['Programa','Mes', alt.Tooltip('IngresosMXN:Q', format=",.0f")]
    ).properties(height=340)
    c1.markdown("**Ingresos por mes x programa (estimado)**")
    c1.altair_chart(chartR, use_container_width=True)
    c1.caption("Cálculo según unidad de cobro (MES/SEM) y duración definida por programa.")

    # Ticket “promedio” por estudiante (estimado)
    if f["Estudiantes"].sum() > 0:
        tkt = int(f["IngresosMXN"].sum() / f["Estudiantes"].sum())
    else:
        tkt = 0
    c2.markdown("**Indicadores de monetización**")
    c2.metric("Ticket estimado por estudiante", f"${k_formatter(tkt)} MXN")
    c2.metric("Ingresos totales estimados", f"${k_formatter(f['IngresosMXN'].sum())} MXN")
    c2.caption("Valores aproximados, útiles para planeación y control.")

# ===== Regiones & Canales =====
with tabs[3]:
    left, right = st.columns(2, gap="large")
    # Regiones
    G = f.groupby("Region", as_index=False)["Estudiantes"].count().rename(columns={"Estudiantes":"Inscripciones"}).sort_values("Inscripciones")
    chartG = alt.Chart(G).mark_bar().encode(
        x=alt.X('Inscripciones:Q'),
        y=alt.Y('Region:N', sort=None),
        tooltip=['Region','Inscripciones']
    ).properties(height=max(240, 28*len(G)))
    left.markdown("**Top regiones**")
    left.altair_chart(chartG, use_container_width=True)
    left.caption("Conteo de inscripciones por región.")

    # Canales
    C = f.groupby("CanalDominante", as_index=False)["Estudiantes"].count().rename(columns={"Estudiantes":"Inscripciones"})
    chartC = alt.Chart(C).mark_bar().encode(
        x=alt.X('CanalDominante:N', title="Canal"),
        y=alt.Y('Inscripciones:Q'),
        tooltip=['CanalDominante','Inscripciones']
    ).properties(height=300)
    right.markdown("**Canales de adquisición**")
    right.altair_chart(chartC, use_container_width=True)
    right.caption("Principales fuentes de adquisición para las ediciones filtradas.")

# ===== Heatmap =====
with tabs[4]:
    H = f.groupby(["MesNum","Mes","Programa"], as_index=False)["Estudiantes"].sum()
    heat = alt.Chart(H).mark_rect().encode(
        x=alt.X('Mes:N', sort=MONTHS),
        y=alt.Y('Programa:N'),
        color=alt.Color('Estudiantes:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['Programa','Mes','Estudiantes']
    ).properties(height=max(240, 28*len(H["Programa"].unique())))
    st.markdown("**Heatmap Mes × Programa (intensidad = estudiantes)**")
    st.altair_chart(heat, use_container_width=True)
    st.caption("Rápida detección de picos y valles por programa y mes.")

# ===== Datos & Notas =====
with tabs[5]:
    t1, t2 = st.tabs(["📄 Datos (filtrados)", "🗒️ Notas del equipo"])
    with t1:
        st.markdown("**Tabla base (con ingresos)**")
        show = f.copy()
        show["IngresosMXN"] = show["IngresosMXN"].round(0).astype(int)
        st.dataframe(show.sort_values(["MesNum","Programa"]), use_container_width=True, hide_index=True)
        st.caption("Puedes descargar la base filtrada para respaldos o análisis adicional.")
        st.download_button("Descargar CSV filtrado", show.to_csv(index=False).encode("utf-8"), file_name=f"cursos_{year}.csv", mime="text/csv")
    with t2:
        with st.form("add_note"):
            nc1, nc2 = st.columns([3,1])
            with nc1:
                note_text = st.text_area("Escribe una nota (visible para el equipo):", height=120,
                                         placeholder="Ej. Revisar pricing de MCP y pauta con micro-influencers…")
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
            notes_df = pd.DataFrame(st.session_state.notes)
            notes_df = notes_df.sort_values("ts", ascending=False)
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

# ---------- Pie / Ayudas ----------
st.markdown("<hr class='sep'/>", unsafe_allow_html=True)
with st.expander("ℹ️ ¿Qué incluye este dashboard?"):
    st.markdown("""
- **KPIs** de estudiantes, ingresos estimados, ediciones y programa líder.
- **Gráficos interactivos**: barras apiladas por mes/programa, línea mensual, áreas por ingresos, barras por región/canal y **heatmap**.
- **Editor de datos** (ediciones) con columnas editables; puedes **agregar** nuevas ediciones en la barra lateral.
- **Notas del equipo** con exportación a CSV.
- Se adapta a tema claro/oscuro del dispositivo y mantiene una estética limpia y profesional.
""")
