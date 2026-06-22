from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Member Action Decision Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DATA_PATH = Path(__file__).with_name("dashboard_customers.csv")
DEMO_MEMBER = "M-10482"
SEGMENT_COLORS = {
    "High-Value Responsive": "#00754A",
    "Frequent Light Buyers": "#00754A",
    "Dormant Value Customers": "#00754A",
    "Low-Value Low-Response": "#00754A",
    "Thin-History Low-Activity": "#00754A",
    "Not clustered - no transactions": "#00754A",
}
SEGMENT_PROFILE_COPY = [
    "These are the program's best customers and they know it. They spend more than double the average (~$233), come in around a dozen times, and fill a full basket (~$21) every visit -- and they redeem almost every offer they get (93%, the highest of any group). Picture the daily commuter who orders the same large oat-milk latte and a pastry and always taps for stars. They clearly love the rewards, but they would keep coming with or without a coupon -- so a voucher here is a thank-you, not a reason to buy.",
    "When these customers show up they spend big -- the largest basket of all five groups (~$22) and a healthy total (~$112) -- and they happily use offers (74% completion). The catch is they've gone quiet: only ~5 visits, and the longest time-since-last-purchase of any active group. Think of the person who used to grab coffee for the whole office every Friday but has drifted off lately. High value, fading activity -- exactly the profile worth a win-back nudge before they're gone for good.",
    "This is the habit crowd: they visit the most of anyone -- about 14 times, like clockwork, with the shortest gap between trips -- but each visit is tiny (~$4, a single small drink). Their total stays modest (~$56) only because the basket never grows. Picture the student who pops in daily for a plain drip coffee. They already love the routine and lean toward discounts over BOGO, so the whole opportunity is simply nudging them to add one more item.",
    "We barely know these customers -- roughly two purchases ever, a long time ago, with enormous gaps between visits (the lowest frequency and longest recency by far). They're closer to strangers than regulars. But one detail stands out: when they do buy, the basket is decent (~$12, bigger than the frequent crowd). Picture someone who tried Starbucks a couple of times months ago and drifted away. Worth a small, cheap test to see if there's a real customer hiding there.",
]
FALLBACK_SEGMENT_PROFILE = "This segment does not have a narrative profile yet. Use the score, offer behavior, and action-list ranking as the primary decision signals for now."
REQUIRED_COLUMNS = {
    "member_id",
    "cluster",
    "cost",
    "decision_score",
    "uplift_score",
    "p_control",
    "p_treat",
    "reward_app_activity",
    "population_fit",
}


@st.cache_data
def load_customer_data():
    frame = pd.read_csv(DATA_PATH)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"{DATA_PATH.name} is missing required columns: {missing_list}")
    frame["member_id"] = frame["member_id"].str.upper()
    return frame


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def find_member(frame, member_id):
    normalized = member_id.strip().upper()
    matched = frame.loc[frame["member_id"].eq(normalized)]
    if matched.empty:
        return frame.iloc[0], False
    return matched.iloc[0], True


def donut(label, value, color):
    angle = round(clamp(value) * 360)
    return f"""
    <div class="donut-item">
      <div class="donut" style="--angle:{angle}deg; --donut-color:{color};">
        <div class="donut-inner">{value:.2f}</div>
      </div>
      <div class="donut-label">{label}</div>
    </div>
    """


