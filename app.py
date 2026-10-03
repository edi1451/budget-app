import streamlit as st
import pandas as pd

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="centered")

st.title("💰 מעקב הוצאות והכנסות אישי")
st.write("ברוך הבא לאפליקציית ניהול התקציב שלך!")

# הגדרת זיכרון זמני לשמירת התנועות באפליקציה
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# טופס להוספת הוצאה/הכנסה
st.subheader("הוספת תנועה חדשה")
with st.form("budget_form", clear_on_submit=True):
    description = st.text_input("תיאור (למשל: סופרמרקט, משכורת)")
    amount = st.number_input("סכום (ש\"ח)", value=0.0, step=10.0)
    trans_type = st.selectbox("סוג תנועה", ["הוצאה", "הכנסה"])
    submitted = st.form_submit_button("הוסף לרשימה")

    if submitted and description:
        st.session_state.transactions.append({
            "תיאור": description,
            "סכום": amount,
            "סוג": trans_type
        })
        st.success(f"נוסף בהצלחה: {description} בסך {amount} ש\"ח ({trans_type})")

st.divider()

# תמונה כללית של החודש
st.subheader("📊 התמונה הכללית של החודש")

if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    
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
else:
    st.info("עדיין לא הוזנו תנועות החודש. הוסף תנועה טופס למעלה כדי לראות את הסיכום!")
