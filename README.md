# Starbucks Member Action Decision Dashboard

This project is a Streamlit dashboard prototype for deciding which Starbucks members should receive a follow-up reward offer.

It is not a model-training notebook or a full campaign automation system. The app starts from prepared customer-level outputs, combines uplift, customer value, and offer cost into a decision score, then turns those scores into a budget-aware customer action list.

## What the Dashboard Shows

- Member lookup by customer ID.
- Customer segment and segment profile narrative.
- Model-derived uplift signals: `uplift_score`, `p_treat`, and `p_control`.
- Cluster-based campaign cost for the selected member.
- Decision score used for prioritization.
- Budget and eligible-cluster controls for building a campaign action list.
- Estimated net profit and ROI for the selected action list.

## Decision Logic

The dashboard uses `dashboard_customers.csv` as its active data source. Each row represents one member.

The main prioritization field is:

```text
decision_score = uplift_score * value - cost
```

Where:

- `uplift_score` is the estimated incremental response from giving an offer.
- `value` is the member's average purchase value, calculated from total spend and purchase frequency.
- `cost` is a fixed campaign cost assigned by customer cluster.

The customer action list filters to eligible clusters, removes customers with negative uplift, sorts remaining customers by `decision_score` and `uplift_score`, then includes customers until the selected budget is reached.

## Data Preparation

`prepare_dashboard_data.py` creates `dashboard_customers.csv` by merging:

- `customer_segments.xlsx`
- `Layer1_customer_uplift_scores.xlsx`

The generated CSV includes the fields required by the dashboard, including customer segment, uplift probabilities, value, cost, decision score, offer-behavior proxies, and basic purchase history features.

If the source Excel files are available, regenerate the dashboard data with:

```bash
python prepare_dashboard_data.py
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` - Streamlit dashboard interface and campaign action-list logic.
- `prepare_dashboard_data.py` - Data preparation script for building `dashboard_customers.csv`.
- `dashboard_customers.csv` - Prepared member-level data used by the app.
- `requirements.txt` - Python dependency list.
- `.streamlit/config.toml` - Local Streamlit settings.
- `CHANGELOG.md` - Notes on design and logic changes.