def bar_rows(member):
    metrics = [
        ("Decision Score", member["decision_score"], 0.61),
        ("Uplift Score", member["uplift_score"], 0.42),
        ("Reward App Activity", member["reward_app_activity"], 0.52),
        ("Population Fit", member["population_fit"], 0.58),
    ]
    rows = []
    for label, member_value, pop_value in metrics:
        rows.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{label}</div>
              <div>
                <div class="bar-track"><div class="bar-fill" style="width:{member_value * 100:.0f}%;"></div></div>
                <div class="bar-track lower"><div class="bar-fill population" style="width:{pop_value * 100:.0f}%;"></div></div>
              </div>
              <div class="bar-value">{member_value:.2f}</div>
            </div>
            """
        )
    return "\n".join(rows)


def build_action_list(frame, budget, eligible_segments):
    if not eligible_segments:
        return frame.head(0).copy(), 0.0

    eligible = frame.loc[frame["cluster"].isin(eligible_segments)].copy()
    eligible = eligible.sort_values(["decision_score", "uplift_score"], ascending=False)
    eligible["cumulative_cost"] = eligible["cost"].cumsum()
    selected = eligible.loc[eligible["cumulative_cost"].le(budget)].copy()
    return selected, float(selected["cost"].sum()) if not selected.empty else 0.0


def segment_profile_copy(cluster, segment_order):
    try:
        index = segment_order.index(cluster)
    except ValueError:
        return FALLBACK_SEGMENT_PROFILE
    if index >= len(SEGMENT_PROFILE_COPY):
        return FALLBACK_SEGMENT_PROFILE
    return SEGMENT_PROFILE_COPY[index]


def action_table_rows(frame):
    if frame.empty:
        return """
        <tr>
          <td colspan="4" class="empty-row">No customers match the current budget and eligibility rules.</td>
        </tr>
        """

    rows = []
    for _, row in frame.iterrows():
        rows.append(
            f"""
            <tr>
              <td class="member-cell">{escape(row["member_id"])}</td>
              <td>{escape(row["cluster"])}</td>
              <td class="numeric">${row["cost"]:.0f}</td>
              <td class="numeric score-cell">{row["decision_score"]:.2f}</td>
            </tr>
            """
        )
    return "\n".join(rows)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  color-scheme: light;
  --primary-50: #EEF8F2;
  --primary-100: #DCEFE5;
  --primary-200: #B8DEC8;
  --primary-300: #7FBE9C;
  --primary-400: #3D996E;
  --primary-500: #00754A;
  --primary-600: #006241;
  --primary-700: #004D35;
  --primary-800: #003B29;

  --secondary-50: #EFF6FF;
  --secondary-100: #DBEAFE;
  --secondary-300: #7DD3FC;
  --secondary-400: #38BDF8;
  --secondary-500: #2D9CDB;
  --secondary-600: #2563EB;
  --secondary-800: #1E3A8A;

  --accent-purple: #7C6FF6;
  --accent-warning: #D9902F;
  --accent-danger: #D94A3A;

  --page-bg: #fbfaf5;
  --shell: rgba(255, 255, 255, 0.86);
  --shell-border: rgba(227, 232, 228, 0.92);
  --surface: #FFFFFF;
  --surface-muted: #F8FAF8;
  --surface-strong: #F0F4F1;
  --border: #E3E8E4;
  --border-strong: #D8E2DC;
  --text-strong: #1F2933;
  --text-base: #3D4842;
  --text-muted: #7B8A82;
  --track: #E6ECE8;
  --ring-track: #E3E8E4;
  --shadow-shell: 0 24px 70px rgba(0, 45, 32, 0.14);
  --shadow-card: 0 8px 24px rgba(15, 35, 25, 0.07);
  --shadow-hover: 0 14px 34px rgba(15, 35, 25, 0.1);
  --radius-shell: 28px;
  --radius-card: 20px;
  --radius-control: 10px;
  --focus-ring: 0 0 0 3px rgba(45, 156, 219, 0.22);
}

:root[data-member-ai-theme="dark"] {
  color-scheme: dark;
  --page-bg: radial-gradient(circle at 86% 8%, rgba(45, 156, 219, 0.24), transparent 30%),
             radial-gradient(circle at 10% 18%, rgba(0, 117, 74, 0.18), transparent 28%),
             linear-gradient(135deg, #071A33 0%, #0A1F3D 55%, #071A33 100%);
  --shell: rgba(13, 36, 69, 0.82);
  --shell-border: rgba(125, 211, 252, 0.18);
  --surface: #0D2445;
  --surface-muted: #102B50;
  --surface-strong: #071A33;
  --border: #244A73;
  --border-strong: #31577F;
  --text-strong: #F8FAFC;
  --text-base: #D6DEE8;
  --text-muted: #9FB0C4;
  --track: #244A73;
  --ring-track: #244A73;
  --shadow-shell: 0 24px 80px rgba(0, 0, 0, 0.35);
  --shadow-card: 0 12px 32px rgba(0, 0, 0, 0.22);
  --shadow-hover: 0 18px 44px rgba(0, 0, 0, 0.26);
  --focus-ring: 0 0 0 3px rgba(56, 189, 248, 0.25);
}

* {
  box-sizing: border-box;
}

html,
body,
[data-testid="stAppViewContainer"] {
  background: var(--page-bg);
  color: var(--text-base);
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
[data-testid="stBaseButton-header"],
.stDeployButton,
#MainMenu,
footer {
  display: none !important;
}

.block-container {
  width: min(1480px, calc(100vw - 32px));
  max-width: 1480px;
  min-height: min(960px, calc(100vh - 32px));
  margin: 16px auto !important;
  padding: 22px !important;
  background: var(--shell);
  border: 1px solid var(--shell-border);
  border-radius: var(--radius-shell);
  box-shadow: var(--shadow-shell);
  backdrop-filter: blur(18px);
}

.block-container div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

div[data-testid="stElementContainer"] {
  margin: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
  height: 100%;
  overflow: hidden;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-card) !important;
  box-shadow: var(--shadow-card) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
  padding: 18px !important;
}

.card {
  height: 100%;
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.brand-card {
  min-height: 132px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background:
    radial-gradient(circle at 88% 14%, rgba(56, 189, 248, 0.16), transparent 30%),
    linear-gradient(145deg, var(--primary-700) 0%, var(--primary-600) 54%, var(--primary-500) 100%);
  border: 0;
  color: #FFFFFF;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--secondary-400) 0%, var(--secondary-500) 46%, var(--accent-purple) 100%);
  box-shadow: 0 12px 28px rgba(45, 156, 219, 0.3);
}

.brand-text {
  color: #FFFFFF;
  font-size: 27px;
  line-height: 1;
  font-weight: 800;
}

.brand-subtitle {
  max-width: 220px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  line-height: 1.45;
  margin: 18px 0 0;
}

.top-card {
  height: 148px;
}

.inspect-card {
  height: 224px;
}

.metric-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.metric-label,
.card-kicker {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.01em;
  line-height: 1.25;
  margin-bottom: 14px;
}

.metric-value {
  color: var(--primary-600);
  font-size: 42px;
  line-height: 1;
  font-weight: 800;
}

.metric-note {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.45;
  margin-top: 14px;
}

.cluster-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  max-width: 100%;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  color: #FFFFFF;
  font-size: 12px;
  line-height: 1.15;
  font-weight: 800;
  background: var(--segment-color);
  box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.12);
}

.detail-card,
.compare-card {
  padding: 22px;
}

.card-title,
.widget-title {
  color: var(--text-strong);
  font-size: 18px;
  line-height: 1.2;
  font-weight: 800;
  margin: 0 0 8px;
}

.card-copy,
.widget-copy {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.48;
  margin: 0 0 14px;
}

div[data-testid="stTextInput"],
div[data-testid="stNumberInput"],
div[data-testid="stMultiSelect"],
div[data-testid="stCheckbox"] {
  width: 100% !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stCheckbox"] label {
  color: var(--text-base) !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
  min-height: 42px !important;
  background: var(--surface-muted) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-control) !important;
  box-shadow: none !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
  border-color: var(--secondary-500) !important;
  box-shadow: var(--focus-ring) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] span {
  color: var(--text-strong) !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}

div[data-testid="stButton"] button {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-control);
  font-size: 13px;
  font-weight: 800;
  transition: transform 160ms ease, box-shadow 160ms ease;
}

div[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: #FFFFFF;
  border: 0;
  box-shadow: 0 12px 26px rgba(0, 98, 65, 0.22);
}

div[data-testid="stButton"] button[kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 32px rgba(0, 98, 65, 0.26);
}

span[data-baseweb="tag"],
div[data-baseweb="tag"] {
  min-height: 28px !important;
  border-radius: 8px !important;
  background: var(--primary-50) !important;
  border: 1px solid var(--primary-100) !important;
}

span[data-baseweb="tag"] span,
div[data-baseweb="tag"] span {
  color: var(--primary-700) !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}

span[data-baseweb="tag"] svg,
div[data-baseweb="tag"] svg {
  fill: var(--primary-600) !important;
}

div[data-testid="stNumberInput"] button {
  background: var(--surface-strong) !important;
  border-left: 1px solid var(--border) !important;
  color: var(--primary-700) !important;
}

.eligible-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 10px 0 8px;
}

.eligible-title {
  color: var(--text-base);
  font-size: 12px;
  font-weight: 800;
}

.eligible-count {
  min-height: 24px;
  padding: 4px 9px;
  border-radius: 999px;
  color: var(--primary-700);
  background: var(--primary-50);
  border: 1px solid var(--primary-100);
  font-size: 11px;
  font-weight: 800;
}

div[data-testid="stCheckbox"] {
  min-height: 26px !important;
  margin: 0 !important;
}

div[data-testid="stCheckbox"] label {
  min-height: 26px !important;
  padding: 2px 0 !important;
  display: flex !important;
  gap: 8px !important;
  align-items: center !important;
}

div[data-testid="stCheckbox"] label > div:first-child {
  width: 16px !important;
  height: 16px !important;
}

div[data-testid="stCheckbox"] p {
  color: var(--text-base) !important;
  font-size: 11px !important;
  font-weight: 750 !important;
  line-height: 1.15 !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

div[data-testid="stCheckbox"] svg {
  color: #FFFFFF !important;
}

div[data-testid="stCheckbox"] label > span:first-of-type {
  background-color: var(--surface-muted) !important;
  border: 1px solid var(--border-strong) !important;
}

div[data-testid="stCheckbox"] label:has(input:checked) > span:first-of-type {
  background-color: var(--primary-600) !important;
  border-color: var(--primary-600) !important;
}

.donut-grid {
  height: 126px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  align-items: center;
  margin-top: 16px;
}

.donut-item {
  display: grid;
  justify-items: center;
  gap: 9px;
}

.donut {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: conic-gradient(var(--donut-color) 0deg, var(--donut-color) var(--angle), var(--ring-track) var(--angle) 360deg);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.2);
}

.donut-inner {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--surface);
  color: var(--text-strong);
  font-size: 14px;
  font-weight: 800;
  border: 1px solid var(--border);
}

.donut-label {
  color: var(--text-base);
  font-size: 11px;
  line-height: 1.2;
  font-weight: 800;
  text-align: center;
}

.bar-row {
  display: grid;
  grid-template-columns: 156px 1fr 48px;
  gap: 14px;
  align-items: center;
  margin: 12px 0;
}

.bar-label {
  color: var(--text-base);
  font-size: 12px;
  font-weight: 800;
}

.bar-track {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--track);
}

.bar-track.lower {
  height: 6px;
  margin-top: 6px;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-400));
}

.bar-fill.population {
  background: linear-gradient(90deg, var(--secondary-500), var(--secondary-300));
  opacity: 0.72;
}

.bar-value {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
  text-align: right;
}

.segment-profile-copy {
  margin: 14px 0 0;
  color: var(--text-base);
  font-size: 12px;
  font-weight: 520;
  line-height: 1.5;
  max-width: 94%;
  max-height: 122px;
  overflow: auto;
  padding-right: 8px;
}

.budget-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 8px;
}

.summary-tile {
  padding: 8px;
  border-radius: 14px;
  background: var(--surface-muted);
  border: 1px solid var(--border);
}

.summary-tile-label {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
}

.summary-tile-value {
  color: var(--text-strong);
  font-size: 16px;
  font-weight: 800;
  margin-top: 3px;
}

.action-table-wrap {
  height: 380px;
  max-height: 380px;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
}

.action-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  color: var(--text-base);
}

.action-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  height: 42px;
  padding: 0 14px;
  background: var(--surface-strong);
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  font-weight: 800;
  text-align: left;
}

.action-table tbody td {
  height: 48px;
  padding: 0 14px;
  border-bottom: 1px solid var(--border);
  color: var(--text-base);
  font-weight: 600;
}

.action-table tbody tr:last-child td {
  border-bottom: 0;
}

.action-table tbody tr:hover td {
  background: var(--surface-muted);
}

.member-cell {
  color: var(--primary-700) !important;
  font-weight: 800 !important;
}

.numeric {
  text-align: right !important;
}

.score-cell {
  color: var(--primary-600) !important;
  font-weight: 800 !important;
}

.empty-row {
  height: 96px !important;
  text-align: center !important;
  color: var(--text-muted) !important;
}
</style>
"""


