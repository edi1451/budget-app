import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ניהול תקציב והוצאות", page_icon="💰", layout="wide")

DATA_FILE = "budget_simple_data.csv"

# הגדרת הרשימות המדויקות כולל מכולת בהוצאות המשתנות
INCOME_LIST = ["העברה מדגני 1", "העברה מדגני 2", "הכנסה נוספת"]

FIXED_EXPENSES = [
    "דיור",
    "הלוואת אשראי",
    "ביטוח רכב",
    "טלפונים ניידים",
    "נטפליקס",
    "ספוטיפאיי"
]

VARIABLE_EXPENSES = [
    "תרופות ותוספים",
    "דלק",
    "גולי",
    "פילטיס",
    "ספר-מישל",
    "מכולת",
    "שונות",
    "אחר"
]

MONTHS_LIST = [
    "אוקטובר 2026", "נובמבר 2026", "דצמבר 2026",
    "ינואר 2027", "פברואר 2027", "מרץ 2027", "אפריל 2027",
    "מאי 2027", "יוני 2027", "יולי 2027", "אוגוסט 2027",
    "ספטמבר 2027", "אוקטובר 2027", "נובמבר 2027", "דצמבר 2027"
]

def get_type(cat):
    if cat in INCOME_LIST:
        return "הכנסה"
    elif cat in FIXED_EXPENSES:
        return "הוצאה קבועה"
    else:
        return "הוצאה משתנה"

# טעינה או יצירה של קובץ הנתונים
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
    except:
        df = pd.DataFrame(columns=["חודש", "יום", "קטגוריה", "סכום", "סוג"])
else:
    df = pd.DataFrame(columns=["חודש", "יום", "קטגוריה", "סכום", "סוג"])

# כפתור איפוס בצד
if os.path.exists(DATA_FILE):
    if st.sidebar.button("🗑️ איפוס מלא"):
        os.remove(DATA_FILE)
        st.rerun()

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
        df_m = df[df["חודש"] == selected_month]

# טופס הוספה / עדכון
st.subheader(f"הוספת / עדכון נתון ל-{selected_month}")
with st.form("add_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        day = st.selectbox("יום בחודש", list(range(1, 32)), index=1)
    with c2:
        cat = st.selectbox("בחר פריט (הכנסה / הוצאה)", INCOME_LIST + FIXED_EXPENSES + VARIABLE_EXPENSES)
    with c3:
        amt = st.number_input("סכום (₪ - מספר שלם)", value=0, step=1, format="%d")
        
    submitted = st.form_submit_button("שמור נתון")
    
    if submitted:
        stype = get_type(cat)
        if not df.empty:
            df = df[~((df["חודש"] == selected_month) & (df["קטגוריה"] == cat))]
        
        new_row = pd.DataFrame([{"חודש": selected_month, "יום": int(day), "קטגוריה": cat, "סכום": int(amt), "סוג": stype}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("הנתון נשמר בהצלחה!")
        st.rerun()

st.divider()

# רענון נתוני החודש
df_current = df[df["חודש"] == selected_month] if not df.empty and "חודש" in df.columns else pd.DataFrame()
if not df_current.empty:
    df_current = df_current.sort_values(by="יום")

# הצגה ב-3 עמודות עם הצבעים המבוקשים: הכנסות בכחול, הוצאות קבועות באדום, הוצאות משתנות בירוק
col_inc, col_fix, col_var = st.columns(3)

tot_inc = 0
tot_fix = 0
tot_var = 0

with col_inc:
    st.markdown("<h3 style='color: blue;'>🔵 הכנסות</h3>", unsafe_allow_html=True)
    df_i = df_current[df_current["סוג"] == "הכנסה"] if not df_current.empty else pd.DataFrame()
    if not df_i.empty:
        show_i = df_i[["יום", "קטגוריה", "סכום"]].copy()
        show_i["סכום"] = show_i["סכום"].apply(lambda x: f"{int(x):,} ₪")
        st.dataframe(show_i, use_container_width=True, hide_index=True)
        tot_inc = int(df_i["סכום"].sum())
    st.metric("סך הכנסות", f"{tot_inc:,} ₪")

with col_fix:
    st.markdown("<h3 style='color: red;'>🔴 הוצאות קבועות</h3>", unsafe_allow_html=True)
    df_f = df_current[df_current["סוג"] == "הוצאה קבועה"] if not df_current.empty else pd.DataFrame()
    if not df_f.empty:
        show_f = df_f[["יום", "קטגוריה", "סכום"]].copy()
        show_f["סכום"] = show_f["סכום"].apply(lambda x: f"{int(x):,} ₪")
        st.dataframe(show_f, use_container_width=True, hide_index=True)
        tot_fix = int(df_f["סכום"].sum())
    st.metric("סך הוצאות קבועות", f"{tot_fix:,} ₪")

with col_var:
    st.markdown("<h3 style='color: green;'>🟢 הוצאות משתנות</h3>", unsafe_allow_html=True)
    df_v = df_current[df_current["סוג"] == "הוצאה משתנה"] if not df_current.empty else pd.DataFrame()
    if not df_v.empty:
        show_v = df_v[["יום", "קטגוריה", "סכום"]].copy()
        show_v["סכום"] = show_v["סכום"].apply(lambda x: f"{int(x):,} ₪")
        st.dataframe(show_v, use_container_width=True, hide_index=True)
        tot_var = int(df_v["סכום"].sum())
    st.metric("סך הוצאות משתנות", f"{tot_var:,} ₪")

st.divider()

# שורת סיכום: הכנסות פחות הוצאות = העברה לחיסכון
savings = tot_inc - (tot_fix + tot_var)
st.subheader("🪙 שורת סיכום: הכנסות פחות הוצאות (העברה לחיסכון)")
if savings >= 0:
    st.success(f"העברה לחיסכון: **{savings:,} ₪**")
else:
    st.error(f"גירעון בחודש זה: **{savings:,} ₪**")

# מחיקת פריט
if not df_current.empty:
    st.divider()
    st.subheader("🗑️ מחיקת פריט מהחודש")
    item_to_del = st.selectbox("בחר פריט למחיקה:", [None] + list(df_current["קטגוריה"].unique()))
    if item_to_del:
        if st.button("מחק פריט נבחר"):
            df = df[~((df["חודש"] == selected_month) & (df["קטגוריה"] == item_to_del))]
            df.to_csv(DATA_FILE, index=False)
            st.success("הפריט נמחק!")
            st.rerun()
