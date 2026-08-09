"""
app.py — U-AWIS (Unified Aviation Weather Information System)
================================================================
Entry point / router Streamlit yang MENGGABUNGKAN tiga dashboard mandiri:
  - acs_dashboard.py        (ACS Climatology Statistics)
  - meteogram_dashboard.py  (Meteogram Master Dashboard)
  - metar_dashboard.py      (METAR / TAF Tactical Ops)

PENTING — PRINSIP DESAIN:
Ketiga file di atas TIDAK disentuh, diedit, atau di-refactor sedikit pun.
File ini hanya berperan sebagai "bingkai" (shell): landing page terpadu,
navigasi atas, branding U-AWIS, dan tema gelap/terang untuk bagian yang
dibangun sendiri di file ini. Setiap dashboard tetap berjalan dengan kode,
caching, dan tampilan aslinya 100% utuh — dieksekusi oleh Streamlit sebagai
"page" lewat st.navigation()/st.Page(), mekanisme resmi Streamlit untuk
multipage app (bukan import module), sehingga st.set_page_config() dan
seluruh logika di masing-masing file tetap berfungsi persis seperti saat
dijalankan sendiri-sendiri.

Struktur repo yang diasumsikan (flat, sesuai repo U-AWIS kalian):
    app.py
    acs_dashboard.py
    meteogram_dashboard.py
    metar_dashboard.py
    *.xlsx (semua file data, ada di root — TIDAK perlu folder data/)
    requirements.txt
"""

import streamlit as st

