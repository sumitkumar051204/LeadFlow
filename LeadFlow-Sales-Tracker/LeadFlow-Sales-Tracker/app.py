"""LeadFlow: a simple B2B lead and sales pipeline dashboard."""
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from sales_logic import STAGES, follow_ups_due, next_lead_id, prepare_leads, summary_metrics, to_csv_bytes

SAMPLE_PATH = Path(__file__).parent / "data" / "sample_leads.csv"
st.set_page_config(page_title="LeadFlow | Sales Tracker", page_icon="📈", layout="wide")


@st.cache_data
def load_sample() -> pd.DataFrame:
    return prepare_leads(pd.read_csv(SAMPLE_PATH))


if "leads" not in st.session_state:
    st.session_state.leads = load_sample()

st.title("📈 LeadFlow | B2B Sales Tracker")
st.caption("Track opportunities, prioritize follow-ups, and understand your sales funnel. Demo data is fictional.")

with st.sidebar:
    st.header("Workspace")
    st.info("Changes live in this browser session. Download your CSV to save and re-upload it later.")
    uploaded = st.file_uploader("Import leads CSV", type=["csv"])
    if uploaded is not None and st.button("Import CSV", use_container_width=True):
        try:
            st.session_state.leads = prepare_leads(pd.read_csv(uploaded))
            st.success("CSV imported successfully")
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
            st.error(f"Could not import CSV: {error}")
    if st.button("Reset to demo data", use_container_width=True):
        st.session_state.leads = load_sample().copy()
        st.success("Demo data restored")
    st.download_button("⬇ Download current leads", data=to_csv_bytes(st.session_state.leads), file_name="my_leads.csv", mime="text/csv", use_container_width=True)

leads = st.session_state.leads
metrics = summary_metrics(leads)
a, b, c, d, e = st.columns(5)
a.metric("Total Leads", metrics["total_leads"])
b.metric("Deals Won", metrics["won_deals"])
c.metric("Lead-to-Win Rate", f'{metrics["conversion_rate"]:.1f}%')
d.metric("Won Deal Value", f'₹{metrics["won_revenue"]:,.0f}')
e.metric("Open Pipeline Value", f'₹{metrics["open_pipeline"]:,.0f}')

overview_tab, follow_tab, manage_tab = st.tabs(["📊 Overview", "📅 Follow-ups", "➕ Manage leads"])
with overview_tab:
    st.subheader("Sales funnel")
    left, right = st.columns([1, 1])
    with left:
        counts = leads["stage"].value_counts().reindex(STAGES, fill_value=0)
        st.bar_chart(counts.rename("Leads"), color="#2563EB")
    with right:
        sources = leads.groupby("source", dropna=False)["lead_id"].count().sort_values(ascending=False)
        st.write("**Leads by acquisition source**")
        st.bar_chart(sources.rename("Leads"), color="#0D9488")
    stage_filter = st.multiselect("Filter by stage", STAGES, default=STAGES)
    search = st.text_input("Search company or contact", placeholder="e.g. textiles")
    visible = leads.loc[leads["stage"].isin(stage_filter)]
    if search:
        visible = visible.loc[visible["company"].str.contains(search, case=False, regex=False) | visible["contact"].str.contains(search, case=False, regex=False)]
    st.dataframe(visible.sort_values("created_date", ascending=False), use_container_width=True, hide_index=True)
    st.caption("Lead-to-win rate = won deals / all leads. Open pipeline excludes Won and Lost. These are snapshot metrics, not a cohort-based funnel.")

with follow_tab:
    st.subheader("Follow-ups due today or earlier")
    due = follow_ups_due(leads, pd.Timestamp(date.today()))
    st.metric("Outstanding follow-ups", len(due))
    if due.empty:
        st.success("No outstanding follow-ups. You're all caught up!")
    else:
        st.dataframe(due[["lead_id", "company", "contact", "stage", "next_follow_up", "notes"]], hide_index=True, use_container_width=True)
    st.caption("Closed leads (Won/Lost) are excluded; missing follow-up dates are not considered overdue.")

with manage_tab:
    st.subheader("Add a new lead")
    with st.form("add_lead", clear_on_submit=True):
        x, y = st.columns(2)
        company = x.text_input("Company *")
        contact = y.text_input("Contact name")
        source = x.selectbox("Lead source", ["IndiaMART", "Website", "Referral", "Cold Outreach", "Trade Fair", "Other"])
        stage = y.selectbox("Sales stage", STAGES)
        value = x.number_input("Potential deal value (₹)", min_value=0.0, step=1000.0)
        next_follow = y.date_input("Next follow-up", value=date.today())
        notes = st.text_area("Notes")
        add = st.form_submit_button("Add lead", type="primary")
    if add:
        if not company.strip():
            st.error("Company is required.")
        else:
            row = pd.DataFrame([{"lead_id": next_lead_id(leads), "company": company.strip(), "contact": contact.strip(), "source": source, "stage": stage, "deal_value": value, "created_date": date.today().isoformat(), "next_follow_up": next_follow.isoformat(), "notes": notes}])
            st.session_state.leads = prepare_leads(pd.concat([leads, row], ignore_index=True))
            st.success("Lead added. Download the CSV from the sidebar to retain it.")
            st.rerun()

    st.divider()
    st.subheader("Update an existing lead")
    if not leads.empty:
        label_to_id = {f'{r.lead_id} · {r.company}': r.lead_id for r in leads.itertuples()}
        chosen = st.selectbox("Choose lead", list(label_to_id))
        current_id = label_to_id[chosen]
        record = leads.loc[leads["lead_id"].eq(current_id)].iloc[0]
        with st.form("update_lead"):
            new_stage = st.selectbox("Change sales stage", STAGES, index=STAGES.index(record["stage"]))
            new_value = st.number_input("Deal value (₹)", min_value=0.0, value=float(record["deal_value"]), step=1000.0)
            fallback_date = record["next_follow_up"].date() if pd.notna(record["next_follow_up"]) else date.today()
            new_follow = st.date_input("Next follow-up date", value=fallback_date)
            new_notes = st.text_area("Notes", value=str(record["notes"]))
            update = st.form_submit_button("Save changes")
        if update:
            idx = leads.index[leads["lead_id"].eq(current_id)][0]
            edited = leads.copy()
            edited.loc[idx, ["stage", "deal_value", "next_follow_up", "notes"]] = [new_stage, new_value, pd.Timestamp(new_follow), new_notes]
            st.session_state.leads = prepare_leads(edited)
            st.success("Lead updated. Export CSV to save changes.")
            st.rerun()