customers = load_customer_data()
segments = customers["cluster"].dropna().drop_duplicates().tolist()
default_member = DEMO_MEMBER if customers["member_id"].eq(DEMO_MEMBER).any() else customers.iloc[0]["member_id"]

if "member_id" not in st.session_state:
    st.session_state.member_id = default_member
elif not customers["member_id"].eq(st.session_state.member_id.strip().upper()).any():
    st.session_state.member_id = default_member

st.session_state.setdefault("budget", 45.0)
st.session_state.setdefault("eligible_segments", segments[:4])
if not set(st.session_state.eligible_segments).intersection(segments):
    st.session_state.eligible_segments = segments[:4]

for index, segment in enumerate(segments):
    st.session_state.setdefault(
        f"eligible_cluster_{index}",
        segment in st.session_state.eligible_segments,
    )

st.session_state.eligible_segments = [
    segment
    for index, segment in enumerate(segments)
    if st.session_state.get(f"eligible_cluster_{index}", False)
]

member, matched = find_member(customers, st.session_state.member_id)
segment_color = SEGMENT_COLORS.get(member["cluster"], "#33E0A1")
profile_copy = segment_profile_copy(member["cluster"], segments)
selected_actions, used_budget = build_action_list(
    customers,
    float(st.session_state.budget),
    st.session_state.eligible_segments,
)
remaining_budget = max(float(st.session_state.budget) - used_budget, 0)

