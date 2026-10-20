import streamlit as st
import pandas as pd
from datetime import datetime
import json
import re
import altair as alt

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
    .stDataFrame, div[data-testid="stDataEditor"] {
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 ניהול הכנסות והוצאות")

# פונקציה בטוחה לחישוב מתמטי
def safe_eval_math(expr):
    if not expr:
        return 0
    if isinstance(expr, (int, float)):
        return int(expr)
    cleaned = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', str(expr))
    if not cleaned.strip():
        return 0
    try:
        result = eval(cleaned, {"__builtins__": None}, {})
        return int(round(result))
    except Exception:
        return 0

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

# אתחול מבנה ברירת מחדל ריק
default_budget_structure = {}
for m in months:
    default_budget_structure[m] = {
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
            {"תיאור": "לוטו", "סכום (₪)": 0},
            {"תיאור": "ספר מישל", "סכום (₪)": 0},
            {"תיאור": "גולי", "סכום (₪)": 0},
            {"תיאור": "אראלה", "סכום (₪)": 0},
            {"תיאור": "שונות", "סכום (₪)": 0},
            {"תיאור": "אחר", "סכום (₪)": 0}
        ]
    }

# טיפול בהעלאת קובץ גיבוי מוקדם בסרגל הצד
st.sidebar.subheader("💾 גיבוי ושחזור נתונים")
uploaded_backup = st.sidebar.file_uploader("📤 טען קובץ גיבוי", type=["json"])

if 'budget_data' not in st.session_state:
    st.session_state.budget_data = default_budget_structure

if uploaded_backup is not None:
    try:
        loaded_data = json.load(uploaded_backup)
        if isinstance(loaded_data, dict):
            st.session_state.budget_data = loaded_data
            st.sidebar.success("הגיבוי נטען בהצלחה!")
    except Exception:
        st.sidebar.error("שגיאה בטעינת הקובץ.")

selected_month = st.sidebar.selectbox("בחר חודש", months)

# מחשבון מהיר בסרגל הצד
st.sidebar.divider()
st.sidebar.subheader("🧮 מחשבון מהיר")
calc_input = st.sidebar.text_input("הקלד תרגיל (למשל: 500+200)", "")
if calc_input:
    result = safe_eval_math(calc_input)
    st.sidebar.success(f"תוצאה: **{result:,} ₪**")

st.sidebar.divider()

# כפתור גיבוי (הורדה)
backup_json = json.dumps(st.session_state.budget_data, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="📥 הורד גיבוי נתונים",
    data=backup_json,
    file_name=f"budget_backup_{datetime.now().strftime('%Y-%m-%d')}.json",
    mime="application/json"
)

st.header(f"ניהול תקציב עבור: {selected_month}")

# וידוא שכל החודשים והקטגוריות קיימים בזיכרון
for m in months:
    if m not in st.session_state.budget_data:
        st.session_state.budget_data[m] = default_budget_structure[m]
    else:
        for cat in ["income", "fixed", "var"]:
            if cat not in st.session_state.budget_data[m]:
                st.session_state.budget_data[m][cat] = default_budget_structure[m][cat]

current_month_data = st.session_state.budget_data[selected_month]

column_configuration = {
    "תיאור": st.column_config.TextColumn("תיאור", required=True),
    "סכום (₪)": st.column_config.NumberColumn("סכום (₪)", format="%,d", default=0)
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔵 הכנסות")
    df_income = pd.DataFrame(current_month_data["income"])
    edited_income = st.data_editor(
        df_income,
        column_order=["תיאור", "סכום (₪)"],
        column_config=column_configuration,
        num_rows="dynamic",
        key=f"inc_{selected_month}"
    )
    current_month_data["income"] = edited_income.to_dict('records')

with col2:
    st.markdown("### 🔴 הוצאות קבועות")
    df_fixed = pd.DataFrame(current_month_data["fixed"])
    edited_fixed = st.data_editor(
        df_fixed,
        column_order=["תיאור", "סכום (₪)"],
        column_config=column_configuration,
        num_rows="dynamic",
        key=f"fix_{selected_month}"
    )
    current_month_data["fixed"] = edited_fixed.to_dict('records')

st.markdown("### 🟢 הוצאות משתנות")
df_var = pd.DataFrame(current_month_data["var"])
edited_var = st.data_editor(
    df_var,
    column_order=["תיאור", "סכום (₪)"],
    column_config=column_configuration,
    num_rows="dynamic",
    key=f"var_{selected_month}"
)
current_month_data["var"] = edited_var.to_dict('records')

total_income = int(pd.to_numeric(edited_income["סכום (₪)"], errors='coerce').fillna(0).sum()) if not edited_income.empty else 0
total_fixed = int(pd.to_numeric(edited_fixed["סכום (₪)"], errors='coerce').fillna(0).sum()) if not edited_fixed.empty else 0
total_var = int(pd.to_numeric(edited_var["סכום (₪)"], errors='coerce').fillna(0).sum()) if not edited_var.empty else 0

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

# גרף עם עמודות צרות יותר וללא כיתוב/אותיות מתחת
st.markdown("---")
st.subheader("📈 השוואת הכנסות מול הוצאות")

leg_col1, leg_col2, leg_col3 = st.columns(3)
leg_col1.markdown("<h4 style='color: #2980b9; margin: 0;'>🟦 הכנסות: ₪{:,}</h4>".format(total_income), unsafe_allow_html=True)
leg_col2.markdown("<h4 style='color: #c0392b; margin: 0;'>🟥 הוצאות קבועות: ₪{:,}</h4>".format(total_fixed), unsafe_allow_html=True)
leg_col3.markdown("<h4 style='color: #27ae60; margin: 0;'>🟩 הוצאות משתנות: ₪{:,}</h4>".format(total_var), unsafe_allow_html=True)

st.write("")

chart_data = pd.DataFrame([
    {"עמודה": "הכנסות", "סוג": "הכנסות", "סכום (₪)": total_income},
    {"עמודה": "הוצאות", "סוג": "הוצאות קבועות", "סכום (₪)": total_fixed},
    {"עמודה": "הוצאות", "סוג": "הוצאות משתנות", "סכום (₪)": total_var}
])

chart = alt.Chart(chart_data).mark_bar(size=45).encode(
    x=alt.X('עמודה:N', sort=["הכנסות", "הוצאות"], axis=None),
    y=alt.Y('סכום (₪):Q', title='סכום (₪)'),
    color=alt.Color('סוג:N', scale=alt.Scale(
        domain=["הכנסות", "הוצאות קבועות", "הוצאות משתנות"],
        range=["#2980b9", "#c0392b", "#27ae60"]
    ), legend=None),
    order=alt.Order('סוג:N', sort='ascending')
).properties(height=350)

st.altair_chart(chart, use_container_width=True)
