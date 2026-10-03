import streamlit as st
import pandas as pd

st.set_page_config(page_title="מעקב תקציב אישי", page_icon="💰", layout="centered")

st.title("💰 מעקב הוצאות והכנסות אישי")
st.write("ברוך הבא לאפליקציית ניהול התקציב שלך!")

# טופס להוספת הוצאה/הכנסה
st.subheader("הוספת תנועה חדשה")
with st.form("budget_form"):
    description = st.text_input("תיאור (למשל: סופרמרקט, משכורת)")
    amount = st.number_input("סכום (ש\"ח)", value=0.0, step=10.0)
    trans_type = st.selectbox("סוג תנועה", ["הוצאה", "הכנסה"])
    submitted = st.form_submit_button("הוסף לרשימה")

    if submitted:
        st.success(def_msg := f"נוסף בהצלחה: {description} בסך {amount} ש\"ח ({trans_type})")

st.divider()
st.info("האפליקציה מוכנה! בהמשך נרחיב אותה לכל מה שתצטרך.")
