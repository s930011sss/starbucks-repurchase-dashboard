from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Member Action Decision Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DATA_PATH = Path(__file__).with_name("demo_customers.csv")
DEFAULT_MEMBER = "M-10482"
SEGMENT_COLORS = {
    "The regulars who live in the rewards app": "#33E0A1",
    "High value weekend explorers": "#39D2FF",
    "Discount-sensitive deal seekers": "#8B6CFF",
    "Quiet members at risk": "#FFCF5A",
    "New members needing a nudge": "#FF8A5B",
}


@st.cache_data
def load_customer_data():
    frame = pd.read_csv(DATA_PATH)
    frame["member_id"] = frame["member_id"].str.upper()
    return frame


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def find_member(frame, member_id):
    normalized = member_id.strip().upper()
    matched = frame.loc[frame["member_id"].eq(normalized)]
    if matched.empty:
        return frame.loc[frame["member_id"].eq(DEFAULT_MEMBER)].iloc[0], False
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


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg-1: #061A3A;
  --bg-2: #0B2454;
  --bg-3: #08152E;
  --card: rgba(11, 30, 66, 0.88);
  --card-soft: rgba(13, 40, 88, 0.72);
  --border: rgba(113, 180, 255, 0.24);
  --text: #F7FBFF;
  --muted: #AFC3E2;
  --blue: #2F80FF;
  --cyan: #39D2FF;
  --purple: #8B6CFF;
  --green: #33E0A1;
  --orange: #FF9A3D;
}

html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 15% 8%, rgba(57, 210, 255, 0.16), transparent 28%),
    radial-gradient(circle at 78% 18%, rgba(139, 108, 255, 0.13), transparent 26%),
    linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 48%, var(--bg-3) 100%);
  color: var(--text);
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer {
  display: none !important;
}

.block-container {
  width: 1440px;
  max-width: 1440px;
  min-height: 960px;
  padding: 24px 32px !important;
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
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 18px !important;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
  padding: 16px 18px !important;
}

.card {
  height: 100%;
  overflow: hidden;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.top-card {
  height: 150px;
}

.inspect-card {
  height: 210px;
}

.action-card {
  height: 410px;
}

.logo-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 24px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 13px;
  background: linear-gradient(135deg, var(--cyan), var(--blue) 58%, var(--purple));
  box-shadow: 0 12px 26px rgba(47, 128, 255, 0.28);
}

.brand-text {
  color: #FFFFFF;
  font-size: 27px;
  font-weight: 800;
}

.metric-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.metric-label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
  line-height: 1.25;
  margin-bottom: 16px;
}

.metric-value {
  color: #FFFFFF;
  font-size: 38px;
  line-height: 1;
  font-weight: 800;
}

.metric-note {
  color: #BED1ED;
  font-size: 12px;
  line-height: 1.45;
  margin-top: 13px;
}

.cluster-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  max-width: 100%;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  color: #061A3A;
  font-size: 12px;
  line-height: 1.15;
  font-weight: 800;
  background: var(--segment-color);
}

.input-card,
.detail-card,
.compare-card,
.customize-card,
.table-card {
  padding: 22px;
}

.card-title {
  color: #FFFFFF;
  font-size: 18px;
  line-height: 1.2;
  font-weight: 800;
  margin: 0 0 8px;
}

.card-copy {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.48;
  margin: 0 0 14px;
}

div[data-testid="stTextInput"],
div[data-testid="stNumberInput"],
div[data-testid="stMultiSelect"] {
  width: 100% !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stMultiSelect"] label {
  color: #BFD2EC !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
  min-height: 42px !important;
  background: rgba(5, 18, 43, 0.76) !important;
  border: 1px solid rgba(113, 180, 255, 0.22) !important;
  border-radius: 10px !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] span {
  color: #F7FBFF !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}

div[data-testid="stButton"] button {
  width: 100%;
  height: 38px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 800;
}

div[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, #39D2FF 0%, #2F80FF 100%);
  color: #FFFFFF;
  border: 0;
  box-shadow: 0 12px 26px rgba(47, 128, 255, 0.28);
}

.widget-title {
  color: #FFFFFF;
  font-size: 18px;
  line-height: 1.2;
  font-weight: 800;
  margin: 0 0 8px;
}

.widget-copy {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.48;
  margin: 0 0 14px;
}

.donut-grid {
  height: 112px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  align-items: center;
  margin-top: 14px;
}

.donut-item {
  display: grid;
  justify-items: center;
  gap: 8px;
}

.donut {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: conic-gradient(var(--donut-color) 0deg, var(--cyan) var(--angle), rgba(113, 180, 255, 0.14) var(--angle) 360deg);
}

.donut-inner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #071A3A;
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 800;
  border: 1px solid rgba(113, 180, 255, 0.22);
}

.donut-label {
  color: #D9E8FF;
  font-size: 11px;
  line-height: 1.2;
  font-weight: 700;
  text-align: center;
}

.bar-row {
  display: grid;
  grid-template-columns: 150px 1fr 44px;
  gap: 14px;
  align-items: center;
  margin: 12px 0;
}

.bar-label {
  color: #D9E8FF;
  font-size: 12px;
  font-weight: 700;
}

.bar-track {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(113, 180, 255, 0.14);
}

