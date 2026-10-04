import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="מעקב תקציב ותזרים אישי", page_icon="💰", layout="wide")

DATA_FILE = "budget_data.csv"

# רשימת הקטגוריות הקבועות שביקשת
FIXED_CATEGORIES = [
    "יתרת פתיחה",
    "ויזה מקס",
    "ויזה כאל",
    "העברה מדגני",
    "העברה לחשבון",
    "תשלום לדנה",
    "גולי",
    "פילטיס",
    "מיגדל",
    "כלל",
    "פסגות הראל",
    "בט\"ל אדי",
    "בט\"ל נרה"
]

# טעינת הנתונים מהקובץ או יצירת טבלה ריקה
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=["חודש", "יום בחודש", "קטגוריה", "סכום"])
else:
    df = pd.DataFrame(columns=["חודש", "יום בחודש", "קטגוריה", "סכום"])

# --- תפריט ניווט בצד ---
st.sidebar.title("🧭 ניווט באפליקציה")
page = st.sidebar.radio("בחר עמוד:", ["📅 ניהול תקציב חודשי", "📈 תזרים שנתי ומצטבר"])

# כפתור איפוס מהיר בצד
if os.path.exists(DATA_FILE):
    if st.sidebar.button("🗑️ איפוס מלא של כל הנתונים"):
        os.remove(DATA_FILE)
        st.rerun()

# רשימת חודשים בסיסית עד סוף 2027 + חודשים קיימים
base_list = [
    "אוקטובר 2026", "נובמבר 2026", "דצמבר 2026",
    "ינואר 2027", "פברואר 2027", "מרץ 2027", "אפריל 2027", 
    "מאי 2027", "יוני 2027", "יולי 2027", "אוגוסט 2027", 
    "ספטמבר 2027", "אוקטובר 2027", "נובמבר 2027", "דצמבר 2027"
]

available_months = list(df["חודש"].unique()) if not df.empty and "חודש" in df.columns else []
all_months_list = []
for m in base_list + available_months:
    if m not in all_months_list:
        all_months_list.append(m)


# ==========================================
# עמוד 1: ניהול תקציב חודשי
# ==========================================
if page == "📅 ניהול תקציב חודשי":
    st.title("💰 מעקב הוצאות ותזרים חודשי")

    st.subheader("📅 בחירת חודש לניהול")
    selected_month = st.selectbox("בחר חודש:", all_months_list)

    st.divider()

    # טופס להוספת תנועה חדשה לפי התאריך (יום בחודש), קטגוריה וסכום
    st.subheader(f"➕ הוספת / עדכון נתונים עבור: {selected_month}")
    with st.form("budget_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            day_of_month = st.selectbox("יום בחודש", [2, 10, 25, 28, 30] + [d for d in range(1, 32) if d not in [2, 10, 25, 28, 30]])
        with col_f2:
            category = st.selectbox("בחר קטגוריה קבועה", FIXED_CATEGORIES)
        with col_f3:
            amount = st.number_input("סכום (ש\"ח)", value=0, step=10, format="%d")
            
        submitted = st.form_submit_button("הוסף / עדכן נתון")

        if submitted and amount != 0:
            if not df.empty and "חודש" in df.columns and "קטגוריה" in df.columns:
                existing_row = df[(df["חודש"] == selected_month) & (df["קטגוריה"] == category)]
                if not existing_row.empty:
                    df.loc[(df["חודש"] == selected_month) & (df["קטגוריה"] == category), "סכום"] += int(amount)
                    df.loc[(df["חודש"] == selected_month) & (df["קטגוריה"] == category), "יום בחודש"] = int(day_of_month)
                else:
                    new_row = pd.DataFrame([{"חודש": selected_month, "יום בחודש": int(day_of_month), "קטגוריה": category, "סכום": int(amount)}])
                    df = pd.concat([df, new_row], ignore_index=True)
            else:
                new_row = pd.DataFrame([{"חודש": selected_month, "יום בחודש": int(day_of_month), "קטגוריה": category, "סכום": int(amount)}])
                df = pd.concat([df, new_row], ignore_index=True)
                
            df.to_csv(DATA_FILE, index=False)
            st.success(f"עודכן בהצלחה ב-{selected_month} (יום {day_of_month}) עבור '{category}': {int(amount)} ₪")
            st.rerun()

    st.divider()

    # סינון הנתונים לפי החודש הנבחר בלבד ומיון לפי יום בחודש
    df_current_month = df[df["חודש"] == selected_month] if not df.empty and "חודש" in df.columns else pd.DataFrame(columns=["חודש", "יום בחודש", "קטגוריה", "סכום"])
    
    if not df_current_month.empty:
        df_current_month = df_current_month.sort_values(by="יום בחודש")

    st.subheader(f"📊 פירוט תנועות עבור {selected_month}")

    if not df_current_month.empty:
        df_display = df_current_month[["יום בחודש", "קטגוריה", "סכום"]].copy()
        df_display["סכום"] = df_display["סכום"].apply(lambda x: f"{int(x):,} ₪")
        df_display.columns = ["יום בחודש", "קטגוריה", "סכום"]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        total_sum = int(df_current_month["סכום"].sum())
        st.metric("סיכום ביניים לחודש", f"{total_sum:,} ₪")
    else:
        st.info(f"אין עדיין נתונים רשומים לחודש {selected_month}.")

    st.divider()

    # --- אזור מחיקת קטגוריה מהחודש הנבחר ---
    st.subheader("🗑 מחיקת שורה מהחודש הנבחר")
    if not df_current_month.empty:
        category_to_delete = st.selectbox("בחר קטגוריה למחיקה:", [None] + list(df_current_month["קטגוריה"].unique()))
        
        if category_to_delete:
            if st.button("מחק את השורה הנבחרת"):
                df = df[~((df["חודש"] == selected_month) & (df["קטגוריה"] == category_to_delete))]
                df.to_csv(DATA_FILE, index=False)
                st.success(f"הקטגוריה '{category_to_delete}' נמחקה בהצלחה!")
                st.rerun()


# ==========================================
# עמוד 2: תזרים שנתי ומצטבר
# ==========================================
elif page == "📈 תזרים שנתי ומצטבר":
    st.title("📈 ניהול תזרים שנתי ומצטבר")
    st.markdown("טבלה זו מרכזת את סיכומי כל החודשים לאורך תקופת המעקב.")

    if df.empty or "חודש" not in df.columns:
        st.info("עדיין אין מספיק נתונים להצגת התזרים. הזן נתונים בעמוד הניהול החודשי.")
    else:
        summary_rows = []
        for m in base_list + [x for x in available_months if x not in base_list]:
            df_m = df[df["חודש"] == m]
            if not df_m.empty:
                total_m = int(df_m["סכום"].sum())
                summary_rows.append({
                    "חודש": m,
                    "סך הכל בחודש (₪)": total_m
                })

        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            display_summary = summary_df.copy()
            display_summary["סך הכל בחודש (₪)"] = display_summary["סך הכל בחודש (₪)"].apply(lambda x: f"{x:,} ₪")

            st.dataframe(display_summary, use_container_width=True, hide_index=True)

            st.divider()
            grand_total = summary_df["סך הכל בחודש (₪)"].sum()
            st.metric("סך הכל כללי לתקופה", f"{grand_total:,} ₪")
        else:
            st.info("אין נתונים להצגה בתזרים השנתי.")
