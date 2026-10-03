import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="wide")

st.title("💰 מעקב הוצאות והכנסות אישי")

DATA_FILE = "budget_data.csv"

# ברירת מחדל ראשונית רק אם הקובץ ריק לחלוטין
INITIAL_FIXED = [
    {"חודש": "אוקטובר 2026", "תיאור": "שכירות / משכנתא", "סכום": 5000, "סוג": "הוצאה קבועה"},
    {"חודש": "אוקטובר 2026", "תיאור": "ארנונה", "סכום": 600, "סוג": "הוצאה קבועה"},
    {"חודש": "אוקטובר 2026", "תיאור": "חשמל ומים", "סכום": 400, "סוג": "הוצאה קבועה"},
    {"חודש": "אוקטובר 2026", "תיאור": "אינטרנט וסלולר", "סכום": 200, "סוג": "הוצאה קבועה"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "חודש" not in df.columns or "סוג" not in df.columns:
                os.remove(DATA_FILE)
                return pd.DataFrame(INITIAL_FIXED)
            return df
        except Exception:
            os.remove(DATA_FILE)
            return pd.DataFrame(INITIAL_FIXED)
    else:
        df_initial = pd.DataFrame(INITIAL_FIXED)
        df_initial.to_csv(DATA_FILE, index=False)
        return df_initial

df = load_data()

# בחירת חודש בראש העמוד
st.subheader("📅 בחירת חודש לניהול")
available_months = list(df["חודש"].unique()) if not df.empty and "חודש" in df.columns else ["אוקטובר 2026"]
selected_month = st.selectbox("בחר חודש:", ["אוקטובר 2026", "נובמבר 2026", "דצמבר 2026", "ינואר 2027"] + [m for m in available_months if m not in ["אוקטובר 2026", "נובמבר 2026", "דצמבר 2026", "ינואר 2027"]])

# בדיקה אוטומטית: אם לחודש הנבחר אין עדיין הוצאות קבועות, ניקח את ההוצאות הקבועות מכל חודש קיים (או מהחודש הראשון) ונעתיק אותן לכאן
current_month_check = df[df["חודש"] == selected_month]
if current_month_check[current_month_check["סוג"] == "הוצאה קבועה"].empty:
    # מחפש את ההוצאות הקבועות שקיימות במערכת (למשל מאוקטובר או מה שהמשתמש הוסיף)
    existing_fixed = df[df["סוג"] == "הוצאה קבועה"]
    if not existing_fixed.empty:
        # לוקחים את רשימת ההוצאות הקבועות הייחודיות (לפי תיאור וסכום) כדי לא ליצור כפילויות מיותרות
        unique_fixed = existing_fixed[["תיאור", "סכום", "סוג"]].drop_duplicates()
        new_fixed_rows = []
        for _, row in unique_fixed.iterrows():
            new_fixed_rows.append({
                "חודש": selected_month,
                "תיאור": row["תיאור"],
                "סכום": row["סכום"],
                "סוג": "הוצאה קבועה"
            })
        if new_fixed_rows:
            df = pd.concat([df, pd.DataFrame(new_fixed_rows)], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

st.divider()

# פונקציית צביעה לשורות בטבלה
def color_rows(row):
    trans_type = row.get("סוג", "")
    if trans_type == "הוצאה קבועה":
        return ['color: #d9534f; font-weight: bold'] * len(row)  # אדום
    elif trans_type == "הוצאה משתנה":
        return ['color: #5cb85c; font-weight: bold'] * len(row)  # ירוק
    elif trans_type == "הכנסה":
        return ['color: #0275d8; font-weight: bold'] * len(row)  # כחול
    return [''] * len(row)

# טופס להוספת תנועה חדשה לחודש הנבחר
st.subheader(f"➕ הוספת תנועה חדשה עבור: {selected_month}")
with st.form("budget_form", clear_on_submit=True):
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        description = st.text_input("תיאור (למשל: סופרמרקט, משכורת)")
    with col_f2:
        amount = st.number_input("סכום (ש\"ח)", value=0, step=10, format="%d")
    with col_f3:
        trans_type = st.selectbox("סוג תנועה", ["הוצאה משתנה", "הוצאה קבועה", "הכנסה"])
        
    submitted = st.form_submit_button("הוסף לרשימה")

    if submitted and description:
        new_row = pd.DataFrame([{"חודש": selected_month, "תיאור": description, "סכום": int(amount), "סוג": trans_type}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"נוסף בהצלחה ל-{selected_month}: {description} בסך {int(amount)} ₪")
        st.rerun()

st.divider()

# סינון הנתונים לפי החודש הנבחר בלבד
df_current_month = df[df["חודש"] == selected_month]

st.subheader(f"📊 סיכום חודשי עבור {selected_month}")

col_left, col_right = st.columns(2)

# --- טור ימין: הכנסות ---
with col_right:
    st.markdown("### 📥 הכנסות")
    df_income = df_current_month[df_current_month["סוג"] == "הכנסה"]
    if not df_income.empty:
        df_income_display = df_income[["תיאור", "סכום", "סוג"]].copy()
        df_income_display["סכום"] = df_income_display["סכום"].apply(lambda x: f"{int(x):,} ₪")
        styled_income = df_income_display.style.apply(color_rows, axis=1)
        st.dataframe(styled_income, use_container_width=True, hide_index=True, column_config={"סוג": None})
        total_income = int(df_income["סכום"].sum())
        st.metric("סך הכל הכנסות", f"{total_income:,} ₪")
    else:
        st.info(f"אין עדיין הכנסות רשומות לחודש {selected_month}.")

# --- טור שמאל: הוצאות ---
with col_left:
    st.markdown("### 📤 הוצאות (קבועות באדום, משתנות בירוק)")
    df_expense = df_current_month[df_current_month["סוג"].isin(["הוצאה קבועה", "הוצאה משתנה", "הוצאה"])]
    if not df_expense.empty:
        df_expense_display = df_expense[["תיאור", "סכום", "סוג"]].copy()
        df_expense_display["סכום"] = df_expense_display["סכום"].apply(lambda x: f"{int(x):,} ₪")
        styled_expense = df_expense_display.style.apply(color_rows, axis=1)
        st.dataframe(styled_expense, use_container_width=True, hide_index=True)
        total_expense = int(df_expense["סכום"].sum())
        st.metric("📦 סך הכל הוצאות כלליות", f"{total_expense:,} ₪")
    else:
        st.info(f"אין עדיין הוצאות רשומות לחודש {selected_month}.")

st.divider()

# --- אזור מחיקת שורה מהחודש הנבחר ---
st.subheader("🗑️ מחיקת שורה / תנועה מהחודש הנבחר")
if not df_current_month.empty:
    row_to_delete = st.selectbox("בחר תנועה למחיקה:", [None] + list(df_current_month["תיאור"].unique()))
    
    if row_to_delete:
        if st.button("מחק את התנועה הנבחרת"):
            df = df[~((df["חודש"] == selected_month) & (df["תיאור"] == row_to_delete))]
            df.to_csv(DATA_FILE, index=False)
            st.success(f"התנועה '{row_to_delete}' נמחקה בהצלחה מ-{selected_month}!")
            st.rerun()

if st.button("איפוס כל הנתונים במערכת"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.rerun()

