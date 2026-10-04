import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="מעקב תקציב ותזרים אישי", page_icon="💰", layout="wide")

DATA_FILE = "budget_data.csv"

# הגדרת רשימות הקטגוריות המדויקות
INCOME_CATEGORIES = ["יתרת פתיחה", "העברה מדגני", "הכנסה נוספת"]
FIXED_EXPENSES = [
    "ויזה מקס",
    "ויזה כאל",
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
VARIABLE_EXPENSES = ["הוצאות משתנות / שוטפות", "אוכל וקניות", "בילויים ופנאי", "שונות"]

ALL_CATEGORIES = INCOME_CATEGORIES + FIXED_EXPENSES + VARIABLE_EXPENSES

# רשימת החודשים
base_list = [
    "אוקטובר 2026", "נובמבר 2026", "דצמבר 2026",
    "ינואר 2027", "פברואר 2027", "מרץ 2027", "אפריל 2027", 
    "מאי 2027", "יוני 2027", "יולי 2027", "אוגוסט 2027", 
    "ספטמבר 2027", "אוקטובר 2027", "נובמבר 2027", "דצמבר 2027"
]

# פונקציית עזר לסוג קטגוריה
def get_category_type(cat):
    if cat in INCOME_CATEGORIES:
        return "הכנסה"
    elif cat in FIXED_EXPENSES:
        return "הוצאה קבועה"
    else:
        return "הוצאה משתנה"

# טעינת נתונים או יצירת מבנה התחלתי
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=["חודש", "יום בחודש", "קטגוריה", "סכום", "סוג"])
else:
    df = pd.DataFrame(columns=["חודש", "יום בחודש", "קטגוריה", "סכום", "סוג"])

# וידוא עמודות תקינות
if "חודש" not in df.columns: df["חודש"] = "אוקטובר 2026"
if "יום בחודש" not in df.columns: df["יום בחודש"] = 2
if "קטגוריה" not in df.columns: df["קטגוריה"] = "לא ידוע"
if "סכום" not in df.columns: df["סכום"] = 0
if "סוג" not in df.columns:
    df["סוג"] = df["קטגוריה"].apply(get_category_type)

# --- תפריט ניווט בצד ---
st.sidebar.title("🧭 ניווט באפליקציה")
page = st.sidebar.radio("בחר עמוד:", ["📅 ניהול תקציב חודשי", "📈 דף תזרים שנתי"])

if os.path.exists(DATA_FILE):
    if st.sidebar.button("🗑️ איפוס מלא של כל הנתונים"):
        os.remove(DATA_FILE)
        st.rerun()

available_months = list(df["חודש"].unique()) if not df.empty and "חודש" in df.columns else []
all_months_list = []
for m in base_list + available_months:
    if m not in all_months_list:
        all_months_list.append(m)


