"""
app.py — U-AWIS (Unified Aviation Weather Information System)
================================================================
MAIN ENTRY / ROUTER — TNI AU Tactical Weather Platform
----------------------------------------------------------------
File ini HANYA berperan sebagai "bingkai" (shell) yang menyatukan
tiga dashboard mandiri:

    - acs_dashboard.py        → ACS Climatology Statistics
    - meteogram_dashboard.py  → Meteogram Master Dashboard
    - metar_dashboard.py      → METAR / TAF Tactical Ops

ATURAN MUTLAK YANG DIPATUHI FILE INI:
  1. Ketiga file di atas TIDAK diubah, di-import, atau di-refactor.
     Mereka dijalankan APA ADANYA oleh Streamlit sebagai "page"
     lewat st.navigation()/st.Page() — mekanisme multipage RESMI
     Streamlit — sehingga st.set_page_config() dan seluruh logika,
     caching, serta tampilan asli tiap file tetap 100% utuh.
  2. CSS/tema yang di-inject di sini hanya mempercantik "chrome"
     milik shell (banner, status bar, kartu Beranda, sidebar-brand,
     tombol page_link). Tidak ada selector yang mematikan/menimpa
     latar konten (.stApp background) milik dashboard, sehingga
     tema militer metar & saklar gelap/terang meteogram tetap jalan.
  3. Jika selector cosmetic tidak cocok di versi Streamlit tertentu,
     styling gagal secara "diam" (degrade) — TIDAK menimbulkan error.

Struktur repo (flat, sesuai repo U-AWIS):
    app.py
    acs_dashboard.py
    meteogram_dashboard.py
    metar_dashboard.py
    *.xlsx            (semua file data di root — tanpa folder data/)
    requirements.txt
"""

from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# 1) KONFIGURASI DASAR — WAJIB perintah Streamlit PERTAMA.
#    Tiap page (acs/meteogram/metar) tetap boleh memanggil
#    st.set_page_config() sendiri untuk override judul/ikon tab.
# ============================================================
st.set_page_config(
    page_title="U_AWIS — TNI AU",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2) STATE & PALET TEMA (Gelap / Terang)
#    Palet "tactical": navy blue, slate gray, aksen emas TNI AU,
#    dan biru baja (steel blue). Nyaman di mata, tidak silau.
# ============================================================
if "uawis_dark" not in st.session_state:
    st.session_state.uawis_dark = True  # default: mode gelap ala ruang ops

THEME = {
    True: dict(   # ---------- DARK / TACTICAL ----------
        app="#0B1220", bg2="#0E1730", card="#131C31", card2="#0F172B",
        border="#24314F", grid="#1B2740",
        text="#E9EEF9", muted="#93A2C4",
        gold="#E0B54A", steel="#3E7CB1", cyan="#38BDF8", ok="#37C77F",
        shadow="0 14px 34px rgba(0,0,0,0.45)",
        heroA="#0E1730", heroB="#152443",
    ),
    False: dict(  # ---------- LIGHT / COZY ----------
        app="#EEF2F8", bg2="#F5F7FC", card="#FFFFFF", card2="#F7F9FD",
        border="#D9E1EE", grid="#E7ECF5",
        text="#12213F", muted="#54627C",
        gold="#B3860B", steel="#1B4965", cyan="#1E6FA8", ok="#1F9D5B",
        shadow="0 10px 24px rgba(19,33,64,0.10)",
        heroA="#1B2C50", heroB="#26406F",
    ),
}


