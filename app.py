import math

import streamlit as st


st.set_page_config(
    page_title="Post-Offer Repurchase Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


MEMBER_PROFILES = {
    "M-10482": {
        "offer_status": "Completed",
        "anchor_time": "Hour 504",
        "membership_tenure_days": 642,
        "purchase_frequency": 14,
        "average_spend": 8.7,
        "prior_completion_rate": 0.72,
        "offer_response_speed": 10,
        "recent7_tx_count": 3,
        "purchase_gap_hours": 38,
        "customer_value": "High",
        "category": "Coffee",
        "cluster": "High-value loyalist",
    },
    "M-23891": {
        "offer_status": "Expired",
        "anchor_time": "Hour 576",
        "membership_tenure_days": 218,
        "purchase_frequency": 3,
        "average_spend": 5.4,
        "prior_completion_rate": 0.18,
        "offer_response_speed": None,
        "recent7_tx_count": 0,
        "purchase_gap_hours": 156,
        "customer_value": "Low",
        "category": "Tea",
        "cluster": "At-risk low response",
    },
    "M-77510": {
        "offer_status": "Completed",
        "anchor_time": "Hour 612",
        "membership_tenure_days": 510,
        "purchase_frequency": 8,
        "average_spend": 12.2,
        "prior_completion_rate": 0.46,
        "offer_response_speed": 34,
        "recent7_tx_count": 1,
        "purchase_gap_hours": 84,
        "customer_value": "High",
        "category": "Bakery",
        "cluster": "High value needs follow-up",
    },
}


DEFAULT_MEMBER = "M-10482"
st.session_state.setdefault("member_id", DEFAULT_MEMBER)


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
  --warning: #FFCF5A;
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
  padding: 24px 36px !important;
}

.block-container > div[data-testid="stVerticalBlock"],
.block-container div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

div[data-testid="stElementContainer"] {
  margin: 0 !important;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 32px;
  width: 1368px;
  height: 904px;
}

.left-rail {
  display: grid;
  grid-template-rows: 204px 1fr;
  gap: 24px;
}

.right-area {
  display: grid;
  grid-template-rows: 180px 306px 1fr;
  gap: 20px;
}

.top-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.middle-row {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
  overflow: hidden;
}

.input-card {
  padding: 22px;
}

.member-title {
  color: #FFFFFF;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 6px;
  letter-spacing: 0;
}

.member-subtitle {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
  margin: 0 0 18px;
}

div[data-testid="stTextInput"] {
  width: 276px !important;
}

div[data-testid="stTextInput"] label {
  color: #BFD2EC !important;
  font-size: 12px !important;
  font-weight: 700 !important;
}

div[data-baseweb="input"] > div {
  min-height: 44px !important;
  height: 44px !important;
  background: rgba(5, 18, 43, 0.76) !important;
  border: 1px solid rgba(113, 180, 255, 0.22) !important;
  border-radius: 10px !important;
}

div[data-baseweb="input"] input {
  color: #F7FBFF !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}

div[data-testid="stButton"] {
  width: 132px;
}

div[data-testid="stButton"] button {
  width: 132px;
  height: 42px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 800;
  border: 1px solid rgba(113, 180, 255, 0.26);
}

div[data-testid="stButton"] button[kind="primary"] {
  background: linear-gradient(135deg, #39D2FF 0%, #2F80FF 100%);
  color: #FFFFFF;
  border: 0;
  box-shadow: 0 12px 26px rgba(47, 128, 255, 0.28);
}

div[data-testid="stButton"] button[kind="secondary"] {
  background: rgba(5, 18, 43, 0.72);
  color: #CFE0F7;
}

.info-card {
  padding: 24px;
}

.eyebrow {
  color: var(--cyan);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.card-title {
  color: #FFFFFF;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.2;
  margin: 0;
}

.card-copy {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.55;
  margin: 8px 0 0;
}

.summary-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.summary-label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 18px;
}

.summary-value {
  color: #FFFFFF;
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
}

.summary-text-value {
  color: #FFFFFF;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
}

.summary-note {
  color: #BED1ED;
  font-size: 12px;
  line-height: 1.45;
  margin-top: 14px;
}

.pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 30px;
  padding: 0 12px;
  color: #061A3A;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  background: var(--green);
}

.analysis-card {
  padding: 22px 24px;
}

.gauge-wrap {
  height: 204px;
  display: grid;
  place-items: center;
}

.gauge {
  width: 168px;
  height: 168px;
  border-radius: 50%;
  background: conic-gradient(var(--green) 0deg, var(--cyan) var(--angle), rgba(113, 180, 255, 0.14) var(--angle) 360deg);
  display: grid;
  place-items: center;
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.08);
}

.gauge-inner {
  width: 122px;
  height: 122px;
  border-radius: 50%;
  background: #071A3A;
  display: grid;
  place-items: center;
  border: 1px solid rgba(113, 180, 255, 0.22);
}