# ==========================================
# עמוד 1: ניהול תקציב חודשי
# ==========================================
if page == "📅 ניהול תקציב חודשי":
    st.title("💰 מעקב תקציב חודשי")

    selected_month = st.selectbox("בחר חודש:", all_months_list)

    st.divider()

    # מנגנון העברת הוצאות קבועות מחודש קודם או אתחול בסיסי
    # בדיקה האם קיימות הוצאות קבועות לחודש הנבחר, ואם לא - ננסה להעתיק מחודש קודם או ליצור ברירת מחדל
    df_current = df[df["חודש"] == selected_month] if not df.empty else pd.DataFrame()
    
    if df_current.empty and len(all_months_list) > 1:
        # מציאת חודש קודם ברשימה
        curr_idx = all_months_list.index(selected_month)
        if curr_idx > 0:
            prev_month = all_months_list[curr_idx - 1]
            df_prev_fixed = df[(df["חודש"] == prev_month) & (df["סוג"] == "הוצאה קבועה")]
            if not df_prev_fixed.empty:
                # שכפול ההוצאות הקבועות לחודש הנוכחי
                copied_rows = df_prev_fixed.copy()
                copied_rows["חודש"] = selected_month
                df = pd.concat([df, copied_rows], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                df_current = df[df["חודש"] == selected_month]

    # טופס להוספת / עדכון תנועה
    st.subheader(f"➕ הוספת / עדכון נתונים עבור: {selected_month}")
    with st.form("budget_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            default_days = [2, 10, 25, 28, 30]
            day_of_month = st.selectbox("יום בחודש", default_days + [d for d in range(1, 32) if d not in default_days])
        with col_f2:
            category = st.selectbox("בחר קטגוריה", ALL_CATEGORIES)
        with col_f3:
            amount = st.number_input("סכום (₪ - מספר שלם)", value=0, step=10, format="%d")
            
        submitted = st.form_submit_button("הוסף / עדכן נתון")

        if submitted and amount != 0:
            trans_type = get_category_type(category)
            
            if not df.empty and "חודש" in df.columns and "קטגוריה" in df.columns:
                existing_row = df[(df["חודש"] == selected_month) & (df["קטגוריה"] == category)]
                if not existing_row.empty:
                    df.loc[(df["חודש"] == selected_month) & (df["קטגוריה"] == category), "סכום"] = int(amount)
                    df.loc[(df["חודש"] == selected_month) & (df["קטגוריה"] == category), "יום בחודש"] = int(day_of_month)
                    df.loc[(df["חודש"] == selected_month) & (df["קטגוריה"] == category), "סוג"] = trans_type
                else:
                    new_row = pd.DataFrame([{
                        "חודש": selected_month, 
                        "יום בחודש": int(day_of_month), 
                        "קטגוריה": category, 
                        "סכום": int(amount),
                        "סוג": trans_type
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
            else:
                new_row = pd.DataFrame([{
                    "חודש": selected_month, 
                    "יום בחודש": int(day_of_month), 
                    "קטגוריה": category, 
                    "סכום": int(amount),
                    "סוג": trans_type
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                
            df.to_csv(DATA_FILE, index=False)
            st.success(f"עודכן בהצלחה ב-{selected_month} עבור '{category}': {int(amount):,} ₪")
            st.rerun()

    st.divider()

    # רענון הנתונים לחודש הנבחר לאחר עדכונים
    df_current_month = df[df["חודש"] == selected_month] if not df.empty and "חודש" in df.columns else pd.DataFrame()
    if not df_current_month.empty and "יום בחודש" in df_current_month.columns:
        df_current_month = df_current_month.sort_values(by="יום בחודש")

    st.subheader(f"📊 פירוט תקציב עבור {selected_month}")

    # תצוגה לפי 3 קטגוריות עם צבעים ייעודיים: הכנסות בכחול, הוצאות קבועות באדום, הוצאות משתנות בירוק
    col1, col2, col3 = st.columns(3)

    total_inc = 0
    total_fixed = 0
    total_var = 0

    with col1:
        st.markdown("<h3 style='color: blue;'>🔵 הכנסות</h3>", unsafe_allow_html=True)
        df_inc = df_current_month[df_current_month["סוג"] == "הכנסה"] if not df_current_month.empty else pd.DataFrame()
        if not df_inc.empty:
            d_disp = df_inc[["יום בחודש", "קטגוריה", "סכום"]].copy()
            d_disp["סכום"] = d_disp["סכום"].apply(lambda x: f"{int(x):,} ₪")
            st.dataframe(d_disp, use_container_width=True, hide_index=True)
            total_inc = int(df_inc["סכום"].sum())
        st.metric("סך הכנסות", f"{total_inc:,} ₪")

    with col2:
        st.markdown("<h3 style='color: red;'>🔴 הוצאות קבועות</h3>", unsafe_allow_html=True)
        df_fix = df_current_month[df_current_month["סוג"] == "הוצאה קבועה"] if not df_current_month.empty else pd.DataFrame()
        if not df_fix.empty:
            d_disp = df_fix[["יום בחודש", "קטגוריה", "סכום"]].copy()
            d_disp["סכום"] = d_disp["סכום"].apply(lambda x: f"{int(x):,} ₪")
            st.dataframe(d_disp, use_container_width=True, hide_index=True)
            total_fixed = int(df_fix["סכום"].sum())
        st.metric("סך הוצאות קבועות", f"{total_fixed:,} ₪")

    with col3:
        st.markdown("<h3 style='color: green;'>🟢 הוצאות משתנות</h3>", unsafe_allow_html=True)
        df_var = df_current_month[df_current_month["סוג"] == "הוצאה משתנה"] if not df_current_month.empty else pd.DataFrame()
        if not df_var.empty:
            d_disp = df_var[["יום בחודש", "קטגוריה", "סכום"]].copy()
            d_disp["סכום"] = d_disp["סכום"].apply(lambda x: f"{int(x):,} ₪")
            st.dataframe(d_disp, use_container_width=True, hide_index=True)
            total_var = int(df_var["סכום"].sum())
        st.metric("סך הוצאות משתנות", f"{total_var:,} ₪")

    st.divider()

    # שורה נוספת: הכנסות פחות הוצאות = העברה לחיסכון / יתרה
    savings_transfer = total_inc - (total_fixed + total_var)
    st.subheader("🪙 שורה נוספת: הכנסות פחות הוצאות (העברה לחיסכון)")
    if savings_transfer >= 0:
        st.success(f"העברה לחיסכון = **{savings_transfer:,} ₪**")
    else:
        st.error(f"גירעון = **{savings_transfer:,} ₪**")

    st.divider()

    # מחיקת שורה
    st.subheader("🗑 מחיקת שורה מהחודש הנבחר")
    if not df_current_month.empty:
        cat_to_del = st.selectbox("בחר קטגוריה למחיקה:", [None] + list(df_current_month["קטגוריה"].unique()))
        if cat_to_del:
            if st.button("מחק את השורה הנבחרת"):
                df = df[~((df["חודש"] == selected_month) & (df["קטגוריה"] == cat_to_del))]
                df.to_csv(DATA_FILE, index=False)
                st.success(f"הקטגוריה '{cat_to_del}' נמחקה בהצלחה!")
                st.rerun()


# ==========================================
# עמוד 2: דף תזרים שנתי
# ==========================================
elif page == "📈 דף תזרים שנתי":
    st.title("📈 דף תזרים שנתי ומצטבר")
    st.markdown("עמוד זה מציג את סיכום התזרים והנתונים המצטברים לאורך כל החודשים.")

    if df.empty or "חודש" not in df.columns:
        st.info("עדיין אין נתונים להצגת התזרים השנתי.")
    else:
        summary_rows = []
        for m in base_list + [x for x in available_months if x not in base_list]:
            df_m = df[df["חודש"] == m]
            if not df_m.empty:
                inc_m = int(df_m[df_m["סוג"] == "הכנסה"]["סכום"].sum()) if "סוג" in df_m.columns else 0
                fix_m = int(df_m[df_m["סוג"] == "הוצאה קבועה"]["סכום"].sum()) if "סוג" in df_m.columns else 0
                var_m = int(df_m[df_m["סוג"] == "הוצאה משתנה"]["סכום"].sum()) if "סוג" in df_m.columns else 0
                net_m = inc_m - (fix_m + var_m)
                
                summary_rows.append({
                    "חודש": m,
                    "סך הכנסות (₪)": inc_m,
                    "הוצאות קבועות (₪)": fix_m,
                    "הוצאות משתנות (₪)": var_m,
                    "העברה לחיסכון / יתרה (₪)": net_m
                })

        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            display_summary = summary_df.copy()
            display_summary["סך הכנסות (₪)"] = display_summary["סך הכנסות (₪)"].apply(lambda x: f"{x:,} ₪")
            display_summary["הוצאות קבועות (₪)"] = display_summary["הוצאות קבועות (₪)"].apply(lambda x: f"{x:,} ₪")
            display_summary["הוצאות משתנות (₪)"] = display_summary["הוצאות משתנות (₪)"].apply(lambda x: f"{x:,} ₪")
            display_summary["העברה לחיסכון / יתרה (₪)"] = display_summary["העברה לחיסכון / יתרה (₪)"].apply(lambda x: f"{x:,} ₪")

            st.dataframe(display_summary, use_container_width=True, hide_index=True)
        else:
            st.info("אין נתונים להצגה בתזרים.")
