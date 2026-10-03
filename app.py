import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="centered")

st.title("💰 מעקב הוצאות והכנסות אישי")
st.write("ברוך הבא לאפליקציית ניהול התקציב שלך!")

DATA_FILE = "budget_data.csv"

# טעינת הנתונים הקיימים או יצירת רשימה ריקה
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["תיאור", "סכום", "סוג"])

df = load_data()

# טופס להוספת הוצאה/הכנסה
st.subheader("הוספת תנועה חדשה")
with st.form("budget_form", clear_on_submit=True):
    description = st.text_input("תיאור (למשל: סופרמרקט, משכורת)")
    amount = st.number_input("סכום (ש\"ח)", value=0.0, step=10.0)
    trans_type = st.selectbox("סוג תנועה", ["הוצאה", "הכנסה"])
    submitted = st.form_submit_button("הוסף לרשימה")

    if submitted and description:
        new_row = pd.DataFrame([{"תיאור": description, "סכום": amount, "סוג": trans_type}])
        df = pd.concat([df, new_row], ignore_index=True)
        # שמירה לקובץ מקומי (שמתעדכן גם בגיטהאב או נשמר בשרת)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"נוסף בהצלחה: {description} בסך {amount} ש\"ח ({trans_type})")
        st.rerun()

st.divider()

# תמונה כללית של החודש
st.subheader("📊 התמונה הכללית של החודש")

if not df.empty:
    # חישוב סיכומים
    total_income = df[df["סוג"] == "הכנסה"]["סכום"].sum()
    total_expense = df[df["סוג"] == "הוצאה"]["סכום"].sum()
    balance = total_income - total_expense
    
    # הצגת מדדים ב-3 עמודות
    col1, col2, col3 = st.columns(3)
    col1.metric("סך הכנסות", f"{total_income:,.2f} ₪")
    col2.metric("סך הוצאות", f"{total_expense:,.2f} ₪")
    col3.metric("מאזן סופי", f"{balance:,.2f} ₪")
    
    st.markdown("### 📝 פירוט התנועות")
    st.dataframe(df, use_container_width=True)
    
    # אפשרות מחיקת נתונים או איפוס במידת הצורך
    if st.button("מחק את כל הנתונים"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()
else:
    st.info("עדיין לא הוזנו תנועות. הוסף תנועה בטופס למעלה!")
