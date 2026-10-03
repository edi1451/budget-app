import streamlit as st
import pandas as pd

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="wide")

st.title("💰 מעקב הוצאות והכנסות אישי")

# אתחול הזיכרון הפנימי של האפליקציה (בלי קבצים חיצוניים שנתקעים)
if "budget_data" not in st.session_state:
    st.session_state.budget_data = pd.DataFrame(columns=["חודש", "תיאור", "סכום", "סוג"])

df = st.session_state.budget_data

# כפתור איפוס מהיר בצד
if st.sidebar.button("🗑️ איפוס מלא של כל הנתונים"):
    st.session_state.budget_data = pd.DataFrame(columns=["חודש", "תיאור", "סכום", "סוג"])
    st.rerun()

# בחירת חודש בראש העמוד
st.subheader("📅 בחירת חודש לניהול")
existing_months = list(df["חודש"].unique()) if not df.empty else []
default_months = ["אוקטובר 2026", "נובמבר 2026", "דצמבר 2026", "ינואר 2027"]
all_months_list = default_months + [m for m in existing_months if m not in default_months]

selected_month = st.selectbox("בחר חודש:", all_months_list)

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
        description = st.text_input("תיאור (למשל: שכירות, סופר, משכורת)")
    with col_f2:
        amount = st.number_input("סכום (ש\"ח)", value=0, step=10, format="%d")
    with col_f3:
        trans_type = st.selectbox("סוג תנועה", ["הוצאה קבועה", "הוצאה משתנה", "הכנסה"])
        
    submitted = st.form_submit_button("הוסף לרשימה")

    if submitted and description:
        new_row = pd.DataFrame([{"חודש": selected_month, "תיאור": description, "סכום": int(amount), "סוג": trans_type}])
        st.session_state.budget_data = pd.concat([st.session_state.budget_data, new_row], ignore_index=True)
        st.success(f"נוסף בהצלחה ל-{selected_month}: {description} בסך {int(amount)} ₪")
        st.rerun()

# כפתור נוח להעתקת ההוצאות הקבועות שהמשתמש עצמו הגדיר
if existing_months:
    with st.expander("📋 העתקת ההוצאות הקבועות שלך מחודש קודם"):
        source_month = st.selectbox("בחר חודש לקחת ממנו הוצאות קבועות:", [m for m in existing_months if m != selected_month])
        if source_month and st.button("📋 העתק את ההוצאות הקבועות שלי לחודש זה"):
            user_fixed = df[(df["חודש"] == source_month) & (df["סוג"] == "הוצאה קבועה")]
            if not user_fixed.empty:
                current_fixed_desc = df[(df["חודש"] == selected_month) & (df["סוג"] == "הוצאה קבועה")]["תיאור"].values
                rows_to_add = []
                for _, r in user_fixed.iterrows():
                    if r["תיאור"] not in current_fixed_desc:
                        rows_to_add.append({
                            "חודש": selected_month,
                            "תיאור": r["תיאור"],
                            "סכום": int(r["סכום"]),
                            "סוג": "הוצאה קבועה"
                        })
                if rows_to_add:
                    st.session_state.budget_data = pd.concat([st.session_state.budget_data, pd.DataFrame(rows_to_add)], ignore_index=True)
                    st.success("ההוצאות הקבועות שלך הועתקו בהצלחה בדיוק כפי שהגדרת!")
                    st.rerun()
                else:
                    st.warning("ההוצאות הקבועות האלו כבר קיימות בחודש הנבחר.")
            else:
                st.info("אין הוצאות קבועות רשומות בחודש שבחרת.")

st.divider()

# סינון הנתונים לפי החודש הנבחר בלבד
df_current_month = st.session_state.budget_data[st.session_state.budget_data["חודש"] == selected_month] if not st.session_state.budget_data.empty else pd.DataFrame()

st.subheader(f"📊 סיכום חודשי עבור {selected_month}")

col_left, col_right = st.columns(2)

# --- טור ימין: הכנסות ---
with col_right:
    st.markdown("### 📥 הכנסות")
    df_income = df_current_month[df_current_month["סוג"] == "הכנסה"] if not df_current_month.empty else pd.DataFrame()
    if not df_income.empty:
        df_income_display = df_income[["תיאור", "סכום"]].copy()
        df_income_display["סכום"] = df_income_display["סכום"].apply(lambda x: f"{int(x):,} ₪")
        st.dataframe(df_income_display, use_container_width=True, hide_index=True)
        total_income = int(df_income["סכום"].sum())
        st.metric("סך הכל הכנסות", f"{total_income:,} ₪")
    else:
        st.info(f"אין עדיין הכנסות רשומות לחודש {selected_month}.")

# --- טור שמאל: הוצאות ---
with col_left:
    st.markdown("### 📤 הוצאות (קבועות באדום, משתנות בירוק)")
    df_expense = df_current_month[df_current_month["סוג"].isin(["הוצאה קבועה", "הוצאה משתנה"])] if not df_current_month.empty else pd.DataFrame()
    if not df_expense.empty:
        df_expense_display = df_expense[["תיאור", "סכום", "סוג"]].copy()
        df_expense_display["סכום"] = df_expense_display["סכום"].apply(lambda x: f"{int(x):,} ₪")
        styled_expense = df_expense_display.style.apply(color_rows, axis=1)
        st.dataframe(styled_expense, use_container_width=True, hide_index=True, column_config={"סוג": None})
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
            st.session_state.budget_data = st.session_state.budget_data[
                ~((st.session_state.budget_data["חודש"] == selected_month) & (st.session_state.budget_data["תיאור"] == row_to_delete))
            ]
            st.success(f"התנועה '{row_to_delete}' נמחקה בהצלחה!")
            st.rerun()
