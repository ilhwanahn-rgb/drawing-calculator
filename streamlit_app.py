import math
import inspect
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="선재/이형재 인발 소성가공 종합 산출 도구", layout="wide")

# --- 디자인 토큰 & 전역 스타일 (냉간인발 봉강 · 템퍼 컬러 · 도면 표제란) ---
INK, STEEL, PANEL, RULE, MUTED = "#1A2027", "#EDEFF1", "#FFFFFF", "#CDD3D9", "#5B6670"
TEMPER_BLUE, STRAW, SCALE_RED, OXIDE_GREEN = "#24548F", "#C9922E", "#B83A2A", "#2F7A55"
FONT_SANS = "Pretendard Variable, Pretendard, 'IBM Plex Sans KR', 'Malgun Gothic', sans-serif"
FONT_MONO = "'IBM Plex Mono', 'D2Coding', Consolas, monospace"

st.markdown(f"""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap');
:root {{
  --ink:{INK}; --steel:{STEEL}; --panel:{PANEL}; --rule:{RULE}; --muted:{MUTED};
  --blue:{TEMPER_BLUE}; --straw:{STRAW}; --red:{SCALE_RED};
  --sans:{FONT_SANS}; --mono:{FONT_MONO};
}}
.stApp {{ background: var(--steel); color: var(--ink); font-family: var(--sans); }}
[data-testid="stMainBlockContainer"], .block-container {{ padding-top: 2.2rem; max-width: 1480px; }}
h1, h2, h3, h4, p, li, label, input, textarea {{ font-family: var(--sans); }}
[data-testid="stHeader"] {{ background: transparent; }}

/* 헤더: 도면 표제란 */
.hdr {{ display:flex; gap:28px; align-items:stretch; justify-content:space-between; flex-wrap:wrap;
        border-bottom: 2px solid var(--ink); padding-bottom: 18px; margin-bottom: 6px; }}
.hdr-eyebrow {{ font-family: var(--mono); font-size: 12px; letter-spacing: .14em; color: var(--blue); font-weight: 600; }}
.hdr h1 {{ font-size: 34px; font-weight: 800; letter-spacing: -0.025em; margin: 6px 0 6px; padding: 0; color: var(--ink); line-height: 1.15; }}
.hdr p {{ margin: 0; color: var(--muted); font-size: 15px; }}
.tblock {{ border-collapse: collapse; font-size: 12.5px; min-width: 420px; background: var(--panel); align-self: flex-end; }}
.tblock th, .tblock td {{ border: 1.2px solid var(--ink); padding: 5px 9px; text-align: left; vertical-align: middle; }}
.tblock th {{ font-weight: 600; color: var(--muted); width: 64px; background: #F6F7F8; white-space: nowrap; }}
.tblock td {{ color: var(--ink); }}
.tblock .mono {{ font-family: var(--mono); font-size: 12px; }}
@media (max-width: 760px) {{ .tblock {{ min-width: 0; width: 100%; }} .hdr h1 {{ font-size: 26px; }} }}

/* 섹션 머리 */
.sec {{ margin: 10px 0 14px; }}
.sec .eb {{ font-family: var(--mono); font-size: 11.5px; letter-spacing: .14em; color: var(--muted); }}
.sec h2 {{ font-size: 23px; font-weight: 750; letter-spacing: -0.02em; margin: 2px 0 4px; padding: 0; color: var(--ink); }}
.sec p {{ margin: 0; color: var(--muted); font-size: 14.5px; }}
.keyin-chip {{ display:inline-block; width: 22px; height: 12px; vertical-align: -1px; margin: 0 4px;
               background: #FFFBF0; border: 1px solid var(--rule); border-left: 4px solid var(--straw); }}
[data-testid="stMarkdownContainer"] h4 {{ font-size: 15px; font-weight: 700; color: var(--ink); letter-spacing: -0.01em;
        border-bottom: 1px solid var(--rule); padding: 0 0 6px; margin: 4px 0 10px; }}

/* 탭: 폴더형 탭 (칸 구분 + 선택 탭 채움) — react-aria(1.6x) + baseweb(구버전) */
[data-testid="stTabs"] [role="tablist"], div[data-baseweb="tab-list"] {{
        display: flex; gap: 6px; border-bottom: 2px solid var(--ink) !important; flex-wrap: wrap; padding: 0; }}
[data-testid="stTab"], button[data-baseweb="tab"] {{
        background: var(--panel) !important; border: 1px solid var(--rule) !important; border-bottom: none !important;
        border-radius: 6px 6px 0 0 !important; padding: 9px 20px !important; margin: 0 !important; cursor: pointer;
        transition: background .15s ease; }}
[data-testid="stTab"] p, button[data-baseweb="tab"] p {{ font-size: 15px; font-weight: 600; color: var(--muted) !important; }}
[data-testid="stTab"]:hover, [data-testid="stTab"][data-hovered], button[data-baseweb="tab"]:hover {{ background: #E4E8EC !important; }}
[data-testid="stTab"]:hover p, [data-testid="stTab"][data-hovered] p, button[data-baseweb="tab"]:hover p {{ color: var(--ink) !important; }}
[data-testid="stTab"][aria-selected="true"], button[data-baseweb="tab"][aria-selected="true"] {{
        background: var(--ink) !important; border-color: var(--ink) !important; }}
[data-testid="stTab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] p {{ color: #FFFFFF !important; font-weight: 700; }}
[data-testid="stTab"][data-focus-visible], button[data-baseweb="tab"]:focus-visible {{ outline: 2px solid var(--blue); outline-offset: 2px; }}
[data-testid="stTabs"] .react-aria-SelectionIndicator, div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {{
        display: none !important; }}

/* 입력: 노란 띠 = 직접 입력(KEY-IN), 회색 띠 = 선택 (react-aria 1.6x + baseweb 구버전 모두 대응) */
[data-testid="stWidgetLabel"] p {{ font-size: 13.5px; font-weight: 600; color: var(--ink); }}
[data-testid="stNumberInputContainer"], [data-testid="stNumberInput"] div[data-baseweb="input"] {{
        background: #FFFBF0 !important; border: 1px solid var(--rule) !important;
        border-left: 5px solid var(--straw) !important; border-radius: 4px !important; }}
[data-testid="stNumberInputContainer"]:focus-within, [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
        border-color: var(--blue) !important; border-left-color: var(--straw) !important; box-shadow: 0 0 0 3px rgba(36,84,143,.18); }}
[data-testid="stNumberInputField"], [data-testid="stNumberInput"] input {{ background: transparent !important;
        font-family: var(--mono) !important; font-size: 16px !important; font-weight: 600 !important; color: var(--ink) !important; }}
[data-testid="stSelectbox"] .react-aria-ComboBox > div[role="group"], [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: var(--panel) !important; border: 1px solid var(--rule) !important;
        border-left: 5px solid var(--muted) !important; border-radius: 4px !important; }}
[data-testid="stSelectbox"] .react-aria-ComboBox > div[role="group"]:focus-within {{ border-color: var(--blue) !important;
        border-left-color: var(--muted) !important; box-shadow: 0 0 0 3px rgba(36,84,143,.18); }}
[data-testid="stSelectbox"] input {{ font-weight: 500; }}

/* 결과 계기판 */
[data-testid="stMetric"] {{ background: var(--panel); border: 1px solid var(--rule); border-top: 3px solid var(--ink);
        border-radius: 3px; padding: 12px 14px 10px; }}
[data-testid="stMetricLabel"] p {{ font-size: 12.5px; font-weight: 600; color: var(--muted); }}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] p {{ font-family: var(--mono) !important; font-weight: 600;
        color: var(--ink); font-size: 26px; letter-spacing: -0.02em; }}
[data-testid="stMetricDelta"], [data-testid="stMetricDelta"] p {{ font-family: var(--mono) !important; font-size: 12px; }}

/* 판정 태그·접힘 패널·버튼 */
[data-testid="stAlert"], [data-testid="stAlertContainer"] {{ border-radius: 3px; }}
[data-testid="stExpander"] details {{ border: 1px solid var(--rule); border-radius: 4px; background: var(--panel); }}
[data-testid="stExpander"] summary p {{ font-weight: 600; }}
.stButton button, .stDownloadButton button {{ border-radius: 3px; font-weight: 600; }}
[data-testid="stCaptionContainer"] p {{ color: var(--muted); }}

/* 결론 배너 */
.verdict {{ background: var(--panel); border: 1px solid var(--rule); border-left: 8px solid var(--muted);
           border-radius: 4px; padding: 14px 20px 14px; margin: 14px 0 10px; }}
.verdict .v-main {{ display:flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }}
.verdict .v-label {{ font-size: 15px; font-weight: 700; color: var(--ink); }}
.verdict .v-num {{ font-family: var(--mono); font-size: 40px; font-weight: 600; line-height: 1; letter-spacing: -0.03em; }}
.verdict .v-num small {{ font-size: 16px; font-weight: 500; }}
.verdict .v-tag {{ font-size: 14px; font-weight: 700; padding: 3px 10px; border-radius: 3px; color: #fff; }}
.verdict .v-sub {{ margin-top: 8px; font-size: 15px; color: var(--ink); line-height: 1.55; }}
.verdict .v-range {{ color: var(--muted); font-size: 13.5px; }}
.verdict .v-todo {{ margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--rule); font-size: 14.5px; font-weight: 600; color: var(--ink); }}
.v-red {{ border-left-color: var(--red); }}   .v-red .v-num {{ color: var(--red); }}   .v-red .v-tag {{ background: var(--red); }}
.v-amber {{ border-left-color: var(--straw); }} .v-amber .v-num {{ color: #9A6C14; }} .v-amber .v-tag {{ background: #B07D1F; }}
.v-green {{ border-left-color: #2F7A55; }} .v-green .v-num {{ color: #2F7A55; }} .v-green .v-tag {{ background: #2F7A55; }}
.v-grey .v-sub {{ margin-top: 0; }}

/* 감면율 게이지 */
.ra-box {{ background: var(--panel); border: 1px solid var(--rule); border-radius: 4px; padding: 14px 20px 14px; margin: 0 0 12px; }}
.ra-title {{ font-size: 14px; font-weight: 700; color: var(--ink); margin-bottom: 30px; }}
.ra-track {{ position: relative; display: flex; height: 30px; border-radius: 3px; }}
.ra-track .z {{ height: 100%; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
.ra-track .z span {{ font-size: 12.5px; font-weight: 700; color: #fff; white-space: nowrap; padding: 0 6px; }}
.z-red {{ background: var(--red); border-radius: 3px 0 0 3px; justify-content: flex-start !important; padding-left: 8px; }}
.z-amber {{ background: #C9922E; }}
.z-green {{ background: #2F7A55; border-radius: 0 3px 3px 0; }}
.ra-now {{ position: absolute; top: -26px; bottom: -6px; width: 0; border-left: 3px solid var(--ink); }}
.ra-now b {{ position: absolute; top: -2px; left: 6px; font-family: var(--mono); font-size: 13px; white-space: nowrap; color: var(--ink); }}
.ra-ticks {{ position: relative; height: 40px; margin-top: 4px; }}
.ra-ticks span {{ position: absolute; transform: translateX(-50%); text-align: center; font-family: var(--mono); font-size: 12.5px;
                  font-weight: 600; color: var(--ink); line-height: 1.25; border-top: 2px solid var(--ink); padding-top: 3px; white-space: nowrap; }}
.ra-ticks small {{ font-family: var(--sans); font-weight: 500; color: var(--muted); font-size: 11.5px; }}
.ra-msg {{ font-size: 14.5px; line-height: 1.65; color: var(--ink); margin-top: 6px; }}
.ra-note {{ display: block; color: var(--muted); font-size: 12.5px; margin-top: 2px; }}

/* 그림 읽는 법 */
.legend-row {{ display:flex; flex-wrap: wrap; gap: 8px 22px; align-items:center; padding: 8px 2px 2px; font-size: 14px; color: var(--ink); }}
.legend-row span {{ display:inline-flex; align-items:center; gap: 7px; white-space: nowrap; }}
.sw {{ display:inline-block; width: 26px; height: 14px; border-radius: 2px; }}
.sw-rod {{ border-top: 2.5px dashed #8A949D; height: 0; border-radius: 0; }}
.sw-die {{ border: 2px solid var(--ink); background: transparent; }}
.sw-prod {{ background: rgba(36,84,143,0.22); border: 2px solid var(--blue); }}
.sw-gap {{ background: rgba(184,58,42,0.6); border: 1px solid var(--red); }}
[data-testid="stMarkdownContainer"] code {{ font-family: var(--mono); color: var(--ink); background: #F3F4F6;
        border: 1px solid #E3E7EB; border-radius: 3px; padding: 1px 6px; font-size: .92em; }}
[data-testid="stMarkdownContainer"] strong {{ font-weight: 650; }}
hr {{ border-color: var(--rule) !important; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>
""", unsafe_allow_html=True)


def section_header(eyebrow, title, desc=None):
    st.markdown(f"<div class='sec'><div class='eb'>{eyebrow}</div><h2>{title}</h2>"
                + (f"<p>{desc}</p>" if desc else "") + "</div>", unsafe_allow_html=True)


