import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ניהול תקציב והוצאות", page_icon="💰", layout="wide")

DATA_FILE = "budget_simple_data.csv"

# הגדרת ההכנסות וההוצאות המדויקות
INCOME_LIST = [
    "מגדל",
    "כלל",
    "הראל",
    "העברה מדגני",
    "העברה לחשבון",
    "הכנסה מיוחדת"
]

FIXED_EXPENSES = [
    "דיור",
    "הלוואת אשראי",
    "ביטוח רכב",
    "טלפונים ניידים",
    "נטפליקס",
    "ספוטיפיי"
]

VARIABLE_EXPENSES = [
    "תרופות ותוספים",
    "דלק",
    "גולי",
    "פילטיס",
    "ספר-מישל",
    "מכולת",
    "לוטו",
    "שונות",
    "אחר"
]

MONTHS_LIST = [
    "דצמבר 2026", "נובמבר 2026", "אוקטובר 2026",
    "אפריל 2027", "מרץ 2027", "פברואר 2027", "ינואר 2027",
    "אוגוסט 2027", "יולי 2027", "יוני 2027", "מאי 2027",
    "דצמבר 2027", "נובמבר 2027", "אוקטובר 2027", "ספטמבר 2027"
]

def get_type(cat):
    if cat in INCOME_LIST:
        return "הכנסה"
    elif cat in FIXED_EXPENSES:
        return "הוצאה קבועה"
    else:
        return "הוצאה משתנה"

# טעינת קובץ נתונים קים או יצירת חדש
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
        if "יום" in df.columns:
            df = df.drop(columns=["יום"])
    except Exception:
        df = pd.DataFrame(columns=["סוג", "סכום", "קטגוריה", "חודש"])
else:
    df = pd.DataFrame(columns=["סוג", "סכום", "קטגוריה", "חודש"])

# סיידבר: ניהול גיבוי ושמירת נתונים
st.sidebar.title("⚙️ ניהול וגיבוי")

# ייצוא/הורדת גיבוי
if not df.empty:
    csv_data = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button(
        label="📥 הורד קובץ גיבוי (CSV)",
        data=csv_data,
        file_name="budget_backup.csv",
        mime="text/csv"
    )

# ייבוא/טעינת גיבוי
uploaded_backup = st.sidebar.file_uploader("📤 טען קובץ גיבוי", type=["csv"])
if uploaded_backup is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_backup)
        df_uploaded.to_csv(DATA_FILE, index=False)
        st.sidebar.success("הנתונים נטענו בהצלחה!")
        st.rerun()
    except Exception as e:
        st.sidebar.error("שגיאה בטעינת הקובץ")

st.title("💰 ניהול הכנסות והוצאות")

selected_month = st.selectbox("בחר חודש:", MONTHS_LIST)

# העברה אוטומטית של הוצאות קבועות מחודש קודם
df_m = df[df["חודש"] == selected_month] if not df.empty else pd.DataFrame()
if df_m.empty and MONTHS_LIST.index(selected_month) > 0:
    prev_month = MONTHS_LIST[MONTHS_LIST.index(selected_month) - 1]
    df_prev_fixed = df[(df["חודש"] == prev_month) & (df["סוג"] == "הוצאה קבועה")]
    if not df_prev_fixed.empty:
        copied = df_prev_fixed.copy()
        copied["חודש"] = selected_month
        df = pd.concat([df, copied], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        df_m = df 
