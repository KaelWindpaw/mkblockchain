import streamlit as st

st.set_page_config(page_title="CV App", page_icon="🐺", layout="wide")

# Pembuatan Siebar
st.sidebar.title("⚙️Pengaturan Profile")
st.write("Masukkan data diri anda di bawah sini")

# Komponen INputan
nama = st.sidebar.text_input("Nama:", "Nama Lengkap")
nim = st.sidebar.text_input("NIM:", "NIM Anda")
jurusan = st.sidebar.selectbox("Jurusan:", ["Teknik Informatika", "Sistem Informasi", "Teknik Elektro", "Teknik Mesin"])

deskripsi = st.sidebar.text_area("Deskripsi Diri:", "Tuliskan deskripsi singkat tentang diri anda di sini.")

# Area Utama
st.title("Curriculum Vitae")
st.markdown("-----------")

kolom_kiri, kolom_kanan = st.columns([2,1])
with kolom_kiri:
    st.header(nama)
    st.image("MVIMG_20260827_191844.jpg.jpeg", width=150)
    st.subheader(f"{jurusan} | (NIM: {nim})")

with kolom_kanan:
    st.write(f"Tentang saya: {deskripsi}")
