import os
from datetime import date
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="SmartFind | Lost & Found",
    page_icon="🔎",
    layout="wide",
)

st.markdown("""
<style>
    .main .block-container { max-width: 1100px; padding-top: 2rem; }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #eef2ff 0%, #ecfeff 100%);
        color: #172554;
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2.3rem; }
    .hero p { margin: .45rem 0 0 0; font-size: 1.05rem; }
    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        padding: 12px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


def get_setting(name: str) -> str:
    """Read a secret from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "")).strip()


@st.cache_resource(show_spinner=False)
def connect_supabase(url: str, key: str):
    return create_client(url, key)


SUPABASE_URL = get_setting("SUPABASE_URL")
SUPABASE_KEY = get_setting("SUPABASE_KEY")

st.markdown("""
<div class="hero">
  <h1>🔎 SmartFind</h1>
  <p>Cloud-Based Lost and Found System</p>
  <p>Report lost items, share found items, and search records from one place.</p>
</div>
""", unsafe_allow_html=True)

if not SUPABASE_URL or not SUPABASE_KEY:
    st.warning("Supabase connection is not configured yet.")
    st.markdown("""
    **Quick setup**
    1. Open `SETUP_GUIDE.md` included in this project ZIP.
    2. Create the Supabase table using `supabase_setup.sql`.
    3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
    4. Add your Supabase Project URL and publishable/anon key.
    5. Restart this app.

    Do not put a `service_role` or secret key in this app.
    """)
    st.stop()

try:
    supabase = connect_supabase(SUPABASE_URL, SUPABASE_KEY)
except Exception as exc:
    st.error("Could not initialize the Supabase client. Check the URL and key in your secrets file.")
    st.caption(f"Technical detail: {exc}")
    st.stop()


def fetch_items(report_type=None, search_text="", category="All", status="All"):
    query = supabase.table("items").select("*")
    if report_type and report_type != "All":
        query = query.eq("report_type", report_type)
    if search_text.strip():
        safe_search = search_text.strip().replace("%", r"\%").replace("_", r"\_")
        query = query.ilike("item_name", f"%{safe_search}%")
    if category != "All":
        query = query.eq("category", category)
    if status != "All":
        query = query.eq("status", status)
    response = query.order("created_at", desc=True).limit(200).execute()
    return response.data or []


menu = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📝 Report an Item", "🔍 Search Items", "✅ Update Status"],
)
st.sidebar.caption("SmartFind • Student mini project")
st.sidebar.info("Demo tip: don't post passwords, full addresses, or sensitive personal details.")