st.html(CSS)

left_col, main_col = st.columns([0.86, 3.14], gap="large")

with left_col:
    st.html(
        """
        <div class="card brand-card">
          <div class="brand-row">
            <div class="brand-mark"></div>
            <div class="brand-text">Starbucks ML</div>
          </div>
          <p class="brand-subtitle">Personalized reward decision engine.</p>
        </div>
        """
    )
    st.html('<div style="height: 14px;"></div>')
    with st.container(border=True):
        st.html(
            """
            <div class="widget-title">Member ID Input</div>
            <p class="widget-copy">Search a member from the CSV-backed demo data.</p>
            """
        )
        st.text_input("Member ID", key="member_id", placeholder=default_member)
        st.button("Search", type="primary")

    st.html('<div style="height: 10px;"></div>')
    with st.container(border=True):
        st.html(
            """
            <div class="widget-title">Campaign Controls</div>
            <p class="widget-copy">Set the campaign budget and choose eligible clusters.</p>
            """
        )
        st.number_input("Budget", min_value=0.0, max_value=5000.0, step=5.0, key="budget")
        st.html(
            f"""
            <div class="eligible-head">
              <div class="eligible-title">Eligible clusters</div>
              <div class="eligible-count">{len(st.session_state.eligible_segments)} selected</div>
            </div>
            """
        )
        for index, segment in enumerate(segments):
            st.checkbox(segment, key=f"eligible_cluster_{index}")
        st.html(
            f"""
            <div class="budget-summary">
              <div class="summary-tile">
                <div class="summary-tile-label">Selected</div>
                <div class="summary-tile-value">{len(selected_actions)}</div>
              </div>
              <div class="summary-tile">
                <div class="summary-tile-label">Used Budget</div>
                <div class="summary-tile-value">${used_budget:.0f}</div>
              </div>
            </div>
            <div class="budget-summary">
              <div class="summary-tile">
                <div class="summary-tile-label">Remaining</div>
                <div class="summary-tile-value">${remaining_budget:.0f}</div>
              </div>
              <div class="summary-tile">
                <div class="summary-tile-label">Source</div>
                <div class="summary-tile-value">CSV</div>
              </div>
            </div>
            """
        )