# ============================================================
# 1) KONFIGURASI DASAR APLIKASI
#    Harus jadi perintah Streamlit PERTAMA di file ini.
#    Streamlit modern (st.navigation/st.Page) mengizinkan setiap
#    halaman/page memanggil st.set_page_config() miliknya sendiri
#    untuk MENIMPA (override) konfigurasi default ini — sehingga
#    acs_dashboard.py, meteogram_dashboard.py, dan metar_dashboard.py
#    tetap bisa punya judul tab & ikon masing-masing tanpa error.
# ============================================================
st.set_page_config(
    page_title="U-AWIS | Unified Aviation Weather Information System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2) STATE & TEMA SHELL (Gelap/Terang)
#    Tema ini HANYA berlaku untuk elemen yang dirender oleh file
#    ini sendiri (banner atas, tag sidebar, dan halaman Beranda).
#    Tidak pernah menyentuh selector global (.stApp, body,
#    .block-container), sehingga tidak mungkin mengubah tampilan
#    asli ketiga dashboard yang sudah punya tema sendiri.
# ============================================================
if "uawis_dark" not in st.session_state:
    st.session_state.uawis_dark = True  # default: tema gelap ala ruang ops

THEME = {
    True: dict(   # ---- Dark Mode: navy gelap lembut, bukan hitam pekat ----
        bg2="#141B2C", card="#161F33", border="#283552",
        text="#E9EDF6", muted="#95A3C2", accent="#D9AE3A", accent2="#3D7AB5",
        shadow="0 10px 28px rgba(0,0,0,0.40)",
    ),
    False: dict(  # ---- Light Mode: putih gading lembut, bukan putih polos ----
        bg2="#FFFFFF", card="#FFFFFF", border="#DCE3EC",
        text="#132140", muted="#54627C", accent="#B3860B", accent2="#1B4965",
        shadow="0 8px 20px rgba(19,33,64,0.10)",
    ),
}

# ============================================================
# 3) DEFINISI HALAMAN (Page) — merujuk LANGSUNG ke file asli.
#    Path relatif terhadap lokasi app.py (root repo).
# ============================================================
acs_pg = st.Page("acs_dashboard.py", title="ACS Climatology", icon="📊")
meteogram_pg = st.Page("meteogram_dashboard.py", title="Meteogram Master", icon="📈")
metar_pg = st.Page("metar_dashboard.py", title="METAR / TAF Tactical Ops", icon="📡")


def render_home():
    """Halaman Beranda U-AWIS — dibangun baru, tidak terkait file dashboard manapun."""
    c = THEME[st.session_state.uawis_dark]

    st.markdown(
        f"""
        <div style="background:{c['card']};border:1px solid {c['border']};
                    border-radius:18px;padding:34px 30px;margin-bottom:22px;
                    box-shadow:{c['shadow']};">
            <h1 style="color:{c['text']};margin:0 0 6px 0;font-size:2.1rem;">
                Selamat Datang di U-AWIS
            </h1>
            <p style="color:{c['muted']};font-size:1rem;max-width:780px;
                       line-height:1.65;margin:0;">
                <b>Unified Aviation Weather Information System</b> menghimpun tiga modul
                analisis cuaca penerbangan ke dalam satu platform operasional: statistik
                klimatologi lapangan (ACS), meteogram sinoptik multi-tahun, serta data
                METAR/TAF taktis — untuk mendukung kesiapan pengambilan keputusan
                penerbangan secara cepat dan terpadu.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    badges = [
        ("🗓️", "Klimatologi 2021–2025", "6 parameter data ACS"),
        ("📡", "METAR / TAF", "Data taktis per pangkalan"),
        ("📈", "Meteogram", "Analisis multi-tahun & musiman"),
    ]
    for col, (icon, title, sub) in zip(st.columns(3), badges):
        with col:
            st.markdown(
                f"""
                <div style="background:{c['bg2']};border:1px solid {c['border']};
                            border-radius:12px;padding:14px 12px;text-align:center;">
                    <div style="font-size:1.4rem;">{icon}</div>
                    <div style="color:{c['text']};font-weight:600;font-size:0.92rem;">
                        {title}
                    </div>
                    <div style="color:{c['muted']};font-size:0.75rem;">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(f"<h3 style='color:{c['text']};'>Modul Operasional</h3>", unsafe_allow_html=True)

    cards = [
        (acs_pg, "📊", "ACS Climatology Statistics",
         "Statistik klimatologi lapangan (Aerodrome Climatological Summary) periode "
         "2021–2025: frekuensi & rata-rata suhu, kelembapan relatif, visibility, cloud "
         "base, serta distribusi arah dan kecepatan angin — lengkap dengan interpretasi "
         "operasional berbasis ICAO/WMO."),
        (meteogram_pg, "📈", "Meteogram Master Dashboard",
         "Meteogram sinoptik per jam dan per tahun untuk suhu, kelembapan, visibility, "
         "cloud base (HS), dan wind rose musiman — dilengkapi mode tampilan gelap/terang "
         "internal untuk analisis pola cuaca yang lebih mendalam."),
        (metar_pg, "📡", "METAR / TAF Tactical Ops",
         "Data METAR & TAF per pangkalan udara, decoding otomatis, unduh laporan PDF, "
         "serta visualisasi windrose taktis bergaya ruang operasi untuk kesiapan misi "
         "penerbangan."),
    ]

    for col, (page_obj, icon, title, desc) in zip(st.columns(3), cards):
        with col:
            st.markdown(
                f"""
                <div style="background:{c['card']};border:1px solid {c['border']};
                            border-radius:16px;padding:20px;min-height:230px;
                            box-shadow:{c['shadow']};">
                    <div style="font-size:1.7rem;">{icon}</div>
                    <div style="color:{c['text']};font-weight:700;font-size:1.05rem;
                                margin:6px 0 8px 0;">{title}</div>
                    <div style="color:{c['muted']};font-size:0.85rem;line-height:1.55;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page_obj, label=f"Buka {title}", icon="➡️", use_container_width=True)

    st.write("")
    st.markdown(
        f"""
        <div style="text-align:center;color:{c['muted']};font-size:0.75rem;
                    padding-top:12px;border-top:1px solid {c['border']};">
            U-AWIS · Unified Aviation Weather Information System &nbsp;•&nbsp;
            Dibangun di atas Streamlit &amp; Plotly &nbsp;•&nbsp; © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


home_pg = st.Page(render_home, title="Beranda", icon="🏠", default=True)

# ============================================================
# 4) NAVIGASI — posisi "top" sengaja dipilih agar sidebar setiap
#    dashboard (yang masing-masing sudah punya menu/filter sendiri)
#    tetap bersih dan tidak berebut ruang dengan menu navigasi utama.
# ============================================================
pg = st.navigation([home_pg, acs_pg, meteogram_pg, metar_pg], position="top")

# ---- Tag identitas ringkas di sidebar (tidak mengubah isi sidebar dashboard) ----
with st.sidebar:
    c = THEME[st.session_state.uawis_dark]
    st.markdown(
        f"""<div style="line-height:1.3;">
            <span style="font-size:1.05rem;font-weight:700;">🛡️ U-AWIS</span><br>
            <span style="font-size:0.72rem;color:{c['muted']};">
                Unified Aviation Weather Information System
            </span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:0.5rem 0 0.8rem 0;'>", unsafe_allow_html=True)

# ---- Banner atas + saklar tema (tampil di semua halaman) ----
c = THEME[st.session_state.uawis_dark]
st.markdown(
    f"""
    <div style="background:linear-gradient(90deg,{c['bg2']} 0%,{c['card']} 100%);
                border:1px solid {c['border']};border-radius:14px;
                padding:14px 22px;margin-bottom:10px;box-shadow:{c['shadow']};">
        <div style="display:flex;align-items:center;justify-content:space-between;
                    flex-wrap:wrap;gap:8px;">
            <div>
                <span style="font-size:1.3rem;font-weight:700;color:{c['text']};
                             letter-spacing:0.4px;">🛡️ U-AWIS</span>
                <span style="font-size:0.8rem;color:{c['muted']};margin-left:10px;">
                    Unified Aviation Weather Information System
                </span>
            </div>
            <div style="font-size:0.7rem;color:{c['accent']};font-weight:700;
                        letter-spacing:1px;text-transform:uppercase;">
                Platform Cuaca Operasional Penerbangan
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

_, col_toggle = st.columns([6, 1])
with col_toggle:
    st.session_state.uawis_dark = st.toggle(
        "🌙 Gelap",
        value=st.session_state.uawis_dark,
        help="Mode gelap/terang untuk Beranda & branding U-AWIS. "
             "Meteogram punya saklar tema sendiri di sidebar-nya; "
             "ACS dan METAR memakai tema tetap sesuai desain aslinya.",
    )

# ============================================================
# 5) EKSEKUSI HALAMAN AKTIF
#    Dibungkus try/except sebagai jaring pengaman tingkat-router
#    (bukan pengganti error handling internal tiap dashboard,
#    yang sudah masing-masing punya penanganannya sendiri).
# ============================================================
try:
    pg.run()
except Exception as e:
    st.error("⚠️ Terjadi kendala saat memuat modul ini. Silakan kembali ke Beranda dan coba lagi.")
    with st.expander("Detail teknis (untuk administrator)"):
        st.exception(e)
    st.page_link(home_pg, label="Kembali ke Beranda", icon="🏠")
