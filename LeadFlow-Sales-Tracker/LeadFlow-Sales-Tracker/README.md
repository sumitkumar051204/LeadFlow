# LeadFlow — B2B Sales & Lead Tracker

A beginner-friendly Python dashboard for small B2B sales teams to organize leads, track deal stages, and never miss important follow-ups. Built with **Python, Streamlit, and pandas**. Suitable as a small portfolio project for sales, product, or business-development applications.

> **Disclosure:** All demo companies, contacts, and values are fictional. This is an independent demo project, not an official IndiaMART product or integration.

## What problem does it solve?

A seller handling inquiries from multiple channels (such as marketplaces, websites, referrals, and trade fairs) might lose track of who needs a call or which deals are close to closing. LeadFlow brings those records together in one simple dashboard.

## Features

- **Sales snapshot:** lead count, won deals, lead-to-win rate, value of won deals, and open pipeline value.
- **Funnel view:** lead distribution across New → Contacted → Qualified → Proposal → Won/Lost.
- **Source breakdown:** compare inquiries from different channels.
- **Follow-up list:** automatically flag active leads whose follow-up dates are today or earlier.
- **Manage leads:** add new leads; update their stage, potential deal value, follow-up date and notes.
- **Import/export CSV:** use your own dataset and download any changes.
- **Search and filter:** explore leads by company, contact or stage.

## Demo preview

After running, you'll see three tabs: **Overview**, **Follow-ups**, and **Manage leads**, along with five KPI tiles. The app loads 12 fictional leads automatically.

## Run locally

Install **Python 3.10+**. In a terminal, from this folder:

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install and start:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in your terminal (usually `http://localhost:8501`).

## How to use

1. Open **Overview** to review KPI tiles, funnel counts, and source breakdown.
2. Open **Follow-ups** to see active leads with dates due today or earlier.
3. Open **Manage leads** to add a prospect, or update an existing lead's status.
4. Download the updated CSV in the sidebar to save your changes.
5. Later, upload that CSV using the sidebar and click **Import CSV** to restore it.

**Data storage limitation:** The app maintains changes in Streamlit session state. It does **not** use a persistent database. Changes are lost when the session resets unless you export them to CSV. Different visitors do not share data.

## Metrics definitions

- **Won deal value:** sum of `deal_value` for stage `Won`. This is the booked opportunity value in the demo, not proof of cash collected.
- **Open pipeline value:** sum of `deal_value` for stages other than `Won` or `Lost` (unweighted).
- **Lead-to-win rate:** `(number of Won leads / total leads) × 100`, a snapshot, **not** a stage-to-stage conversion metric.
- **Outstanding follow-up:** open lead with a nonblank `next_follow_up` date on or before the current local date.

## Project structure

```text
LeadFlow-Sales-Tracker/
├── app.py                     # Streamlit interface
├── sales_logic.py             # Data validation and business logic
├── data/
│   └── sample_leads.csv       # Fictional demo inquiries
├── tests/
│   └── test_sales_logic.py    # Unit tests
├── .streamlit/
│   └── config.toml            # App appearance
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Explain it in an interview (30–45 seconds)

"I built LeadFlow, a lightweight B2B sales tracker, because small sellers often receive inquiries across different channels and struggle to track follow-ups and deal progress. I used Streamlit for a quick interactive interface and pandas for data cleaning, lead filters, funnel counts, and sales KPIs. Users can add leads, change deal stages, see overdue follow-ups, and export their records as CSV. I separated calculations into a testable Python module. The current version uses session-based storage, and I would add SQLite, authentication, and reminders next."

**Be prepared to demonstrate:** adding a lead, updating it to Won, noticing a KPI change, exporting and importing the CSV. Review the code and make any changes needed so you can accurately describe your own contribution.

## Future enhancements

- SQLite or PostgreSQL persistence
- Login and role-based access
- Scheduled email or WhatsApp reminders (with user consent)
- Deal-owner assignments and sales forecasting

## GitHub upload

Create a new GitHub repository named `LeadFlow-Sales-Tracker` and upload **the contents of this folder** (or use `git init`, `git add .`, `git commit`, then push to your repository). Do not upload the `.venv` directory.

## License

MIT — see [LICENSE](LICENSE).

## HTML + CSS frontend (Flask)

An additional **responsive HTML/CSS dashboard** is included. It uses Flask to connect browser forms to the same Python sales metrics in `sales_logic.py`.

```bash
pip install -r requirements.txt
python web_app.py
```

Open **http://127.0.0.1:5000**. The HTML dashboard includes KPI cards, CSS sales-funnel charts, lead-source breakdowns, due follow-ups, search and stage filters, lead creation, stage updates, and CSV export.

**Files:** `web_app.py` (Flask backend), `templates/dashboard.html` (HTML/Jinja), `static/style.css` (responsive styles), `sales_logic.py` (shared analytics). The Flask app copies fictional demo records to `data/leads.csv` on first run and persists edits there; that working CSV is Git-ignored. It does not connect to IndiaMART or store real customer data. No login/authentication is implemented: run locally for a portfolio demonstration, **not** publicly with sensitive information.

The original Streamlit app is also available via `streamlit run app.py`. These two demo UIs have **separate storage/session behavior**: Streamlit uses its own session state, while Flask persists to `data/leads.csv`.
