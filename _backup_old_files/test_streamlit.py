import streamlit as st

st.title("Test Streamlit")
st.write("Se vedi questo messaggio, Streamlit funziona correttamente!")

if st.button("Clicca qui"):
    st.success("Bottone funziona!")