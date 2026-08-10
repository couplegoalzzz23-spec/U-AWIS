"""
app.py — U-AWIS (Unified Aviation Weather Information System)
================================================================
MAIN ENTRY / ROUTER — TNI AU Tactical Weather Platform  ·  v3.0
----------------------------------------------------------------
Menggabungkan tiga dashboard mandiri (TIDAK diubah sedikit pun):
    - metar_dashboard.py     → Tactical METAR & TAF   (desain GELAP)
    - acs_dashboard.py       → Aviation Meteorology    (desain TERANG)
    - meteogram_dashboard.py → Diurnal Patterns        (punya saklar sendiri)

PRINSIP DESAIN (alasan teknis, dibuktikan dari kode aslinya):
  • acs_dashboard.py mengunci grafiknya TERANG (plot_bgcolor="white") &
    heading biru → hanya enak dilihat di tema TERANG.
  • metar_dashboard.py mengunci grafiknya GELAP (template="plotly_dark",
    marker neon, animasi radar) → hanya enak dilihat di tema GELAP.
  • meteogram_dashboard.py sudah punya radio "Mode Tampilan" (Dark/Light)
    yang ikut mengganti template grafik → sudah sempurna, TIDAK disentuh.

Karena grafik ACS/METAR bersifat hardcoded dan file tidak boleh diedit,
satu toggle global mustahil membuat keduanya bagus sekaligus. Maka:
  → Aviation Meteorology  DIKUNCI TERANG + dijamin selalu terbaca.
  → Tactical METAR & TAF  DIKUNCI GELAP  + dijamin selalu terbaca.
  → Diurnal Patterns      memakai saklarnya sendiri (kita LEWATI total).
  → Saklar Terang/Gelap + Bahasa (ID/EN) di sini mengatur Beranda & shell.

Semua CSS shell disuntik SEBELUM & SESUDAH page dijalankan (sebelum =
cegah kedip; sesudah = pasti menang cascade dgn !important) dan TIDAK
PERNAH menyentuh halaman Diurnal Patterns, sehingga fungsionalitas ketiga
dashboard tetap 100% utuh & bebas konflik.

CATATAN: tema TIDAK lagi bergantung pada .streamlit/config.toml. Seluruh
pengaturan tema (termasuk perbaikan akar bug "tulisan putih" ACS) sudah
dijamin oleh injeksi CSS di dalam file ini — cukup satu file app.py.

Struktur repo (flat) — TIDAK perlu membuat folder apa pun:
    app.py
    metar_dashboard.py  acs_dashboard.py  meteogram_dashboard.py
    *.xlsx
    requirements.txt
"""

