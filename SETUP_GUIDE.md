# SmartFind — Cloud-Based Lost and Found System

A beginner-friendly Cloud Computing mini project using Streamlit (Python UI) and Supabase (hosted PostgreSQL database).

## What works

- Report a Lost or Found item
- Save reports to Supabase Cloud
- Search by item name
- Filter by report type, category, and status
- View recent reports and summary counts
- Mark an open report as Returned

## Requirements

- Python 3.10 or newer recommended
- Internet connection
- Supabase account/project
- VS Code or another editor (optional)

## 1. Install dependencies

Open a terminal in the `SmartFind_Cloud_Project` folder:

```bash
python -m pip install -r requirements.txt
```

## 2. Create the Supabase table

1. Open https://supabase.com/dashboard and create/open a project.
2. Open **SQL Editor** → **New query**.
3. Copy all of `supabase_setup.sql` into the query editor.
4. Click **Run**.
5. Confirm the `items` table exists under **Table Editor**.

### Important demo security note

The SQL policies in this ZIP are intentionally permissive so a student can run a simple anonymous classroom demo without building login first. Anyone who obtains the public project URL and public key can read records, submit reports, and update statuses. Use fake/demo data only; do not add phone numbers, passwords, full addresses, identity-card numbers, or other sensitive personal information. For a real deployment, implement authentication and restrictive Row Level Security policies before sharing the app publicly.

## 3. Add Supabase credentials

1. In the Supabase dashboard, open **Project Settings** and find the project API keys / API settings.
2. Copy the **Project URL**.
3. Copy the **publishable key**. If the dashboard only shows legacy keys, use the `anon` public key.
4. In the project folder, open `.streamlit`.
5. Copy `secrets.toml.example` and rename the copy to `secrets.toml`.
6. Put your real URL and public key in that file.

The file should look like this:

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-public-publishable-or-anon-key"
```

Do not use the `service_role` key or any secret key in this app. Do not share or upload `secrets.toml`.

## 4. Run the app

From the project folder, run:

```bash
python -m streamlit run app.py
```

Streamlit should open the app in your browser. If it does not, open the local URL printed in the terminal, usually `http://localhost:8501`.

## 5. Test it

1. Open **Report an Item** and add a demo Lost item.
2. Add a demo Found item.
3. Open **Search Items** and search by name or filter.
4. Open **Update Status**, select an open report, and mark it Returned.
5. In Supabase **Table Editor → items**, confirm the records are stored in the cloud.

## Troubleshooting

- **Missing credentials warning:** check `.streamlit/secrets.toml` spelling, file location, quotes, URL, and key. Restart Streamlit after editing.
- **Permission / RLS error:** run `supabase_setup.sql` again in the correct Supabase project.
- **ModuleNotFoundError:** run `python -m pip install -r requirements.txt` in the same Python environment used to run Streamlit.
- **No table found:** confirm the table is named exactly `items` in the `public` schema.
- **Key not working:** use the public publishable key or legacy `anon` key, never `service_role`.

## Project architecture

Browser → Streamlit Python app → Supabase client/API → Supabase PostgreSQL cloud database.

## Viva points

- Cloud computing: database is hosted remotely and accessed over the internet.
- SaaS/PaaS context: Streamlit hosting can publish the UI; Supabase provides managed database services.
- PostgreSQL: relational database storing structured item reports.
- CRUD: create reports, read/search reports, update status.
- Row Level Security (RLS): database-level rules controlling access. The included open policies are for a controlled demo only.
