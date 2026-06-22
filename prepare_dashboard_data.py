from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SEGMENTS_PATH = BASE_DIR / "customer_segments.xlsx"
UPLIFT_PATH = BASE_DIR / "Layer1_customer_uplift_scores.xlsx"
OUTPUT_PATH = BASE_DIR / "dashboard_customers_1.csv"

COST_BY_CLUSTER = {
    "High-Value Responsive": 3.5,
    "Frequent Light Buyers": 2.5,
    "Dormant Value Customers": 4.0,
    "Low-Value Low-Response": 0.0,
    "Thin-History Low-Activity": 1.0,
    "Not clustered - no transactions": 0,
}
DEFAULT_COST = 5


def normalize_score(series):
    cleaned = pd.to_numeric(series, errors="coerce").fillna(0)
    lower = cleaned.quantile(0.01)
    upper = cleaned.quantile(0.99)
    clipped = cleaned.clip(lower=lower, upper=upper)
    span = clipped.max() - clipped.min()
    if span == 0:
        return pd.Series(0.5, index=series.index)
    return ((clipped - clipped.min()) / span).round(4)


def build_dashboard_data():
    segments = pd.read_excel(SEGMENTS_PATH)
    uplift = pd.read_excel(UPLIFT_PATH)

    merged = segments.merge(uplift, on="person", how="inner", validate="one_to_one")

    frequency = pd.to_numeric(merged["frequency"], errors="coerce")
    total_spend = pd.to_numeric(merged["total_spend"], errors="coerce")
    value = (total_spend / frequency.where(frequency > 0)).fillna(0)

    cost = merged["cluster_name"].map(COST_BY_CLUSTER).fillna(DEFAULT_COST)
    uplift_score = pd.to_numeric(merged["uplift_score"], errors="coerce").fillna(0)
    decision_score_raw = uplift_score * value - cost

    dashboard = pd.DataFrame(
        {
            "member_id": merged["person"].astype(str).str.upper(),
            "cluster": merged["cluster_name"].fillna("Not clustered - no transactions"),
            "cost": cost.astype(float),
            "decision_score": normalize_score(decision_score_raw),
            "decision_score_raw": decision_score_raw.round(4),
            "value": value.round(4),
            "uplift_score": uplift_score.round(4),
            "p_control": pd.to_numeric(merged["p_control"], errors="coerce").fillna(0).round(4),
            "p_treat": pd.to_numeric(merged["p_treat"], errors="coerce").fillna(0).round(4),
            "reward_app_activity": pd.to_numeric(merged["promo_tx_share"], errors="coerce").fillna(0).clip(0, 1).round(4),
            "population_fit": pd.to_numeric(merged["completion_rate"], errors="coerce").fillna(0).clip(0, 1).round(4),
            "preferred_offer_type": merged["preferred_offer_type"].fillna("Unknown"),
            "maturity_flag": merged["maturity_flag"].fillna("unknown"),
            "total_spend": total_spend.fillna(0).round(2),
            "frequency": frequency.fillna(0).astype(int),
            "recency_h": pd.to_numeric(merged["recency_h"], errors="coerce").fillna(0).astype(int),
        }
    )

    dashboard = dashboard.sort_values(["decision_score", "uplift_score"], ascending=False)
    dashboard.to_csv(OUTPUT_PATH, index=False)
    return dashboard


if __name__ == "__main__":
    output = build_dashboard_data()
    print(f"Wrote {len(output):,} rows to {OUTPUT_PATH.name}")
    print("Columns:")
    for column in output.columns:
        print(f"- {column}")