.gauge-number {
  color: #FFFFFF;
  font-size: 34px;
  font-weight: 800;
}

.bar-row {
  display: grid;
  grid-template-columns: 168px 1fr 44px;
  gap: 14px;
  align-items: center;
  margin: 16px 0;
}

.bar-label {
  color: #D9E8FF;
  font-size: 12px;
  font-weight: 700;
}

.bar-track {
  height: 10px;
  border-radius: 999px;
  background: rgba(113, 180, 255, 0.14);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--blue), var(--cyan));
}

.bar-value {
  color: var(--muted);
  font-size: 12px;
  text-align: right;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-top: 22px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(113, 180, 255, 0.13);
}

.info-row:last-child {
  border-bottom: 0;
}

.info-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.info-value {
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 800;
  text-align: right;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  color: #061A3A;
  background: var(--green);
  font-size: 12px;
  font-weight: 800;
}

.status-chip.expired {
  background: var(--warning);
}

.detail-card {
  height: 369px;
  padding: 24px 28px;
}

.detail-layout {
  display: block;
  margin-top: 18px;
}

.strategy-headline {
  color: #FFFFFF;
  font-size: 28px;
  line-height: 1.15;
  font-weight: 800;
  margin: 12px 0 10px;
}

.strategy-body {
  color: #BFD2EC;
  font-size: 14px;
  line-height: 1.65;
  margin: 0;
  max-width: 860px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 18px;
  max-width: 760px;
}

.action-tile {
  min-height: 76px;
  border-radius: 14px;
  padding: 14px;
  background: rgba(5, 18, 43, 0.54);
  border: 1px solid rgba(113, 180, 255, 0.16);
}

.action-title {
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 8px;
}

.action-copy {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
}

