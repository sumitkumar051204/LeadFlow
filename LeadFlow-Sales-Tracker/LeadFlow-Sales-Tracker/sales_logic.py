"""Reusable data validation and sales metrics for LeadFlow."""
from __future__ import annotations

import pandas as pd

STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"]
REQUIRED_COLUMNS = ["lead_id", "company", "contact", "source", "stage", "deal_value", "created_date", "next_follow_up", "notes"]


def prepare_leads(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate a leads CSV and return clean, typed data."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    leads = frame.copy()
    for field in ("lead_id", "company", "contact", "source", "stage"):
        leads[field] = leads[field].fillna("").astype(str).str.strip()
    if leads["lead_id"].eq("").any() or leads["lead_id"].duplicated().any():
        raise ValueError("Lead IDs must be unique and non-empty.")
    if leads["company"].eq("").any():
        raise ValueError("Company names cannot be empty.")
    if not leads["stage"].isin(STAGES).all():
        raise ValueError("Invalid stage. Use: " + ", ".join(STAGES))
    leads["deal_value"] = pd.to_numeric(leads["deal_value"], errors="coerce")
    if leads["deal_value"].isna().any() or leads["deal_value"].lt(0).any():
        raise ValueError("Deal values must be non-negative numbers.")
    for field in ("created_date", "next_follow_up"):
        leads[field] = pd.to_datetime(leads[field], errors="coerce")
    if leads["created_date"].isna().any():
        raise ValueError("Every lead needs a valid created_date (YYYY-MM-DD).")
    leads["notes"] = leads["notes"].fillna("").astype(str)
    return leads


def summary_metrics(leads: pd.DataFrame) -> dict:
    """Won revenue is booked value; pipeline excludes won/lost deals."""
    total = len(leads)
    won = leads["stage"].eq("Won")
    active = ~leads["stage"].isin(["Won", "Lost"])
    return {
        "total_leads": total,
        "won_deals": int(won.sum()),
        "conversion_rate": (100 * won.sum() / total) if total else 0.0,
        "won_revenue": float(leads.loc[won, "deal_value"].sum()),
        "open_pipeline": float(leads.loc[active, "deal_value"].sum()),
    }


def follow_ups_due(leads: pd.DataFrame, today: pd.Timestamp) -> pd.DataFrame:
    """Due today or overdue, excluding closed opportunities."""
    active = ~leads["stage"].isin(["Won", "Lost"])
    due = leads["next_follow_up"].notna() & (leads["next_follow_up"].dt.normalize() <= today.normalize())
    return leads.loc[active & due].sort_values("next_follow_up")


def next_lead_id(leads: pd.DataFrame) -> str:
    """Allocate an ID without reusing any current numeric suffix."""
    nums = pd.to_numeric(leads["lead_id"].str.extract(r"^L(\d+)$")[0], errors="coerce")
    return f"L{int(nums.max()) + 1:03d}" if nums.notna().any() else "L001"


def to_csv_bytes(leads: pd.DataFrame) -> bytes:
    """Export dates in portable ISO format."""
    output = leads.copy()
    for name in ("created_date", "next_follow_up"):
        output[name] = output[name].dt.strftime("%Y-%m-%d").fillna("")
    return output.to_csv(index=False).encode("utf-8")
