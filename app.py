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
    
    /* יישור שדות וטבלאות מימין לשמאל */
    .stDataFrame, div[data-testid="stDataEditor"] {
        direction: rtl !important;
        text-align: right !important;
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

# הגדרת עמודות עם פורמט מפריד אלפים מפורש
column_configuration = {
    "תיאור": st.column_config.TextColumn("תיאור"),
    "סכום (₪)": st.column_config.NumberColumn("סכום (₪)", format="%,d")
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔵 הכנסות")
    df_income = pd.DataFrame(current_data["income"])
    edited_income = st.data_editor(
        df_income,
        column_order=["תיאור", "סכום (₪)"],
        column_config=column_configuration,
        num_rows="dynamic",
        key=f"income_{selected_month}"
    )
    current_data["income"] = edited_income.to_dict('records')

with col2:
    st.markdown("### 🔴 הוצאות קבועות")
    df_fixed = pd.DataFrame(current_data["fixed"])
    edited_fixed = st.data_editor(
        df_fixed,
        column_order=["תיאור", "סכום (₪)"],
        column_config=column_configuration,
        num_rows="dynamic",
        key=f"fixed_{selected_month}"
    )
    current_data["fixed"] = edited_fixed.to_dict('records')

st.markdown("### 🟢 הוצאות משתנות")
df_var = pd.DataFrame(current_data["var"])
edited_var = st.data_editor(
    df_var,
    column_order=["תיאור", "סכום (₪)"],
    column_config=column_configuration,
    num_rows="dynamic",
    key=f"var_{selected_month}"
)
current_data["var"] = edited_var.to_dict('records')

# חישובים
total_income = int(edited_income["סכום (₪)"].sum()) if not edited_income.empty else 0
total_fixed = int(edited_fixed["סכום (₪)"].sum()) if not edited_fixed.empty else 0
total_var = int(edited_var["סכום (₪)"].sum()) if not edited_var.empty else 0

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
