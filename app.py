import streamlit as st

# =====================================================================
# 1. BLACK-BOX ISOLATION MONKEY-PATCH (ANTI-CRASH LOGIC)
# Mencegah error duplikasi st.set_page_config() dari sub-halaman
# =====================================================================
if not hasattr(st, '_original_set_page_config'):
    st._original_set_page_config = st.set_page_config
    
    def robust_set_page_config(*args, **kwargs):
        if not st.session_state.get('_page_config_initialized', False):
            st.session_state['_page_config_initialized'] = True
            try:
                st._original_set_page_config(*args, **kwargs)
            except Exception:
                pass
        else:
            pass

    st.set_page_config = robust_set_page_config

# Set konfigurasi inisial pertama kali secara aman sebelum router berjalan
st.set_page_config(
    page_title="U-AWIS | Unified Aviation Weather",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# 2. CONTROLLER THEME ENGINE (POJOK KANAN ATAS)
# Solusi agar tidak ganda di Sidebar & mematuhi instruksi pojok kanan
# =====================================================================
if 'app_theme' not in st.session_state:
    st.session_state.app_theme = 'Dark Mode'

# Render pemilih mode tampilan di ujung kanan atas Main Area
top_col1, top_col2 = st.columns([8.5, 1.5])
with top_col2:
    st.session_state.app_theme = st.selectbox(
        "Tema Sistem",
        options=["Dark Mode", "Light Mode"],
        index=0 if st.session_state.app_theme == "Dark Mode" else 1,
        label_visibility="collapsed"
    )

# Inject CSS dinamis berdasarkan mode yang dipilih
if st.session_state.app_theme == "Light Mode":
    st.markdown("""
        <style>
        /* BASE LAYER LIGHT MODE */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }
        [data-testid="stSidebar"] {
            background-color: #F1F5F9 !important;
        }
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #0F172A !important;
        }
        h1, h2, h3, h4, h5, h6, .uawis-header h1 {
            color: #1E3A8A !important;
        }
        .uawis-header {
            background: linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%) !important;
            border-left: 6px solid #1E3A8A !important;
        }
        .module-card {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
        }
        .module-card h3 { color: #B45309 !important; }
        .module-card p { color: #475569 !important; }
        
        /* FIX VISIBILITAS DROPDOWN (ANTI-BLIND/TIDAK TERLIHAT) */
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
        }
        div[data-baseweb="popover"], div[data-baseweb="popover"] ul {
            background-color: #FFFFFF !important;
        }
        div[data-baseweb="popover"] li, div[data-baseweb="popover"] li span, div[data-baseweb="popover"] li p {
            color: #0F172A !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li:hover span {
            background-color: #E2E8F0 !important;
            color: #1E3A8A !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        /* BASE LAYER DARK MODE */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background-color: #0b0c0c !important;
            color: #cfd2c3 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111111 !important;
        }
        h1, h2, h3, h4, h5, h6, .uawis-header h1 {
            color: #a9df52 !important;
        }
        .uawis-header {
            background: linear-gradient(135deg, #162A4A 0%, #0D1B2A 100%) !important;
            border-left: 6px solid #00B4D8 !important;
        }
        
        /* FIX VISIBILITAS DROPDOWN (ANTI-BLIND/TIDAK TERLIHAT) */
        div[data-baseweb="select"] > div {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border: 1px solid #334155 !important;
        }
        div[data-baseweb="popover"], div[data-baseweb="popover"] ul {
            background-color: #1E293B !important;
        }
        div[data-baseweb="popover"] li, div[data-baseweb="popover"] li span, div[data-baseweb="popover"] li p {
            color: #FFFFFF !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li:hover span {
            background-color: #334155 !important;
            color: #00B4D8 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 3. GLOBAL FIX: SMART SIDEBAR & ANTI-CLIPPING DROPDOWN
# =====================================================================
st.markdown("""
    <style>
    /* A. MEMBUAT TATA LETAK SIDEBAR MENJADI PADAT TAPI RAPI */
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem !important;
        /* RUANG KOSONG TAK TERLIHAT (PHANTOM SPACE) */
        /* Ini menjamin dropdown paling bawah tidak akan pernah menabrak tepi layar */
        padding-bottom: 400px !important; 
    }
    
    /* Mengatur jarak (gap) antar elemen agar tidak terlalu jauh */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important; 
    }
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0 !important;
    }
    
    /* Merapatkan jarak batas garis horizontal (hr) */
    [data-testid="stSidebar"] hr {
        margin-top: 0.8rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* B. PENGATURAN DROPDOWN POPOVER */
    /* Kita kembalikan perilaku normal portal, hanya batasi tingginya agar rapi */
    div[data-baseweb="popover"] ul, 
    div[role="listbox"], 
    ul[role="listbox"] {
        max-height: 250px !important; 
        overflow-y: auto !important;
    }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# 4. SYSTEM HOMEPAGE RENDER (UI/UX OVERVIEW)
# =====================================================================
def render_home_page():
    st.markdown("""
        <style>
        .uawis-header {
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            margin-bottom: 35px;
        }
        .uawis-header h1 {
            margin: 0;
            font-size: 2.8rem;
            font-family: 'Consolas', monospace;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .status-badge {
            background-color: #059669;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            vertical-align: middle;
            margin-left: 10px;
        }
        .module-card {
            padding: 25px;
            border-radius: 10px;
            border-top: 4px solid #F59E0B;
            text-align: center;
            height: 100%;
            transition: transform 0.2s ease;
        }
        .module-card h3 { 
            font-size: 1.4rem; 
            margin-bottom: 15px;
        }
        .module-card p {
            font-size: 0.95rem;
            line-height: 1.5;
            font-family: sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="uawis-header">
            <h1>🌐 U-AWIS COMMAND CENTER</h1>
            <p>Unified Aviation Weather Information System — Sistem Terpadu Pemantauan Meteorologi Penerbangan</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📡 System Modules Status <span class='status-badge'>ONLINE</span>", unsafe_allow_html=True)
    st.write("") 
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="module-card">
            <h3>🛰️ Tactical METAR & TAF</h3>
            <p>Sistem pemantauan cuaca taktis real-time. Menampilkan data observasi (METAR) dan prakiraan (TAF) untuk pangkalan TNI AU di seluruh wilayah Indonesia.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="module-card">
            <h3>📊 Aviation Meteorology</h3>
            <p>Sistem rekapitulasi histori cuaca. Menyajikan ringkasan kondisi aerodrome RSN berdasarkan pengolahan data ACS periode 2021 hingga 2025.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="module-card">
            <h3>🌤️ Diurnal Patterns</h3>
            <p>Sistem analisis meteorologi lanjutan. Memetakan pola diurnal aerodrome RSN dari data ACS 2021-2025 untuk mendukung perencanaan penerbangan.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("ℹ️ **Petunjuk Penggunaan:** Silakan buka menu navigasi (Sidebar) di sebelah kiri layar untuk memilih dan menjalankan spesifik modul dashboard.")
    st.caption("U-AWIS Unified Platform © 2026")


# =====================================================================
# 5. REGISTRASI HALAMAN & RUN ROUTER NAVIGASI
# =====================================================================
page_home = st.Page(
    render_home_page, 
    title="U-AWIS Overview", 
    icon="🏠", 
    default=True
)

page_metar = st.Page(
    "metar_dashboard.py", 
    title="Tactical METAR & TAF", 
    icon="🛰️"
)

page_acs = st.Page(
    "acs_dashboard.py", 
    title="Aviation Meteorology", 
    icon="📊"
)

page_diurnal = st.Page(
    "meteogram_dashboard.py", 
    title="Diurnal Patterns", 
    icon="🌤️"
)

# Struktur Navigasi Utama dikelompokkan secara rapi
pg = st.navigation({
    "MAIN SYSTEM": [page_home],
    "OPERATIONAL MODULES": [page_metar, page_acs, page_diurnal]
})

# Menjalankan router inti Streamlit
pg.run()
