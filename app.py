import streamlit as st
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="ניהול תקציב והוצאות", page_icon="💰", layout="wide")

# הגדרת כיוון כתיבה מימין לשמאל (RTL) לכל האפליקציה
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .stApp {
        direction: rtl !important;
        text-align: right !important;
    }
    
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, label, div {
        text-align: right !important;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: right !important;
        justify-content: flex-end !important;
    }
    
    /* יישור שדות קלט מימין לשמאל */
    input {
        text-align: right !important;
        direction: rtl !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 ניהול הכנסות והוצאות")

# יצירת רשימת חודשים עד דצמבר 2027
months = []
start_date = datetime(2026, 10, 1)
end_date = datetime(2027, 12, 1)

current = start_date
while current <= end_date:
    month_name = current.strftime("%B %Y")
    heb_months = {
        "January": "ינואר", "February": "פברואר", "March": "מרץ", "April": "אפריל",
        "May": "מאי", "June": "יוני", "July": "יולי", "August": "אוגוסט",
        "September": "ספטמבר", "October": "אוקטובר", "November": "נובמבר", "December": "דצמבר"
    }
    for eng, heb in heb_months.items():
        month_name = month_name.replace(eng, heb)
    months.append(month_name)
    
    if current.month == 12:
        current = datetime(current.year + 1, 1, 1)
    else:
        current = datetime(current.year, current.month + 1, 1)

selected_month = st.sidebar.selectbox("בחר חודש", months)

# ניהול נתונים ב-st.session_state
if 'budget_data' not in st.session_state:
    st.session_state.budget_data = {}

for m in months:
    if m not in st.session_state.budget_data:
        st.session_state.budget_data[m] = {
            "income": [
                {"תיאור": "העברה מדגני", "סכום (₪)": 0},
                {"תיאור": "פנסיה מיגדל", "סכום (₪)": 0},
                {"תיאור": "פנסיה כלל", "סכום (₪)": 0},
                {"תיאור": "פנסיה פסגות הראל", "סכום (₪)": 0},
                {"תיאור": "העברת הלוואה", "סכום (₪)": 0},
                {"תיאור": "ביטוח לאומי אדי", "סכום (₪)": 0},
                {"תיאור": "ביטוח לאומי נרה", "סכום (₪)": 0},
                {"תיאור": "מיוחד", "סכום (₪)": 0}
            ],
            "fixed": [
                {"תיאור": "הוצאות דיור", "סכום (₪)": 0},
                {"תיאור": "טלפונים ניידים", "סכום (₪)": 0},
                {"תיאור": "החזר הלוואת אשראי", "סכום (₪)": 0},
                {"תיאור": "ביטוח מכונית", "סכום (₪)": 0},
                {"תיאור": "ספוטיפאיי", "סכום (₪)": 0},
                {"תיאור": "נטפליקס", "סכום (₪)": 0}
            ],
            "var": [
                {"תיאור": "מכולת+נספרס", "סכום (₪)": 0},
                {"תיאור": "תרופות ותוספים", "סכום (₪)": 0},
                {"תיאור": "דלק", "סכום (₪)": 0},
                {"תיאור": "ספר מישל", "סכום (₪)": 0},
                {"תיאור": "גולי", "סכום (₪)": 0},
                {"תיאור": "אראלה", "סכום (₪)": 0},
                {"תיאור": "שונות", "סכום (₪)": 0},
                {"תיאור": "אחר", "סכום (₪)": 0}
            ]
        }

st.sidebar.divider()
st.sidebar.subheader("💾 גיבוי ושחזור נתונים")

# כפתור גיבוי (ייצוא) בתפריט הצדדי
backup_json = json.dumps(st.session_state.budget_data, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="📥 הורד גיבוי נתונים",
    data=backup_json,
    file_name=f"budget_backup_{datetime.now().strftime('%Y-%m-%d')}.json",
    mime="application/json"
)

# כפתור טעינה מגיבוי (ייבוא) בתפריט הצדדי
uploaded_backup = st.sidebar.file_uploader("📤 טען קובץ גיבוי", type=["json"])
if uploaded_backup is not None:
    try:
        loaded_data = json.load(uploaded_backup)
        st.session_state.budget_data = loaded_data
        st.sidebar.success("הגיבוי נטען בהצלחה!")
        st.rerun()
    except Exception as e:
        st.sidebar.error("שגיאה בטעינת הקובץ.")

st.header(f"ניהול תקציב עבור: {selected_month}")

current_data = st.session_state.budget_data[selected_month]

# פונקציה להצגת טבלה עם פסיקים לאלפים
def render_category_inputs(category_name, items_list, key_prefix):
    st.markdown(f"### {category_name}")
    
    # כותרות הטבלה (תיאור מימין, סכום משמאל)
    hdr_col1, hdr_col2 = st.columns([3, 2])
    with hdr_col1:
        st.markdown("**תיאור**")
    with hdr_col2:
        st.markdown("**סכום (₪)**")
        
    updated_items = []
    total = 0
    
    for idx, item in enumerate(items_list):
        c1, c2 = st.columns([3, 2])
        with c1:
            desc = st.text_input(
                label=f"desc_{key_prefix}_{idx}",
                value=item["תיאור"],
                key=f"desc_{key_prefix}_{selected_month}_{idx}",
                label_visibility="collapsed"
            )
        with c2:
            # פורמט עם פסיקים לאלפים (format="%d" מציג שלמים עם הפרדת אלפים)
            val = st.number_input(
                label=f"val_{key_prefix}_{idx}",
                value=int(item["סכום (₪)"]),
                step=1,
                format="%d",
                key=f"val_{key_prefix}_{selected_month}_{idx}",
                label_visibility="collapsed"
            )
        updated_items.append({"תיאור": desc, "סכום (₪)": int(val)})
        total += int(val)
        
    return updated_items, total

col1, col2 = st.columns(2)

with col1:
    updated_income, total_income = render_category_inputs("🔵 הכנסות", current_data["income"], "inc")
    current_data["income"] = updated_income

with col2:
    updated_fixed, total_fixed = render_category_inputs("🔴 הוצאות קבועות", current_data["fixed"], "fix")
    current_data["fixed"] = updated_fixed

st.divider()

updated_var, total_var = render_category_inputs("🟢 הוצאות משתנות", current_data["var"], "var")
current_data["var"] = updated_var

# חישוב יתרה להעברה לחיסכון
total_expenses = total_fixed + total_var
transfer_to_savings = total_income - total_expenses

st.divider()
st.subheader("📊 סיכום חודשי")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("סך הכנסות", f"₪{total_income:,}")
metric_col2.metric("הוצאות קבועות", f"₪{total_fixed:,}")
metric_col3.metric("הוצאות משתנות", f"₪{total_var:,}")

if transfer_to_savings >= 0:
    metric_col4.metric("העברה לחיסכון (הכנסות - הוצאות)", f"₪{transfer_to_savings:,}", delta="חיסכון חיובי")
else:
    metric_col4.metric("גירעון / חיסכון שלילי", f"₪{transfer_to_savings:,}", delta="חריגה", delta_color="inverse")