def style_fig(fig, height=None, legend_bottom=True):
    """Plotly 공통 테마: 도면 그리드"""
    fig.update_layout(
        font=dict(family=FONT_SANS, size=12, color=INK),
        title_font=dict(family=FONT_SANS, size=15, color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PANEL,
        hoverlabel=dict(font_family=FONT_MONO, bgcolor=PANEL, bordercolor=RULE),
        legend=dict(font=dict(size=11), bgcolor="rgba(255,255,255,0.85)",
                    **(dict(orientation="h", yanchor="top", y=-0.08, x=0) if legend_bottom else {})),
    )
    fig.update_xaxes(gridcolor="#E3E7EB", linecolor=RULE, zeroline=False, tickfont=dict(family=FONT_MONO, size=11))
    fig.update_yaxes(gridcolor="#E3E7EB", linecolor=RULE, zeroline=False, tickfont=dict(family=FONT_MONO, size=11))
    if height:
        fig.update_layout(height=height)
    return fig


def add_dim(fig, x0, x1, y_base0, y_base1, y_dim, text, vertical=False):
    """측정기 화면 같은 치수선 (보조선 + 양방향 화살표 + 값)"""
    if not vertical:
        for xx, yb in ((x0, y_base0), (x1, y_base1)):
            fig.add_shape(type="line", x0=xx, x1=xx, y0=yb, y1=y_dim + 0.6 * np.sign(y_dim - yb or 1),
                          line=dict(color=INK, width=0.8))
        fig.add_annotation(x=x1, y=y_dim, ax=x0, ay=y_dim, axref="x", ayref="y", xref="x", yref="y", text="",
                           showarrow=True, arrowhead=2, arrowside="end+start", arrowsize=0.9, arrowwidth=1, arrowcolor=INK)
        fig.add_annotation(x=(x0 + x1) / 2, y=y_dim, text=text, showarrow=False, yshift=10,
                           font=dict(family=FONT_MONO, size=11.5, color=INK), bgcolor="rgba(255,255,255,0.9)")
    else:
        for yy, xb in ((x0, y_base0), (x1, y_base1)):
            fig.add_shape(type="line", y0=yy, y1=yy, x0=xb, x1=y_dim - 0.6 * np.sign(xb - y_dim or 1),
                          line=dict(color=INK, width=0.8))
        fig.add_annotation(x=y_dim, y=x1, ax=y_dim, ay=x0, axref="x", ayref="y", xref="x", yref="y", text="",
                           showarrow=True, arrowhead=2, arrowside="end+start", arrowsize=0.9, arrowwidth=1, arrowcolor=INK)
        fig.add_annotation(x=y_dim, y=(x0 + x1) / 2, text=text, showarrow=False, textangle=-90, xshift=-10,
                           font=dict(family=FONT_MONO, size=11.5, color=INK), bgcolor="rgba(255,255,255,0.9)")


SQRT2, SQRT3 = math.sqrt(2.0), math.sqrt(3.0)


def _full_width_kw(fn):
    """Streamlit 버전 호환: 신버전(width='stretch' 기본)은 인자 생략, 구버전은 use_container_width=True"""
    try:
        p = inspect.signature(fn).parameters.get("width")
        if p is not None and p.default == "stretch":
            return {}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


FW_CHART = _full_width_kw(st.plotly_chart)
FW_DF = _full_width_kw(st.dataframe)
FW_ED = _full_width_kw(st.data_editor)
SHAPE_HEX, SHAPE_SQ, SHAPE_TR = "정육각형", "사각형 (정/직사각)", "이형 (트랙/장원형)"
FEM_COLORS = ["#1A1AD2", "#1F55FF", "#1E90FF", "#14C8F0", "#12E0B4", "#2FD95A", "#8FE32A", "#E3E61C", "#FFC41A", "#FF8C14", "#F24E10", "#C8140C"]


def fem_scale(banded=True):
    """FEM 결과처럼 파랑(낮음) → 초록 → 노랑 → 빨강(높음) 12단계"""
    n = len(FEM_COLORS)
    if not banded:
        return [[i / (n - 1), c] for i, c in enumerate(FEM_COLORS)]
    cs = []
    for i, c in enumerate(FEM_COLORS):
        cs += [[i / n, c], [(i + 1) / n, c]]
    return cs


CS_STRAIN = CS_TEMP = fem_scale(True)

# ==========================================
# 실측 R DB  (사각 봉강 이형 형상측정, 비전측정기 원호피팅 R, 2026.09~10)
# R 순서 = [TL, TR, BL, BR] (측정 화면 기준) · die_r = 실제 확인한 다이스 모서리 R (0.0 = R 없음/샤프)
# ==========================================
MEASURED_DB = [
    dict(id="P269LE005-1", grade="AISI1020", d0=27.0, a=19.05, die="S11024016", die_r=0.3, lcx=18.959, lcy=18.968, R=[1.342, 1.465, 1.266, 0.991]),
    dict(id="P269LE046-1", grade="AISI1020", d0=27.0, a=20.00, die="S11122504", die_r=0.0, lcx=19.924, lcy=19.904, R=[2.525, 3.339, 1.787, 2.095]),
    dict(id="P269LE046-2", grade="AISI1020", d0=27.0, a=20.00, die="S11122504", die_r=0.0, lcx=19.926, lcy=19.977, R=[2.836, 2.401, 2.741, 3.311]),
    dict(id="P269LD103-1", grade="S20C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.923, lcy=21.918, R=[3.484, 0.600, 1.488, 0.419]),
    dict(id="P269LD103-3", grade="S20C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.939, lcy=21.941, R=[2.045, 2.090, 2.048, 1.723]),
    dict(id="P269LD103-4", grade="S20C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.965, lcy=21.972, R=[2.888, 2.403, 1.540, 1.773]),
    dict(id="P269LD103-5", grade="S20C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.932, lcy=21.913, R=[0.572, 1.165, 3.615, 1.726]),
    dict(id="P269LD103-6", grade="S20C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.955, lcy=21.924, R=[2.368, 2.276, 3.085, 2.902]),
    dict(id="P269LD103-7", grade="S20C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.960, lcy=21.912, R=[2.921, 1.281, 3.278, 3.429]),
    dict(id="P268LD195-1", grade="S45C",     d0=27.0, a=19.00, die="S11016504", die_r=0.0, lcx=18.997, lcy=18.994, R=[0.652, 1.127, 0.777, 1.138]),
    dict(id="P269LD030-1", grade="S45C",     d0=27.0, a=19.00, die="S11016504", die_r=0.0, lcx=18.984, lcy=18.960, R=[1.342, 1.699, 0.745, 1.359]),
    dict(id="P269LD031-1", grade="S45C",     d0=28.0, a=19.00, die="S11016504", die_r=0.3, lcx=18.927, lcy=18.927, R=[0.780, 1.094, 0.716, 0.780]),
    dict(id="P268LD194-1", grade="S45C",     d0=30.0, a=22.00, die="S11125505", die_r=0.0, lcx=21.992, lcy=21.989, R=[2.221, 2.584, 1.523, 2.558]),
    dict(id="P266LD204-1", grade="SS400",    d0=27.0, a=20.00, die="S11122504", die_r=0.0, lcx=19.982, lcy=19.950, R=[2.213, 2.092, 2.160, 1.936]),
]
DIE_INFO = {
    "S11016504": dict(spec="AP 30 / BL 6", size=19.0,  note="같은 코드라도 0.3R·R 없음 다이가 섞여 있음 (LD031 0.3R, LD195·LD030 R 없음)"),
    "S11024016": dict(spec="AP 30 / BL 6", size=19.05, note="0.3R 확인 (LE005)"),
    "S11122504": dict(spec="AP 32 / BL 7", size=20.0,  note="R 없음 확인 (LE046, LD204)"),
    "S11125505": dict(spec="AP 32 / BL 8", size=22.0,  note="R 없음 확인 (LD103, LD194)"),
}
DIE_R_OPTIONS = {"R 없음 (샤프)": 0.0, "0.3R": 0.3, "0.5R": 0.5, "1.0R": 1.0, "직접 입력": None}
DEFAULT_DIE_R = 0.0   # 실측 8로트 중 6로트가 R 없음


# 실측 56개 코너 최우도 보정값 (물리 기반 '코너 갭' 모델, 조건별 교차검증 완료)
MODEL_DEFAULT = dict(
    delta_star=0.0162,   # 추가 코너 수축량 δ = δ*·a  (a=20 → 0.32 mm)
    w_star=0.0068,       # 충전/미충전 전이 폭 w = w*·a (a=20 → 0.14 mm, 고정)
    sigma=0.327,         # 코너별 국부 반경 편차 σε (mm) : 선재 공차·진원도·편심·다이스 정렬
    noise=0.15,          # 측정 + 충전 한계 산포 (mm)
    fill_le20=0.83,      # 한 번 인발로 도달 가능한 최소 R (□≤20) — 0.3R·R 없음 다이 모두 완전충전 시 0.72–1.09
    fill_gt20=0.36,      # 같은 값 (□>20) — R 없음 다이, 편심 bar 최소 0.42 근거 (불확실)
    source="기본 보정 (실측 14본·56코너, 실제 다이 R 0.3R/R 없음 반영, 2026.10)",
)
CV_TABLE = pd.DataFrame({
    "검증 지표 (조건별 Leave-one-out)": ["bar 평균 R 오차 (MAE)", "코너별 R 오차 (MAE)", "P10~P90 구간 실측 포함률"],
    "기존 식 (다이스R 1.0 + 0.18·W·e^(-5.2RA))": ["0.49 mm", "0.66 mm", "구간 없음"],
    "기존 식 (실제 다이 R 적용 시)": ["1.18 mm", "-", "구간 없음"],
    "신규 코너갭 모델": ["0.32 mm", "0.54 mm", "보정 80 % · 교차검증 66 %"],
})

if "model" not in st.session_state:
    st.session_state["model"] = dict(MODEL_DEFAULT)
MODEL = st.session_state["model"]

# ==========================================
# 수학 / 예측 모델 함수
# ==========================================


def norm_cdf(x):
    if not np.isfinite(x):
        return 1.0 if x > 0 else 0.0
    return 0.5 * (1.0 + math.erf(x / SQRT2))


def norm_ppf(p):
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _softplus(z):
    return np.logaddexp(0.0, z)


def _e_from_x(x, e_die, delta, w):
    """국부 갭 x → 코너 후퇴량 e (mm). 완전충전이면 e→e_die, 미충전이면 e≈x+δ"""
    return e_die + w * _softplus((x + delta - e_die) / w)


def shape_geom(shape, W, H):
    """n: 코너수, h: 중심→샤프 꼭짓점 거리, kf: 후퇴량 e = kf·R, a_ref: 기준 치수, A_sharp: 샤프 단면적"""
    if shape == SHAPE_HEX:
        return dict(n=6, h=W / SQRT3, kf=2.0 / SQRT3 - 1.0, a_ref=W, A_sharp=SQRT3 / 2.0 * W ** 2, loss=2 * SQRT3 - np.pi)
    return dict(n=4, h=math.hypot(W, H) / 2.0, kf=SQRT2 - 1.0, a_ref=(W + H) / 2.0, A_sharp=W * H, loss=4.0 - np.pi)


KF_SQ = SQRT2 - 1.0
KF_HEX = 2.0 / SQRT3 - 1.0


def shape_kf(shape):
    """꼭짓점 후퇴량 e = kf·R 의 kf (사각 0.414, 육각 0.155)"""
    return KF_HEX if shape == SHAPE_HEX else KF_SQ


def fill_min_for(size, model, shape=None):
    """한 번 인발 최소 도달 R.
    보정값(fill_le20/gt20)은 사각 R 기준 → '최소 꼭짓점 후퇴량 e = R·kf'가 형상과 무관하다고 보고 형상별 R로 환산
    (육각: ×2.68 · 외부 육각 인발 데이터와 비교해 R 그대로 옮기는 것보다 잘 맞음)"""
    if model.get("fill_override") is not None:
        return float(model["fill_override"])
    base = model["fill_le20"] if size <= 20.0 + 1e-9 else model["fill_gt20"]
    return base * KF_SQ / shape_kf(shape)


def effective_die_R(size, R_design, model, shape=None):
    """최소 도달 R = max(다이스 모서리 R, 한 번 인발 최소 R)"""
    return max(R_design, fill_min_for(size, model, shape))


Z_GRID = np.linspace(-6.0, 6.0, 601)
PZ = np.exp(-0.5 * Z_GRID ** 2); PZ = PZ / PZ.sum()


def ncdf_vec(x):
    """표준정규 CDF (벡터, Abramowitz-Stegun 7.1.26, 오차 < 1.5e-7)"""
    x = np.asarray(x, float)
    z = np.abs(x) / SQRT2
    t = 1.0 / (1.0 + 0.3275911 * z)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-z * z)
    return 0.5 * (1.0 + np.sign(x) * y)


def _corner_dist(g, a, R_die, kf, model, rmax):
    """국부 갭 편차 ε 격자에 대한 코너 R 값 (노이즈 제외)"""
    e_die = R_die * kf
    f = _e_from_x(g + model["sigma"] * Z_GRID, e_die, model["delta_star"] * a, model["w_star"] * a) / kf
    return np.minimum(f, rmax)


def _mix_cdf(r, f, sn):
    r = np.atleast_1d(np.asarray(r, float))
    return (PZ[None, :] * ncdf_vec((r[:, None] - f[None, :]) / sn)).sum(1)


def predict_R(shape, W, H, d0, R_design, model):
    G = shape_geom(shape, W, H)
    kf, a = G["kf"], G["a_ref"]
    g = G["h"] - d0 / 2.0
    R_die = effective_die_R(a, R_design, model, shape)
    rmax = min(W, H) / 2.0 * 0.995
    f = _corner_dist(g, a, R_die, kf, model, rmax)
    sn = model["noise"]
    rg = np.linspace(max(0.0, f.min() - 5 * sn), f.max() + 5 * sn, 900)
    cdf = _mix_cdf(rg, f, sn)
    qf = lambda p: float(min(rmax, max(0.02, np.interp(p, cdf, rg))))
    s = model["sigma"]
    return dict(
        g=g, h=G["h"], kf=kf, a=a, e_die=R_die * kf, delta=model["delta_star"] * a, w=model["w_star"] * a, sigma=s,
        R_die=R_die, R_design=R_design, noise=sn, f=f,
        mean=float((PZ * f).sum()), rms=float(np.sqrt((PZ * f ** 2).sum())),
        p10=qf(0.10), p50=qf(0.50), p90=qf(0.90),
        p_fill=norm_cdf((R_die * kf - model["delta_star"] * a - g) / s),
        k_ratio=d0 / (2.0 * G["h"]),
        RA_k1=1.0 - G["A_sharp"] / (np.pi * G["h"] ** 2),
    )


def prob_R_le(spec, pred):
    return float(_mix_cdf(spec, pred["f"], pred["noise"])[0])


def required_d0(shape, W, H, spec, conf, R_design, model):
    """P(R ≤ spec) ≥ conf 를 만족하는 최소 투입 선경 (갭 g 이분탐색)"""
    G = shape_geom(shape, W, H)
    kf, a = G["kf"], G["a_ref"]
    R_die = effective_die_R(a, R_design, model, shape)
    rmax = min(W, H) / 2.0 * 0.995
    P = lambda g: float(_mix_cdf(spec, _corner_dist(g, a, R_die, kf, model, rmax), model["noise"])[0])
    lo, hi = -6.0, 6.0
    if P(lo) < conf:
        return np.nan
    if P(hi) >= conf:
        return 2.0 * (G["h"] - hi)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if P(mid) >= conf:
            lo = mid
        else:
            hi = mid
    return 2.0 * (G["h"] - lo)


def old_model_R(W, RA, R_die):
    """기존 앱 식 (비교용)"""
    return R_die + 0.18 * W * np.exp(-5.2 * RA)


# ==========================================
# 2D 단면 정점 생성 (코너별 R 지원)
# 사각 코너 인덱스: 0=TR, 1=TL, 2=BL, 3=BR / 육각: 0=30°(우상)부터 반시계
# ==========================================
def corner_arc(shape, W, H, k, r, m=40):
    r = max(1e-6, min(r, min(W, H) / 2.0 * 0.999))
    if shape == SHAPE_HEX:
        phi = np.pi / 6 + k * np.pi / 3
        dc = (W / 2.0 - r) / np.cos(np.pi / 6)
        cx, cy = dc * np.cos(phi), dc * np.sin(phi)
        t = np.linspace(phi - np.pi / 6, phi + np.pi / 6, m)
    else:
        sx, sy = [(1, 1), (-1, 1), (-1, -1), (1, -1)][k]
        cx, cy = sx * (W / 2.0 - r), sy * (H / 2.0 - r)
        t = np.linspace(k * np.pi / 2, (k + 1) * np.pi / 2, m)
    return cx + r * np.cos(t), cy + r * np.sin(t)


def corner_vertex(shape, W, H, k):
    if shape == SHAPE_HEX:
        phi = np.pi / 6 + k * np.pi / 3
        return (W / SQRT3) * np.cos(phi), (W / SQRT3) * np.sin(phi)
    sx, sy = [(1, 1), (-1, 1), (-1, -1), (1, -1)][k]
    return sx * W / 2.0, sy * H / 2.0


def rounded_polygon(shape, W, H, radii, n_points=240):
    n = 6 if shape == SHAPE_HEX else 4
    radii = list(radii) if np.ndim(radii) else [float(radii)] * n
    m = n_points // n
    xs, ys = [], []
    for k in range(n):
        x, y = corner_arc(shape, W, H, k, radii[k], m)
        xs.append(x); ys.append(y)
    return np.concatenate(xs), np.concatenate(ys)


def track_points(W, H, n_points=240):
    r_track = H / 2.0
    straight_len = max(0.0, (W - H) / 2.0)
    a1 = np.linspace(-np.pi / 2, np.pi / 2, n_points // 2)
    a2 = np.linspace(np.pi / 2, 3 * np.pi / 2, n_points // 2)
    x = np.concatenate([straight_len + r_track * np.cos(a1), -straight_len + r_track * np.cos(a2)])
    y = np.concatenate([r_track * np.sin(a1), r_track * np.sin(a2)])
    return x, y


def generate_shape_points(shape, w, h, r, n_points=120):
    """(기존 호환) 단일 R 단면"""
    if shape == SHAPE_TR:
        return track_points(w, h, n_points)
    return rounded_polygon(shape, w, h, r, n_points)


def resample_polar(x, y, n):
    """3D 모핑용: 다각형 단면을 균일 각도 광선과의 교점으로 재표본화 (직선 평탄부 정확 보존)"""
    P = np.c_[x, y]
    E = np.roll(P, -1, axis=0) - P
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    dx, dy = np.cos(th)[:, None], np.sin(th)[:, None]
    den = dx * E[None, :, 1] - dy * E[None, :, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (P[None, :, 0] * E[None, :, 1] - P[None, :, 1] * E[None, :, 0]) / den
        s_ = (P[None, :, 0] * dy - P[None, :, 1] * dx) / den
    ok = np.isfinite(t) & (t > 0) & (s_ >= -1e-9) & (s_ <= 1 + 1e-9)
    r = np.where(ok, t, np.inf).min(axis=1)
    r = np.where(np.isfinite(r), r, np.hypot(x, y).max())
    return r * np.cos(th), r * np.sin(th)

def db_radii_ccw(R_tl_tr_bl_br):
    """DB 순서 [TL,TR,BL,BR] → 그리기 순서 [TR,TL,BL,BR]"""
    tl, tr, bl, br = R_tl_tr_bl_br
    return [tr, tl, bl, br]


def match_db(d0, W, H, tol_d=0.3, tol_a=0.08):
    if abs(W - H) > 1e-6:
        return []
    return [r for r in MEASURED_DB if abs(r["d0"] - d0) <= tol_d and abs(r["a"] - W) <= tol_a]


# ==========================================
# 변형·온도 간이 해석 (AFDEX 같은 FEM 대신, 즉시 계산되는 근사)
#  1) 형상 변화: 원형 단면 → 제품 단면을 '면적 비율이 같은 부채꼴끼리' 대응시키는 운동학적 매핑
#     (표면일수록 제품 형상, 중심일수록 균일 축소) → 최종 변형 기울기의 유효 변형률
#  2) 표면 전단(잉여변형): Δ = (α/r)(1+√(1−r))², Φ = 0.8 + Δ/4.4 (Hosford–Caddell),
#     반경에 비례·다이가 깊게 누르는 방향일수록 크게 배분
#  3) 온도: 소성일의 90 %가 열 (Hollomon 경화, TS로 K 추정) + 다이 마찰열(접촉 길이·시간, 반무한체 표면 가열)
# ==========================================
RHO_C_STEEL, K_TH_STEEL, BETA_HEAT, ETA_FRIC = 7850.0 * 460.0, 45.0, 0.9, 0.35   # 마찰열 35 %가 소재로 (외부 FEM·실측과 맞춤)
KAPPA_STEEL = K_TH_STEEL / RHO_C_STEEL


def _ierfc(x):
    erfc = 2.0 * (1.0 - ncdf_vec(np.asarray(x) * SQRT2))
    return np.exp(-np.asarray(x) ** 2) / math.sqrt(math.pi) - x * erfc


def _section_boundary(shape, W, H, r):
    if shape == SHAPE_TR:
        return track_points(W, H, 1440)
    return rounded_polygon(shape, W, H, r, 1440)


@st.cache_data(show_spinner=False, max_entries=64)
def deform_fields(shape, W, H, r_prod, r_die, d0, two_alpha=30.0, v_mpm=20.0, mu=0.05, ts_kgf=55.0, bearing=6.0,
                  n_h=0.18, T0=25.0, ngrid=111, M=720):
    phi_g = np.linspace(0, 2 * np.pi, M, endpoint=False)
    xb, yb = _section_boundary(shape, W, H, r_prod)
    xr, yr = resample_polar(xb, yb, M)
    rho_o = np.hypot(xr, yr)
    xd, yd = _section_boundary(shape, W, H, r_die)
    xdr, ydr = resample_polar(xd, yd, M)
    rho_d = np.hypot(xdr, ydr)
    A_out = 0.5 * abs(np.dot(xb, np.roll(yb, -1)) - np.dot(yb, np.roll(xb, -1)))
    R0 = d0 / 2.0
    lam = math.pi * R0 ** 2 / A_out
    if lam <= 1.0 + 1e-6:
        return None
    eps_h = math.log(lam)
    R_eq = math.sqrt(A_out / math.pi)
    dA = 0.5 * rho_o ** 2 * (2 * np.pi / M)
    phi_e = np.r_[phi_g, 2 * np.pi]
    th_e = 2 * np.pi * np.r_[0.0, np.cumsum(dA)] / dA.sum()
    rho_e = np.r_[rho_o, rho_o[0]]

    def rho_of(phi):
        return np.interp(np.mod(phi, 2 * np.pi), phi_e, rho_e)

    def th_of(phi):
        pm = np.mod(phi, 2 * np.pi)
        return np.interp(pm, phi_e, th_e) + (phi - pm)

    def out_xy(s_, phi):
        rr = s_ * ((1 - s_ ** 2) * R_eq + s_ ** 2 * rho_of(phi))
        return rr * np.cos(phi), rr * np.sin(phi)

    def in_xy(s_, phi):
        th = phi + s_ ** 2 * (th_of(phi) - phi)
        return s_ * R0 * np.cos(th), s_ * R0 * np.sin(th)

    TS = ts_kgf * 9.80665
    Kh = TS * (math.e / n_h) ** n_h
    Wp = lambda e: Kh * np.power(np.maximum(e, 1e-9), n_h + 1) / (n_h + 1)   # 소성일 (MJ/m³)
    a = math.radians(two_alpha / 2.0)
    r_ = 1 - 1 / lam
    Delta = (a / r_) * (1 + math.sqrt(1 - r_)) ** 2
    Phi = max(1.0, 0.8 + Delta / 4.4)
    drho = R0 - rho_o
    g_raw = np.clip(drho / max(drho.max(), 1e-9), 0.0, 1.0)
    kw = max(1, int(M * 8 / 360))                               # ±8° 원형 이동평균 (전단은 둘레로 퍼짐)
    g_sm = np.convolve(np.r_[g_raw[-kw:], g_raw, g_raw[:kw]], np.ones(2 * kw + 1) / (2 * kw + 1), mode="valid")
    g_e = np.r_[g_sm, g_sm[0]]
    g_mean = float(g_sm.mean())
    c_red = (Phi - 1.0) * eps_h * 1.5            # 단면 평균 (Φ−1)·ε 이 되도록 표면(s=1) 값 설정

    def strain(s_, phi):
        s_ = np.maximum(s_, 0.03)
        hs = hp = 1e-4
        o1 = out_xy(s_ + hs, phi); o0 = out_xy(s_ - hs, phi); o3 = out_xy(s_, phi + hp); o2 = out_xy(s_, phi - hp)
        i1 = in_xy(s_ + hs, phi); i0 = in_xy(s_ - hs, phi); i3 = in_xy(s_, phi + hp); i2 = in_xy(s_, phi - hp)
        A11, A21 = (o1[0] - o0[0]) / (2 * hs), (o1[1] - o0[1]) / (2 * hs)
        A12, A22 = (o3[0] - o2[0]) / (2 * hp), (o3[1] - o2[1]) / (2 * hp)
        B11, B21 = (i1[0] - i0[0]) / (2 * hs), (i1[1] - i0[1]) / (2 * hs)
        B12, B22 = (i3[0] - i2[0]) / (2 * hp), (i3[1] - i2[1]) / (2 * hp)
        dB = B11 * B22 - B12 * B21
        F11 = (A11 * B22 - A12 * B21) / dB; F12 = (-A11 * B12 + A12 * B11) / dB
        F21 = (A21 * B22 - A22 * B21) / dB; F22 = (-A21 * B12 + A22 * B11) / dB
        S1 = F11 ** 2 + F12 ** 2 + F21 ** 2 + F22 ** 2
        D = np.abs(F11 * F22 - F12 * F21)
        disc = np.sqrt(np.maximum(S1 ** 2 - 4 * D ** 2, 0))
        sg1 = np.sqrt((S1 + disc) / 2); sg2 = np.sqrt(np.maximum((S1 - disc) / 2, 1e-12))
        nrm = np.sqrt(sg1 * sg2 * lam)                      # 비압축 보정 (축 방향 연신 λ 균일)
        e1, e2 = np.log(sg1 / nrm), np.log(sg2 / nrm)
        e_shape = np.sqrt(2.0 / 3.0 * (e1 ** 2 + e2 ** 2 + math.log(lam) ** 2))
        g_loc = np.interp(np.mod(phi, 2 * np.pi), phi_e, g_e)
        e_red = c_red * s_ * (g_mean + (g_loc - g_mean) * s_ ** 2)   # 안쪽일수록 둘레 방향 차이가 흐려짐
        return e_shape, e_red

    Lm = rho_o.max() * 1.04
    xs = np.linspace(-Lm, Lm, ngrid)
    X, Y = np.meshgrid(xs, xs)
    PH = np.mod(np.arctan2(Y, X), 2 * np.pi)
    RH = np.hypot(X, Y)
    RB = rho_of(PH)
    inside = RH <= RB
    lo, hi = np.zeros_like(RH), np.ones_like(RH)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        fm = mid * ((1 - mid ** 2) * R_eq + mid ** 2 * RB) - RH
        hi = np.where(fm > 0, mid, hi); lo = np.where(fm > 0, lo, mid)
    S_ = 0.5 * (lo + hi)
    e_sh, e_rd = strain(S_, PH)
    EPS = e_sh + e_rd
    dT_p = BETA_HEAT * Wp(EPS) * 1e6 / RHO_C_STEEL
    es_sh, es_rd = strain(np.ones_like(phi_g), phi_g)
    eps_surf = es_sh + es_rd
    sig_bar = Wp(eps_surf) / np.maximum(eps_surf, 1e-9)    # 표면 평균 유동응력 (MPa)
    p_die = 0.8 * sig_bar                                   # 다이 면압 ≈ 0.8 × 유동응력 (근사)
    v_out = v_mpm / 60.0
    v_cone = v_out * (1 + 1 / lam) / 2
    Lc = np.maximum(drho, 0.0) / math.sin(a) * 1e-3          # 어프로치 접촉 길이 (m)
    touch = (rho_d - rho_o) < 0.03                           # 베어링에 닿는 둘레 (모서리 미충전부는 안 닿음)
    Lb = np.where(touch, bearing * 1e-3, 0.0)
    E = ETA_FRIC * mu * p_die * 1e6 * (Lc + Lb)              # 소재로 들어가는 마찰열 (J/m²)
    t_c = np.maximum(Lc / v_cone + Lb / v_out, 1e-6)
    dT_fs = np.where(Lc + Lb > 0, 2 * E / (math.sqrt(math.pi * K_TH_STEEL * RHO_C_STEEL) * np.sqrt(t_c)), 0.0)
    dT_fs_g = np.interp(PH, phi_e, np.r_[dT_fs, dT_fs[0]])
    t_g = np.interp(PH, phi_e, np.r_[t_c, t_c[0]])
    z = np.maximum(RB - RH, 0) * 1e-3
    dT_f = dT_fs_g * math.sqrt(math.pi) * _ierfc(z / (2 * np.sqrt(KAPPA_STEEL * t_g)))
    T = T0 + dT_p + dT_f
    # 유효응력(가공경화 후 강도): Swift σ = K(ε0+ε)ⁿ, 투입재 항복 ≈ 0.65·TS
    eps0 = (0.65 * TS / Kh) ** (1.0 / n_h)
    sig_f = lambda e: Kh * np.power(eps0 + np.maximum(e, 0.0), n_h)
    SIG = sig_f(EPS)
    EPS = np.where(inside, EPS, np.nan); T = np.where(inside, T, np.nan); SIG = np.where(inside, SIG, np.nan)
    T_surf = T0 + BETA_HEAT * Wp(eps_surf) * 1e6 / RHO_C_STEEL + dT_fs
    c = ngrid // 2
    eps_axis = float(e_sh[c, c] + e_rd[c, c])
    T_axis = float(T0 + BETA_HEAT * Wp(eps_axis) * 1e6 / RHO_C_STEEL)

    # --- 다이 면압: Sachs 슬래브법 (축 방향 인발응력 σx 누적) + 둘레별 접촉 시작 위치 ---
    ta = math.tan(a)
    pen_d = np.maximum(R0 - rho_d, 0.0)                         # 다이가 원형 소재를 누르는 깊이 (각도별)
    L_ap = max(float(pen_d.max()) / ta, 1e-3)                  # 어프로치 접촉 길이 (가장 깊게 누르는 곳 기준)
    nxa = 80
    xa = np.linspace(0.0, L_ap, nxa)
    r_die_x = rho_d[None, :] + (L_ap - xa[:, None]) * ta
    r_mat = np.minimum(R0, r_die_x)
    A_x = 0.5 * (r_mat ** 2).sum(1) * (2 * np.pi / M)
    eh_x = np.log(math.pi * R0 ** 2 / A_x)
    Bf = mu / ta
    sx = np.zeros(nxa)
    for i in range(1, nxa):
        de = eh_x[i] - eh_x[i - 1]
        sf_mid = float(sig_f(0.5 * (eh_x[i] + eh_x[i - 1]) * Phi))
        sx[i] = sx[i - 1] + ((1 + Bf) * sf_mid - Bf * sx[i - 1]) * de
    sf_x = sig_f(eh_x * Phi)
    contact = r_die_x <= R0 + 1e-9
    P_ap = np.where(contact, np.maximum(sf_x - sx, 0.0)[:, None], 0.0)
    nxb = 12 if bearing > 0 else 0
    xb_ = np.linspace(L_ap, L_ap + bearing, nxb + 1)[1:] if nxb else np.zeros(0)
    p_bear = 0.5 * max(float(sf_x[-1] - sx[-1]), 0.0)
    P_b = np.where(touch[None, :], p_bear, 0.0) * np.ones((nxb, 1))
    die_x = np.r_[xa, xb_]
    die_P = np.vstack([P_ap, P_b]) if nxb else P_ap
    return dict(x=xs, eps=EPS, T=T, sig=SIG, inside=inside, dx=float(xs[1] - xs[0]), phi=phi_g, rho=rho_o,
                eps_surf=eps_surf, T_surf=T_surf, dT_fs=dT_fs, sig_surf=sig_f(eps_surf), sig0=float(sig_f(0.0)),
                eps_h=eps_h, lam=lam, Delta=Delta, Phi=Phi, eps_axis=eps_axis, T_axis=T_axis, sig_axis=float(sig_f(eps_axis)),
                eps_mean=float(np.nanmean(EPS)), T_mean=float(np.nanmean(T)), depth_mm=float(np.sqrt(KAPPA_STEEL * t_c.max()) * 1e3),
                t_contact=float(t_c.max()), p_die=float(p_die.max()), K=Kh, n=n_h, eps0=eps0,
                die_x=die_x, die_P=die_P, L_ap=L_ap, sig_draw=float(sx[-1]), sf_exit=float(sf_x[-1]))


@st.cache_data(show_spinner=False, max_entries=64)
def cool_down(T, inside, dx_mm, t_s):
    """출구 후 t초 동안 단면 안 열전도 (공기 냉각 무시, 2차원 양해법)"""
    if t_s <= 0:
        return T
    k = KAPPA_STEEL * 1e6                                        # mm²/s
    dt = 0.24 * dx_mm ** 2 / k
    nstep = int(math.ceil(t_s / dt)); dt = t_s / nstep
    m = inside.astype(bool)
    U = np.where(m, np.nan_to_num(T), 0.0)
    for _ in range(nstep):
        acc = -4.0 * U
        for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
            nb = np.roll(U, sh, ax); nm = np.roll(m, sh, ax)
            acc += np.where(nm, nb, U)
        U = np.where(m, U + k * dt / dx_mm ** 2 * acc, 0.0)
    return np.where(m, U, np.nan)


def locate_point(shape, W, H, x, y, rho_b):
    """단면 위치를 말로: 평면부 중앙 / 모서리 / 그 사이 · 표면 / 내부 / 중심"""
    rho = math.hypot(x, y)
    depth = 1 - rho / max(rho_b, 1e-9)
    radial = "표면" if depth < 0.12 else ("중심부" if depth > 0.65 else "표면 아래")
    if depth > 0.65:
        return "중심부"
    phi = math.degrees(math.atan2(y, x)) % 360
    if shape == SHAPE_TR:
        ang = "직선부" if abs(x) <= max(0.0, (W - H) / 2) + 0.15 * H else "원호부"
    else:
        corners = ([30 + 60 * k for k in range(6)] if shape == SHAPE_HEX else
                   [math.degrees(math.atan2(sy * H, sx * W)) % 360 for sx, sy in [(1, 1), (-1, 1), (-1, -1), (1, -1)]])
        flats = [60 * k for k in range(6)] if shape == SHAPE_HEX else [0, 90, 180, 270]
        dist = lambda a_, b_: min(abs(a_ - b_), 360 - abs(a_ - b_))
        dc, dfl = min(dist(phi, c_) for c_ in corners), min(dist(phi, f_) for f_ in flats)
        ang = "평면부 중앙" if dfl < 0.3 * (dfl + dc) else ("모서리" if dc < 0.3 * (dfl + dc) else "평면–모서리 사이")
    return f"{ang} {radial}"


st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-eyebrow">COLD DRAWING · ROUND → SHAPE</div>
    <h1>선재·이형재 인발 종합 산출</h1>
    <p>감면율과 모서리 R 예측, 인발력·설비 검증, 중량, 직진도 환산을 한 화면에서 계산합니다.</p>
  </div>
  <table class="tblock">
    <tr><th>도구</th><td>인발 계산기 v2</td><th>단위</th><td class="mono">mm · kgf/mm²</td></tr>
    <tr><th>R 모델</th><td colspan="3">{MODEL.get('source', '')}</td></tr>
    <tr><th>보정값</th><td colspan="3" class="mono">δ* {MODEL['delta_star']:.4f} · w* {MODEL['w_star']:.4f} · σε {MODEL['sigma']:.3f} · 최소충전 R □ {MODEL['fill_le20']:.2f}/{MODEL['fill_gt20']:.2f} · HEX {MODEL['fill_le20'] * KF_SQ / KF_HEX:.2f}/{MODEL['fill_gt20'] * KF_SQ / KF_HEX:.2f}</td></tr>
    <tr><th>다이 R</th><td colspan="3">사각: 실측 확인 0.3R 또는 R 없음(샤프) · 육각: 대부분 R 없음 · 육각 R은 사각 실측을 120° 모서리로 환산한 추정</td></tr>
  </table>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "감면율 · 예상 모서리 R",
    "인발력 · 설비 검증",
    "중량",
    "직진도 환산",
    "실측 R DB · 모델 보정",
])

# ==========================================
# [TAB 1] 형상별 감면율 및 모서리 R 예측
# ==========================================
with tab1:
    section_header("REDUCTION · CORNER R", "감면율과 예상 모서리 R",
                   "<span class='keyin-chip'></span>노란 띠 칸에 소재·제품 치수를 넣으면, 제품 모서리가 얼마나 둥글게 나올지 그림으로 보여줍니다.")

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        d_in = st.number_input("투입 소재(원형) 선경 d (mm)", value=27.0, min_value=1.0, step=0.5, key="t1_din")
        shape_type = st.selectbox("제품 단면 형상", [SHAPE_HEX, SHAPE_SQ, SHAPE_TR], index=1, key="t1_shape")

    with col_in2:
        if shape_type == SHAPE_HEX:
            W = st.number_input("대면 치수 W (mm)", value=19.0, step=0.5, key="t1_w")
            H = W
        elif shape_type == SHAPE_SQ:
            W = st.number_input("폭 W (mm)", value=20.0, step=0.5, key="t1_w_sq")
            H = st.number_input("높이 H (mm)", value=20.0, step=0.5, key="t1_h_sq")
        else:
            W = st.number_input("전체 폭 W (mm)", value=30.0, step=0.5, key="t1_w_tr")
            H = st.number_input("높이 H (mm)", value=18.0, step=0.5, key="t1_h_tr")

        if shape_type != SHAPE_TR:
            r_max = float(min(W, H) / 2.0)
            die_choice = st.radio("다이스 모서리 R", list(DIE_R_OPTIONS.keys()), index=0, horizontal=True, key="t1_dier",
                                  help=("육각 다이는 대부분 R 없음(샤프)입니다. 실제 다이를 확인해 선택하세요." if shape_type == SHAPE_HEX else
                                        "실측 확인 결과 0.3R 다이와 R 없는(샤프) 다이가 섞여 있습니다. 같은 다이 코드라도 다를 수 있으니 실제 다이를 확인해 선택하세요."))
            if DIE_R_OPTIONS[die_choice] is None:
                R = st.number_input("다이스 모서리 R 직접 입력 (mm)", value=0.3, min_value=0.0, max_value=r_max, step=0.05, key="t1_dier_custom")
            else:
                R = min(DIE_R_OPTIONS[die_choice], r_max)
        else:
            R = H / 2.0

    is_hex = shape_type == SHAPE_HEX
    e_min = None
    with st.expander("예측 옵션 (요구 R 상한" + (" · 맞꼭지 최소 e" if is_hex else "") + " · 신뢰도 · 최소 도달 R)", expanded=False):
        oc = st.columns(4 if is_hex else 3)
        if is_hex:
            spec_R = oc[0].number_input("고객 요구 모서리 R 상한 (mm)", value=3.0, min_value=0.05, step=0.1, key="t1_spec_hex",
                                        help="육각은 꼭짓점이 조금만 덜 차도 R 값이 크게 나옵니다(후퇴 0.1 mm ≈ R 0.65 mm). 기본 3.0 — 고객 요구값으로 바꾸세요.")
            Gh0 = shape_geom(SHAPE_HEX, W, W)
            e_def = round(2 * (Gh0["h"] - spec_R * Gh0["kf"]), 2)
            e_min = oc[1].number_input("고객 요구 맞꼭지 최소 e (mm)", value=float(e_def), min_value=0.0, step=0.01, key=f"t1_emin_{W:.3f}",
                                       help=f"맞꼭지 = 마주 보는 꼭짓점 사이 거리. 샤프 육각이면 1.1547×W = {2 * Gh0['h']:.2f} mm. "
                                            "기본값은 위 R 상한을 맞꼭지로 바꾼 값이니 고객 도면 값으로 바꾸세요.")
        else:
            spec_R = oc[0].number_input("고객 요구 모서리 R 상한 (mm)", value=1.5, min_value=0.05, step=0.1, key="t1_spec")
        conf = oc[-2].slider("권장 선경 산출 신뢰도", 0.50, 0.99, 0.90, 0.01, key="t1_conf")
        fm_default = fill_min_for((W + H) / 2.0, MODEL, shape_type)
        fill_min_in = oc[-1].number_input("한 번 인발로 도달 가능한 최소 R (mm)", value=float(fm_default), min_value=0.0, step=0.05,
                                          key=f"t1_fillmin_{shape_type}_{fm_default:.3f}",
                                          help=("소재가 다이를 꽉 채워도 제품 모서리 R이 이 값 아래로는 잘 내려가지 않습니다. "
                                                + (f"육각은 실측이 없어 사각 실측의 최소 꼭짓점 후퇴량(□≤20 {MODEL['fill_le20'] * KF_SQ:.2f} mm, □>20 {MODEL['fill_gt20'] * KF_SQ:.2f} mm)을 120° 모서리로 환산: "
                                                   f"W≤20 {MODEL['fill_le20'] * KF_SQ / KF_HEX:.2f} mm, W>20 {MODEL['fill_gt20'] * KF_SQ / KF_HEX:.2f} mm."
                                                   if is_hex else "실측 보정값: □≤20 0.83 mm, □>20 0.36 mm(불확실).")))
    MODEL_T1 = {**MODEL, "fill_override": fill_min_in}

    # --- 단면적 / 감면율 (금형 기준) ---
    A1 = (np.pi / 4.0) * (d_in ** 2)
    if shape_type == SHAPE_TR:
        A2 = (W - H) * H + (np.pi / 4.0) * (H ** 2)
        max_diag = W
    else:
        G = shape_geom(shape_type, W, H)
        A2 = G["A_sharp"] - G["loss"] * R ** 2
        max_diag = 2 * G["h"] - 2 * R * G["kf"]
    RA = (1.0 - A2 / A1) * 100.0 if A1 > 0 else 0.0

    pred = None
    if shape_type != SHAPE_TR and RA > 0:
        pred = predict_R(shape_type, W, H, d_in, R, MODEL_T1)
        G = shape_geom(shape_type, W, H)
        A2_pred = G["A_sharp"] - G["loss"] * pred["rms"] ** 2
        diag_pred = 2 * G["h"] - 2 * pred["p50"] * G["kf"]
        p_spec = prob_R_le(spec_R, pred)
        spec_eff = spec_R
        if is_hex:
            # 맞꼭지 e = 2h − kf·(R_a + R_b) → 코너 하나당 허용 R 로 환산 (마주 보는 두 코너가 같다고 가정)
            R_eq_e = (2 * G["h"] - e_min) / (2 * G["kf"])
            spec_eff = min(spec_R, R_eq_e)
            p_e = prob_R_le(R_eq_e, pred) if R_eq_e > 0 else 0.0
            e_of = lambda r_: 2 * G["h"] - 2 * r_ * G["kf"]
            e_p50, e_lo, e_hi = e_of(pred["p50"]), e_of(pred["p90"]), e_of(pred["p10"])
        d_req = required_d0(shape_type, W, H, spec_eff, conf, R, MODEL_T1) if spec_eff > 0 else np.nan
        RA_req = (1 - A2 / (np.pi / 4 * d_req ** 2)) * 100 if np.isfinite(d_req) else np.nan

    prod_name = (f"□{W:.2f}" if abs(W - H) < 1e-9 else f"{W:.2f}×{H:.2f}") if shape_type == SHAPE_SQ else (f"HEX {W:.2f}" if shape_type == SHAPE_HEX else f"트랙 {W:.1f}×{H:.1f}")
    die_name = "R 없음" if R < 1e-9 else f"R {R:.2f}"

    # ---------------- ① 결론 한 줄 ----------------
    if pred:
        die_surface = 2 * (pred["h"] - R * pred["kf"])   # 다이스 모서리(대각/맞꼭지) 지름
        short = die_surface - d_in
        diag_word = "맞꼭지(꼭짓점 사이)" if is_hex else "모서리 대각"
        if pred["p90"] <= spec_eff and pred["p_fill"] >= 0.5:
            tone, tag = "v-green", "잘 채워짐 · 한 번 인발 한계 수준"
        elif pred["p50"] <= spec_eff:
            tone, tag = "v-amber", "경계 구간 · 코너마다 차이"
        else:
            tone, tag = "v-red", "모서리 미충전 · 자연 R"
        why = (f"소재 Ø{d_in:.1f}이 다이스 {diag_word} {die_surface:.2f} mm보다 <b>{short:.2f} mm 작아서</b>(모서리마다 {short / 2:.2f} mm) 모서리 끝까지 금속이 닿지 않습니다."
               if short > 0 else
               f"소재 Ø{d_in:.1f}이 다이스 {diag_word} {die_surface:.2f} mm보다 <b>{-short:.2f} mm 커서</b>(모서리마다 {-short / 2:.2f} mm) 모서리까지 금속이 채워집니다.")
        goal = f"목표 R ≤ {spec_R:.1f} mm" + (f" · 맞꼭지 e ≥ {e_min:.2f} mm" if is_hex else "")
        if np.isfinite(d_req):
            todo = (f"{goal} (신뢰도 {conf:.0%}) → 소재 <b>Ø{d_req:.2f} 이상</b> 필요 (감면율 {RA_req:.1f}%)"
                    if d_req > d_in + 0.005 else f"{goal} 충족 (신뢰도 {conf:.0%} 기준 최소 소재 Ø{d_req:.2f})")
        else:
            todo = f"{goal}는 한 번 인발로 어렵습니다 (최소 도달 R 약 {pred['R_die']:.2f} mm" + (
                f" ↔ 맞꼭지 최대 약 {2 * pred['h'] - 2 * pred['R_die'] * pred['kf']:.2f} mm)" if is_hex else ")")
        e_line = (f"<br><span class='v-range'>맞꼭지 e 약 <b>{e_p50:.2f} mm</b> (코너에 따라 {e_lo:.2f}–{e_hi:.2f} · 샤프 육각 {2 * pred['h']:.2f}) — "
                  f"요구 ≥ {e_min:.2f} 만족 확률 {p_e * 100:.0f}% (코너 기준)</span>") if is_hex else ""
        st.markdown(f"""
<div class="verdict {tone}">
  <div class="v-main"><span class="v-label">예상 모서리 R</span><span class="v-num">{pred['p50']:.1f}<small> mm</small></span>
       <span class="v-tag">{tag}</span></div>
  <div class="v-sub">{why}<br><span class="v-range">코너마다 대략 {pred['p10']:.1f}–{pred['p90']:.1f} mm 사이로 나옵니다.</span>{e_line}</div>
  <div class="v-todo">{todo}</div>
</div>""", unsafe_allow_html=True)
        # --- 감면율로 보는 모서리 상태 (자연 R ↔ 다이 R) ---
        Gg = shape_geom(shape_type, W, H)
        ra_of = lambda dd: (1 - A2 / (np.pi / 4 * dd ** 2)) * 100
        d_k1 = die_surface                                            # 소재 = 다이스 모서리 대각
        g90 = pred["e_die"] - pred["delta"] - 1.2816 * pred["sigma"]  # 코너 90 %가 꽉 차는 갭
        d_90 = 2 * (pred["h"] - g90)
        ra_k1, ra_90 = ra_of(d_k1), ra_of(d_90)
        lo = max(0.0, math.floor(min(RA, ra_k1) - 8))
        hi = min(85.0, math.ceil(max(RA, ra_90) + 6))
        pos = lambda v: max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))
        if RA < ra_k1:
            msg = (f"현재 감면율 <b>{RA:.1f}%</b>는 {ra_k1:.1f}% 미만이라 <b>모서리 R 부위까지 소재가 차지 않아</b> "
                   f"다이 R과 관계없이 <b>자연 R(약 {pred['p50']:.1f} mm)</b>로 나옵니다.")
        elif RA < ra_90:
            msg = (f"현재 감면율 <b>{RA:.1f}%</b>는 경계({ra_k1:.1f}%)를 넘었지만, 아직 코너마다 채워지는 정도가 달라 "
                   f"자연 R과 다이 R 사이(약 {pred['p50']:.1f} mm)로 나옵니다.")
        else:
            msg = (f"현재 감면율 <b>{RA:.1f}%</b>면 <b>모서리까지 소재가 꽉 차서</b> 다이 R대로 나옵니다 "
                   f"(한 번 인발 한계 약 {pred['R_die']:.1f} mm).")
        ra_note = (f"※ 육각은 다이 R이 없어도 꽉 차면 약 {pred['R_die']:.1f} mm로 나옵니다 — 120° 모서리는 꼭짓점이 {pred['R_die'] * pred['kf']:.2f} mm만 덜 차도 "
                   f"R이 이만큼 됩니다(사각 실측의 한 번 인발 최소 후퇴량을 육각으로 환산). 맞꼭지로는 약 {2 * pred['h'] - 2 * pred['R_die'] * pred['kf']:.2f} mm."
                   if is_hex else
                   f"※ 다이 R이 약 {pred['R_die']:.1f} mm보다 작으면(0.3R·R 없음) 꽉 차도 약 {pred['R_die']:.1f} mm로 나옵니다 — 한 번 인발 한계(□19 실측).")
        if is_hex:
            msg = msg.replace("다이 R대로", f"최소 R(약 {pred['R_die']:.1f} mm)로").replace("자연 R과 다이 R 사이", "자연 R과 최소 R 사이")
        st.markdown(f"""
<div class="ra-box">
  <div class="ra-title">감면율로 보는 모서리 상태</div>
  <div class="ra-track">
    <div class="z z-red" style="width:{pos(ra_k1):.1f}%"><span>자연 R · 모서리 미충전</span></div>
    <div class="z z-amber" style="width:{pos(ra_90) - pos(ra_k1):.1f}%"><span>경계</span></div>
    <div class="z z-green" style="width:{100 - pos(ra_90):.1f}%"><span>꽉 참 · {'최소 R' if is_hex else '다이 R'}</span></div>
    <div class="ra-now" style="left:{pos(RA):.1f}%"><b>현재 {RA:.1f}%</b></div>
  </div>
  <div class="ra-ticks">
    <span style="left:{pos(ra_k1):.1f}%">{ra_k1:.1f}%<br><small>소재 = 다이 {'맞꼭지' if is_hex else '대각'} Ø{d_k1:.2f}</small></span>
    <span style="left:{pos(ra_90):.1f}%">{ra_90:.1f}%<br><small>꽉 참(90%) Ø{d_90:.2f}</small></span>
  </div>
  <div class="ra-msg">{msg}<br>
    {'모서리까지 채우려면' if is_hex else '다이 R대로 나오려면'} 감면율 <b>{ra_k1:.1f}% 이상</b>(소재 Ø{d_k1:.2f} 이상)이어야 모서리에 소재가 닿기 시작하고,
    안정적으로는 <b>{ra_90:.1f}% 이상</b>(Ø{d_90:.2f} 이상)이 필요합니다.
    <span class="ra-note">{ra_note}</span>
  </div>
</div>""", unsafe_allow_html=True)
        if shape_type == SHAPE_HEX:
            st.caption("육각 실측이 아직 없어, 사각 56코너로 맞춘 모델을 육각 기하(120° 모서리, 경계 감면율 17.3%)로 옮긴 추정값입니다. "
                       "외부 육각 인발 실험(Rumiński 등 2025, Ø15.8·Ø16.8 → HEX14)의 모서리 미충전 면적과 비교하면 예측 2.5·1.1 % vs 실험 2.2·1.6 %로 비슷합니다(기본 보정 기준). "
                       "육각 실측을 5번 탭 표에 넣고 재보정하면 정확해집니다.")
        elif abs(W - H) > 1e-6:
            st.caption("직사각은 정사각 실측으로 맞춘 모델의 근사값입니다.")
    elif shape_type == SHAPE_TR:
        st.markdown("<div class='verdict v-grey'><div class='v-sub'>트랙형(장원형)은 모서리가 없어 R 예측 대상이 아닙니다.</div></div>", unsafe_allow_html=True)
    else:
        st.warning("투입 소재가 제품 단면보다 커야 계산할 수 있습니다.")

    # ---------------- ② 읽는 법 + 더 보기 ----------------
    matches = match_db(d_in, W, H) if (pred and shape_type == SHAPE_SQ) else []
    lg1, lg2 = st.columns([2.6, 1.4])
    lg1.markdown(f"""
<div class="legend-row">
  <span><i class="sw sw-rod"></i>투입 소재 Ø{d_in:.1f}</span>
  <span><i class="sw sw-die"></i>다이 {prod_name} ({die_name if shape_type != SHAPE_TR else '—'})</span>
  <span><i class="sw sw-prod"></i>예상 제품</span>
  {'<span><i class="sw sw-gap"></i>덜 채워지는 모서리 (다이와의 차이)</span>' if pred else ''}
</div>""", unsafe_allow_html=True)
    with lg2:
        tg1, tg2 = st.columns(2)
        show_band = tg1.toggle("예측 범위", value=False, key="t1_band", disabled=not pred,
                               help="코너마다 R이 달라질 수 있는 범위(P10–P90)를 노란 띠로 표시합니다.")
        show_meas = tg2.toggle(f"실측 겹치기 ({len(matches)}본)", value=False, key="t1_showmeas", disabled=not matches,
                               help="입력과 같은 조건(선경·치수)의 실측 단면을 보라색으로 겹쳐 봅니다.")

    # ---------------- ③ 그림 2개 ----------------
    n_vis = 360
    th = np.linspace(0, 2 * np.pi, n_vis)
    x_in, y_in = (d_in / 2.0) * np.cos(th), (d_in / 2.0) * np.sin(th)
    ROD_C, DIE_C, PROD_C, PROD_F, GAP_F, MEAS_C = "#8A949D", INK, TEMPER_BLUE, "rgba(36,84,143,0.16)", "rgba(184,58,42,0.55)", "#6A5AA8"
    n_c = 6 if shape_type == SHAPE_HEX else 4

    def gap_crescents(r_die, r_prod):
        gx, gy = [], []
        if r_prod <= r_die + 0.02:
            return gx, gy
        for k in range(n_c):
            xa, ya = corner_arc(shape_type, W, H, k, max(r_die, 1e-4), 40)
            xb, yb = corner_arc(shape_type, W, H, k, r_prod, 40)
            gx += list(xa) + list(xb[::-1]) + [xa[0], None]
            gy += list(ya) + list(yb[::-1]) + [ya[0], None]
        return gx, gy

    fig_2d = go.Figure()
    fig_2d.add_trace(go.Scatter(x=x_in, y=y_in, mode="lines", line=dict(color=ROD_C, dash="dash", width=2),
                                hoverinfo="skip", showlegend=False))
    if shape_type == SHAPE_TR:
        xo, yo = track_points(W, H, n_vis)
        fig_2d.add_trace(go.Scatter(x=xo, y=yo, mode="lines", fill="toself", fillcolor=PROD_F,
                                    line=dict(color=PROD_C, width=3), hoverinfo="skip", showlegend=False))
    else:
        if pred:
            xp, yp = rounded_polygon(shape_type, W, H, pred["p50"], n_vis)
            fig_2d.add_trace(go.Scatter(x=np.r_[xp, xp[0]], y=np.r_[yp, yp[0]], mode="lines", fill="toself", fillcolor=PROD_F,
                                        line=dict(color=PROD_C, width=2.5), hoverinfo="skip", showlegend=False))
            gx, gy = gap_crescents(R, pred["p50"])
            if gx:
                fig_2d.add_trace(go.Scatter(x=gx, y=gy, mode="lines", fill="toself", fillcolor=GAP_F,
                                            line=dict(color=SCALE_RED, width=0.8), hoverinfo="skip", showlegend=False))
            if show_band:
                bx, by = [], []
                for k in range(n_c):
                    xl, yl = corner_arc(shape_type, W, H, k, pred["p10"], 40)
                    xh, yh = corner_arc(shape_type, W, H, k, pred["p90"], 40)
                    bx += list(xl) + list(xh[::-1]) + [xl[0], None]
                    by += list(yl) + list(yh[::-1]) + [yl[0], None]
                fig_2d.add_trace(go.Scatter(x=bx, y=by, mode="lines", fill="toself", fillcolor="rgba(201,146,46,0.40)",
                                            line=dict(color="rgba(160,112,26,0.9)", width=0.8), hoverinfo="skip", showlegend=False))
        xd, yd = rounded_polygon(shape_type, W, H, R, n_vis)
        fig_2d.add_trace(go.Scatter(x=np.r_[xd, xd[0]], y=np.r_[yd, yd[0]], mode="lines", line=dict(color=DIE_C, width=1.6),
                                    hoverinfo="skip", showlegend=False))
        if show_meas:
            for mrow in matches[:7]:
                radii = db_radii_ccw(mrow["R"])
                xm, ym = rounded_polygon(SHAPE_SQ, mrow["lcx"], mrow["lcy"], radii, n_vis)
                fig_2d.add_trace(go.Scatter(x=np.r_[xm, xm[0]], y=np.r_[ym, ym[0]], mode="lines", line=dict(color=MEAS_C, width=1.2),
                                            showlegend=False,
                                            hovertemplate=f"실측 {mrow['id']}<br>R " + " / ".join(f"{v:.2f}" for v in mrow["R"]) + "<extra></extra>"))
    # 직접 라벨 (범례 대신)
    rr = d_in / 2.0
    fig_2d.add_annotation(x=-rr * 0.72, y=rr * 0.72, ax=-rr * 0.98, ay=rr * 1.12, axref="x", ayref="y", showarrow=True,
                          arrowhead=0, arrowcolor=ROD_C, text=f"투입 소재 Ø{d_in:.1f}", font=dict(size=12, color=MUTED), xanchor="right")
    if shape_type != SHAPE_TR:
        fig_2d.add_annotation(x=0, y=-H / 2 if shape_type == SHAPE_SQ else -W / SQRT3, text=f"다이 {prod_name}", showarrow=False,
                              yshift=-14, font=dict(size=12, color=INK))
    fig_2d.add_annotation(x=0, y=0, text="예상 제품", showarrow=False, font=dict(size=14, color=PROD_C))
    if pred:
        vx, vy = corner_vertex(shape_type, W, H, 0)
        ax_, ay_ = corner_arc(shape_type, W, H, 0, pred["p50"], 41)
        fig_2d.add_annotation(x=ax_[20], y=ay_[20], ax=vx + 0.16 * pred["a"], ay=vy + 0.16 * pred["a"], axref="x", ayref="y",
                              showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor=SCALE_RED,
                              text=f"<b>모서리 R {pred['p50']:.1f}</b>", font=dict(family=FONT_MONO, size=13, color=SCALE_RED),
                              bgcolor="rgba(255,255,255,0.95)", bordercolor=SCALE_RED, borderwidth=1, xanchor="left")
    lim = max(d_in / 2.0, max_diag / 2.0) * 1.32
    fig_2d.update_layout(title="전체 단면 — 둥근 소재가 다이를 지나면",
                         xaxis=dict(scaleanchor="y", scaleratio=1, range=[-lim, lim], showticklabels=False, showgrid=False),
                         yaxis=dict(range=[-lim, lim], showticklabels=False, showgrid=False),
                         height=470, showlegend=False, margin=dict(l=10, r=10, t=46, b=10))

    col_l, col_r = st.columns([1, 1])
    style_fig(fig_2d)
    fig_2d.update_xaxes(showgrid=False, showticklabels=False); fig_2d.update_yaxes(showgrid=False, showticklabels=False)
    col_l.plotly_chart(fig_2d, **FW_CHART)

    if pred:
        # 모서리 확대 (오른쪽 위 모서리)
        vx, vy = corner_vertex(shape_type, W, H, 0)
        u = np.array([vx, vy]) / math.hypot(vx, vy)
        r50 = pred["p50"]
        span = max(2.6, 1.7 * math.tan(math.pi / n_c) * max(r50, pred["p90"] if show_band else r50) + 1.0)   # 원호가 변을 따라 R·tan(π/n)만큼 뻗음
        fz = go.Figure()
        fz.add_trace(go.Scatter(x=x_in, y=y_in, mode="lines", line=dict(color=ROD_C, dash="dash", width=2), hoverinfo="skip"))
        xp, yp = rounded_polygon(shape_type, W, H, r50, n_vis * 4)
        fz.add_trace(go.Scatter(x=np.r_[xp, xp[0]], y=np.r_[yp, yp[0]], mode="lines", fill="toself", fillcolor=PROD_F,
                                line=dict(color=PROD_C, width=3), hoverinfo="skip"))
        xa, ya = corner_arc(shape_type, W, H, 0, max(R, 1e-4), 60)
        xb, yb = corner_arc(shape_type, W, H, 0, r50, 60)
        if r50 > R + 0.02:
            fz.add_trace(go.Scatter(x=list(xa) + list(xb[::-1]) + [xa[0]], y=list(ya) + list(yb[::-1]) + [ya[0]], mode="lines",
                                    fill="toself", fillcolor=GAP_F, line=dict(color=SCALE_RED, width=1), hoverinfo="skip"))
        if show_band:
            xl, yl = corner_arc(shape_type, W, H, 0, pred["p10"], 60)
            xh, yh = corner_arc(shape_type, W, H, 0, pred["p90"], 60)
            fz.add_trace(go.Scatter(x=list(xl) + list(xh[::-1]) + [xl[0]], y=list(yl) + list(yh[::-1]) + [yl[0]], mode="lines",
                                    fill="toself", fillcolor="rgba(201,146,46,0.40)", line=dict(color="rgba(160,112,26,0.9)", width=0.8),
                                    hoverinfo="skip"))
        if show_meas:
            for mrow in matches:
                for k_db, rv in zip(["TL", "TR", "BL", "BR"], mrow["R"]):
                    xm_, ym_ = corner_arc(SHAPE_SQ, W, H, 0, rv, 50)
                    fz.add_trace(go.Scatter(x=xm_, y=ym_, mode="lines", line=dict(color=MEAS_C, width=1.2),
                                            hovertemplate=f"실측 {mrow['id']} {k_db}: R {rv:.2f}<extra></extra>"))
        xd, yd = rounded_polygon(shape_type, W, H, R, n_vis * 4)
        fz.add_trace(go.Scatter(x=np.r_[xd, xd[0]], y=np.r_[yd, yd[0]], mode="lines", line=dict(color=DIE_C, width=2.2), hoverinfo="skip"))
        # R 화살표 (측정기 화면처럼: 원호 중심 → 원호)
        if shape_type == SHAPE_HEX:
            cen = ((W / 2 - r50) / math.cos(math.pi / 6)) * u
        else:
            cen = np.array([W / 2 - r50, H / 2 - r50])
        mid = cen + r50 * u
        fz.add_annotation(x=mid[0], y=mid[1], ax=cen[0], ay=cen[1], axref="x", ayref="y", showarrow=True,
                          arrowhead=2, arrowwidth=1.6, arrowcolor=PROD_C, text="")
        fz.add_annotation(x=cen[0], y=cen[1], text=f"<b>R {r50:.1f}</b>", showarrow=False, xanchor="right", yanchor="top",
                          xshift=-4, yshift=-2, font=dict(family=FONT_MONO, size=14, color=PROD_C))
        fz.add_trace(go.Scatter(x=[cen[0]], y=[cen[1]], mode="markers", marker=dict(symbol="cross-thin", size=10, color=PROD_C,
                                line=dict(width=1.5, color=PROD_C)), hoverinfo="skip"))
        # 소재 표면 ↔ 다이스 모서리 거리
        d_pt = (pred["h"] - R * pred["kf"]) * u
        r_pt = (d_in / 2.0) * u
        miss = float(np.dot(d_pt - r_pt, u))
        gap_col = SCALE_RED if miss > 0 else OXIDE_GREEN
        fz.add_trace(go.Scatter(x=[r_pt[0], d_pt[0]], y=[r_pt[1], d_pt[1]], mode="lines+markers", line=dict(color=gap_col, width=3),
                                marker=dict(size=7, color=gap_col), hoverinfo="skip"))
        perp = np.array([-u[1], u[0]])
        lab = (d_pt + r_pt) / 2 + perp * 0.18 * span
        fz.add_annotation(x=lab[0], y=lab[1], text=(f"소재가 모서리까지 {miss:.2f} mm 못 미침" if miss > 0 else f"소재가 모서리보다 {-miss:.2f} mm 큼"),
                          showarrow=False, font=dict(size=12, color=gap_col), bgcolor="rgba(255,255,255,0.9)", xanchor="right")
        # 직접 라벨
        fz.add_annotation(x=vx, y=vy - 0.10 * span, text="다이스 모서리", showarrow=False, xanchor="left", yanchor="top", xshift=8,
                          font=dict(size=12, color=INK))
        if r50 > R + 0.02:
            xm2, ym2 = corner_arc(shape_type, W, H, 0, r50 * 0.62 + R * 0.38, 41)
            gp = np.array([xm2[20], ym2[20]]) + u * (0.18 * (r50 - R))
            fz.add_annotation(x=gp[0], y=gp[1], ax=vx + 0.10 * span, ay=vy - 0.42 * span, axref="x", ayref="y", showarrow=True,
                              arrowhead=0, arrowwidth=1, arrowcolor=SCALE_RED, text="덜 채워지는 부분",
                              font=dict(size=12, color=SCALE_RED), bgcolor="rgba(255,255,255,0.92)", xanchor="left")
        fz.add_annotation(x=vx - 0.62 * span, y=vy - 0.62 * span, text="예상 제품", showarrow=False, font=dict(size=14, color=PROD_C))
        z_title = ("모서리 확대 — 거의 다 채워짐 (남은 빨간 부분은 한 번 인발 한계)" if pred["p_fill"] >= 0.5
                   else "모서리 확대 — 빨간 부분만큼 덜 채워집니다")
        fz.update_layout(title=z_title, showlegend=False,
                         xaxis=dict(scaleanchor="y", scaleratio=1, range=[vx - span, vx + 0.42 * span], constrain="domain", title="mm"),
                         yaxis=dict(range=[vy - span, vy + 0.42 * span], constrain="domain"),
                         height=470, margin=dict(l=10, r=10, t=46, b=10))
        style_fig(fz); fz.update_layout(showlegend=False)
        col_r.plotly_chart(fz, **FW_CHART)
    else:
        col_r.empty()

    # ---------------- ④ 숫자로 보기 ----------------
    if pred:
        st.markdown("#### 숫자로 보기")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("예상 모서리 R (중앙값)", f"{pred['p50']:.2f} mm", f"코너별 {pred['p10']:.2f} – {pred['p90']:.2f} mm", delta_color="off")
        d2.metric("모서리가 꽉 찰 확률", f"{pred['p_fill'] * 100:.0f} %", f"소재/다이 {'맞꼭지' if is_hex else '대각'} 비 {pred['k_ratio']:.3f}", delta_color="off")
        if is_hex:
            d3.metric(f"R ≤ {spec_R:.1f} · e ≥ {e_min:.2f} 만족", f"{prob_R_le(spec_eff, pred) * 100:.0f} %",
                      f"R만 {p_spec * 100:.0f}% · 맞꼭지만 {p_e * 100:.0f}% (코너 기준)", delta_color="off")
        else:
            d3.metric(f"R ≤ {spec_R:.1f} mm 만족 확률", f"{p_spec * 100:.0f} %", f"예측 실단면적 {A2_pred:.1f} mm²", delta_color="off")
        if np.isfinite(d_req):
            d4.metric(f"권장 최소 소재 (신뢰도 {conf:.0%})", f"Ø {d_req:.2f}", f"감면율 {RA_req:.1f} % · 현재 대비 {d_req - d_in:+.2f}", delta_color="inverse")
        else:
            d4.metric("권장 최소 소재", "산출 불가",
                      (f"요구 맞꼭지가 한 번 인발 최대 약 {2 * pred['h'] - 2 * pred['R_die'] * pred['kf']:.2f}보다 큼"
                       if is_hex and spec_eff < spec_R else f"목표 R이 최소 도달 R {pred['R_die']:.2f} 이하"), delta_color="off")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("소재 단면적 A₁", f"{A1:.2f} mm²", f"Ø {d_in:.2f} mm", delta_color="off")
    c2.metric("제품 단면적 A₂ (다이 기준)", f"{A2:.2f} mm²", f"감면율 {RA:.2f} %", delta_color="off")
    c3.metric("다이 맞꼭지 치수" if is_hex else "다이 대각 치수", f"{max_diag:.2f} mm", f"다이 {die_name}", delta_color="off")
    if pred:
        c4.metric("예상 제품 맞꼭지 e" if is_hex else "예상 제품 대각 치수", f"{diag_pred:.2f} mm",
                  (f"다이 대비 {diag_pred - max_diag:+.2f} · e/W {diag_pred / W:.3f}" if is_hex else f"다이 대비 {diag_pred - max_diag:+.2f} mm"),
                  delta_color="off")
    else:
        c4.metric("제품 대각 치수", f"{max_diag:.2f} mm", "트랙형", delta_color="off")
    if pred and is_hex:
        st.caption(f"육각은 꼭짓점이 0.1 mm만 덜 차도 R이 {0.1 / pred['kf']:.2f} mm 커지지만(사각은 {0.1 / KF_SQ:.2f} mm), 맞꼭지 e는 R 1 mm당 {2 * pred['kf']:.2f} mm만 줄어듭니다. "
                   "그래서 육각은 R 값이 커 보여도 맞꼭지 치수는 크게 줄지 않을 수 있으니 두 값을 함께 보세요.")
    elif pred:
        st.caption(f"다이가 R 없음(샤프)이어도 한 번 인발로는 제품 모서리가 약 {pred['R_die']:.2f} mm보다 날카로워지기 어렵습니다 "
                   f"(□19 실측: 0.3R·R 없음 다이 모두 꽉 찬 조건에서 0.72–1.09 mm).")

    if matches:
        st.markdown(f"#### 같은 조건 실측 (Ø{d_in:.1f} → □{W:.2f}, {len(matches)}본)")
        mdf = pd.DataFrame([{
            "제조번호": m["id"], "강종": m["grade"], "다이스": m["die"], "다이 R": ("R 없음" if m["die_r"] == 0 else f"{m['die_r']:.1f}R"),
            "LC(가로×세로)": f"{m['lcx']:.3f}×{m['lcy']:.3f}",
            "R TL": m["R"][0], "R TR": m["R"][1], "R BL": m["R"][2], "R BR": m["R"][3],
            "평균 R": round(float(np.mean(m["R"])), 2), "최대-최소": round(float(np.ptp(m["R"])), 2),
        } for m in matches])
        st.dataframe(mdf, hide_index=True, **FW_DF)
        allR = np.concatenate([m["R"] for m in matches])
        st.caption(f"실측 코너 {len(allR)}개: 평균 {allR.mean():.2f} · P10 {np.quantile(allR, 0.1):.2f} · P90 {np.quantile(allR, 0.9):.2f} mm  ↔  예측 평균 {pred['mean']:.2f} · P10 {pred['p10']:.2f} · P90 {pred['p90']:.2f} mm")

    if pred:
        with st.expander("예측 모델 설명 & 기존 식 비교"):
            old = old_model_R(W, RA / 100.0, R)
            st.markdown(f"""
- **기존 식**: R_eff = 다이 R + 0.18·W·e^(-5.2·RA) = **{old:.2f} mm** (감면율에 거의 둔감 → 꽉 차는 조건은 과대, 덜 차는 조건은 과소 예측)
- **최소 도달 R** = max(다이 R, 한 번 인발 최소 R) = **{pred['R_die']:.2f} mm** — 다이를 R 없음으로 만들어도 제품 모서리가 그만큼 날카로워지지는 않음
- **코너 갭 모델 (실측 보정)**: 투입 소재 반경과 다이스 모서리(샤프 꼭짓점)의 차이 **g = h − d/2 = {pred['g']:+.3f} mm**가 지배인자
  - 꼭짓점 후퇴량 c = c_die + w·ln(1+exp((g+ε+δ−c_die)/w)),  R = c / (1/cos(π/n) − 1)  ({'육각 n=6 → R = 6.46·c' if is_hex else '사각 n=4 → R = 2.41·c'})
  - δ = {pred['delta']:.3f} mm (재료 유동에 의한 추가 코너 수축), w = {pred['w']:.3f} mm (전이 폭), σε = {pred['sigma']:.3f} mm (코너별 편차: 선재 공차·편심·다이 정렬)
  - 덜 차는 구간에서 R은 갭 1 mm당 약 {1 / pred['kf']:.2f} mm 증가 (기하학적 기울기{'' if is_hex else ' — 실측 기울기 ≈2.3과 일치'})
- 강종(AISI1020/S20C/S45C/SS400) 효과는 실측 상 유의하지 않아 모델에서 제외
""" + ("""
**육각 적용 방법 (육각 실측 없음)**
- 경계 감면율: 소재 = 다이 맞꼭지(1.1547·W)일 때 RA = 1 − 3√3/(2π) = **17.3 %** (사각 36.3 %). 육각은 원에 더 가까워 훨씬 낮은 감면율에서 모서리가 찹니다.
- δ·w·σε는 사각 값을 그대로 쓰고, '한 번 인발 최소 R'은 **최소 꼭짓점 후퇴량이 형상과 같다**고 보고 환산 (사각 0.83 mm → 육각 2.22 mm, W ≤ 20).
  R 값을 그대로 옮기는 방식(0.83 mm)은 외부 육각 실험(Ø16.8 조건)의 미충전 면적을 약 1/4로 과소 예측해 채택하지 않았습니다.
- 외부 점검: Rumiński 등(2025) X6CrNiTi18-10 HEX14 — Ø15.8(RA 13.5 %) 미충전 2.21 % / Ø16.8(RA 23.5 %) 1.58 % ↔ 모델 2.45 % / 1.09 %.
  같은 논문에서 RA 37.5 %(Ø18.6 → HEX14)는 인발 중 파단(스테인리스) → 육각에 사각만큼 큰 감면율은 필요하지 않음.
- 맞꼭지 e = 2h − 2·0.155·R → R이 1 mm 커져도 e는 0.31 mm만 줄어듦.
""" if is_hex else ""))
            st.dataframe(CV_TABLE, hide_index=True, **FW_DF)

    # ---------------- 3D + 변형·온도 간이 해석 ----------------
    st.markdown("#### 3D 인발 형상과 변형·온도 (간이 해석)")
    with st.expander("해석 조건 — 다이 각 · 인발 속도 · 마찰 · 소재 강도 · 베어링", expanded=False):
        h1, h2, h3, h4, h5 = st.columns(5)
        two_alpha = h1.number_input("어프로치 각 2α (°)", value=30.0, min_value=4.0, max_value=60.0, step=1.0, key="t1_ap",
                                    help="다이 라벨의 AP 값(사내 다이 AP 30·32). 반각 α = AP/2 로 계산합니다.")
        v_mpm = h2.number_input("인발 속도 (m/min)", value=20.0, min_value=1.0, max_value=300.0, step=1.0, key="t1_vel")
        mu_f = h3.number_input("마찰계수 μ", value=0.05, min_value=0.01, max_value=0.30, step=0.01, key="t1_mu",
                               help="인산염 피막 + 비누 윤활 약 0.03–0.06, 윤활 불량이면 0.1 이상.")
        ts_in = h4.number_input("소재 인장강도 TS (kgf/mm²)", value=55.0, min_value=20.0, max_value=150.0, step=1.0, key="t1_ts",
                                help="2번 탭 강종표 참고: S20C 48.5 · S45C 71 · SCM435 96. 가공경화 지수 n = 0.18로 가정합니다.")
        bl_in = h5.number_input("베어링 길이 (mm)", value=6.0, min_value=0.0, max_value=30.0, step=0.5, key="t1_bl",
                                help="다이 라벨의 BL 값(사내 BL 6–8).")
    dfz = None
    if shape_type == SHAPE_TR or pred:
        r_prod_df = (H / 2.0) if shape_type == SHAPE_TR else float(pred["p50"])
        r_die_df = (H / 2.0) if shape_type == SHAPE_TR else float(R)
        dfz = deform_fields(shape_type, float(W), float(H), r_prod_df, r_die_df, float(d_in),
                            float(two_alpha), float(v_mpm), float(mu_f), float(ts_in), float(bl_in))
    v1, v2 = st.columns([3, 1])
    FIELD_OPTS = ["다이 면압 (힘)", "유효 응력 (경도)", "온도", "유효 변형률", "형상만"]
    color_opt = v2.radio("색 표시", FIELD_OPTS if dfz else ["형상만"], key="t1_3d_color",
                         help="다이 면압: 다이가 소재를 누르는 힘(MPa) · 유효 응력: 가공경화로 단단해진 정도(MPa, 경도 환산) · "
                              "온도: 인발 중 표면 온도 · 유효 변형률: 누적 소성변형량 — 모두 간이 해석")
    band_on = v2.checkbox("FEM처럼 단계별 색", value=True, key="t1_cs_band", help="끄면 부드러운 무지개 색으로 표시합니다.")
    view_opt = v2.radio("보기 방향", ["측면 사선 (기본)", "출구 정면", "입구 정면"], key="t1_3d_view")
    show_die3d = v2.checkbox("출구에 다이 형상 겹치기", value=True, key="t1_3d_die")
    v2.caption("길이 방향은 개략 비율입니다 (입구 소재 30 · 어프로치 50 · 베어링/제품 20). 파랑 = 낮음, 빨강 = 높음.")
    CS_F = fem_scale(band_on)

    n_pts = 180
    th3 = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
    x_in3, y_in3 = (d_in / 2.0) * np.cos(th3), (d_in / 2.0) * np.sin(th3)
    if shape_type == SHAPE_TR:
        xs_, ys_ = track_points(W, H, 720)
        out_label = f"트랙 {W:.1f}×{H:.1f}"
    else:
        r_out = pred["p50"] if pred else R
        xs_, ys_ = rounded_polygon(shape_type, W, H, r_out, 720)
        out_label = (f"□{W:.1f}" if shape_type == SHAPE_SQ else f"HEX {W:.1f}") + f" · 예상 R {r_out:.2f}"
    x_out, y_out = resample_polar(xs_, ys_, n_pts)

    Z_IN, Z_AP, Z_END = 30.0, 80.0, 100.0
    z_levels = np.r_[np.linspace(0, Z_IN, 4), np.linspace(Z_IN, Z_AP, 26)[1:], np.linspace(Z_AP, Z_END, 5)[1:]]
    field_on = dfz is not None and color_opt != "형상만"
    smooth = lambda t_: t_ * t_ * (3 - 2 * t_)
    if dfz:
        sig_of = lambda e: dfz["K"] * np.power(dfz["eps0"] + np.maximum(e, 0.0), dfz["n"])
        hv_of = lambda sg: 0.306 * sg                                   # Tabor: HV ≈ 3σ/9.81
        nrow = len(dfz["die_x"])

        def die_row(xmm):
            k_ = float(np.interp(xmm, dfz["die_x"], np.arange(nrow)))
            i0 = min(int(k_), nrow - 2) if nrow > 1 else 0
            w_ = k_ - i0
            return dfz["die_P"][i0] * (1 - w_) + dfz["die_P"][min(i0 + 1, nrow - 1)] * w_

        def x_of_z(z):
            if z <= Z_IN:
                return None
            if z <= Z_AP:
                return (z - Z_IN) / (Z_AP - Z_IN) * dfz["L_ap"]
            return dfz["L_ap"] + (z - Z_AP) / (Z_END - Z_AP) * max(float(bl_in), 0.0)
    FIELD_META = {
        "다이 면압 (힘)": ("MPa", "%{intensity:.0f} MPa", 0.0),
        "유효 응력 (경도)": ("MPa", "%{intensity:.0f} MPa", dfz["sig0"] if dfz else 0.0),
        "온도": ("°C", "%{intensity:.0f} °C", 25.0),
        "유효 변형률": ("ε", "ε %{intensity:.2f}", 0.0),
    }
    if field_on:
        unit_, hov_, base_v = FIELD_META[color_opt]
        eps_s3 = np.interp(th3, dfz["phi"], dfz["eps_surf"], period=2 * np.pi)
        T_s3 = np.interp(th3, dfz["phi"], dfz["T_surf"], period=2 * np.pi)

        def surf_vals(z):
            t_ = 0.0 if z <= Z_IN else (1.0 if z >= Z_AP else (z - Z_IN) / (Z_AP - Z_IN))
            f_ = smooth(t_)
            tb = 0.0 if z <= Z_AP else (z - Z_AP) / (Z_END - Z_AP)
            if color_opt == "온도":
                return 25.0 + (T_s3 - 25.0) * (0.82 * f_ + 0.18 * tb)
            if color_opt == "유효 변형률":
                return eps_s3 * f_
            if color_opt == "유효 응력 (경도)":
                return sig_of(eps_s3 * f_)
            xm = x_of_z(z)
            if xm is None:
                return np.zeros(n_pts)
            return np.interp(th3, dfz["phi"], die_row(xm), period=2 * np.pi)
        sec_field = {"온도": dfz["T"], "유효 변형률": dfz["eps"], "유효 응력 (경도)": dfz["sig"]}.get(color_opt)
    X_3d, Y_3d, Z_3d, V_3d = [], [], [], []
    for z in z_levels:
        t = 0.0 if z <= Z_IN else (1.0 if z >= Z_AP else (z - Z_IN) / (Z_AP - Z_IN))
        f = smooth(t)
        X_3d.extend((1 - f) * x_in3 + f * x_out)
        Y_3d.extend((1 - f) * y_in3 + f * y_out)
        Z_3d.extend([z] * n_pts)
        if field_on:
            V_3d.extend(surf_vals(z))
    nL = len(z_levels)
    I, J, K = [], [], []
    for i in range(nL - 1):
        for j in range(n_pts):
            nj = (j + 1) % n_pts
            p1, p2, p3, p4 = i * n_pts + j, i * n_pts + nj, (i + 1) * n_pts + j, (i + 1) * n_pts + nj
            I.extend([p1, p2]); J.extend([p2, p4]); K.extend([p3, p3])
    # 양 끝 마개(cap): 중심점 + 링 삼각형 팬
    def _cap(xr, yr, z0, base):
        idx_c = base + n_pts
        return ([*xr, 0.0], [*yr, 0.0], [z0] * (n_pts + 1),
                [idx_c] * n_pts, [base + j for j in range(n_pts)], [base + (j + 1) % n_pts for j in range(n_pts)])
    nb = len(X_3d)
    cx_, cy_, cz_, ci, cj, ck = _cap(x_in3, y_in3, 0.0, nb)
    X_3d += cx_; Y_3d += cy_; Z_3d += cz_; I += ci; J += cj; K += ck
    if field_on:
        V_3d += [base_v] * (n_pts + 1)
    nb = len(X_3d)
    cx_, cy_, cz_, ci, cj, ck = _cap(x_out, y_out, Z_END, nb)
    X_3d += cx_; Y_3d += cy_; Z_3d += cz_; I += ci; J += cj; K += ck
    if field_on:
        V_3d += list(surf_vals(Z_END)) + [float(np.nanmin(sec_field)) if sec_field is not None else base_v]

    fig_3d = go.Figure()
    scene_ann = []
    if field_on:
        vmax = float(np.nanmax(V_3d))
        if sec_field is not None:
            vmax = max(vmax, float(np.nanmax(sec_field)))
        vmin = min(base_v, float(np.nanmin(V_3d)))
        fig_3d.add_trace(go.Mesh3d(x=X_3d, y=Y_3d, z=Z_3d, i=I, j=J, k=K, intensity=V_3d,
                                   colorscale=CS_F, cmin=vmin, cmax=vmax,
                                   showscale=True, colorbar=dict(title=unit_, len=0.62, thickness=14, x=1.0, nticks=13),
                                   opacity=1.0, flatshading=False, name="인발재",
                                   lighting=dict(ambient=0.72, diffuse=0.55, specular=0.1, roughness=0.7, fresnel=0.05),
                                   lightposition=dict(x=200, y=-300, z=400), hovertemplate=hov_ + "<extra></extra>"))
        xg3 = dfz["x"]
        if sec_field is not None:                                     # 출구 끝면 = 단면 분포
            fig_3d.add_trace(go.Surface(x=xg3, y=xg3, z=np.where(np.isnan(sec_field), np.nan, Z_END + 0.08), surfacecolor=sec_field,
                                        colorscale=CS_F, cmin=vmin, cmax=vmax, showscale=False, hoverinfo="skip",
                                        lighting=dict(ambient=0.9, diffuse=0.2), name="출구 단면"))
        else:
            fig_3d.add_trace(go.Surface(x=xg3, y=xg3, z=np.where(np.isnan(dfz["sig"]), np.nan, Z_END + 0.08),
                                        surfacecolor=np.zeros_like(dfz["sig"]), colorscale=[[0, "#C9CED3"], [1, "#C9CED3"]],
                                        showscale=False, hoverinfo="skip", name="출구 단면"))
        # 최댓값 위치 표시
        if color_opt == "다이 면압 (힘)":
            Pm_ = dfz["die_P"]
            near = np.argwhere(Pm_ >= 0.995 * Pm_.max())                    # 최댓값과 같은 곳 중 화면 쪽(카메라 방향)을 표시
            cam_ang = {"측면 사선 (기본)": math.atan2(0.95, -1.75)}.get(view_opt, math.pi / 2)
            ang_d = np.abs((dfz["phi"][near[:, 1]] - cam_ang + np.pi) % (2 * np.pi) - np.pi)
            ip, jp = near[int(np.argmin(ang_d))]
            xh = float(dfz["die_x"][ip]); ph = float(dfz["phi"][jp])
            zh = (Z_IN + xh / dfz["L_ap"] * (Z_AP - Z_IN)) if xh <= dfz["L_ap"] else (Z_AP + (xh - dfz["L_ap"]) / max(float(bl_in), 1e-6) * (Z_END - Z_AP))
            fh = smooth(min(1.0, max(0.0, (zh - Z_IN) / (Z_AP - Z_IN))))
            rh = (1 - fh) * d_in / 2.0 + fh * float(np.interp(ph, th3, np.hypot(x_out, y_out), period=2 * np.pi))
            hot3 = (rh * 1.05 * math.cos(ph), rh * 1.05 * math.sin(ph), zh, f"최대 면압 {float(dfz['die_P'].max()):.0f} MPa")
        else:
            sf_ = np.nan_to_num(sec_field, nan=-1e18)
            near = np.argwhere(sf_ >= float(np.nanmax(sec_field)) - 0.005 * (float(np.nanmax(sec_field)) - float(np.nanmin(sec_field)) + 1e-9))
            cam_ang = {"측면 사선 (기본)": math.atan2(0.95, -1.75)}.get(view_opt, math.pi / 2)
            ang_n = np.arctan2(xg3[near[:, 0]], xg3[near[:, 1]])
            ih = near[int(np.argmin(np.abs((ang_n - cam_ang + np.pi) % (2 * np.pi) - np.pi)))]
            fmt_ = {"온도": "최고 {:.0f} °C", "유효 변형률": "최대 ε {:.2f}", "유효 응력 (경도)": "최대 {:.0f} MPa"}[color_opt]
            hot3 = (float(xg3[ih[1]]), float(xg3[ih[0]]), Z_END + 0.4, fmt_.format(float(np.nanmax(sec_field))))
        fig_3d.add_trace(go.Scatter3d(x=[hot3[0]], y=[hot3[1]], z=[hot3[2]], mode="markers",
                                      marker=dict(size=7, color="#FFFFFF", line=dict(color=INK, width=3)), showlegend=False, hoverinfo="skip"))
        scene_ann = [dict(x=hot3[0], y=hot3[1], z=hot3[2], text=f"<b>{hot3[3]}</b>", showarrow=True, arrowhead=2, arrowcolor=INK,
                          ax=-60, ay=-46, font=dict(size=13, color=INK), bgcolor="rgba(255,255,255,0.95)", bordercolor=INK, borderwidth=1)]
    else:
        fig_3d.add_trace(go.Mesh3d(x=X_3d, y=Y_3d, z=Z_3d, i=I, j=J, k=K, intensity=Z_3d,
                                   colorscale=[[0, "#AEB6BE"], [0.3, "#9FB6D3"], [0.8, TEMPER_BLUE], [1, "#173A63"]],
                                   showscale=False, opacity=1.0, flatshading=False, name="인발재",
                                   lighting=dict(ambient=0.45, diffuse=0.8, specular=0.25, roughness=0.5, fresnel=0.1),
                                   lightposition=dict(x=200, y=-300, z=400), hoverinfo="skip"))
    fig_3d.add_trace(go.Scatter3d(x=np.r_[x_in3, x_in3[0]], y=np.r_[y_in3, y_in3[0]], z=np.zeros(n_pts + 1), mode="lines",
                                  line=dict(color=MUTED, width=5), name=f"입구 원형 Ø{d_in:.1f}"))
    fig_3d.add_trace(go.Scatter3d(x=np.r_[x_out, x_out[0]], y=np.r_[y_out, y_out[0]], z=np.full(n_pts + 1, Z_END), mode="lines",
                                  line=dict(color=INK if field_on else STRAW, width=5 if field_on else 7), name=f"출구 {out_label}"))
    if show_die3d and shape_type != SHAPE_TR:
        xd3, yd3 = rounded_polygon(shape_type, W, H, R, 720)
        fig_3d.add_trace(go.Scatter3d(x=np.r_[xd3, xd3[0]], y=np.r_[yd3, yd3[0]], z=np.full(len(xd3) + 1, Z_END + 0.3), mode="lines",
                                      line=dict(color=INK, width=3, dash="dash"), name=f"다이 형상 (R {R:.2f})"))
    y_lab = max(d_in, max_diag) / 2.0 * 1.02
    for zz, nm in [(Z_IN, "어프로치 시작"), (Z_AP, "베어링·제품")]:
        fig_3d.add_trace(go.Scatter3d(x=[0, 0], y=[y_lab * 0.75, y_lab], z=[zz, zz], mode="lines+text", text=["", nm],
                                      textposition="top center", line=dict(color="#8A949D", width=2, dash="dot"),
                                      textfont=dict(size=11, color=MUTED), showlegend=False, hoverinfo="skip"))
    cams = {
        "측면 사선 (기본)": dict(eye=dict(x=-1.75, y=0.95, z=1.45), up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0)),
        "출구 정면": dict(eye=dict(x=0.0, y=-0.001, z=2.6), up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0)),
        "입구 정면": dict(eye=dict(x=0.0, y=-0.001, z=-2.6), up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0)),
    }
    lim3 = max(d_in, max_diag) / 2.0 * 1.08
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title="x (mm)", range=[-lim3, lim3], backgroundcolor="#F6F7F8"),
            yaxis=dict(title="y (mm)", range=[-lim3, lim3], backgroundcolor="#F6F7F8"),
            zaxis=dict(title="인발 방향 →", range=[0, Z_END + 2], backgroundcolor="#EEF0F2", showticklabels=False),
            aspectmode="manual", aspectratio=dict(x=1, y=1, z=2.2), camera=cams[view_opt], annotations=scene_ann,
        ),
        height=560, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color=INK),
        legend=dict(orientation="h", y=1.0, x=0.0, yanchor="bottom", bgcolor="rgba(255,255,255,0.7)"),
        uirevision=view_opt,
    )
    fig_3d.update_layout(font=dict(family=FONT_SANS, size=12, color=INK))
    v1.plotly_chart(fig_3d, **FW_CHART)

    # ---------------- 출구 단면 · 다이 면 지도 ----------------
    if dfz:
        st.markdown("#### 어디가 가장 힘을 받고, 단단해지고, 뜨거운가")
        xg = dfz["x"]
        Ee, Tt, Ss = dfz["eps"], dfz["T"], dfz["sig"]
        rho_at = lambda xx, yy: float(np.interp(math.atan2(yy, xx) % (2 * np.pi), dfz["phi"], dfz["rho"], period=2 * np.pi))

        def where_(F):
            ii = np.unravel_index(int(np.nanargmax(F)), F.shape)
            xx, yy = float(xg[ii[1]]), float(xg[ii[0]])
            return xx, yy, locate_point(shape_type, W, H, xx, yy, rho_at(xx, yy))
        xe_, ye_, loc_e = where_(Ee)
        xs2, ys2, loc_s = where_(Ss)
        xt_, yt_, loc_t = where_(Tt)
        ip, jp = np.unravel_index(int(np.argmax(dfz["die_P"])), dfz["die_P"].shape)
        P_max, x_pmax, ph_p = float(dfz["die_P"].max()), float(dfz["die_x"][ip]), float(dfz["phi"][jp])
        rb_p = float(np.interp(ph_p, dfz["phi"], dfz["rho"], period=2 * np.pi))
        loc_p = locate_point(shape_type, W, H, rb_p * math.cos(ph_p), rb_p * math.sin(ph_p), rb_p).replace(" 표면", "")
        where_p = ("베어링 안" if x_pmax > dfz["L_ap"] + 1e-6 else
                   f"어프로치 입구에서 {x_pmax:.0f} mm 들어간 곳 (어프로치 접촉 길이 {dfz['L_ap']:.0f} mm 중 {x_pmax / dfz['L_ap'] * 100:.0f}% 지점)")
        if shape_type == SHAPE_TR:
            ang_c, c_name = 0.0, "원호부(양 끝)"
        else:
            ang_c, c_name = (math.pi / 6 if shape_type == SHAPE_HEX else math.atan2(H, W)), "모서리"
        e_c = float(np.interp(ang_c, dfz["phi"], dfz["eps_surf"], period=2 * np.pi))
        T_c = float(np.interp(ang_c, dfz["phi"], dfz["T_surf"], period=2 * np.pi))
        s_c = float(sig_of(e_c))
        col_c = dfz["die_P"][:, int(np.argmin(np.abs(dfz["phi"] - ang_c)))]
        P_c = float(col_c.max())
        e_max, T_max, s_max = float(np.nanmax(Ee)), float(np.nanmax(Tt)), float(np.nanmax(Ss))
        T05 = cool_down(Tt, dfz["inside"], dfz["dx"], 0.5)
        if shape_type == SHAPE_TR:
            why_c = ""
        elif e_c < 0.85 * e_max and T_c < 0.8 * T_max:
            why_c = " — 다이와 닿는 길이가 짧아 덜 변형되고 덜 뜨거움 (모서리 R이 생기는 것과 같은 이유)"
        elif pred and pred["p_fill"] >= 0.5:
            why_c = " — 모서리까지 소재가 꽉 차면서 변형이 큼"
        else:
            why_c = ""
        st.markdown(f"""
<div class="ra-box">
  <div class="ra-title">한눈에 보기 (인발 속도 {v_mpm:.0f} m/min · 2α {two_alpha:.0f}° · μ {mu_f:.2f} · TS {ts_in:.0f} kgf/mm²)</div>
  <div class="ra-msg">
    <b>가장 힘을 받는 곳</b>: 다이의 <b>{loc_p}</b> 쪽, {where_p} — 면압 약 <b>{P_max:.0f} MPa</b>. 다이가 가장 빨리 닳는 곳입니다.<br>
    <b>가장 단단해지는 곳</b>: 제품 {loc_s} — 유효 응력 <b>{s_max:.0f} MPa</b> (경도 약 HV {hv_of(s_max):.0f}) · 중심 {dfz['sig_axis']:.0f} MPa (HV {hv_of(dfz['sig_axis']):.0f}) · 투입재 {dfz['sig0']:.0f} MPa.<br>
    <b>가장 뜨거운 곳</b>: {loc_t} <b>{T_max:.0f} °C</b> — 표면 {dfz['depth_mm']:.1f} mm 이내 얇은 층의 순간 온도. 출구 0.5초 뒤 최고 {float(np.nanmax(T05)):.0f} °C, 2초 뒤면 단면 전체가 약 <b>{dfz['T_mean']:.0f} °C</b>로 고르게 됩니다 (출구 뒤 온도계로 재는 값).<br>
    <b>{c_name}</b>: 면압 {P_c:.0f} MPa · 응력 {s_c:.0f} MPa · ε {e_c:.2f} · {T_c:.0f} °C{why_c}.
  </div>
</div>""", unsafe_allow_html=True)

        def _sec_fig(Z, title, unit_fmt, hot_xy, hot_txt, center_txt, zmin, cbar_t):
            fg = go.Figure(go.Heatmap(x=xg, y=xg, z=Z, colorscale=CS_F, zmin=float(np.nanmin(Z)), zmax=float(np.nanmax(Z)), zsmooth="best",
                                      colorbar=dict(thickness=12, len=0.85, title=cbar_t, nticks=13), hovertemplate=unit_fmt + "<extra></extra>"))
            if shape_type != SHAPE_TR:
                xd_, yd_ = rounded_polygon(shape_type, W, H, R, 360)
                fg.add_trace(go.Scatter(x=np.r_[xd_, xd_[0]], y=np.r_[yd_, yd_[0]], mode="lines", line=dict(color=INK, width=1.2, dash="dot"),
                                        hoverinfo="skip", showlegend=False))
            xb_, yb_ = _section_boundary(shape_type, W, H, (H / 2.0) if shape_type == SHAPE_TR else pred["p50"])
            fg.add_trace(go.Scatter(x=np.r_[xb_, xb_[0]], y=np.r_[yb_, yb_[0]], mode="lines", line=dict(color=INK, width=1.6),
                                    hoverinfo="skip", showlegend=False))
            fg.add_trace(go.Scatter(x=[hot_xy[0]], y=[hot_xy[1]], mode="markers", marker=dict(symbol="circle-open", size=16, color=INK,
                                    line=dict(width=2.5)), hoverinfo="skip", showlegend=False))
            ux, uy = hot_xy[0], hot_xy[1]
            nrm_ = max(math.hypot(ux, uy), 1e-6)
            fg.add_annotation(x=ux, y=uy, ax=ux + 0.24 * xg.max() * ux / nrm_, ay=uy + 0.24 * xg.max() * uy / nrm_, axref="x", ayref="y",
                              showarrow=True, arrowhead=2, arrowcolor=INK, text=f"<b>{hot_txt}</b>", font=dict(size=13, color=INK),
                              bgcolor="rgba(255,255,255,0.92)", bordercolor=INK, borderwidth=1)
            fg.add_annotation(x=0, y=0, text=center_txt, showarrow=False, font=dict(size=12, color=INK), bgcolor="rgba(255,255,255,0.85)")
            lim_ = xg.max() * 1.28
            fg.update_layout(title=title, height=430, margin=dict(l=10, r=10, t=46, b=10),
                             xaxis=dict(scaleanchor="y", scaleratio=1, range=[-lim_, lim_], showticklabels=False, showgrid=False, zeroline=False),
                             yaxis=dict(range=[-lim_, lim_], showticklabels=False, showgrid=False, zeroline=False))
            style_fig(fg)
            fg.update_xaxes(showgrid=False, showticklabels=False, zeroline=False); fg.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
            return fg

        s1c, s2c = st.columns(2)
        left_opt = s1c.radio("왼쪽 단면", ["유효 응력 (경도)", "유효 변형률"], horizontal=True, key="t1_sec_left")
        t_opt = s2c.radio("온도 보는 시점", ["출구 직후", "0.5초 뒤", "2초 뒤"], horizontal=True, key="t1_sec_time",
                          help=f"인발 속도 {v_mpm:.0f} m/min이면 0.5초 = 출구에서 {v_mpm / 60 * 0.5:.2f} m, 2초 = {v_mpm / 60 * 2:.2f} m 지난 위치")
        if left_opt == "유효 응력 (경도)":
            s1c.plotly_chart(_sec_fig(Ss, "유효 응력 — 가공경화로 단단해진 정도 (MPa)", "%{z:.0f} MPa", (xs2, ys2),
                                      f"최대 {s_max:.0f} MPa · HV {hv_of(s_max):.0f}", f"중심 {dfz['sig_axis']:.0f}", dfz["sig0"], "MPa"), **FW_CHART)
        else:
            s1c.plotly_chart(_sec_fig(Ee, "유효 변형률 ε (누적 소성변형)", "ε %{z:.2f}", (xe_, ye_), f"최대 ε {e_max:.2f}",
                                      f"중심 {dfz['eps_axis']:.2f}", 0.0, "ε"), **FW_CHART)
        t_sec = {"출구 직후": 0.0, "0.5초 뒤": 0.5, "2초 뒤": 2.0}[t_opt]
        Tv = Tt if t_sec == 0 else cool_down(Tt, dfz["inside"], dfz["dx"], t_sec)
        iv = np.unravel_index(int(np.nanargmax(Tv)), Tv.shape)
        s2c.plotly_chart(_sec_fig(Tv, f"온도 — {t_opt} (°C)", "%{z:.0f} °C", (float(xg[iv[1]]), float(xg[iv[0]])),
                                  f"최고 {float(np.nanmax(Tv)):.0f} °C", f"중심 {float(Tv[len(xg) // 2, len(xg) // 2]):.0f} °C", 25.0, "°C"), **FW_CHART)

        # 다이 면 펼친 그림
        ph_deg = np.degrees(dfz["phi"])
        sel = ph_deg <= 180.0 + 1e-9
        fd = go.Figure(go.Heatmap(x=dfz["die_x"], y=ph_deg[sel], z=dfz["die_P"][:, sel].T, colorscale=CS_F, zmin=0, zmax=P_max,
                                  zsmooth="best", colorbar=dict(thickness=12, len=0.9, title="MPa", nticks=13),
                                  hovertemplate="다이 속 %{x:.1f} mm · 둘레 %{y:.0f}°<br>면압 %{z:.0f} MPa<extra></extra>"))
        if shape_type == SHAPE_HEX:
            ticks = [(a_, "평면 중앙") for a_ in (0, 60, 120, 180)] + [(a_, "모서리") for a_ in (30, 90, 150)]
        elif shape_type == SHAPE_TR:
            ticks = [(0, "원호 끝"), (90, "직선부 중앙"), (180, "원호 끝")]
        else:
            ca = math.degrees(math.atan2(H, W))
            ticks = [(0, "평면 중앙 (W)"), (90, "평면 중앙 (H)"), (180, "평면 중앙 (W)"), (ca, "모서리"), (180 - ca, "모서리")]
        ticks.sort()
        fd.add_vline(x=dfz["L_ap"], line=dict(color=INK, dash="dot", width=1.2), annotation_text="베어링 시작", annotation_position="top")
        fd.add_trace(go.Scatter(x=[x_pmax], y=[min(math.degrees(ph_p), 360 - math.degrees(ph_p))], mode="markers+text",
                                text=[f"<b>최대 {P_max:.0f} MPa</b>"], textposition="top right", textfont=dict(size=12, color=INK),
                                marker=dict(symbol="circle-open", size=16, color=INK, line=dict(width=2.5)), hoverinfo="skip", showlegend=False))
        fd.update_layout(title="다이 면압 — 다이 안쪽 면을 펼친 그림 (어디가 가장 힘을 받나)", height=340, margin=dict(l=10, r=10, t=46, b=10),
                         xaxis=dict(title="다이 속 위치 (mm) — 0 = 소재가 처음 닿는 곳, 인발 방향 →", showgrid=False),
                         yaxis=dict(title="둘레 위치", tickvals=[t_[0] for t_ in ticks], ticktext=[t_[1] for t_ in ticks], showgrid=False, range=[-6, 186]))
        style_fig(fd)
        fd.update_xaxes(showgrid=False); fd.update_yaxes(showgrid=False)
        st.plotly_chart(fd, **FW_CHART)

        q1, q2, q3, q4 = st.columns(4)
        q1.metric("최대 다이 면압", f"{P_max:.0f} MPa", loc_p, delta_color="off")
        q2.metric("최대 유효 응력", f"{s_max:.0f} MPa", f"경도 약 HV {hv_of(s_max):.0f} · {loc_s}", delta_color="off")
        q3.metric("표면 순간 최고 온도", f"{T_max:.0f} °C", f"표면 {dfz['depth_mm']:.1f} mm 이내 · {loc_t}", delta_color="off")
        q4.metric("봉 전체 평균 온도", f"{dfz['T_mean']:.0f} °C", "출구 1–2초 뒤 측정값에 가까움", delta_color="off")
        st.caption("점선 = 다이, 실선 = 예상 제품. 간이 해석은 경향(어디가 더/덜)을 보는 용도입니다 — FEM(AFDEX 등)처럼 응력·속도장을 푼 값이 아닙니다. "
                   "연속 작업으로 다이가 데워지면 표면 온도는 더 올라가고, 다이로 빠지는 열·공기 냉각을 넣으면 평균 온도는 조금 내려갑니다.")
        with st.expander("간이 해석 방법 · 외부 FEM·실측과 비교 · 한계"):
            st.markdown(f"""
- **형상 변화**: 원형 단면을 '면적 비율이 같은 부채꼴끼리' 제품 단면에 대응시키고(표면일수록 제품 형상, 중심일수록 균일 축소), 최종 변형 기울기로 유효 변형률을 계산 — 균일 변형 ln λ = **{dfz['eps_h']:.3f}** (λ {dfz['lam']:.3f})
- **표면 전단(잉여변형)**: Δ = (α/r)(1+√(1−r))² = **{dfz['Delta']:.2f}**, 잉여일 계수 Φ = 0.8 + Δ/4.4 = **{dfz['Phi']:.2f}** (Hosford–Caddell). 반경에 비례하고, 다이가 깊게 누르는 방향(평면부 중앙)일수록 크게 배분
- **유효 응력·경도**: Swift 경화식 σ = K(ε₀+ε)ⁿ, n 0.18, K는 TS에서 추정({dfz['K']:.0f} MPa), 투입재 항복 ≈ 0.65·TS. 경도는 HV ≈ 0.31·σ(MPa) (Tabor 근사) — 단면 경도를 재면 바로 맞춰볼 수 있습니다
- **다이 면압**: Sachs 슬래브법으로 축 방향 인발응력을 쌓아 가며 면압 = 유동응력 − 인발응력. 각 둘레 위치는 다이가 소재에 닿기 시작하는 곳부터 면압이 생기고, 모서리처럼 안 닿는 곳은 0. 출구 인발응력 {dfz['sig_draw']:.0f} MPa (출구 유동응력의 {dfz['sig_draw'] / dfz['sf_exit'] * 100:.0f} %)
- **변형열**: 소성일의 90 %가 열 · 강 ρc = 3.61 MJ/m³K
- **마찰열**: 전단 μ·면압 × 접촉 길이(어프로치 + 베어링), 그중 35 %가 소재로, 접촉 시간 최대 {dfz['t_contact'] * 1000:.0f} ms 동안 표면 가열(반무한체 해). 출구 뒤는 단면 안 열전도로 고르게 퍼짐(공기 냉각 무시)
- **한계**: 가공 발열에 의한 연화, 다이 온도 상승, 윤활막 상태, 다이 입구·베어링 입구의 국부 면압 집중, 잔류응력은 반영하지 않음
""")
            ext_cmp = []
            for nm, shp_x, Wx, d0x, fem in [("S3 사각", SHAPE_SQ, 13.98, 17.0, (0.215, 0.377)), ("H2 육각", SHAPE_HEX, 13.99, 16.8, (0.287, 0.398)),
                                            ("H3 육각", SHAPE_HEX, 13.99, 15.8, (0.159, 0.275))]:
                prx = predict_R(shp_x, Wx, Wx, d0x, 0.0, MODEL)
                fx = deform_fields(shp_x, Wx, Wx, float(prx["p50"]), 0.0, d0x, 16.0)
                ext_cmp.append({"시편": nm, "조건": f"Ø{d0x:.1f} → {Wx:.0f}", "FEM 중심 ε": fem[0], "간이 중심 ε": round(fx["eps_axis"], 3),
                                "FEM 표면 ε": fem[1], "간이 표면 평균 ε": round(float(np.mean(fx["eps_surf"])), 3),
                                "간이 표면 최대 ε": round(float(np.max(fx["eps_surf"])), 3)})
            st.dataframe(pd.DataFrame(ext_cmp), hide_index=True, **FW_DF)
            st.caption("변형률 FEM: Rumiński·Skubisz·Micek (2025) Table 5 (스테인리스, 다이 각 미기재 → 간이 해석은 논문의 최적각 2α 16°로 계산). "
                       "논문도 '변형이 각 변 중앙에 집중되고, 모서리는 덜 경화'된다고 보고 — 간이 해석의 분포 경향과 같습니다.")
            fT = deform_fields(SHAPE_TR, 11.63, 11.63, 11.63 / 2, 11.63 / 2, 13.0, 12.0, 4.2, 0.10, 46.0, 3.0, 0.16, 26.0)
            st.dataframe(pd.DataFrame([
                {"구분": "논문 FEM·실측 (강선 Ø13 → Ø11.63, 감면율 20 %, 4.2 m/min, 반각 6°)", "표면 최고 (°C)": "약 93 (고경화재 n 0.5)",
                 "중심 (°C)": "42 → 62", "비고": "표면은 베어링 입구에서 최고, 이후 안쪽으로 퍼짐"},
                {"구분": "간이 해석 (같은 조건, μ 0.10, TS 46, n 0.16)", "표면 최고 (°C)": f"{float(np.nanmax(fT['T'])):.0f}",
                 "중심 (°C)": f"{fT['T_axis']:.0f} (평균 {fT['T_mean']:.0f})", "비고": "마찰열 35 %가 소재로 들어가도록 맞춤"},
            ]), hide_index=True, **FW_DF)
            st.caption("온도 비교: Materials 16(14) 5203 (2023), 'Influence of Strain Hardening Rate of Material on Temperature and Strain Distributions during Wire Drawing'.")

