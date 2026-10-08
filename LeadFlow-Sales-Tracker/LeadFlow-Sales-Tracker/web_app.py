"""Flask HTML frontend for LeadFlow. Demo data is saved locally in CSV."""
from datetime import date
from pathlib import Path
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from sales_logic import prepare_leads, summary_metrics, follow_ups_due, next_lead_id, to_csv_bytes, STAGES
from io import BytesIO

ROOT = Path(__file__).resolve().parent
DATA_PATH = Path(os.environ.get('LEADFLOW_DATA_PATH', str(ROOT / 'data' / 'leads.csv')))
SAMPLE_PATH = ROOT / 'data' / 'sample_leads.csv'
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'local-demo-only-change-this-key')


def load_leads():
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        DATA_PATH.write_bytes(SAMPLE_PATH.read_bytes())
    return prepare_leads(pd.read_csv(DATA_PATH))


def save_leads(leads):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_bytes(to_csv_bytes(prepare_leads(leads)))


@app.get('/')
def dashboard():
    leads = load_leads()
    metrics = summary_metrics(leads)
    due = follow_ups_due(leads, pd.Timestamp.today())
    q = request.args.get('q', '').strip()
    stage = request.args.get('stage', '')
    filtered = leads.copy()
    if q:
        filtered = filtered[filtered['company'].str.contains(q, case=False, regex=False) | filtered['contact'].str.contains(q, case=False, regex=False)]
    if stage in STAGES:
        filtered = filtered[filtered['stage'].eq(stage)]
    source_counts = leads['source'].value_counts().to_dict()
    stage_counts = {s: int((leads['stage'] == s).sum()) for s in STAGES}
    records = []
    for item in filtered.to_dict('records'):
        item['next_follow_up_display'] = item['next_follow_up'].strftime('%d %b %Y') if pd.notna(item['next_follow_up']) else '—'
        records.append(item)
    return render_template('dashboard.html', metrics=metrics, due=due, due_records=due.to_dict('records'), records=records, stages=STAGES, source_counts=source_counts, stage_counts=stage_counts, max_stage=max(stage_counts.values(), default=1) or 1, max_source=max(source_counts.values(), default=1) or 1, q=q, stage=stage, today=date.today().isoformat())


@app.post('/leads')
def add_lead():
    leads = load_leads()
    try:
        company = request.form.get('company', '').strip()
        contact = request.form.get('contact', '').strip()
        source = request.form.get('source', '').strip() or 'Other'
        stage = request.form.get('stage', 'New')
        amount = float(request.form.get('deal_value', 0))
        followup = request.form.get('next_follow_up', '')
        if not company or not contact or stage not in STAGES or amount < 0:
            raise ValueError('Please provide a company, contact, valid stage, and non-negative deal value.')
        if followup:
            date.fromisoformat(followup)
        new = dict(lead_id=next_lead_id(leads), company=company, contact=contact, source=source, stage=stage, deal_value=amount, created_date=date.today().isoformat(), next_follow_up=followup, notes=request.form.get('notes', '').strip())
        leads = pd.concat([leads, pd.DataFrame([new])], ignore_index=True)
        save_leads(leads)
        flash('Lead added successfully.', 'success')
    except (ValueError, TypeError) as exc:
        flash(str(exc), 'error')
    return redirect(url_for('dashboard'))


@app.post('/leads/<lead_id>/stage')
def update_stage(lead_id):
    leads = load_leads()
    stage = request.form.get('stage', '')
    if stage not in STAGES or not leads['lead_id'].eq(lead_id).any():
        flash('Invalid lead or stage.', 'error')
    else:
        leads.loc[leads['lead_id'].eq(lead_id), 'stage'] = stage
        save_leads(leads)
        flash(f'{lead_id} updated to {stage}.', 'success')
    return redirect(url_for('dashboard'))


@app.get('/export')
def export():
    return send_file(BytesIO(to_csv_bytes(load_leads())), mimetype='text/csv', as_attachment=True, download_name='leadflow_leads.csv')


if __name__ == '__main__':
    app.run(debug=False, port=5000)
