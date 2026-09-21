import streamlit as st

st.set_page_config(page_title="CV App", page_icon="😎", layout="wide")

# Pembuatan Sidebar
st.sidebar.title("⚙️ Pengaturan Profile")
st.write("Masukkan data diri anda di bawah sini")

# Komponen Inputan Data Diri
nama = st.sidebar.text_input("Nama:", "Nama Lengkap")
nim = st.sidebar.text_input("NIM:", "NIM Anda")
jurusan = st.sidebar.selectbox("Jurusan:", ["Teknik Informatika", "Sistem Informasi", "Teknik Elektro", "Teknik Mesin"])
deskripsi = st.sidebar.text_area("Deskripsi Diri:", "Tuliskan deskripsi singkat tentang diri anda di sini.")

st.sidebar.markdown("---")
st.sidebar.subheader("🏆 Portofolio & Riwayat")

# Komponen Inputan Baru: Sertifikat & Pengalaman
sertifikat = st.sidebar.text_area("Sertifikat (Pisahkan dengan baris baru):", "- Sertifikat Python Dasar (Dicoding)\n- Sertifikat Web Development")
pengalaman = st.sidebar.text_area("Pengalaman (Pisahkan dengan baris baru):", "- Staf Himpunan Mahasiswa (2025)\n- Frontend Developer Intern (2026)")

# Area Utama
st.title("Curriculum Vitae")
st.markdown("-----------")

kolom_kiri, kolom_kanan = st.columns([2, 1])

with kolom_kiri:
    st.header(nama)
    # Catatan: Pastikan file gambar "nukas.jpeg" ada di direktori yang sama
    st.image("abie 2.jpeg", width=150)
    st.subheader(f"{jurusan} | (NIM: {nim})")
    
    # Menampilkan Pengalaman di kolom kiri
    st.markdown("### 💼 Pengalaman")
    st.write(pengalaman)

with kolom_kanan:
    st.write(f"**Tentang saya:** {deskripsi}")
    
    st.markdown("---")
    
    # Menampilkan Sertifikat di kolom kanan
    format_sertif = st.markdown("### 📜 Sertifikat")
    st.write(sertifikat)