def inject_shell_css(c: dict) -> None:
    """Suntikkan CSS COSMETIK untuk elemen milik shell saja.

    Aman & degrade-friendly: hanya menyentuh top-nav, sidebar-brand,
    kartu Beranda, dan tombol page_link. Tidak mengunci latar konten
    dashboard, jadi tema asli ketiga file tetap berlaku penuh.
    """
    st.markdown(
        f"""
        <style>
        /* ---- Top navigation bar (st.navigation position='top') ---- */
        header[data-testid="stHeader"] {{
            background: linear-gradient(90deg, {c['heroA']} 0%, {c['heroB']} 100%);
            border-bottom: 1px solid {c['border']};
        }}
        [data-testid="stHeader"] a, [data-testid="stHeader"] span,
        [data-testid="stHeader"] p {{ color: {c['text']} !important; }}

        /* ---- Kartu & badge Beranda ---- */
        .uawis-hero {{
            background: linear-gradient(135deg, {c['heroA']} 0%, {c['heroB']} 100%);
            border: 1px solid {c['border']}; border-radius: 20px;
            padding: 34px 32px; box-shadow: {c['shadow']};
            position: relative; overflow: hidden;
        }}
        .uawis-hero::after {{
            content:""; position:absolute; right:-40px; top:-40px;
            width:220px; height:220px; border-radius:50%;
            background: radial-gradient(circle, {c['gold']}22 0%, transparent 70%);
        }}
        .uawis-kicker {{
            display:inline-block; font-size:.68rem; letter-spacing:2px;
            font-weight:800; text-transform:uppercase; color:{c['gold']};
            border:1px solid {c['gold']}66; border-radius:999px;
            padding:4px 12px; margin-bottom:14px;
        }}
        .uawis-title {{ color:#FFFFFF; font-size:2.15rem; font-weight:800;
            margin:0 0 8px 0; letter-spacing:.3px; }}
        .uawis-sub {{ color:#C7D3EC; font-size:1rem; line-height:1.7;
            max-width:820px; margin:0; }}

        .uawis-badge {{
            background:{c['card']}; border:1px solid {c['border']};
            border-radius:14px; padding:14px 12px; text-align:center;
            box-shadow:{c['shadow']};
        }}
        .uawis-badge .ic {{ font-size:1.5rem; }}
        .uawis-badge .tt {{ color:{c['text']}; font-weight:700; font-size:.92rem;
            margin-top:4px; }}
        .uawis-badge .ss {{ color:{c['muted']}; font-size:.74rem; }}

        .uawis-card {{
            background:{c['card']}; border:1px solid {c['border']};
            border-radius:18px; padding:22px 20px 16px 20px; min-height:236px;
            box-shadow:{c['shadow']}; transition:transform .18s ease,
            border-color .18s ease, box-shadow .18s ease;
        }}
        .uawis-card:hover {{ transform:translateY(-4px);
            border-color:{c['gold']}; box-shadow:0 18px 40px rgba(0,0,0,.35); }}
        .uawis-card .cic {{ font-size:1.85rem; }}
        .uawis-card .ctt {{ color:{c['text']}; font-weight:800; font-size:1.06rem;
            margin:8px 0 8px 0; }}
        .uawis-card .cds {{ color:{c['muted']}; font-size:.85rem; line-height:1.6; }}

        .uawis-section {{ color:{c['text']}; font-weight:800; font-size:1.2rem;
            margin:6px 0 2px 0; }}
        .uawis-hr {{ height:1px; background:{c['border']}; border:none;
            margin:14px 0 6px 0; }}

        /* ---- Tombol page_link agar rapi & sewarna ---- */
        [data-testid="stPageLink"] a {{
            border:1px solid {c['border']} !important; border-radius:12px !important;
            background:{c['card2']} !important; font-weight:600 !important;
        }}
        [data-testid="stPageLink"] a:hover {{
            border-color:{c['gold']} !important; background:{c['bg2']} !important;
        }}

        /* ---- Sidebar brand block ---- */
        .uawis-side-brand {{ line-height:1.25; }}
        .uawis-side-brand .n {{ font-size:1.05rem; font-weight:800; color:{c['text']}; }}
        .uawis-side-brand .d {{ font-size:.72rem; color:{c['muted']}; }}
        .uawis-side-foot {{ font-size:.68rem; color:{c['muted']};
            line-height:1.5; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def tactical_status_bar(c: dict) -> None:
    """Status strip ops: jam UTC & lokal live (JS) + indikator sistem.

    Dirender via components.html (iframe terisolasi) sehingga TOTAL
    aman terhadap CSS/JS dashboard manapun — tidak ada kebocoran style.
    """
    dark = st.session_state.uawis_dark
    strip_bg = c["heroA"] if dark else "#FFFFFF"
    components.html(
        f"""
        <div id="uawis-ops" style="
            font-family:-apple-system,Segoe UI,Roboto,system-ui,sans-serif;
            background:{strip_bg}; border:1px solid {c['border']};
            border-radius:12px; padding:8px 16px; display:flex;
            align-items:center; justify-content:space-between; flex-wrap:wrap;
            gap:10px; box-shadow:{c['shadow']};">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="width:9px;height:9px;border-radius:50%;
                background:{c['ok']};box-shadow:0 0 0 4px {c['ok']}33;
                display:inline-block;"></span>
            <span style="font-weight:800;letter-spacing:1px;font-size:.72rem;
                text-transform:uppercase;color:{c['ok']};">SYSTEM OPERATIONAL</span>
            <span style="color:{c['muted']};font-size:.72rem;">· U-AWIS · TNI AU</span>
          </div>
          <div style="display:flex;align-items:center;gap:18px;
              font-variant-numeric:tabular-nums;">
            <div style="text-align:right;">
              <div style="font-size:.6rem;letter-spacing:1.5px;color:{c['gold']};
                  font-weight:800;">UTC / ZULU</div>
              <div id="uawis-utc" style="font-size:.95rem;font-weight:700;
                  color:{c['text']};">--:--:--</div>
            </div>
            <div style="width:1px;height:26px;background:{c['border']};"></div>
            <div style="text-align:right;">
              <div style="font-size:.6rem;letter-spacing:1.5px;color:{c['steel']};
                  font-weight:800;">LOKAL / WIB</div>
              <div id="uawis-loc" style="font-size:.95rem;font-weight:700;
                  color:{c['text']};">--:--:--</div>
            </div>
          </div>
        </div>
        <script>
          function pad(n){{return String(n).padStart(2,'0');}}
          function tick(){{
            const now = new Date();
            const u = pad(now.getUTCHours())+':'+pad(now.getUTCMinutes())+':'+pad(now.getUTCSeconds());
            // WIB = UTC+7
            const w = new Date(now.getTime() + 7*3600*1000);
            const l = pad(w.getUTCHours())+':'+pad(w.getUTCMinutes())+':'+pad(w.getUTCSeconds());
            const eu = document.getElementById('uawis-utc');
            const el = document.getElementById('uawis-loc');
            if(eu) eu.textContent = u + 'Z';
            if(el) el.textContent = l + ' WIB';
          }}
          tick(); setInterval(tick, 1000);
        </script>
        """,
        height=64,
    )


# ============================================================
# 3) DEFINISI HALAMAN (Page) — merujuk LANGSUNG ke file asli.
#    Path relatif terhadap lokasi app.py (root repo).
# ============================================================
acs_pg = st.Page("acs_dashboard.py", title="ACS Climatology", icon="📊")
meteogram_pg = st.Page("meteogram_dashboard.py", title="Meteogram Master", icon="📈")
metar_pg = st.Page("metar_dashboard.py", title="METAR / TAF Ops", icon="📡")


def render_home():
    """Beranda U-AWIS — dibangun mandiri, tidak terkait file dashboard."""
    c = THEME[st.session_state.uawis_dark]
    inject_shell_css(c)

    # ---- Status bar taktis (jam live + status sistem) ----
    tactical_status_bar(c)
    st.write("")

    # ---- Hero ----
    st.markdown(
        f"""
        <div class="uawis-hero">
            <span class="uawis-kicker">Platform Cuaca Operasional Penerbangan</span>
            <div class="uawis-title">🛡️ U-AWIS</div>
            <p class="uawis-sub">
                <b>Unified Aviation Weather Information System</b> menghimpun tiga modul
                analisis cuaca penerbangan ke dalam satu platform komando: statistik
                klimatologi lapangan (ACS), meteogram sinoptik multi-tahun, serta data
                METAR/TAF taktis — untuk mendukung kesiapan dan kecepatan pengambilan
                keputusan misi penerbangan TNI Angkatan Udara.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # ---- Ringkasan kapabilitas ----
    badges = [
        ("🗓️", "Klimatologi 2021–2025", "6 parameter ACS"),
        ("📡", "METAR / TAF", "Data taktis per pangkalan"),
        ("📈", "Meteogram", "Analisis multi-tahun & musiman"),
        ("🛰️", "Standar ICAO/WMO", "Interpretasi operasional"),
    ]
    for col, (icon, title, sub) in zip(st.columns(4), badges):
        with col:
            st.markdown(
                f"""<div class="uawis-badge">
                        <div class="ic">{icon}</div>
                        <div class="tt">{title}</div>
                        <div class="ss">{sub}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown('<div class="uawis-section">Modul Operasional</div>', unsafe_allow_html=True)
    st.markdown('<hr class="uawis-hr">', unsafe_allow_html=True)

    cards = [
        (acs_pg, "📊", "ACS Climatology Statistics",
         "Aerodrome Climatological Summary 2021–2025: frekuensi & rata-rata suhu, "
         "kelembapan relatif, visibility, cloud base, serta distribusi arah dan "
         "kecepatan angin — lengkap dengan interpretasi operasional ICAO/WMO."),
        (meteogram_pg, "📈", "Meteogram Master Dashboard",
         "Meteogram sinoptik per jam & per tahun untuk suhu, kelembapan, visibility, "
         "cloud base (HS), dan wind rose musiman — dengan mode tampilan gelap/terang "
         "internal untuk analisis pola cuaca mendalam."),
        (metar_pg, "📡", "METAR / TAF Tactical Ops",
         "METAR & TAF per pangkalan udara, decoding otomatis, unduh laporan PDF, serta "
         "visualisasi windrose taktis bergaya ruang operasi untuk kesiapan misi."),
    ]

    for col, (page_obj, icon, title, desc) in zip(st.columns(3), cards):
        with col:
            st.markdown(
                f"""<div class="uawis-card">
                        <div class="cic">{icon}</div>
                        <div class="ctt">{title}</div>
                        <div class="cds">{desc}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
            st.page_link(page_obj, label=f"Buka {title}", icon="➡️",
                         use_container_width=True)

    st.write("")
    st.markdown(
        f"""
        <div style="text-align:center;color:{c['muted']};font-size:.74rem;
                    padding-top:14px;border-top:1px solid {c['border']};margin-top:8px;">
            U-AWIS · Unified Aviation Weather Information System &nbsp;•&nbsp;
            Dibangun di atas Streamlit &amp; Plotly &nbsp;•&nbsp;
            Untuk Operasional TNI AU &nbsp;•&nbsp; © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


home_pg = st.Page(render_home, title="Beranda", icon="🏠", default=True)

# ============================================================
# 4) NAVIGASI — posisi "top" agar sidebar tiap dashboard (yang
#    masing-masing sudah punya menu/filter sendiri) tetap bersih.
# ============================================================
pg = st.navigation(
    [home_pg, acs_pg, meteogram_pg, metar_pg],
    position="top",
)

# ---- CSS shell diterapkan di SEMUA halaman (cosmetic, aman) ----
c = THEME[st.session_state.uawis_dark]
inject_shell_css(c)

# ---- Brand + saklar tema di sidebar (tidak mengubah isi sidebar dashboard) ----
with st.sidebar:
    st.markdown(
        f"""<div class="uawis-side-brand">
                <span class="n">🛡️ U-AWIS</span><br>
                <span class="d">Unified Aviation Weather Information System</span>
            </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:.5rem 0 .7rem 0;'>", unsafe_allow_html=True)

    st.session_state.uawis_dark = st.toggle(
        "🌙 Mode Gelap (Tactical)",
        value=st.session_state.uawis_dark,
        help="Saklar gelap/terang untuk Beranda & branding U-AWIS. "
             "Meteogram punya saklar tema sendiri; ACS & METAR memakai "
             "tema tetap sesuai desain aslinya.",
    )

    st.markdown("<hr style='margin:.7rem 0 .6rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="uawis-side-foot">
                <b>TNI ANGKATAN UDARA</b><br>
                Aviation Weather Decision Support<br>
                Build {datetime.now(timezone.utc):%Y.%m.%d} · v2.0
            </div>""",
        unsafe_allow_html=True,
    )

# ============================================================
# 5) EKSEKUSI HALAMAN AKTIF — dibungkus jaring pengaman router.
#    (Bukan pengganti error handling internal tiap dashboard.)
# ============================================================
try:
    pg.run()
except Exception as e:
    st.error("⚠️ Terjadi kendala saat memuat modul ini. "
             "Silakan kembali ke Beranda dan coba lagi.")
    with st.expander("Detail teknis (untuk administrator)"):
        st.exception(e)
    st.page_link(home_pg, label="Kembali ke Beranda", icon="🏠")