# ==========================================
# [TAB 2] 인발력 산출 및 설비 부하 검증
# ==========================================
with tab2:
    section_header("DRAWING LOAD · 95% CAPACITY", "인발력과 설비 검증",
                   "<span class='keyin-chip'></span>투입 선경, 제품 치수, 강종을 넣으면 소요 인발력과 호기별 작업 가능 여부(설비 능력 95% 기준)를 판정합니다.")

    machines_db = [
        {"name": "CD-0-2호기", "min_d": 3.8,  "max_d": 6.0,  "max_cap": 2.0},
        {"name": "CD-0-3호기", "min_d": 5.49, "max_d": 9.0,  "max_cap": 2.0},
        {"name": "CD-1호기",   "min_d": 8.0,  "max_d": 13.0, "max_cap": 5.0},
        {"name": "CD-5호기",   "min_d": 9.0,  "max_d": 15.0, "max_cap": 6.5},
        {"name": "CD-2-2호기", "min_d": 14.0, "max_d": 18.0, "max_cap": 8.0},
        {"name": "CD-3호기",   "min_d": 16.0, "max_d": 24.0, "max_cap": 15.0},
        {"name": "CD-4호기",   "min_d": 19.0, "max_d": 41.0, "max_cap": 25.0},
    ]

    steel_categories = {
        "1. 전자연철봉": {"SUYB1": 33.5},
        "2. 냉간압조용 탄소강 (SWRCH / Boron)": {
            "SWRCH6A": 33.1, "SWRCH8A": 34.2, "SWRCH10A (10A)": 35.5, "SWRCH12A (12A)": 38.8, "SWRCH15K": 41.4,
            "SWRCH18A": 46.4, "SWRCH20K": 44.4, "SWRCH22A": 47.1, "SWRCH25K(F)": 49.5, "SWRCH30K": 58.3,
            "SWRCH35K(F)": 60.5, "SWRCH38K(F)": 60.9, "SWRCH45K(F) (45K)": 64.7, "AISI/SAE 10B21": 51.1,
            "AISI/SAE 10B30": 57.6, "AISI/SAE 10B35": 60.8, "AISI/SAE 10B38": 64.1,
        },
        "3. 기계구조용강 (S-C계열)": {"S20C": 48.5, "S25C": 51.6, "S35C": 69.9, "S45C (W/R)": 71.0, "S48C": 78.2},
        "4. 경화능 보증 구조용강 (H계열)": {
            "SCr415H": 52.2, "SCr420H": 58.2, "SCM415 (W/R)": 60.0, "SCM420 (W/R)": 79.0, "SCM435 (W/R)": 96.0,
            "SCM440 (W/R)": 104.0, "W/R-SNCM220H": 73.0, "LA-SNCM220H (SL04)": 58.0,
        },
        "5. 베어링 / 스프링 / 고온합금강": {"SUJ2 (베어링강)": 115.0, "SUP9 (스프링강)": 95.0, "SNB16 (고온합금강볼트)": 118.2, "SA-100CRMNS7-4": 80.0},
        "6. 쾌삭강 (SUM)": {"SUM22 (W/R)": 40.0, "SUM24L (W/R)": 42.0, "SUM43 (W/R)": 69.0, "AISI/SAE 1151": 72.3},
        "7. 스테인리스강 (STS / SUS)": {
            "SUS303C": 52.8, "SUS303F": 59.9, "SUS304 (W/R)": 58.0, "SUS316L (W/R)": 54.0, "SUS410": 57.9, "SUS416": 56.8,
            "SUS420J2": 68.5, "SUS430F": 56.6, "W/R-SUS440C": 77.0, "XM7 (원재)": 75.0, "XM7 (12% 인발시)": 94.0,
        },
        "8. 기타 열처리 & 합금/포스코강": {
            "W/R-SNCM439": 110.0, "SA-SNCM439": 71.0, "AISI/SAE 1050SH": 82.5, "AISI/SAE 1060S": 87.1, "AISI/SAE 1541": 81.0,
            "AISI/SAE 4140": 114.0, "AISI/SAE 4037": 65.1, "AISI/SAE 9254": 96.7, "POSMA45R": 82.6, "POSMA45RM": 76.0,
            "POSA1038B": 64.2, "POSA1021B": 52.6, "POSA5120BH": 53.7,
        },
        "9. 사용자 직접 입력": {"직접 입력": 40.0},
    }

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("#### 변형 유형과 치수")
        draw_mode = st.selectbox("인발 변형 유형 선택", ["1. 원형 - 원형", "2. 원형 - 사각", "3. 원형 - 육각"], key="t2_mode")
        d_in_t2 = st.number_input("투입 원형 선경 W/ROD (MM)", value=28.0, min_value=1.0, step=0.5, key="t2_din_keyin")
        c_shape, R_used, a2_sharp = 1.0, 0.0, None

        if draw_mode == "1. 원형 - 원형":
            d_out_t2 = st.number_input("제품 원형 선경 (MM)", value=26.0, min_value=0.5, step=0.1, key="t2_dout_rd")
            a2_t2 = (np.pi / 4.0) * (d_out_t2 ** 2)
            diag_t2 = d_out_t2
            prod_size_for_m = d_out_t2
        else:
            is_sq = draw_mode == "2. 원형 - 사각"
            shp = SHAPE_SQ if is_sq else SHAPE_HEX
            w_out_t2 = st.number_input("제품 사각 한변 치수 (MM)" if is_sq else "제품 육각 대면 치수 W (MM)",
                                       value=19.0, min_value=0.5, step=0.1, key="t2_wout_sq" if is_sq else "t2_wout_hex")
            cr1, cr2 = st.columns(2)
            die_choice2 = cr1.selectbox("다이스 모서리 R", list(DIE_R_OPTIONS.keys()), index=0, key="t2_dier")
            R_die_t2 = (cr1.number_input("다이스 모서리 R 직접 입력 (mm)", value=0.3, min_value=0.0, step=0.05, key="t2_rdie_custom")
                        if DIE_R_OPTIONS[die_choice2] is None else DIE_R_OPTIONS[die_choice2])
            use_R = cr2.checkbox("예측 모서리 R 반영 단면적", value=True, key="t2_useR",
                                 help="실측 보정 모델의 예상 R로 모서리 미충전 면적을 차감합니다 (끄면 기존 샤프 단면).")
            c_shape = st.number_input("형상 보정계수 C (기본 1.00 = 기존 엑셀식)", value=1.00, min_value=0.80, max_value=1.50, step=0.01,
                                      key="t2_cshape", help="이형인발 잉여변형 보정용. 실측 인발하중으로 보정 후 사용 권장. 참고: Rumiński 등(2025)은 하중 계산에 사각 1.10, 육각 1.15의 형상계수를 사용 (사각 1.05–1.15 범위 검토).")
            Gt = shape_geom(shp, w_out_t2, w_out_t2)
            a2_sharp = Gt["A_sharp"]
            if d_in_t2 > 2 * Gt["h"] * 0.5:
                pr2 = predict_R(shp, w_out_t2, w_out_t2, d_in_t2, R_die_t2, MODEL)
                R_used = pr2["rms"] if use_R else 0.0
                R_disp = pr2["p50"] if use_R else 0.0
            else:
                R_used, R_disp = 0.0, 0.0
            a2_t2 = a2_sharp - Gt["loss"] * R_used ** 2
            diag_t2 = 2 * Gt["h"] - 2 * Gt["kf"] * R_disp
            prod_size_for_m = w_out_t2

        st.markdown("---")
        st.markdown("#### 강종")
        cat_choice = st.selectbox("1단계: 강종 분류 선택", list(steel_categories.keys()), key="t2_cat")
        sub_steels = steel_categories[cat_choice]
        steel_choice = st.selectbox("2단계: 세부 강종 선택", list(sub_steels.keys()), key="t2_steel")
        if cat_choice == "9. 사용자 직접 입력" or steel_choice == "직접 입력":
            ts_kgf = st.number_input("T.S (W/ROD) (kgf/mm²)", value=40.0, step=1.0, key="t2_custom_ts")
        else:
            ts_kgf = sub_steels[steel_choice]

    a1_t2 = (np.pi / 4.0) * (d_in_t2 ** 2)
    ra_ratio = (a1_t2 - a2_t2) / a1_t2 if a1_t2 > 0 else 0.0
    ra_percent = ra_ratio * 100.0

    with col_f2:
        st.markdown("#### 단면과 감면율")
        st.write(f"• **투입 면적 (A₁):** `{a1_t2:.2f} mm²`")
        if a2_sharp is not None:
            st.write(f"• **제품 면적 (A₂):** `{a2_t2:.3f} mm²`  (샤프 {a2_sharp:.3f} − 모서리 미충전 {a2_sharp - a2_t2:.3f}, 예상 R {R_used:.2f} mm 반영)")
        else:
            st.write(f"• **제품 면적 (A₂):** `{a2_t2:.3f} mm²`")
        st.write(f"• **감면율 (RA):** `{ra_ratio:.6f}` (`{ra_percent:.2f}%`)")
        st.write(f"• **제품 대표 치수 (D):** `{diag_t2:.3f} mm`")
        st.write(f"• **적용 강종 분류:** `{cat_choice}` ➔ `{steel_choice}` (`T.S {ts_kgf:.1f} kgf/mm²`)")

    if a1_t2 > a2_t2 and a2_t2 > 0:
        force_excel = (1.25 / 0.35) * a2_t2 * ts_kgf * (0.03 + 0.55 * ra_ratio) / 1000.0
        force_ton = force_excel * c_shape
        st.markdown("---")
        m_c1, m_c2, m_c3 = st.columns(3)
        m_c1.metric("산출 인발력 (TON)", f"{force_ton:.3f} Ton", f"{force_ton * 9.80665:.2f} kN")
        m_c2.metric("적용 감면율 (RA)", f"{ra_percent:.2f} %", f"변형 유형: {draw_mode}")
        if a2_sharp is not None:
            ra_sh = (a1_t2 - a2_sharp) / a1_t2
            f_sharp = (1.25 / 0.35) * a2_sharp * ts_kgf * (0.03 + 0.55 * ra_sh) / 1000.0
            m_c3.metric("기존 (샤프 단면, C=1.00)", f"{f_sharp:.3f} Ton", f"신규−기존 {force_ton - f_sharp:+.3f} t", delta_color="off")
        st.info("**적용 엑셀 공식:** 인발력 (TON) = 1.25 / 0.35 × 제품면적(A₂) × T.S × (0.03 + 0.55 × 감면율비율) / 1000 × 형상 보정계수 C")

        st.markdown("---")
        st.markdown("#### 호기별 작업 가능 여부 (설비 능력 95% 기준)")
        m_eval_data, matched_machines = [], []
        for m in machines_db:
            size_ok = (m["min_d"] <= prod_size_for_m <= m["max_d"])
            usable_cap = m["max_cap"] * 0.95
            force_ok = (force_ton <= usable_cap)
            load_ratio = (force_ton / usable_cap) * 100.0 if usable_cap > 0 else 0.0
            if size_ok and force_ok:
                status = "🟢 작업 가능 (이상없음)"
                matched_machines.append(f"**{m['name']}** (부하율 {load_ratio:.1f}%)")
            elif size_ok and not force_ok:
                status = "🔴 인발력 초과 (작업불가)"
            else:
                status = "⚪ 선경 규격 미달/초과"
            m_eval_data.append({
                "작업 호기": m["name"], "작업 가능 제품선경": f"{m['min_d']} ~ {m['max_d']} mm",
                "설비 Max 톤수": f"{m['max_cap']:.1f} t", "95% 한계 인발력": f"{usable_cap:.2f} t",
                "소요 인발력": f"{force_ton:.3f} t", "설비 부하율": f"{load_ratio:.1f} %", "판정 결과": status,
            })
        if matched_machines:
            st.success(f"✅ **현재 작업 조건({draw_mode} / {force_ton:.3f}t)에 이상이 없는 추천 설비:** " + ", ".join(matched_machines))
        else:
            st.error(f"⚠️ **경고:** 현재 소요 인발력({force_ton:.3f}t) 조건에 안전하게(95% 이내) 작업할 수 있는 설비가 없습니다.")
        st.dataframe(pd.DataFrame(m_eval_data), **FW_DF)
    else:
        st.warning("투입 선경이 제품 단면보다 커야 인발력 연산이 가능합니다.")