.bar-track.lower {
  height: 6px;
  margin-top: 6px;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--blue), var(--cyan));
}

.bar-fill.population {
  background: linear-gradient(90deg, var(--purple), var(--cyan));
  opacity: 0.62;
}

.bar-value {
  color: var(--muted);
  font-size: 12px;
  text-align: right;
}

.budget-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}

.summary-tile {
  padding: 9px 10px;
  border-radius: 12px;
  background: rgba(5, 18, 43, 0.54);
  border: 1px solid rgba(113, 180, 255, 0.16);
}

.summary-tile-label {
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
}

.summary-tile-value {
  color: #FFFFFF;
  font-size: 17px;
  font-weight: 800;
  margin-top: 5px;
}

div[data-testid="stDataFrame"] {
  border: 1px solid rgba(113, 180, 255, 0.18);
  border-radius: 12px;
  overflow: hidden;
}
</style>
"""


customers = load_customer_data()
segments = list(SEGMENT_COLORS.keys())

st.session_state.setdefault("member_id", DEFAULT_MEMBER)
st.session_state.setdefault("budget", 45.0)
st.session_state.setdefault("eligible_segments", [segments[0], segments[1], segments[2]])

member, matched = find_member(customers, st.session_state.member_id)
segment_color = SEGMENT_COLORS.get(member["cluster"], "#33E0A1")
selected_actions, used_budget = build_action_list(
    customers,
    float(st.session_state.budget),
    st.session_state.eligible_segments,
)
remaining_budget = max(float(st.session_state.budget) - used_budget, 0)

st.html(CSS)

top_cols = st.columns([1.05, 1, 1, 1], gap="large")
with top_cols[0]:
    st.html(
        """
        <div class="card logo-card top-card">
          <div class="brand-mark"></div>
          <div class="brand-text">Member AI</div>
        </div>
        """
    )
with top_cols[1]:
    st.html(
        f"""
        <div class="card metric-card top-card">
          <div class="metric-label">Decision Score</div>
          <div class="metric-value">{member["decision_score"]:.2f}</div>
          <div class="metric-note">Data source: Layer 1 scoring output.</div>
        </div>
        """
    )
with top_cols[2]:
    st.html(
        f"""
        <div class="card metric-card top-card">
          <div class="metric-label">Customer Segment</div>
          <div class="cluster-pill" style="--segment-color:{segment_color};">{member["cluster"]}</div>
          <div class="metric-note">Data source: Layer 2 clustering output.</div>
        </div>
        """
    )
with top_cols[3]:
    st.html(
        f"""
        <div class="card metric-card top-card">
          <div class="metric-label">Cost for this customer</div>
          <div class="metric-value">${member["cost"]:.0f}</div>
          <div class="metric-note">Fixed cost from the member's cluster group.</div>
        </div>
        """
    )

st.html('<div style="height: 18px;"></div>')

inspect_cols = st.columns([1.28, 1.28, 2.55], gap="large")
with inspect_cols[0]:
    with st.container(border=True):
        st.html(
            """
            <div class="widget-title">Member ID Input</div>
            <p class="widget-copy">Search a member from the CSV-backed demo data.</p>
            """
        )
        st.text_input("Member ID", key="member_id", placeholder=DEFAULT_MEMBER)
        st.button("Search", type="primary")

with inspect_cols[1]:
    st.html(
        f"""
        <div class="card detail-card inspect-card">
          <div class="card-title">Detail Score</div>
          <p class="card-copy">Uplift score, p-control, and p-treat from Layer 2.</p>
          <div class="donut-grid">
            {donut("Uplift", member["uplift_score"], "#33E0A1")}
            {donut("P-Control", member["p_control"], "#39D2FF")}
            {donut("P-Treat", member["p_treat"], "#8B6CFF")}
          </div>
        </div>
        """
    )

with inspect_cols[2]:
    st.html(
        f"""
        <div class="card compare-card inspect-card">
          <div class="card-title">Member vs Population Average</div>
          <p class="card-copy">Top bar: selected member. Lower bar: population average.</p>
          {bar_rows(member)}
        </div>
        """
    )

st.html('<div style="height: 18px;"></div>')

action_cols = st.columns([1.28, 3.95], gap="large")
with action_cols[0]:
    with st.container(border=True):
        st.html(
            """
            <div class="widget-title">Customize Column</div>
            <p class="widget-copy">Set the campaign budget and choose eligible clusters.</p>
            """
        )
        st.number_input("Budget", min_value=0.0, max_value=500.0, step=5.0, key="budget")
        st.multiselect("Eligible filter", options=segments, key="eligible_segments")
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

with action_cols[1]:
    table = selected_actions[["member_id", "cluster", "cost", "decision_score"]].rename(
        columns={
            "member_id": "Customer ID",
            "cluster": "Cluster",
            "cost": "Cost",
            "decision_score": "Decision Score",
        }
    )
    with st.container(border=True):
        st.html(
            """
            <div class="widget-title">Customer Action List</div>
            <p class="widget-copy">Customers are sorted by decision score and included until cumulative cost reaches the selected budget.</p>
            """
        )
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            height=260,
            column_config={
                "Cost": st.column_config.NumberColumn("Cost", format="$%.0f"),
                "Decision Score": st.column_config.NumberColumn("Decision Score", format="%.2f"),
            },
        )
