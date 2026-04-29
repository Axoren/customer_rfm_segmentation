"""Customer RFM segmentation pipeline.

This script cleans transaction-level retail data, calculates Recency,
Frequency, and Monetary metrics, assigns RFM scores, and creates business
segments for CRM prioritization.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DATA_PATH = Path("data/online_retail.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_PATH = OUTPUT_DIR / "rfm_segments.csv"


SEGMENT_RULES = {
    "Champions": {"min_r": 4, "min_f": 4, "min_m": 4},
    "Loyal Customers": {"min_r": 3, "min_f": 4, "min_m": 3},
    "Potential Loyalists": {"min_r": 4, "min_f": 2, "min_m": 2},
    "At Risk High Value": {"max_r": 2, "min_f": 3, "min_m": 4},
    "Need Attention": {"max_r": 3, "min_f": 2, "min_m": 2},
}


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load transaction-level retail data."""
    return pd.read_csv(path, encoding="ISO-8859-1")


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transactions before RFM calculation."""
    clean_df = df.copy()
    clean_df.columns = clean_df.columns.str.strip()

    clean_df = clean_df.dropna(subset=["CustomerID", "InvoiceDate"])
    clean_df = clean_df.loc[~clean_df["InvoiceNo"].astype(str).str.startswith("C")]
    clean_df = clean_df.loc[clean_df["Quantity"] > 0]
    clean_df = clean_df.loc[clean_df["UnitPrice"] > 0]

    clean_df["CustomerID"] = clean_df["CustomerID"].astype(int)
    clean_df["InvoiceDate"] = pd.to_datetime(clean_df["InvoiceDate"])
    clean_df["revenue"] = clean_df["Quantity"] * clean_df["UnitPrice"]

    return clean_df


def build_rfm_table(df: pd.DataFrame, analysis_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Calculate Recency, Frequency, and Monetary values per customer."""
    if analysis_date is None:
        analysis_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("CustomerID")
        .agg(
            last_purchase_date=("InvoiceDate", "max"),
            frequency=("InvoiceNo", "nunique"),
            monetary=("revenue", "sum"),
        )
        .reset_index()
    )

    rfm["recency"] = (analysis_date - rfm["last_purchase_date"]).dt.days
    return rfm


def add_rfm_scores(rfm: pd.DataFrame) -> pd.DataFrame:
    """Assign R, F, and M scores using quartiles."""
    scored = rfm.copy()

    scored["r_score"] = pd.qcut(scored["recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    scored["f_score"] = pd.qcut(
        scored["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]
    ).astype(int)
    scored["m_score"] = pd.qcut(
        scored["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]
    ).astype(int)

    scored["rfm_score"] = scored["r_score"] + scored["f_score"] + scored["m_score"]
    scored["rfm_code"] = (
        scored["r_score"].astype(str)
        + scored["f_score"].astype(str)
        + scored["m_score"].astype(str)
    )

    return scored


def assign_segment(row: pd.Series) -> str:
    """Assign a CRM segment based on RFM scores."""
    r_score = row["r_score"]
    f_score = row["f_score"]
    m_score = row["m_score"]

    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        return "Champions"
    if r_score >= 3 and f_score >= 4 and m_score >= 3:
        return "Loyal Customers"
    if r_score >= 4 and f_score >= 2 and m_score >= 2:
        return "Potential Loyalists"
    if r_score <= 2 and f_score >= 3 and m_score >= 4:
        return "At Risk High Value"
    if r_score <= 3 and f_score >= 2 and m_score >= 2:
        return "Need Attention"
    return "Low Value Casual"


def add_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """Add business-friendly segment labels."""
    segmented = rfm.copy()
    segmented["segment"] = segmented.apply(assign_segment, axis=1)
    return segmented


def build_segment_summary(segmented: pd.DataFrame) -> pd.DataFrame:
    """Build segment-level summary for CRM prioritization."""
    summary = (
        segmented.groupby("segment")
        .agg(
            customers=("CustomerID", "nunique"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            total_monetary=("monetary", "sum"),
            avg_monetary=("monetary", "mean"),
        )
        .reset_index()
    )

    total_customers = summary["customers"].sum()
    total_monetary = summary["total_monetary"].sum()

    summary["customer_share"] = summary["customers"] / total_customers
    summary["monetary_share"] = np.where(
        total_monetary == 0,
        0,
        summary["total_monetary"] / total_monetary,
    )

    return summary.sort_values("total_monetary", ascending=False)


def save_outputs(segmented: pd.DataFrame, summary: pd.DataFrame) -> None:
    """Save customer-level and segment-level outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    segmented.to_csv(OUTPUT_PATH, index=False)
    summary.to_csv(OUTPUT_DIR / "rfm_segment_summary.csv", index=False)


def print_summary(summary: pd.DataFrame) -> None:
    """Print segment summary."""
    print("RFM Segment Summary")
    print("=" * 80)
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.2f}"))


def main() -> None:
    """Run the RFM segmentation pipeline."""
    raw_df = load_data()
    clean_df = clean_transactions(raw_df)
    rfm = build_rfm_table(clean_df)
    scored = add_rfm_scores(rfm)
    segmented = add_segments(scored)
    summary = build_segment_summary(segmented)
    save_outputs(segmented, summary)
    print_summary(summary)


if __name__ == "__main__":
    main()