from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# 1) KONFIGURASI DASAR — WAJIB perintah Streamlit PERTAMA.
# ============================================================
st.set_page_config(
    page_title="U_AWIS — TNI AU",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- State default ----
st.session_state.setdefault("uawis_dark", True)   # tema Beranda/shell
st.session_state.setdefault("uawis_lang", "ID")   # ID / EN


# ============================================================
# 2) I18N — teks SHELL saja (isi ketiga dashboard tetap asli).
# ============================================================
STR = {
    "ID": {
        "brand_sub": "Unified Aviation Weather Information System",
        "theme_label": "🌙 Mode Gelap (Beranda)",
        "theme_help": "Mengatur tema Beranda & tampilan shell U-AWIS.\n"
                      "• Aviation Meteorology dikunci TERANG (desain grafiknya).\n"
                      "• Tactical METAR & TAF dikunci GELAP (desain taktisnya).\n"
                      "• Diurnal Patterns punya saklar Dark/Light sendiri.",
        "lang_label": "🌐 Bahasa",
        "nav_home": "Beranda",
        "nav_metar": "Tactical METAR & TAF",
        "nav_acs": "Aviation Meteorology",
        "nav_meteo": "Diurnal Patterns",
        "kicker": "Platform Cuaca Operasional Penerbangan",
        "hero_sub": "Sistem terpadu pemantauan meteorologi penerbangan untuk mendukung "
                    "kesiapan dan kecepatan pengambilan keputusan misi TNI Angkatan Udara.",
        "modules_status": "Status Modul Sistem",
        "online": "ONLINE",
        "card_metar_d": "Pemantauan cuaca taktis real-time: observasi METAR & prakiraan TAF "
                        "per pangkalan udara TNI AU, decoding otomatis, unduh laporan PDF, "
                        "serta windrose bergaya ruang operasi.",
        "card_acs_d": "Rekapitulasi & statistik klimatologi lapangan (Aerodrome Climatological "
                      "Summary) 2021–2025: suhu, kelembapan, visibility, cloud base, dan angin "
                      "— dengan interpretasi operasional ICAO/WMO.",
        "card_meteo_d": "Analisis pola diurnal & musiman multi-tahun: meteogram per jam, "
                        "wind rose, dan tren harian untuk perencanaan penerbangan.",
        "open_btn": "Buka",
        "hint_t": "Petunjuk Penggunaan",
        "hint_d": "Gunakan menu navigasi di bagian atas untuk berpindah antar modul. "
                  "Tiap modul tampil pada tema optimalnya dan selalu terbaca di layar apa pun.",
        "utc_label": "UTC / ZULU",
        "local_label": "LOKAL / WIB",
        "sys_ok": "SYSTEM OPERATIONAL",
        "unit_name": "TNI ANGKATAN UDARA",
        "unit_role": "Aviation Weather Decision Support",
        "footer": "U-AWIS · Unified Aviation Weather Information System  ·  "
                  "Dibangun di atas Streamlit & Plotly  ·  Untuk Operasional TNI AU  ·  © 2026",
    },
    "EN": {
        "brand_sub": "Unified Aviation Weather Information System",
        "theme_label": "🌙 Dark Mode (Home)",
        "theme_help": "Controls the Home page & U-AWIS shell theme.\n"
                      "• Aviation Meteorology is locked LIGHT (its chart design).\n"
                      "• Tactical METAR & TAF is locked DARK (its tactical design).\n"
                      "• Diurnal Patterns has its own Dark/Light switch.",
        "lang_label": "🌐 Language",
        "nav_home": "Home",
        "nav_metar": "Tactical METAR & TAF",
        "nav_acs": "Aviation Meteorology",
        "nav_meteo": "Diurnal Patterns",
        "kicker": "Aviation Weather Operations Platform",
        "hero_sub": "A unified aviation weather monitoring system supporting fast, ready "
                    "decision-making for Indonesian Air Force (TNI AU) missions.",
        "modules_status": "System Modules Status",
        "online": "ONLINE",
        "card_metar_d": "Real-time tactical weather: METAR observations & TAF forecasts per "
                        "TNI AU air base, automatic decoding, PDF report export, and an "
                        "ops-room styled windrose.",
        "card_acs_d": "Aerodrome Climatological Summary statistics 2021–2025: temperature, "
                      "humidity, visibility, cloud base, and wind — with ICAO/WMO "
                      "operational interpretation.",
        "card_meteo_d": "Multi-year diurnal & seasonal analysis: hourly meteograms, wind "
                        "rose, and daily trends for flight planning.",
        "open_btn": "Open",
        "hint_t": "How to Use",
        "hint_d": "Use the top navigation to switch modules. Each module renders in its "
                  "optimal theme and stays readable on any screen.",
        "utc_label": "UTC / ZULU",
        "local_label": "LOCAL / WIB",
        "sys_ok": "SYSTEM OPERATIONAL",
        "unit_name": "INDONESIAN AIR FORCE",
        "unit_role": "Aviation Weather Decision Support",
        "footer": "U-AWIS · Unified Aviation Weather Information System  ·  "
                  "Built on Streamlit & Plotly  ·  For TNI AU Operations  ·  © 2026",
    },
}


def T(key: str) -> str:
    return STR[st.session_state.uawis_lang][key]


# ============================================================
# 3) PALET WARNA (untuk Beranda & shell)
# ============================================================
def palette(dark: bool) -> dict:
    if dark:
        return dict(
            app="#0B1220", bg2="#0E1730", card="#131C31", card2="#0F172B",
            border="#24314F", text="#E9EEF9", muted="#93A2C4",
            gold="#E0B54A", steel="#3E7CB1", ok="#37C77F",
            side="#0E1730", sidetext="#E9EEF9",
            heroA="#0E1730", heroB="#152443",
            shadow="0 14px 34px rgba(0,0,0,.45)",
        )
    return dict(
        app="#EEF2F8", bg2="#F5F7FC", card="#FFFFFF", card2="#F7F9FD",
        border="#D9E1EE", text="#12213F", muted="#54627C",
        gold="#B3860B", steel="#1B4965", ok="#1F9D5B",
        side="#FFFFFF", sidetext="#12213F",
        heroA="#1B2C50", heroB="#26406F",
        shadow="0 10px 24px rgba(19,33,64,.10)",
    )


# ============================================================
# 4) THEME OVERRIDE PER-HALAMAN (disuntik SETELAH pg.run()).
#    Semua pakai !important + selector spesifik agar menang
#    cascade tanpa mengedit file dashboard.
#    Header top-nav dibuat navy konsisten (teks selalu terang)
#    agar label menu selalu jelas di kedua tema.
# ============================================================
def _shared_chrome(c: dict) -> str:
    """Header top-nav (dipakai semua page shell)."""
    return f"""
        header[data-testid="stHeader"] {{
            background: linear-gradient(90deg, #0E1730 0%, #1B2C50 100%) !important;
            border-bottom: 1px solid {c['border']} !important;
        }}
        header[data-testid="stHeader"] a,
        header[data-testid="stHeader"] p,
        header[data-testid="stHeader"] span,
        header[data-testid="stHeader"] div[role="tab"] {{ color: #E9EEF9 !important; }}
        header[data-testid="stHeader"] svg {{ fill: #E9EEF9 !important; }}
    """


def css_home(dark: bool) -> str:
    c = palette(dark)
    return f"""
    <style>
      .stApp {{ background: {c['app']} !important; }}
      [data-testid="stMain"], .main .block-container {{ color: {c['text']} !important; }}
      section[data-testid="stSidebar"] {{
          background: {c['side']} !important;
          border-right: 1px solid {c['border']} !important;
      }}
      section[data-testid="stSidebar"] * {{ color: {c['sidetext']} !important; }}
      {_shared_chrome(c)}
    </style>
    """


def css_acs_light() -> str:
    """Aviation Meteorology — DIKUNCI TERANG & dijamin terbaca (fix tulisan putih)."""
    return f"""
    <style>
      .stApp {{ background: #F5F7FA !important; }}
      [data-testid="stMain"] .stMarkdown,
      [data-testid="stMain"] p,
      [data-testid="stMain"] li,
      [data-testid="stMain"] label,
      [data-testid="stMain"] span,
      [data-testid="stMarkdownContainer"] {{ color: #16233D !important; }}
      [data-testid="stMain"] h1, [data-testid="stMain"] h2,
      [data-testid="stMain"] h3, [data-testid="stMain"] h4 {{
          color: #003366 !important; -webkit-text-fill-color: #003366 !important;
      }}
      div[data-testid="stMetricValue"] {{ color: #003366 !important; }}
      section[data-testid="stSidebar"] {{
          background: #FFFFFF !important;
          border-right: 1px solid #D9E1EE !important;
      }}
      section[data-testid="stSidebar"] * {{ color: #16233D !important; }}
      {_shared_chrome(palette(False))}
    </style>
    """


def css_metar_dark() -> str:
    """Tactical METAR & TAF — DIKUNCI GELAP & dijamin terbaca (fix hijau-di-atas-putih)."""
    return f"""
    <style>
      .stApp, [data-testid="stMain"], .main .block-container {{
          background: #0B0C0C !important;
      }}
      [data-testid="stMain"] .stMarkdown,
      [data-testid="stMain"] p, [data-testid="stMain"] li,
      [data-testid="stMain"] label, [data-testid="stMain"] span,
      [data-testid="stMarkdownContainer"] {{ color: #CFD2C3 !important; }}
      [data-testid="stMain"] h1, [data-testid="stMain"] h2,
      [data-testid="stMain"] h3, [data-testid="stMain"] h4 {{
          color: #A9DF52 !important; -webkit-text-fill-color: #A9DF52 !important;
      }}
      div[data-testid="stMetricValue"] {{ color: #A9DF52 !important; }}
      section[data-testid="stSidebar"] {{
          background: #111111 !important;
          border-right: 1px solid #2F3A2F !important;
      }}
      section[data-testid="stSidebar"] * {{ color: #D0D3CA !important; }}
      {_shared_chrome(palette(True))}
    </style>
    """


# ============================================================
# 5) STATUS BAR TAKTIS (jam UTC/WIB live) — iframe terisolasi,
#    aman total terhadap CSS/JS dashboard manapun.
# ============================================================
def tactical_status_bar(c: dict) -> None:
    strip_bg = c["heroA"] if st.session_state.uawis_dark else "#FFFFFF"
    components.html(
        f"""
        <div style="font-family:-apple-system,Segoe UI,Roboto,system-ui,sans-serif;
            background:{strip_bg};border:1px solid {c['border']};border-radius:12px;
            padding:8px 16px;display:flex;align-items:center;justify-content:space-between;
            flex-wrap:wrap;gap:10px;box-shadow:{c['shadow']};">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="width:9px;height:9px;border-radius:50%;background:{c['ok']};
                box-shadow:0 0 0 4px {c['ok']}33;display:inline-block;"></span>
            <span style="font-weight:800;letter-spacing:1px;font-size:.72rem;
                text-transform:uppercase;color:{c['ok']};">{T('sys_ok')}</span>
            <span style="color:{c['muted']};font-size:.72rem;">· U-AWIS · TNI AU</span>
          </div>
          <div style="display:flex;align-items:center;gap:18px;
              font-variant-numeric:tabular-nums;">
            <div style="text-align:right;">
              <div style="font-size:.6rem;letter-spacing:1.5px;color:{c['gold']};
                  font-weight:800;">{T('utc_label')}</div>
              <div id="u" style="font-size:.95rem;font-weight:700;color:{c['text']};">--:--:--</div>
            </div>
            <div style="width:1px;height:26px;background:{c['border']};"></div>
            <div style="text-align:right;">
              <div style="font-size:.6rem;letter-spacing:1.5px;color:{c['steel']};
                  font-weight:800;">{T('local_label')}</div>
              <div id="l" style="font-size:.95rem;font-weight:700;color:{c['text']};">--:--:--</div>
            </div>
          </div>
        </div>
        <script>
          function p(n){{return String(n).padStart(2,'0');}}
          function tick(){{
            const now=new Date();
            const u=p(now.getUTCHours())+':'+p(now.getUTCMinutes())+':'+p(now.getUTCSeconds());
            const w=new Date(now.getTime()+7*3600*1000);
            const l=p(w.getUTCHours())+':'+p(w.getUTCMinutes())+':'+p(w.getUTCSeconds());
            const eu=document.getElementById('u'),el=document.getElementById('l');
            if(eu)eu.textContent=u+'Z'; if(el)el.textContent=l+' WIB';
          }}
          tick(); setInterval(tick,1000);
        </script>
        """,
        height=64,
    )


# ============================================================
# 6) HALAMAN BERANDA — dibangun mandiri (tidak terkait dashboard).
# ============================================================
def render_home():
    dark = st.session_state.uawis_dark
    c = palette(dark)

    st.markdown(
        f"""
        <style>
          .uawis-hero {{ background:linear-gradient(135deg,{c['heroA']} 0%,{c['heroB']} 100%);
              border:1px solid {c['border']};border-radius:20px;padding:32px 30px;
              box-shadow:{c['shadow']};position:relative;overflow:hidden;}}
          .uawis-hero::after {{ content:"";position:absolute;right:-40px;top:-40px;
              width:220px;height:220px;border-radius:50%;
              background:radial-gradient(circle,{c['gold']}22 0%,transparent 70%);}}
          .uawis-kicker {{ display:inline-block;font-size:.66rem;letter-spacing:2px;
              font-weight:800;text-transform:uppercase;color:{c['gold']};
              border:1px solid {c['gold']}66;border-radius:999px;padding:4px 12px;
              margin-bottom:12px;}}
          .uawis-title {{ color:#FFFFFF;font-size:2.1rem;font-weight:800;margin:0 0 8px 0;
              letter-spacing:.3px;}}
          .uawis-sub {{ color:#C7D3EC;font-size:1rem;line-height:1.7;max-width:840px;margin:0;}}
          .uawis-status {{ display:flex;align-items:center;gap:10px;margin:6px 0 2px 0;}}
          .uawis-status .t {{ color:{c['text']};font-weight:800;font-size:1.15rem;}}
          .uawis-pill {{ background:{c['ok']}22;color:{c['ok']};border:1px solid {c['ok']}66;
              font-size:.62rem;font-weight:800;letter-spacing:1px;border-radius:999px;
              padding:2px 10px;}}
          .uawis-card {{ background:{c['card']};border:1px solid {c['border']};
              border-top:3px solid {c['gold']};border-radius:16px;padding:20px 18px 14px 18px;
              min-height:224px;box-shadow:{c['shadow']};transition:transform .18s ease,
              border-color .18s ease;}}
          .uawis-card:hover {{ transform:translateY(-4px);border-color:{c['gold']};}}
          .uawis-card .cic {{ font-size:1.7rem;}}
          .uawis-card .ctt {{ color:{c['text']};font-weight:800;font-size:1.05rem;
              margin:8px 0 8px 0;}}
          .uawis-card .cds {{ color:{c['muted']};font-size:.85rem;line-height:1.6;}}
          .uawis-hint {{ background:{c['card2']};border:1px solid {c['border']};
              border-left:4px solid {c['steel']};border-radius:12px;padding:12px 16px;
              color:{c['muted']};font-size:.85rem;line-height:1.55;}}
          .uawis-hint b {{ color:{c['text']};}}
          [data-testid="stPageLink"] a {{ border:1px solid {c['border']} !important;
              border-radius:12px !important;background:{c['card2']} !important;
              font-weight:600 !important;}}
          [data-testid="stPageLink"] a:hover {{ border-color:{c['gold']} !important;}}
        </style>
        """,
        unsafe_allow_html=True,
    )

    tactical_status_bar(c)
    st.write("")

    st.markdown(
        f"""
        <div class="uawis-hero">
            <span class="uawis-kicker">{T('kicker')}</span>
            <div class="uawis-title">🛡️ U-AWIS COMMAND CENTER</div>
            <p class="uawis-sub">{T('hero_sub')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown(
        f"""<div class="uawis-status">
                <span class="t">📡 {T('modules_status')}</span>
                <span class="uawis-pill">{T('online')}</span>
            </div>""",
        unsafe_allow_html=True,
    )
    st.write("")

    cards = [
        (metar_pg, "📡", T("nav_metar"), T("card_metar_d")),
        (acs_pg, "📊", T("nav_acs"), T("card_acs_d")),
        (meteogram_pg, "📈", T("nav_meteo"), T("card_meteo_d")),
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
            st.page_link(page_obj, label=f"{T('open_btn')} {title}", icon="➡️",
                         use_container_width=True)

    st.write("")
    st.markdown(
        f"""<div class="uawis-hint"><b>ℹ️ {T('hint_t')}:</b> {T('hint_d')}</div>""",
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown(
        f"""<div style="text-align:center;color:{c['muted']};font-size:.74rem;
                    padding-top:12px;border-top:1px solid {c['border']};">{T('footer')}</div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# 7) SIDEBAR CONTROLS — dibuat SEBELUM navigasi agar bahasa/tema
#    langsung berlaku pada run yang sama.
# ============================================================
with st.sidebar:
    st.markdown(
        f"""<div style="line-height:1.25;">
                <span style="font-size:1.05rem;font-weight:800;">🛡️ U-AWIS</span><br>
                <span style="font-size:.72rem;opacity:.85;">{T('brand_sub')}</span>
            </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:.5rem 0 .7rem 0;'>", unsafe_allow_html=True)

    st.session_state.uawis_lang = st.radio(
        T("lang_label"), ["ID", "EN"],
        index=0 if st.session_state.uawis_lang == "ID" else 1,
        horizontal=True,
    )
    st.session_state.uawis_dark = st.toggle(
        T("theme_label"), value=st.session_state.uawis_dark, help=T("theme_help"),
    )

    st.markdown("<hr style='margin:.7rem 0 .6rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style="font-size:.68rem;opacity:.8;line-height:1.5;">
                <b>{T('unit_name')}</b><br>{T('unit_role')}<br>
                Build {datetime.now(timezone.utc):%Y.%m.%d} · v3.0
            </div>""",
        unsafe_allow_html=True,
    )

# ============================================================
# 8) DEFINISI HALAMAN + NAVIGASI (urutan: Beranda → METAR → ACS → Meteogram)
#    url_path dibiarkan default (= nama file) agar link lama tetap valid.
# ============================================================
home_pg = st.Page(render_home, title=T("nav_home"), icon="🏠", default=True)
metar_pg = st.Page("metar_dashboard.py", title=T("nav_metar"), icon="📡")
acs_pg = st.Page("acs_dashboard.py", title=T("nav_acs"), icon="📊")
meteogram_pg = st.Page("meteogram_dashboard.py", title=T("nav_meteo"), icon="📈")

pg = st.navigation([home_pg, metar_pg, acs_pg, meteogram_pg], position="top")

# ---- Deteksi halaman aktif (identitas objek + fallback url_path) ----
_pairs = [("home", home_pg), ("metar", metar_pg), ("acs", acs_pg), ("meteo", meteogram_pg)]
active = next((k for k, p in _pairs if p is pg), None)
if active is None:
    _up = (getattr(pg, "url_path", "") or "").strip("/")
    active = {"metar_dashboard": "metar", "acs_dashboard": "acs",
              "meteogram_dashboard": "meteo"}.get(_up, "home")

# ============================================================
# 9) EKSEKUSI HALAMAN + OVERRIDE TEMA (pengganti config.toml)
#    Diurnal Patterns (meteo) DILEWATI: ia punya tema sendiri.
#    CSS disuntik 2x: SEBELUM pg.run() (cegah kedip) & SESUDAH
#    (pasti menang cascade atas CSS !important milik dashboard).
# ============================================================
def theme_css_for(page_key: str):
    """Kembalikan CSS tema untuk page shell; None utk meteo (jangan disentuh)."""
    if page_key == "home":
        return css_home(st.session_state.uawis_dark)
    if page_key == "acs":
        return css_acs_light()
    if page_key == "metar":
        return css_metar_dark()
    return None  # meteo → hormati saklar internalnya

# --- SEBELUM: minimalkan kedip tema saat halaman pertama kali dilukis ---
_css = theme_css_for(active)
if _css:
    st.markdown(_css, unsafe_allow_html=True)

# --- Jalankan modul terpilih (dengan jaring pengaman) ---
try:
    pg.run()
except Exception as e:
    st.error("⚠️ Terjadi kendala saat memuat modul ini. Silakan kembali ke Beranda.")
    with st.expander("Detail teknis (untuk administrator)"):
        st.exception(e)
    active = "home"

# --- SESUDAH: kunci hasil akhir agar selalu menang atas CSS dashboard ---
_css = theme_css_for(active)
if _css:
    st.markdown(_css, unsafe_allow_html=True)
