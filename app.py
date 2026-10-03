import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="wide")

st.title("💰 מעקב הוצאות והכנסות אישי")

DATA_FILE = "budget_data.csv"

# הגדרת הוצאות קבועות בסיסיות שרצות איתך קדימה
FIXED_EXPENSES = [
    {"תיאור": "שכירות / משכנתא", "סכום": 5000.0, "סוג": "הוצאה קבועה"},
    {"תיאור": "ארנונה", "סכום": 600.0, "סוג": "הוצאה קבועה"},
    {"תיאור": "חשמל ומים", "סכום": 400.0, "סוג": "הוצאה קבועה"},
    {"תיאור": "אינטרנט וסלולר", "סכום": 200.0, "סוג": "הוצאה קבועה"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df_initial = pd.DataFrame(FIXED_EXPENSES)
        df_initial.to_csv(DATA_FILE, index=False)
        return df_initial

df = load_data()

# פונקציית צביעה לשורות בטבלה
def color_rows(row):
    if row["סוג"] == "הוצאה קבועה":
        return ['color: #d9534f; font-weight: bold'] * len(row)  # אדום
    elif row["סוג"] == "הוצאה משתנה":
        return ['color: #5cb85c; font-weight: bold'] * len(row)  # ירוק
    elif row["סוג"] == "הכנסה":
        return ['color: #0275d8; font-weight: bold'] * len(row)  # כחול
    return [''] * len(row)

# טופס להוספת תנועה חדשה
st.subheader("➕ הוספת תנועה חדשה")
with st.form("budget_form", clear_on_submit=True):
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        description = st.text_input("תיאור (למשל: סופרמרקט, משכורת)")
    with col_f2:
        amount = st.number_input("סכום (ש\"ח)", value=0.0, step=10.0)
    with col_f3:
        trans_type = st.selectbox("סוג תנועה", ["הוצאה משתנה", "הוצאה קבועה", "הכנסה"])
        
    submitted = st.form_submit_button("הוסף לרשימה")

    if submitted and description:
        new_row = pd.DataFrame([{"תיאור": description, "סכום": amount, "סוג": trans_type}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"נוסף בהצלחה: {description} בסך {amount} ₪ ({trans_type})")
        st.rerun()

st.divider()

# חלוקה לשני טורים: הכנסות והוצאות
st.subheader("📊 סיכום חודשי לפי טורים")

col_left, col_right = st.columns(2)

# --- טור ימין: הכנסות ---
with col_right:
    st.markdown("### 📥 הכנסות")
    df_income = df[df["סוג"] == "הכנסה"]
    if not df_income.empty:
        styled_income = df_income[["תיאור", "סכום"]].style.apply(color_rows, axis=1)
        st.dataframe(styled_income, use_container_width=True, hide_index=True)
        total_income = df_income["סכום"].sum()
        st.metric("סך הכל הכנסות", f"{total_income:,.2f} ₪")
    else:
        st.info("אין עדיין הכנסות רשומות.")

# --- טור שמאל: הוצאות (קבועות ומשתנות) ---
with col_left:
    st.markdown("### 📤 הוצאות (קבועות באדום, משתנות בירוק)")
    df_expense = df[df["סוג"].isin(["הוצאה קבועה", "הוצאה משתנה", "הוצאה"])]
    if not df_expense.empty:
        styled_expense = df_expense[["תיאור", "סכום", "סוג"]].style.apply(color_rows, axis=1)
        st.dataframe(styled_expense, use_container_width=True, hide_index=True)
        total_expense = df_expense["סכום"].sum()
        st.metric("📦 סך הכל הוצאות כלליות", f"{total_expense:,.2f} ₪")
    else:
        st.info("אין עדיין הוצאות רשומות.")

st.divider()

# --- אזור מחיקת שורה ספציפית ---
st.subheader("🗑️ מחיקת שורה / תנועה")
if not df.empty:
    row_to_delete = st.selectbox("בחר תנועה למחיקה לפי התיאור שלה:", [None] + list(df["תיאור"].unique()))
    
    if row_to_delete:
        if st.button("מחק את התנועה הנבחרת"):
            df = df[df["תיאור"] != row_to_delete]
            df.to_csv(DATA_FILE, index=False)
            st.success(f"התנועה '{row_to_delete}' נמחקה בהצלחה!")
            st.rerun()

if st.button("איפוס כל הנתונים וחזרה להוצאות הקבועות הבסיסיות"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.rerun()