# ==========================================
# [TAB 3] 중량 계산 (원형/사각/육각 지원)
# ==========================================
with tab3:
    section_header("BAR WEIGHT", "규격별 중량",
                   "<span class='keyin-chip'></span>단면 치수, 길이, 비중으로 중량을 계산합니다. 사각·육각은 모서리 R만큼 줄어든 단면적을 반영합니다.")
    hint_R = f" (1번 탭 예상 R P50 = {pred['p50']:.2f} mm)" if pred else ""

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("#### 제품 형상과 치수")
        bar_shape = st.selectbox("제품 형상 선택", ["원형 (Round Bar)", "사각형 (Square / Rect Bar)", "정육각형 (Hexagon Bar)"], key="w_shape")
        if bar_shape == "원형 (Round Bar)":
            d_calc = st.number_input("외경 직경 D (mm)", value=25.0, step=0.5, key="w_d")
            calc_area = (np.pi / 4.0) * (d_calc ** 2)
            shape_desc = f"원형 직경 Ø {d_calc:.2f} mm"
        elif bar_shape == "사각형 (Square / Rect Bar)":
            col_sq1, col_sq2 = st.columns(2)
            with col_sq1:
                w_sq = st.number_input("폭 W (mm)", value=25.0, step=0.5, key="w_sq_w")
            with col_sq2:
                h_sq = st.number_input("높이 H (mm)", value=25.0, step=0.5, key="w_sq_h")
            r_sq = st.number_input("모서리 R (mm)" + hint_R, value=0.0, min_value=0.0, max_value=float(min(w_sq, h_sq) / 2), step=0.1, key="w_sq_r")
            calc_area = w_sq * h_sq - (4.0 - np.pi) * r_sq ** 2
            shape_desc = f"사각 W {w_sq:.2f} × H {h_sq:.2f} mm, R {r_sq:.2f}"
        else:
            w_hex = st.number_input("대면 치수 W (mm)", value=25.0, step=0.5, key="w_hex_w")
            r_hex = st.number_input("모서리 R (mm)" + hint_R, value=0.0, min_value=0.0, max_value=float(w_hex / 2), step=0.1, key="w_hex_r")
            calc_area = (np.sqrt(3.0) / 2.0) * (w_hex ** 2) - (2 * SQRT3 - np.pi) * r_hex ** 2
            shape_desc = f"육각 대면 W {w_hex:.2f} mm, R {r_hex:.2f}"

        length_mm = st.number_input("제품 1본당 길이 L (mm)", value=3020.0, step=10.0, key="w_l")
        density_dict = {
            "Carbon Steel (7.85)": 7.85, "Stainless Steel 304 (7.93)": 7.93, "Stainless Steel 316 (7.98)": 7.98,
            "Stainless Steel 420 (7.70)": 7.70, "Stainless Steel 430 (7.70)": 7.70, "사용자 직접 입력": 7.85,
        }
        mat_choice = st.selectbox("재질 비중 (Specific Gravity Sg)", list(density_dict.keys()), key="w_mat")
        rho = st.number_input("비중 직접 입력", value=7.85, step=0.01, key="w_rho") if mat_choice == "사용자 직접 입력" else density_dict[mat_choice]

    with col_w2:
        st.markdown("#### 수량")
        quantity = st.number_input("총 수량 (EA)", value=1, step=1, key="w_qty")
        piece_weight_kg = calc_area * length_mm * rho * (10 ** -6)
        piece_weight_lb = piece_weight_kg * 2.20462
        total_weight_kg = piece_weight_kg * quantity
        total_weight_ton = total_weight_kg / 1000.0

    st.markdown("---")
    st.markdown("#### 중량 결과")
    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("단품 1본 중량 (kg)", f"{piece_weight_kg:.3f} kg", f"단면적: {calc_area:.2f} mm² ({shape_desc})", delta_color="off")
    wc2.metric("단품 1본 중량 (lb)", f"{piece_weight_lb:.3f} lb", delta_color="off")
    wc3.metric(f"총 중량 (Total Weight, {quantity} EA)", f"{total_weight_kg:.2f} kg", f"{total_weight_ton:.4f} Ton")
    st.info("**적용 공식:** 중량(kg) = 단면적(A, mm²) × 길이(L, mm) × 비중(Sg) × 10⁻⁶  ·  사각 A = W·H − (4−π)R², 육각 A = (√3/2)W² − (2√3−π)R²")

