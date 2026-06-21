import math

import streamlit as st


st.set_page_config(
    page_title="Member Strategy AI Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DEFAULTS = {
    "member_id": "M-10482",
    "membership_tier": "Gold",
    "recency": 18,
    "purchase_frequency": 7,
    "total_spending": 1280.0,
    "average_order_value": 182.0,
    "discount_usage_level": "Medium",
    "main_product_category": "Beauty",
}


def reset_fields():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.session_state["model_has_run"] = False


for field, default in DEFAULTS.items():
    st.session_state.setdefault(field, default)
st.session_state.setdefault("model_has_run", True)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg-1: #061A3A;
  --bg-2: #0B2454;
  --bg-3: #08152E;
  --card: rgba(11, 30, 66, 0.88);
  --border: rgba(113, 180, 255, 0.24);
  --text: #F7FBFF;
  --muted: #9FB5D7;
  --blue: #2F80FF;
  --cyan: #39D2FF;
  --purple: #8B6CFF;
  --green: #33E0A1;
}

html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 18% 6%, rgba(47, 128, 255, 0.18), transparent 30%),
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
  height: 960px;
  padding: 0 36px 0 !important;
}

.block-container > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

.block-container > div[data-testid="stVerticalBlock"] > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

.app-header {
  height: 72px;
  min-height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.element-container:has(.app-header) {
  height: 72px !important;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--cyan), var(--blue) 58%, var(--purple));
  box-shadow: 0 12px 26px rgba(47, 128, 255, 0.28);
}

.brand-title {
  margin: 0;
  font-size: 22px !important;
  line-height: 1.1 !important;
  font-weight: 800;
  letter-spacing: 0;
}

.brand-subtitle {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px !important;
  line-height: 1.25 !important;
}

.header-meta {
  color: #BFD2EC;
  font-size: 13px;
  padding: 8px 12px;
  border: 1px solid rgba(57, 210, 255, 0.24);
  border-radius: 999px;
  background: rgba(11, 30, 66, 0.48);
}

.metric-card,
.chart-card,
.strategy-card,
.logic-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.section-title {
  color: #EAF3FF;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  margin: 0 0 10px;
}

.section-kicker {
  color: var(--muted);
  font-size: 12px;
  margin-top: -7px;
  margin-bottom: 16px;
}

.left-panel-title {
  margin: 0 0 4px;
  color: #F7FBFF;
  font-size: 18px !important;
  line-height: 1.2 !important;
  font-weight: 800;
}

.left-panel-subtitle {
  margin: 0 0 20px;
  color: var(--muted);
  font-size: 12px !important;
  line-height: 1.45 !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
  color: #BFD2EC !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  margin-bottom: 4px !important;
}

div[data-testid="stTextInput"],
div[data-testid="stNumberInput"],
div[data-testid="stSelectbox"] {
  width: 272px !important;
  margin-bottom: 7px !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
  min-height: 44px !important;
  height: 44px !important;
  background: rgba(5, 18, 43, 0.76) !important;
  border: 1px solid rgba(113, 180, 255, 0.22) !important;
  border-radius: 10px !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] span {
  color: #F7FBFF !important;
  font-size: 13px !important;
}

div[data-testid="stButton"] {
  width: 132px;
}

div[data-testid="stButton"] button {
  width: 132px;
  height: 44px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13px;
  border: 1px solid rgba(113, 180, 255, 0.28);
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

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 336px);
  gap: 16px;
  margin-bottom: 10px;
}

.metric-card {
  width: 336px;
  height: 150px;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.metric-label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 18px;
}

.metric-value {
  color: #FFFFFF;
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
}

.metric-note {
  color: #BFD2EC;
  font-size: 12px;
  margin-top: 12px;
  line-height: 1.45;
}

.metric-chip {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  color: #061A3A;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  background: var(--green);
}

.row-two {
  display: grid;
  grid-template-columns: 360px 668px;
  gap: 20px;
  margin-bottom: 8px;
}

.chart-card {
  height: 270px;
  padding: 22px;
}

.gauge-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 190px;
}

.gauge {
  width: 164px;
  height: 164px;
  border-radius: 50%;
  background: conic-gradient(var(--green) 0deg, var(--cyan) var(--angle), rgba(113, 180, 255, 0.14) var(--angle) 360deg);
  display: grid;
  place-items: center;
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.08);
}

.gauge-inner {
  width: 118px;
  height: 118px;
  border-radius: 50%;
  background: #071A3A;
  display: grid;
  place-items: center;
  border: 1px solid rgba(113, 180, 255, 0.22);
}

.gauge-number {
  color: #FFFFFF;
  font-size: 30px;
  font-weight: 800;
}

.bar-row {
  display: grid;
  grid-template-columns: 154px 1fr 46px;
  gap: 12px;
  align-items: center;
  margin: 17px 0;
}

