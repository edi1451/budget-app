import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="wide")

st.title("💰 מעקב הוצאות והכנסות אישי")

DATA_FILE = "budget_data.csv"

# טעינת הנתונים מהקובץ או יצירת טבלה ריקה
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=["חודש", "תיאור", "סכום", "סוג"])
else:
    df = pd.DataFrame(columns=["חודש", "תיאור", "סכום", "סוג"])

# כפתור איפוס מהיר בצד (אם תרצה למחוק הכל ולהתחיל נקי לחלוטין)
if os.path.exists(DATA_FILE):
    if st.sidebar.button("🗑️ איפוס מלא של כל הנתונים"):
        os.remove(DATA_FILE)
        st.rerun()

# הצגת חודשים עד סוף 2027 + חודשים קיימים
available_months = list(df["חודש"].unique()) if not df.empty and "חודש" in df.columns else []
base_list = [
    "אוקטובר 2026", "נובמבר 2026", "דצמבר 2026",
    "ינואר 2027", "פברואר 2027", "מרץ 2027", "אפריל 2027", 
    "מאי 2027", "יוני 2027", "יולי 2027", "אוגוסט 2027", 
    "ספטמבר 2027", "אוקטובר 2027", "נובמבר 2027", "דצמבר 2027"
]
all_months_list = []
for m in base_list + available_months:
    if m not in all_months_list:
        all_months_list.append(m)

st.subheader("📅 בחירת חודש לניהול")
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

# טופס להוספת תנועה חדשה לפי קטגוריות מובנות בעברית
st.subheader(f"➕ הוספת / עדכון סכום עבור: {selected_month}")
with st.form("budget_form", clear_on_submit=True):
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        trans_type = st.selectbox("סוג תנועה", ["הוצאה משתנה", "הוצאה קבועה", "הכנסה"])
    with col_f2:
        # קטגוריות מובנות בעברית
        if trans_type == "הוצאה קבועה":
            category = st.selectbox("בחר קטגוריה", ["שכירות / משכנתא", "ועד בית", "ארנונה", "חשמל ומים", "אינטרנט וסלולר", "ביטוחים", "ביטוח רכב", "הלוואות", "הלוואת אשראי", "אחר (קבוע)"])
        elif trans_type == "הוצאה משתנה":
            category = st.selectbox("בחר קטגוריה", ["סופרמרקט / מכולת", "ספוטיפאי", "נטפליקס", "ספר-מישל", "פילטיס", "גולי", "דלק", "טלפונים ניידים", "קופ\"ח ותרופות", "תחבורה ציבורית", "בילויים במסעדות", "קניות שוטפות", "שונות", "אחר (משתנה)"])
        else:
            category = st.selectbox("בחר קטגוריה", ["משכורת ראשית", "משכורת נוספת / פרילנס", "החזר מס / מענקים", "הכנסה אחרת"])
    with col_f3:
        amount = st.number_input("סכום להוספה (ש\"ח)", value=0, step=10, format="%d")
        
    submitted = st.form_submit_button("הוסף / עדכון סכום")

    if submitted and amount > 0:
        if not df.empty and "חודש" in df.columns and "תיאור" in df.columns:
            existing_row = df[(df["חודש"] == selected_month) & (df["תיאור"] == category) & (df["סוג"] == trans_type)]
            if not existing_row.empty:
                df.loc[(df["חודש"] == selected_month) & (df["תיאור"] == category) & (df["סוג"] == trans_type), "סכום"] += int(amount)
            else:
                new_row = pd.DataFrame([{"חודש": selected_month, "תיאור": category, "סכום": int(amount), "סוג": trans_type}])
                df = pd.concat([df, new_row], ignore_index=True)
        else:
            new_row = pd.DataFrame([{"חודש": selected_month, "תיאור": category, "סכום": int(amount), "סוג": trans_type}])
            df = pd.concat([df, new_row], ignore_index=True)
            
        df.to_csv(DATA_FILE, index=False)
        st.success(f"עודכן בהצלחה ב-{selected_month} עבור '{category}': נוספו {int(amount)} ₪")
        st.rerun()

# אזור להעתקת הוצאות קבועות מחודש קודם באישור שלך בלבד
if available_months:
    with st.expander("📋 העתקת הוצאות קבועות מחודש קודם"):
        source_month = st.selectbox("בחר חודש מקור להעתקה:", [m for m in available_months if m != selected_month])
        if source_month and st.button("העתק את ההוצאות הקבועות לחודש זה"):
            fixed_to_copy = df[(df["חודש"] == source_month) & (df["סוג"] == "הוצאה קבועה")]
            if not fixed_to_copy.empty:
                for _, r in fixed_to_copy.iterrows():
                    cat_name = r["תיאור"]
                    cat_amount = int(r["סכום"])
                    existing_target = df[(df["חודש"] == selected_month) & (df["תיאור"] == cat_name) & (df["סוג"] == "הוצאה קבועה")]
                    if existing_target.empty:
                        new_r = pd.DataFrame([{"חודש": selected_month, "תיאור": cat_name, "סכום": cat_amount, "סוג": "הוצאה קבועה"}])
                        df = pd.concat([df, new_r], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("ההוצאות הקבועות הועתקו והוזנו בהצלחה!")
                st.rerun()
            else:
                st.info("אין הוצאות קבועות רשומות בחודש שבחרת.")

st.divider()

# סינון הנתונים לפי החודש הנבחר בלבד
df_current_month = df[df["חודש"] == selected_month] if not df.empty and "חודש" in df.columns else pd.DataFrame(columns=["חודש", "תיאור", "סכום", "סוג"])

st.subheader(f"📊 סיכום חודשי עבור {selected_month}")

col_left, col_right = st.columns(2)

total_income = 0
total_expense = 0

# --- טור ימין: הכנסות ---
with col_right:
    st.markdown("### 📥 הכנסות (בכחול)")
    df_income = df_current_month[df_current_month["סוג"] == "הכנסה"] if not df_current_month.empty else pd.DataFrame()
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

# --- שורה תחתונה: חישוב העברה לחיסכון (הכנסות פחות הוצאות) ---
savings_amount = total_income - total_expense
st.subheader("🪙 סיכום סופי: הכנסות פחות הוצאות (העברה לחיסכון)")

if savings_amount >= 0:
    st.success(f"💰 סכום פנוי להעברה לחיסכון החודש: **{savings_amount:,} ₪**")
else:
    st.error(f"⚠️ גירעון החודש (הוצאות גבוהות מההכנסות): **{savings_amount:,} ₪**")

st.divider()

# --- אזור מחיקת קטגוריה מהחודש הנבחר ---
st.subheader("🗑️ מחיקת קטגוריה מהחודש הנבחר")
if not df_current_month.empty:
    category_to_delete = st.selectbox("בחר קטגוריה למחיקה:", [None] + list(df_current_month["תיאור"].unique()))
    
    if category_to_delete:
        if st.button("מחק את הקטגוריה הנבחרת"):
            df = df[~((df["חודש"] == selected_month) & (df["תיאור"] == category_to_delete))]
            df.to_csv(DATA_FILE, index=False)
            st.success(f"הקטגוריה '{category_to_delete}' נמחקה בהצלחה מהקובץ!")
            st.rerun()