if menu == "🏠 Home":
    st.subheader("Welcome to SmartFind")
    st.write("A simple cloud-powered portal for reporting and finding lost belongings.")
    try:
        all_items = fetch_items()
        lost_count = sum(1 for item in all_items if item.get("report_type") == "Lost")
        found_count = sum(1 for item in all_items if item.get("report_type") == "Found")
        open_count = sum(1 for item in all_items if item.get("status") == "Open")
        c1, c2, c3 = st.columns(3)
        c1.metric("Lost reports", lost_count)
        c2.metric("Found reports", found_count)
        c3.metric("Open reports", open_count)
        st.markdown("### Latest reports")
        if all_items:
            st.dataframe(
                [
                    {
                        "Item": x.get("item_name", ""),
                        "Type": x.get("report_type", ""),
                        "Category": x.get("category", ""),
                        "Location": x.get("location", ""),
                        "Date": x.get("item_date", ""),
                        "Status": x.get("status", ""),
                    }
                    for x in all_items[:8]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No reports yet. Use 'Report an Item' to add the first record.")
    except Exception as exc:
        st.error("Could not load records from Supabase.")
        st.caption("Check that the SQL setup and Row Level Security policies have been applied.")
        st.caption(f"Technical detail: {exc}")

elif menu == "📝 Report an Item":
    st.subheader("Report a Lost or Found Item")
    st.write("Please avoid sharing sensitive information such as passwords or full home addresses.")
    with st.form("report_form", clear_on_submit=True):
        report_type = st.radio("Report type", ["Lost", "Found"], horizontal=True)
        item_name = st.text_input("Item name *", placeholder="e.g. Blue water bottle")
        category = st.selectbox(
            "Category *",
            ["ID Card", "Phone", "Bag", "Keys", "Books", "Bottle", "Wallet", "Clothing", "Other"],
        )
        description = st.text_area("Description", placeholder="Colour, brand, or identifying details (no sensitive data)")
        location = st.text_input("Last seen / found location *", placeholder="e.g. College library")
        item_date = st.date_input("Date lost / found", value=date.today(), max_value=date.today())
        submitted = st.form_submit_button("Submit Report", type="primary", use_container_width=True)

    if submitted:
        if not item_name.strip() or not location.strip():
            st.error("Please fill in the item name and location.")
        else:
            payload = {
                "item_name": item_name.strip()[:120],
                "category": category,
                "description": description.strip()[:1000],
                "location": location.strip()[:160],
                "item_date": item_date.isoformat(),
                "report_type": report_type,
                "status": "Open",
            }
            try:
                result = supabase.table("items").insert(payload).execute()
                if result.data:
                    st.success("Report submitted successfully and saved to Supabase Cloud! ☁️")
                    st.info("You can find it in the Search Items page.")
                else:
                    st.success("Request sent. Check Search Items to confirm the record appears.")
            except Exception as exc:
                st.error("Could not save the report. Check your Supabase table and RLS policies.")
                st.caption(f"Technical detail: {exc}")

elif menu == "🔍 Search Items":
    st.subheader("Search Lost & Found Reports")
    col1, col2 = st.columns([2, 1])
    with col1:
        search_text = st.text_input("Search by item name", placeholder="e.g. ID card")
    with col2:
        report_filter = st.selectbox("Report type", ["All", "Lost", "Found"])
    col3, col4 = st.columns(2)
    with col3:
        category_filter = st.selectbox(
            "Category",
            ["All", "ID Card", "Phone", "Bag", "Keys", "Books", "Bottle", "Wallet", "Clothing", "Other"],
        )
    with col4:
        status_filter = st.selectbox("Status", ["All", "Open", "Returned"])
    if st.button("Search", type="primary"):
        try:
            matches = fetch_items(report_filter, search_text, category_filter, status_filter)
            if not matches:
                st.info("No matching reports found.")
            else:
                st.success(f"Found {len(matches)} matching report(s).")
                for item in matches:
                    with st.container(border=True):
                        left, right = st.columns([4, 1])
                        with left:
                            st.markdown(f"**{item.get('item_name', 'Unnamed item')}**")
                            st.caption(
                                f"{item.get('report_type', '')} • {item.get('category', '')} • "
                                f"{item.get('status', '')}"
                            )
                            st.write(item.get("description") or "No description provided.")
                            st.write(f"**Location:** {item.get('location') or 'Not specified'}")
                            st.write(f"**Date:** {item.get('item_date') or 'Not specified'}")
                        with right:
                            st.caption(f"Report ID: {item.get('id')}")
        except Exception as exc:
            st.error("Search failed. Check the database setup and policies.")
            st.caption(f"Technical detail: {exc}")

elif menu == "✅ Update Status":
    st.subheader("Mark an Item as Returned")
    st.write("Use the report ID shown on the Search Items page.")
    try:
        open_items = fetch_items(status="Open")
        if not open_items:
            st.info("There are no open reports to update.")
        else:
            options = {
                f"#{x.get('id')} — {x.get('item_name')} ({x.get('report_type')})": x
                for x in open_items
            }
            selected_label = st.selectbox("Choose a report", list(options.keys()))
            selected_item = options[selected_label]
            st.write(f"**Location:** {selected_item.get('location') or 'Not specified'}")
            if st.button("Mark as Returned", type="primary"):
                try:
                    response = (
                        supabase.table("items")
                        .update({"status": "Returned"})
                        .eq("id", selected_item["id"])
                        .execute()
                    )
                    if response.data:
                        st.success("Status updated to Returned.")
                        st.rerun()
                    else:
                        st.warning("No record was updated. Check your database policies.")
                except Exception as exc:
                    st.error("Could not update the status.")
                    st.caption(f"Technical detail: {exc}")
    except Exception as exc:
        st.error("Could not load open reports.")
        st.caption(f"Technical detail: {exc}")

st.divider()
st.caption("SmartFind is a CLOUD COMPUTING PROJECT DEVELOPED BY BHUMI,TANUSHRI,DIVYA,ADITI. Verify ownership before returning an item.")