.bar-label {
  color: #CFE0F7;
  font-size: 12px;
  font-weight: 600;
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

.row-three {
  display: grid;
  grid-template-columns: 708px 320px;
  gap: 20px;
}

.strategy-card,
.logic-card {
  height: 372px;
  padding: 24px;
}

.strategy-tag {
  display: inline-flex;
  height: 30px;
  padding: 0 12px;
  align-items: center;
  border-radius: 999px;
  background: rgba(57, 210, 255, 0.12);
  color: var(--cyan);
  border: 1px solid rgba(57, 210, 255, 0.26);
  font-size: 12px;
  font-weight: 800;
}

.strategy-headline {
  margin: 18px 0 10px;
  color: #FFFFFF;
  font-size: 28px;
  line-height: 1.18;
  font-weight: 800;
}

.strategy-body {
  color: #BFD2EC;
  font-size: 14px;
  line-height: 1.7;
  width: 92%;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 24px;
}

.action-tile {
  min-height: 88px;
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

.logic-list {
  margin-top: 18px;
}

.logic-item {
  display: grid;
  grid-template-columns: 10px 1fr;
  gap: 12px;
  margin-bottom: 18px;
}

.logic-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 4px;
}

.logic-text {
  color: #CFE0F7;
  font-size: 13px;
  line-height: 1.5;
}

.stMarkdown {
  margin-bottom: 0;
}

.block-container > div[data-testid="stVerticalBlock"] > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div:first-child > div[data-testid="stVerticalBlock"] {
  width: 320px;
  height: 844px;
  padding: 24px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}
</style>
"""


def clamp(value, low, high):
    return max(low, min(high, value))


def compute_prediction():
    tier_weight = {"Basic": 0.0, "Silver": 0.08, "Gold": 0.16, "Platinum": 0.24}
    discount_weight = {"Low": -0.04, "Medium": 0.04, "High": 0.11}

    recency = st.session_state.recency
    frequency = st.session_state.purchase_frequency
    spending = st.session_state.total_spending
    aov = st.session_state.average_order_value

    score = (
        0.22
        + tier_weight[st.session_state.membership_tier]
        + discount_weight[st.session_state.discount_usage_level]
        + clamp((45 - recency) / 120, -0.16, 0.22)
        + clamp(frequency / 34, 0.0, 0.24)
        + clamp(math.log1p(spending) / 42, 0.0, 0.18)
        + clamp(aov / 1600, 0.0, 0.09)
    )
    probability = clamp(score, 0.05, 0.94)

    if probability >= 0.72:
        segment = "High-Value Loyalist"
        strategy = "VIP retention and premium bundle"
        tone = "High confidence"
    elif probability >= 0.48:
        segment = "Potential Growth Member"
        strategy = "Personalized cross-sell campaign"
        tone = "Medium confidence"
    else:
        segment = "At-Risk Member"
        strategy = "Win-back incentive and reminder"
        tone = "Needs attention"

    return probability, segment, strategy, tone


def comparison_values(probability):
    member = {
        "Recency Score": clamp((60 - st.session_state.recency) / 60 * 100, 0, 100),
        "Frequency": clamp(st.session_state.purchase_frequency / 15 * 100, 0, 100),
        "Spending": clamp(st.session_state.total_spending / 2500 * 100, 0, 100),
        "Order Value": clamp(st.session_state.average_order_value / 420 * 100, 0, 100),
        "Propensity": probability * 100,
    }
    cluster = {
        "Recency Score": 62,
        "Frequency": 58,
        "Spending": 54,
        "Order Value": 49,
        "Propensity": 57,
    }
    return member, cluster


def pct(value):
    return f"{round(value * 100)}%"


probability, segment, strategy, confidence = compute_prediction()
member_values, cluster_values = comparison_values(probability)
angle = round(probability * 360)

st.html(CSS)

st.html(
    """
    <div class="app-header">
      <div class="brand-row">
        <div class="brand-mark"></div>
        <div>
          <div class="brand-title">Member Strategy AI</div>
          <p class="brand-subtitle">Single-member prediction and action recommendation dashboard</p>
        </div>
      </div>
      <div class="header-meta">ML Strategy Console · Desktop Prototype</div>
    </div>
    """
)

left_col, right_col = st.columns([320, 1048], gap="large")

with left_col:
    st.html(
        """
        <div class="left-panel-title">Member Input</div>
        <p class="left-panel-subtitle">Enter one member profile to generate a purchase prediction and marketing strategy.</p>
        """
    )

    st.text_input("Member ID", key="member_id")
    st.selectbox("Membership Tier", ["Basic", "Silver", "Gold", "Platinum"], key="membership_tier")
    st.number_input("Recency", min_value=0, max_value=365, step=1, key="recency")
    st.number_input("Purchase Frequency", min_value=0, max_value=100, step=1, key="purchase_frequency")
    st.number_input("Total Spending", min_value=0.0, max_value=100000.0, step=10.0, key="total_spending")
    st.number_input("Average Order Value", min_value=0.0, max_value=10000.0, step=5.0, key="average_order_value")
    st.selectbox("Discount Usage Level", ["Low", "Medium", "High"], key="discount_usage_level")
    st.selectbox(
        "Main Product Category",
        ["Beauty", "Electronics", "Fashion", "Home", "Sports", "Grocery"],
        key="main_product_category",
    )

    button_col_1, button_col_2 = st.columns(2, gap="small")
    with button_col_1:
        if st.button("Run Model", type="primary"):
            st.session_state["model_has_run"] = True
    with button_col_2:
        st.button("Reset Fields", on_click=reset_fields)

with right_col:
    st.html(
        f"""
        <div>
          <p class="section-title">Prediction Summary</p>
          <div class="summary-grid">
            <div class="metric-card">
              <div class="metric-label">Repurchase Probability</div>
              <div class="metric-value">{pct(probability)}</div>
              <div class="metric-note">{confidence} based on activity, spending, tier, and discount behavior.</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Customer Segment</div>
              <div class="metric-value" style="font-size: 24px; line-height: 1.18;">{segment}</div>
              <div class="metric-note">Primary category: {st.session_state.main_product_category}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Strategy Recommendation</div>
              <div class="metric-chip">{strategy}</div>
              <div class="metric-note">Recommended next best action for member {st.session_state.member_id}.</div>
            </div>
          </div>
        </div>
        """
    )

    bars = ""
    for label in member_values:
        member_score = member_values[label]
        cluster_score = cluster_values[label]
        bars += f"""
        <div class="bar-row">
          <div class="bar-label">{label}</div>
          <div>
            <div class="bar-track"><div class="bar-fill" style="width:{member_score:.0f}%;"></div></div>
            <div class="bar-track" style="height:6px; margin-top:6px;"><div class="bar-fill" style="width:{cluster_score:.0f}%; background:linear-gradient(90deg, #8B6CFF, #39D2FF); opacity:.68;"></div></div>
          </div>
          <div class="bar-value">{member_score:.0f}</div>
        </div>
        """

    st.html(
        f"""
        <div>
          <p class="section-title">Model Explanation</p>
          <div class="row-two">
            <div class="chart-card">
              <p class="section-title">Probability Gauge</p>
              <p class="section-kicker">Predicted probability of next-period repurchase</p>
              <div class="gauge-wrap">
                <div class="gauge" style="--angle:{angle}deg;">
                  <div class="gauge-inner">
                    <div class="gauge-number">{pct(probability)}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="chart-card">
              <p class="section-title">Member vs Cluster Average</p>
              <p class="section-kicker">Top bar: selected member · lower bar: segment benchmark</p>
              {bars}
            </div>
          </div>
        </div>
        """
    )

    st.html(
        f"""
        <div>
          <p class="section-title">Strategy Recommendation</p>
          <div class="row-three">
            <div class="strategy-card">
              <span class="strategy-tag">Next Best Action</span>
              <div class="strategy-headline">{strategy}</div>
              <p class="strategy-body">
                The member shows a {pct(probability)} repurchase probability and belongs to the
                {segment.lower()} segment. Focus the offer on {st.session_state.main_product_category.lower()}
                products, keep the message concise, and connect the incentive to the member's recent purchase pattern.
              </p>
              <div class="action-grid">
                <div class="action-tile">
                  <div class="action-title">Offer</div>
                  <div class="action-copy">Use a targeted reward calibrated to the discount usage level.</div>
                </div>
                <div class="action-tile">
                  <div class="action-title">Channel</div>
                  <div class="action-copy">Prioritize app push and email for fast campaign activation.</div>
                </div>
                <div class="action-tile">
                  <div class="action-title">Timing</div>
                  <div class="action-copy">Trigger within 48 hours while intent signals remain active.</div>
                </div>
              </div>
            </div>
            <div class="logic-card">
              <p class="section-title">Logic Summary</p>
              <p class="section-kicker">Business-readable model drivers</p>
              <div class="logic-list">
                <div class="logic-item">
                  <div class="logic-dot" style="background:#33E0A1;"></div>
                  <div class="logic-text">Recent activity and order frequency raise the predicted repurchase signal.</div>
                </div>
                <div class="logic-item">
                  <div class="logic-dot" style="background:#39D2FF;"></div>
                  <div class="logic-text">Spending and tier level indicate stronger customer value potential.</div>
                </div>
                <div class="logic-item">
                  <div class="logic-dot" style="background:#8B6CFF;"></div>
                  <div class="logic-text">Discount sensitivity shapes the recommended incentive intensity.</div>
                </div>
                <div class="logic-item">
                  <div class="logic-dot" style="background:#2F80FF;"></div>
                  <div class="logic-text">Category preference guides the campaign content and product bundle.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    )