# ==========================================
# [TAB 4] 직진도 환산 (엑셀 수식 적용)
# ==========================================
with tab4:
    section_header("STRAIGHTNESS", "환산 직진도",
                   "<span class='keyin-chip'></span>수요가 기준 길이·직진도를 생산 제품 길이 기준으로 환산합니다.")
    st.info("**적용 공식:** 환산 직진도 = (직진도 × 제품길이²) / 수요가길이²")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("#### 수요가 기준")
        req_length = st.number_input("수요가길이 (mm)", value=4920.0, step=10.0, key="s_req_l")
        req_straightness = st.number_input("직진도 (mm)", value=1.000, step=0.01, format="%.3f", key="s_req_s")
    with col_s2:
        st.markdown("#### 제품 기준")
        prod_length = st.number_input("제품길이 (mm)", value=1000.0, step=10.0, key="s_prod_l")
    conv_straightness = (req_straightness * (prod_length ** 2)) / (req_length ** 2) if req_length > 0 else 0.0
    with col_s3:
        st.markdown("#### 결과")
        st.metric("환산 직진도", f"{conv_straightness:.3f} mm")

# ==========================================
# [TAB 5] 실측 R DB & 모델 보정
# ==========================================
def _nelder_mead(f, x0, steps, max_iter=3000, tol=1e-9):
    n = len(x0)
    S = [np.array(x0, float)]
    for i in range(n):
        x = np.array(x0, float); x[i] += steps[i]; S.append(x)
    F = [f(x) for x in S]
    for _ in range(max_iter):
        o = np.argsort(F); S = [S[i] for i in o]; F = [F[i] for i in o]
        if abs(F[-1] - F[0]) < tol:
            break
        c = np.mean(S[:-1], axis=0)
        xr = c + (c - S[-1]); fr = f(xr)
        if fr < F[0]:
            xe = c + 2 * (c - S[-1]); fe = f(xe)
            S[-1], F[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < F[-2]:
            S[-1], F[-1] = xr, fr
        else:
            xc = c + 0.5 * (S[-1] - c); fc = f(xc)
            if fc < F[-1]:
                S[-1], F[-1] = xc, fc
            else:
                S = [S[0]] + [S[0] + 0.5 * (x - S[0]) for x in S[1:]]
                F = [F[0]] + [f(x) for x in S[1:]]
    i = int(np.argmin(F))
    return S[i], F[i]


def fit_model(df_long, base):
    """df_long: 열 [d0, a, R, (Rdes), (shape)] → 최우도 재보정 (δ*, σε, 최소충전 R(사각 기준) ≤20 / >20 ; w*·노이즈 고정)
    육각 행: a = 대면 W, 사각과 같은 '최소 꼭짓점 후퇴량'을 공유 (R 환산 ×kf_sq/kf_hex)"""
    d = df_long.dropna(subset=["d0", "a", "R"])
    d = d[(d["R"] > 0) & (d["a"] > 0) & (d["d0"] > 0)]
    a = d["a"].to_numpy(float); y = d["R"].to_numpy(float)
    hexm = (d["shape"] == SHAPE_HEX).to_numpy() if "shape" in d else np.zeros(len(a), bool)
    kf = np.where(hexm, KF_HEX, KF_SQ)
    g = np.where(hexm, a / SQRT3, a / SQRT2) - d["d0"].to_numpy(float) / 2.0
    rdes = d["Rdes"].fillna(DEFAULT_DIE_R).to_numpy(float) if "Rdes" in d else np.full(len(a), DEFAULT_DIE_R)
    cls = (a > 20.0 + 1e-9)
    sn, w = base["noise"], base["w_star"]
    pri = [math.log(MODEL_DEFAULT["fill_le20"]), math.log(MODEL_DEFAULT["fill_gt20"])]
    Wd = (w * a)[:, None]
    kfc = kf[:, None]

    def nll(p):
        ds, s = p[0], math.exp(p[1])
        if not (-0.1 < ds < 0.2 and 0.02 < s < 1.5):
            return 1e12
        f0, f1 = math.exp(p[2]), math.exp(p[3])
        ed = np.maximum(rdes * kf, np.where(cls, f1, f0) * KF_SQ)[:, None]   # 다이 R 후퇴량 vs 최소 후퇴량
        x = g[:, None] + s * Z_GRID[None, :]
        Rn = (ed + Wd * np.logaddexp(0.0, (x + ds * a[:, None] - ed) / Wd)) / kfc
        lik = (np.exp(-0.5 * ((y[:, None] - Rn) / sn) ** 2) / (sn * math.sqrt(2 * math.pi)) * PZ[None, :]).sum(1) + 1e-300
        pen = 0.5 * ((p[2] - pri[0]) / 0.5) ** 2 + 0.5 * ((p[3] - pri[1]) / 0.5) ** 2
        return float(-np.log(lik).sum() + pen)

    x0 = [base["delta_star"], math.log(base["sigma"]), math.log(base["fill_le20"]), math.log(base["fill_gt20"])]
    steps = [0.005, 0.2, 0.2, 0.2]
    best, fb = _nelder_mead(nll, x0, steps)
    for _ in range(2):
        best, fb = _nelder_mead(nll, best, [s * 0.5 for s in steps])
    newm = {**base, "delta_star": float(best[0]), "sigma": float(math.exp(best[1])),
            "fill_le20": float(math.exp(best[2])), "fill_gt20": float(math.exp(best[3]))}
    return newm, fb, len(y), int(hexm.sum())


# 외부 육각 인발 실험 (Rumiński, Skubisz, Micek 2025, J. Min. Metall. B 61(2) 233–248, X6CrNiTi18-10, Table 1·4)
HEX_EXT = [
    dict(id="H3", d0=15.8, A_th=169.42, A_act=165.68),
    dict(id="H2", d0=16.8, A_th=169.42, A_act=166.74),
]


with tab5:
    section_header("MEASURED R · CALIBRATION", "실측 R DB와 모델 보정",
                   "비전측정기 원호피팅 R 14본·56코너가 들어 있습니다. 새 측정값을 표에 추가하고 재보정하면 예측에 바로 반영됩니다.")

    rows = []
    for m in MEASURED_DB:
        pr = predict_R(SHAPE_SQ, m["a"], m["a"], m["d0"], m["die_r"], MODEL)
        ra = 1 - m["a"] ** 2 / (np.pi / 4 * m["d0"] ** 2)
        rows.append({
            "제조번호": m["id"], "강종": m["grade"], "선경→사각": f"{m['d0']:.0f}→{m['a']}", "다이스": m["die"],
            "RA(%)": round(ra * 100, 1), "선경/대각": round(m["d0"] / (SQRT2 * m["a"]), 3), "갭 g(mm)": round(pr["g"], 3),
            "R TL": m["R"][0], "R TR": m["R"][1], "R BL": m["R"][2], "R BR": m["R"][3],
            "실측 평균": round(float(np.mean(m["R"])), 2), "예측 평균": round(pr["mean"], 2),
            "예측 P10~P90": f"{pr['p10']:.2f}~{pr['p90']:.2f}",
            "기존식(R1.0)": round(old_model_R(m["a"], ra, 1.0), 2),
        })
    db_df = pd.DataFrame(rows)
    st.dataframe(db_df, hide_index=True, **FW_DF)
    st.download_button("실측 DB CSV 다운로드", db_df.to_csv(index=False).encode("utf-8-sig"), "실측R_DB.csv", "text/csv")

    # 감면율-R 산점도 + 모델 곡선
    curve_shape = st.radio("곡선 형상", ["사각 □20", "육각 HEX19"], horizontal=True, key="t5_curve",
                           help="육각은 실측이 없어 모델 곡선만 표시합니다 (사각 실측 기반 환산).")
    c_hex = curve_shape.startswith("육각")
    g1, g2 = st.columns([1.3, 1])
    fig_ra = go.Figure()
    shp_c, a_ref, Rd_ref = (SHAPE_HEX, 19.0, DEFAULT_DIE_R) if c_hex else (SHAPE_SQ, 20.0, DEFAULT_DIE_R)
    A_ref = shape_geom(shp_c, a_ref, a_ref)["A_sharp"]
    ra_grid = np.linspace(0.08, 0.32, 120) if c_hex else np.linspace(0.26, 0.46, 120)
    q = {"p10": [], "p50": [], "p90": []}
    for r_ in ra_grid:
        d0g = math.sqrt(A_ref / (np.pi / 4 * (1 - r_)))
        pr = predict_R(shp_c, a_ref, a_ref, d0g, Rd_ref, MODEL)
        for kq in q:
            q[kq].append(pr[kq])
    fig_ra.add_trace(go.Scatter(x=ra_grid * 100, y=q["p90"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig_ra.add_trace(go.Scatter(x=ra_grid * 100, y=q["p10"], mode="lines", line=dict(width=0), fill="tonexty",
                                fillcolor="rgba(201,146,46,0.28)", name=f"예측 P10~P90 ({'HEX19' if c_hex else '□20'}, 다이 R 없음)"))
    fig_ra.add_trace(go.Scatter(x=ra_grid * 100, y=q["p50"], mode="lines", line=dict(color=TEMPER_BLUE, width=3), name="예측 P50"))
    if not c_hex:
        fig_ra.add_trace(go.Scatter(x=ra_grid * 100, y=[old_model_R(20, r_, 1.0) for r_ in ra_grid], mode="lines",
                                    line=dict(color="#8A949D", dash="dash", width=2), name="기존식 (다이스R 1.0)"))
    gcolor = {"AISI1020": OXIDE_GREEN, "S20C": "#6A5AA8", "S45C": SCALE_RED, "SS400": "#8A6A1F"}
    rng = np.random.default_rng(1)
    shown = set()
    for m in ([] if c_hex else MEASURED_DB):
        ra = (1 - m["a"] ** 2 / (np.pi / 4 * m["d0"] ** 2)) * 100
        jit = rng.uniform(-0.35, 0.35)
        fig_ra.add_trace(go.Scatter(x=[ra + jit] * 4, y=m["R"], mode="markers",
                                    marker=dict(color=gcolor.get(m["grade"], "#000"), size=8, opacity=0.75),
                                    name=m["grade"], legendgroup=m["grade"], showlegend=m["grade"] not in shown,
                                    hovertemplate=f"{m['id']} ({m['d0']:.0f}→{m['a']})<br>R %{{y:.3f}}<extra></extra>"))
        shown.add(m["grade"])
    if c_hex:
        fig_ra.add_vline(x=(1 - 3 * SQRT3 / (2 * np.pi)) * 100, line=dict(color=INK, dash="dot"),
                         annotation_text="선경 = 맞꼭지 (RA 17.3%)", annotation_position="top")
    else:
        fig_ra.add_vline(x=(1 - 2 / np.pi) * 100, line=dict(color=INK, dash="dot"),
                         annotation_text="선경 = 대각 (RA 36.3%)", annotation_position="top")
    fig_ra.update_layout(title=("감면율과 모서리 R — 육각 모델 (실측 없음)" if c_hex else "감면율과 모서리 R — 실측 56코너 · 모델"),
                         xaxis_title="감면율 RA (%)", yaxis_title="모서리 R (mm)",
                         height=470, plot_bgcolor=PANEL, paper_bgcolor="rgba(0,0,0,0)",
                         legend=dict(orientation="h", y=-0.2, font=dict(size=11)), margin=dict(t=50, l=10, r=10))
    style_fig(fig_ra); fig_ra.update_layout(legend=dict(y=-0.2))
    g1.plotly_chart(fig_ra, **FW_CHART)

    fig_par = go.Figure()
    fig_par.add_trace(go.Scatter(x=[0, 3.5], y=[0, 3.5], mode="lines", line=dict(color="#8A949D", dash="dash"), name="y = x"))
    fig_par.add_trace(go.Scatter(x=db_df["예측 평균"], y=db_df["실측 평균"], mode="markers", name="신규 모델",
                                 marker=dict(size=11, color=TEMPER_BLUE, symbol="diamond"), text=db_df["제조번호"],
                                 hovertemplate="%{text}<br>예측 %{x:.2f} / 실측 %{y:.2f}<extra></extra>"))
    fig_par.add_trace(go.Scatter(x=db_df["기존식(R1.0)"], y=db_df["실측 평균"], mode="markers", name="기존식 (다이스R 1.0)",
                                 marker=dict(size=9, color="#8A949D", symbol="x"), text=db_df["제조번호"],
                                 hovertemplate="%{text}<br>기존 %{x:.2f} / 실측 %{y:.2f}<extra></extra>"))
    fig_par.update_layout(title="bar 평균 R — 예측 vs 실측", xaxis_title="예측 (mm)", yaxis_title="실측 (mm)",
                          xaxis=dict(range=[0, 3.5]), yaxis=dict(range=[0, 3.5]), height=470,
                          plot_bgcolor=PANEL, paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-0.2), margin=dict(t=50, l=10, r=10))
    style_fig(fig_par); fig_par.update_layout(legend=dict(y=-0.2))
    g2.plotly_chart(fig_par, **FW_CHART)

    st.markdown("#### 교차검증 (조건을 하나씩 빼고 예측)")
    st.dataframe(CV_TABLE, hide_index=True, **FW_DF)
    st.markdown("""
- **지배 인자 = 코너 갭** g = (다이스 샤프 꼭짓점 반경) − (투입 원형 반경). 사각은 **RA 36.3 % (선경 = 대각)** 를 경계로 거동이 급변합니다.
- 미충전 구간 실측 기울기 ≈ 2.3 mm/mm ↔ 기하학적 기울기 1/(√2−1) = 2.41 → 모델 구조가 물리적으로 타당.
- **실제 다이 R 확인 결과**: 8로트 중 2로트만 0.3R(LE005, LD031), 나머지는 R 없음(샤프). □19는 0.3R·R 없음 다이 모두 꽉 찬 조건에서 0.72–1.09 → 한 번 인발로는 **약 0.83 mm 아래로 날카로워지지 않음**. □22(R 없음)는 편심 bar 한쪽 코너에서 0.42–0.60이 관측됨.
- 강종 차이는 bar 간 편차에 묻혀 유의하지 않음 · 한 bar 안의 코너 편차(SD 0.3–0.9 mm)가 bar 간 편차보다 큼 → **선재 편심/진원도·다이스 정렬** 관리가 R 균일성의 핵심.
- **육각**: 경계 감면율 **17.3 % (선경 = 맞꼭지)**. 사내 실측이 없어 δ·σε는 사각 값을 쓰고, 한 번 인발 최소 R은 같은 최소 꼭짓점 후퇴량으로 환산(□≤20 0.83 → HEX 2.22 mm).
""")

    st.markdown("#### 육각 — 외부 실험으로 점검 (사내 실측 없음)")
    ext_rows = []
    loss_hex = 2 * SQRT3 - math.pi
    for ex in HEX_EXT:
        Wx = math.sqrt(ex["A_th"] / (SQRT3 / 2.0))
        prx = predict_R(SHAPE_HEX, Wx, Wx, ex["d0"], 0.0, MODEL)
        ext_rows.append({
            "시편": ex["id"], "조건": f"Ø{ex['d0']:.1f} → HEX{Wx:.1f}",
            "RA(%)": round((1 - ex["A_th"] / (np.pi / 4 * ex["d0"] ** 2)) * 100, 1), "갭 g(mm)": round(prx["g"], 2),
            "실험 미충전(%)": round((ex["A_th"] - ex["A_act"]) / ex["A_th"] * 100, 2),
            "모델 미충전(%)": round(loss_hex * (prx["rms"] ** 2 + MODEL["noise"] ** 2) / ex["A_th"] * 100, 2),
            "실험 환산 R(mm)": round(math.sqrt((ex["A_th"] - ex["A_act"]) / loss_hex), 2),
            "모델 R P50 (P10~P90)": f"{prx['p50']:.2f} ({prx['p10']:.2f}~{prx['p90']:.2f})",
        })
    st.dataframe(pd.DataFrame(ext_rows), hide_index=True, **FW_DF)
    st.caption("출처: Rumiński·Skubisz·Micek (2025) J. Min. Metall. Sect. B 61(2) 233–248, 스테인리스 X6CrNiTi18-10 · Table 1·4. "
               "미충전 = 이론 단면적 − 실제 단면적. 환산 R = 미충전이 모두 6개 모서리 R에서 생겼다고 볼 때의 R(대면 치수 오차도 섞여 있어 참고용). "
               "같은 논문에서 Ø18.6(RA 37.5 %)은 인발 중 파단.")

    st.markdown("---")
    st.markdown("#### 측정값 추가와 재보정 (사각 · 육각)")
    A_COL = "제품 a (사각 한변·육각 대면)"
    base_rows = [{"제조번호": m["id"], "강종": m["grade"], "형상": "사각", "투입선경 d0": m["d0"], A_COL: m["a"], "다이스": m["die"],
                  "다이스 모서리R": m["die_r"],
                  "R1": m["R"][0], "R2": m["R"][1], "R3": m["R"][2], "R4": m["R"][3], "R5": None, "R6": None} for m in MEASURED_DB]
    st.caption("육각은 형상을 '육각'으로 고르고 R1–R6 (6코너)을 넣으세요. 사각은 R1–R4만 씁니다. 표 맨 아래 빈 줄을 눌러 행을 추가합니다.")
    edit_df = st.data_editor(
        pd.DataFrame(base_rows), num_rows="dynamic", key="t5_editor2",
        column_config={
            "형상": st.column_config.SelectboxColumn("형상", options=["사각", "육각"], default="사각", required=True),
            "R5": st.column_config.NumberColumn("R5", help="육각만", format="%.3f"),
            "R6": st.column_config.NumberColumn("R6", help="육각만", format="%.3f"),
        }, **FW_ED)
    b1, b2, b3 = st.columns([1, 1, 2])
    if b1.button("입력 데이터로 모델 재보정", type="primary"):
        long = []
        for _, r in edit_df.iterrows():
            is_h = str(r.get("형상", "사각")).startswith("육")
            for c in (["R1", "R2", "R3", "R4", "R5", "R6"] if is_h else ["R1", "R2", "R3", "R4"]):
                try:
                    rdes = r.get("다이스 모서리R")
                    rdes = float(rdes) if rdes is not None and not pd.isna(rdes) else DEFAULT_DIE_R
                    long.append(dict(d0=float(r["투입선경 d0"]), a=float(r[A_COL]), Rdes=rdes, R=float(r[c]),
                                     shape=SHAPE_HEX if is_h else SHAPE_SQ))
                except (TypeError, ValueError):
                    pass
        long_df = pd.DataFrame(long).dropna(subset=["d0", "a", "R"]) if long else pd.DataFrame()
        if len(long_df) < 12:
            st.error("코너 데이터가 12개 이상 필요합니다.")
        else:
            with st.spinner("최우도 재보정 중..."):
                newm, fb, nobs, nhex = fit_model(long_df, dict(MODEL_DEFAULT))
            newm["source"] = f"사용자 재보정 ({nobs}코너" + (f" · 육각 {nhex}코너 포함" if nhex else "") + ")"
            st.session_state["model"] = newm
            st.rerun()
    if b2.button("기본 보정값 복원"):
        st.session_state["model"] = dict(MODEL_DEFAULT)
        st.rerun()
    b3.markdown(f"**현재 모델:** {MODEL.get('source', '')}  \n"
                f"δ* = {MODEL['delta_star']:.4f} · w* = {MODEL['w_star']:.4f} · σε = {MODEL['sigma']:.3f} mm  \n"
                f"한 번 인발 최소 도달 R: □≤20 {MODEL['fill_le20']:.2f} · □>20 {MODEL['fill_gt20']:.2f} mm "
                f"(육각 환산 W≤20 {MODEL['fill_le20'] * KF_SQ / KF_HEX:.2f} · W>20 {MODEL['fill_gt20'] * KF_SQ / KF_HEX:.2f} mm)")
    st.caption("※ 실제 투입 선재 직경(실측)·다이스 도면 R을 함께 기록하면 예측 정확도가 가장 크게 개선됩니다. "
               "육각 실측을 넣고 재보정하면 사각·육각이 같은 '최소 꼭짓점 후퇴량'을 공유하는 조건으로 함께 맞춥니다. "
               "재보정 결과는 이 화면을 새로고침하면 기본값으로 돌아갑니다.")
