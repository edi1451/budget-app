import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ניהול תקציב והוצאות", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    .income { color: #0066cc; font-weight: bold; }
    .fixed-expense { color: #cc0000; font-weight: bold; }
    .var-expense { color: #009933; font-weight: bold; }
    .savings { color: #7a00cc; font-weight: bold; font-size: 20px; }
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

st.header(f"ניהול תקציב עבור: {selected_month}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔵 הכנסות")
    income_data = pd.DataFrame([
        {"תיאור": "העברה מדגני", "סכום (₪)": 0},
        {"תיאור": "פנסיה מיגדל", "סכום (₪)": 0},
        {"תיאור": "פנסיה כלל", "סכום (₪)": 0},
        {"תיאור": "פנסיה פסגות הראל", "סכום (₪)": 0},
        {"תיאור": "העברת הלוואה", "סכום (₪)": 0},
        {"תיאור": "ביטוח לאומי אדי", "סכום (₪)": 0},
        {"תיאור": "ביטוח לאומי נרה", "סכום (₪)": 0},
        {"תיאור": "מיוחד", "סכום (₪)": 0}
    ])
    edited_income = st.data_editor(income_data, num_rows="dynamic", key=f"income_{selected_month}")

with col2:
    st.markdown("### 🔴 הוצאות קבועות")
    fixed_exp_data = pd.DataFrame([
        {"תיאור": "הוצאות דיור", "סכום (₪)": 0},
        {"תיאור": "טלפונים ניידים", "סכום (₪)": 0},
        {"תיאור": "החזר הלוואת אשראי", "סכום (₪)": 0},
        {"תיאור": "ביטוח מכונית", "סכום (₪)": 0},
        {"תיאור": "ספוטיפאיי", "סכום (₪)": 0},
        {"תיאור": "נטפליקס", "סכום (₪)": 0}
    ])
    edited_fixed = st.data_editor(fixed_exp_data, num_rows="dynamic", key=f"fixed_{selected_month}")

st.markdown("### 🟢 הוצאות משתנות")
var_exp_data = pd.DataFrame([
    {"תיאור": "מכולת+נספרס", "סכום (₪)": 0},
    {"תיאור": "תרופות ותוספים", "סכום (₪)": 0},
    {"תיאור": "דלק", "סכום (₪)": 0},
    {"תיאור": "ספר מישל", "סכום (₪)": 0},
    {"תיאור": "גולי", "סכום (₪)": 0},
    {"תיאור": "אראלה", "סכום (₪)": 0},
    {"תיאור": "שונות", "סכום (₪)": 0},
    {"תיאור": "אחר", "סכום (₪)": 0}
])
edited_var = st.data_editor(var_exp_data, num_rows="dynamic", key=f"var_{selected_month}")

# חישובים (מספרים שלמים בלבד)
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