</style>
"""


def clamp(value, low, high):
    return max(low, min(high, value))


def load_member(member_id):
    normalized = member_id.strip().upper()
    return MEMBER_PROFILES.get(normalized, MEMBER_PROFILES[DEFAULT_MEMBER])


def compute_prediction(profile):
    response = 0 if profile["offer_response_speed"] is None else clamp((48 - profile["offer_response_speed"]) / 48, 0, 1)
    recency_component = clamp((168 - profile["purchase_gap_hours"]) / 168, 0, 1)
    score = (
        0.18
        + clamp(profile["membership_tenure_days"] / 1000, 0, 0.22)
        + clamp(profile["purchase_frequency"] / 40, 0, 0.22)
        + clamp(profile["average_spend"] / 40, 0, 0.16)
        + profile["prior_completion_rate"] * 0.16
        + response * 0.16
        + profile["recent7_tx_count"] * 0.035
        + recency_component * 0.12
    )
    probability = clamp(score, 0.08, 0.94)

    if probability >= 0.72:
        strategy = "Loyalty follow-up, no heavy discount"
        segment = "High Propensity Loyalist"
        tone = "High confidence"
    elif probability >= 0.50:
        strategy = "Personalized retention offer"
        segment = "High Value Needs Follow-Up"
        tone = "Medium confidence"
    else:
        strategy = "Win-back reminder"
        segment = "At-Risk Low Response"
        tone = "Needs attention"

    return probability, segment, strategy, tone


def pct(value):
    return f"{round(value * 100)}%"


def response_speed_label(value):
    if value is None:
        return "No completion"
    return f"{value}h"


member_id = st.session_state.member_id
profile = load_member(member_id)
probability, segment, strategy, confidence = compute_prediction(profile)
angle = round(probability * 360)

member_values = {
    "Membership Tenure": clamp(profile["membership_tenure_days"] / 900 * 100, 0, 100),
    "Purchase Frequency": clamp(profile["purchase_frequency"] / 18 * 100, 0, 100),
    "Average Spend": clamp(profile["average_spend"] / 16 * 100, 0, 100),
    "Prior Completion": profile["prior_completion_rate"] * 100,
    "Recent Activity": clamp(profile["recent7_tx_count"] / 4 * 100, 0, 100),
}
cluster_values = {
    "Membership Tenure": 58,
    "Purchase Frequency": 52,
    "Average Spend": 50,
    "Prior Completion": 46,
    "Recent Activity": 42,
}

status_class = "expired" if profile["offer_status"] == "Expired" else ""
matched_member = st.session_state.member_id.strip().upper() in MEMBER_PROFILES

bars = ""
for label, member_score in member_values.items():
    cluster_score = cluster_values[label]
    bars += f"""
    <div class="bar-row">
      <div class="bar-label">{label}</div>
      <div>
        <div class="bar-track"><div class="bar-fill" style="width:{member_score:.0f}%;"></div></div>
        <div class="bar-track" style="height:6px; margin-top:6px;"><div class="bar-fill" style="width:{cluster_score:.0f}%; background:linear-gradient(90deg, #8B6CFF, #39D2FF); opacity:.62;"></div></div>
      </div>
      <div class="bar-value">{member_score:.0f}</div>
    </div>
    """

st.html(CSS)

left_col, right_col = st.columns([320, 1016], gap="large")

with left_col:
    with st.container():
        st.html(
            """
            <div class="card input-card">
              <div class="member-title">Member Input</div>
              <p class="member-subtitle">Search by member ID. The backend reconstructs the latest offer-resolution context and model features.</p>
            """
        )
        st.text_input("Member ID", key="member_id", placeholder="M-10482")
        button_col_1, button_col_2 = st.columns(2, gap="small")
        with button_col_1:
            st.button("Run Model", type="primary")
        with button_col_2:
            if st.button("Demo Reset"):
                st.session_state.member_id = DEFAULT_MEMBER
                st.rerun()
        st.html("</div>")

    st.html(
        f"""
        <div class="card info-card" style="height: 614px; margin-top: 24px;">
          <div class="eyebrow">Customer Basic Information</div>
          <div class="card-title">Profile and latest offer context</div>
          <p class="card-copy">These values are generated from raw member, transaction, and offer history. They are readable summaries, not manual model inputs.</p>
          <div class="info-grid">
            <div class="info-row"><span class="info-label">Member ID</span><span class="info-value">{st.session_state.member_id.strip().upper()}</span></div>
            <div class="info-row"><span class="info-label">Lookup Status</span><span class="info-value">{"Matched demo member" if matched_member else "Using demo fallback"}</span></div>
            <div class="info-row"><span class="info-label">Latest Offer Status</span><span class="info-value"><span class="status-chip {status_class}">{profile["offer_status"]}</span></span></div>
            <div class="info-row"><span class="info-label">Anchor Time</span><span class="info-value">{profile["anchor_time"]}</span></div>
            <div class="info-row"><span class="info-label">Membership Tenure</span><span class="info-value">{profile["membership_tenure_days"]} days</span></div>
            <div class="info-row"><span class="info-label">Purchase Frequency</span><span class="info-value">{profile["purchase_frequency"]} prior tx</span></div>
            <div class="info-row"><span class="info-label">Average Spend</span><span class="info-value">${profile["average_spend"]:.2f}</span></div>
            <div class="info-row"><span class="info-label">Prior Completion Rate</span><span class="info-value">{pct(profile["prior_completion_rate"])}</span></div>
            <div class="info-row"><span class="info-label">Offer Response Speed</span><span class="info-value">{response_speed_label(profile["offer_response_speed"])}</span></div>
          </div>
        </div>
        """
    )

with right_col:
    st.html(
        f"""
        <div class="right-area">
          <div class="top-summary">
            <div class="card summary-card">
              <div class="summary-label">Repurchase Probability</div>
              <div class="summary-value">{pct(probability)}</div>
              <div class="summary-note">Predicted 72-hour repeat purchase propensity after the latest offer resolution.</div>
            </div>
            <div class="card summary-card">
              <div class="summary-label">Customer Segment</div>
              <div class="summary-text-value">{segment}</div>
              <div class="summary-note">Based on value, purchase rhythm, and offer response behaviour.</div>
            </div>
            <div class="card summary-card">
              <div class="summary-label">Strategy Recommendation</div>
              <div class="pill">{strategy}</div>
              <div class="summary-note">{confidence}. Translate model score into next-best-action.</div>
            </div>
          </div>

          <div class="middle-row">
            <div class="card analysis-card">
              <div class="card-title">Probability Gauge</div>
              <p class="card-copy">Likelihood of another transaction in the next 72 hours.</p>
              <div class="gauge-wrap">
                <div class="gauge" style="--angle:{angle}deg;">
                  <div class="gauge-inner">
                    <div class="gauge-number">{pct(probability)}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="card analysis-card">
              <div class="card-title">Member vs Cluster Average</div>
              <p class="card-copy">Top bar: selected member. Lower bar: similar-member benchmark.</p>
              {bars}
            </div>
          </div>

          <div class="card detail-card">
            <div class="eyebrow">Strategy Recommendation Detail</div>
            <div class="detail-layout">
              <div>
                <span class="pill">Next Best Action</span>
                <div class="strategy-headline">{strategy}</div>
                <p class="strategy-body">
                  Member {st.session_state.member_id.strip().upper()} has a {pct(probability)} predicted repurchase propensity after a {profile["offer_status"].lower()} offer.
                  The recommendation is based on membership tenure, purchase frequency, average spend, prior offer completion, and recent activity.
                </p>
                <div class="action-grid">
                  <div class="action-tile">
                    <div class="action-title">Offer</div>
                    <div class="action-copy">Use incentive intensity according to propensity and value level.</div>
                  </div>
                  <div class="action-tile">
                    <div class="action-title">Channel</div>
                    <div class="action-copy">Prioritize app push and email for fast follow-up after resolution.</div>
                  </div>
                  <div class="action-tile">
                    <div class="action-title">Timing</div>
                    <div class="action-copy">Act within the 72-hour decision window.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    )