with main_col:
    top_cols = st.columns(3, gap="large")
    with top_cols[0]:
        st.html(
            f"""
            <div class="card metric-card top-card">
              <div class="card-title">Decision Score</div>
              <div class="metric-value">{member["decision_score"]:.2f}</div>
            </div>
            """
        )
    with top_cols[1]:
        st.html(
            f"""
            <div class="card metric-card top-card">
              <div class="card-title">Customer Segment</div>
              <div class="cluster-pill" style="--segment-color:{segment_color};">{member["cluster"]}</div>
            </div>
            """
        )
    with top_cols[2]:
        st.html(
            f"""
            <div class="card metric-card top-card">
              <div class="card-title">Cost for this customer</div>
              <div class="metric-value">${member["cost"]:.0f}</div>
              <div class="metric-note">Fixed cost from the member's cluster group.</div>
            </div>
            """
        )

    st.html('<div style="height: 20px;"></div>')

    inspect_cols = st.columns([1, 2], gap="large")
    with inspect_cols[0]:
        st.html(
            f"""
            <div class="card detail-card inspect-card">
              <div class="card-title">Detail Score</div>
              <div class="donut-grid">
                {donut("Uplift", member["uplift_score"], "#00754A")}
                {donut("P-Control", member["p_control"], "#38BDF8")}
                {donut("P-Treat", member["p_treat"], "#7C6FF6")}
              </div>
            </div>
            """
        )

    with inspect_cols[1]:
        st.html(
            f"""
            <div class="card compare-card inspect-card">
              <div class="card-title">Customer Segment Profile</div>
              <div class="cluster-pill" style="--segment-color:{segment_color};">{escape(str(member["cluster"]))}</div>
              <p class="segment-profile-copy">{escape(profile_copy)}</p>
            </div>
            """
        )

    st.html('<div style="height: 20px;"></div>')

    table_rows = action_table_rows(selected_actions)
    with st.container(border=True):
        st.html(
            f"""
            <div class="widget-title">Customer Action List</div>
            <p class="widget-copy">Customers are sorted by decision score and included until cumulative cost reaches the selected budget.</p>
            <div class="action-table-wrap">
              <table class="action-table">
                <thead>
                  <tr>
                    <th>Customer ID</th>
                    <th>Cluster</th>
                    <th class="numeric">Cost</th>
                    <th class="numeric">Decision Score</th>
                  </tr>
                </thead>
                <tbody>
                  {table_rows}
                </tbody>
              </table>
            </div>
            """
        )
