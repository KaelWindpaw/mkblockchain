import streamlit as st
from core import Blockchain # Mengimpor mesin Blockchain yang kita buat

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Blockchain Explorer", page_icon="🔗", layout="wide")
st.title("☕ Blockchain for Halal Coffee Supply Chain")

# --- SESSION STATE MANAGEMENT ---
if 'my_blockchain' not in st.session_state:
    st.session_state.my_blockchain = Blockchain()

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("➕ Tambah Data Baru")

# Contoh Kasus: Rantai Pasok Kopi
petani = st.sidebar.text_input("Nama Petani/Aktor:")
jumlah_kopi = st.sidebar.number_input("Jumlah Panen (Kg):", min_value=1)
lokasi = st.sidebar.text_input("Lokasi Kebun:")

if st.sidebar.button("Tambahkan ke Blockchain"):
    if petani and lokasi:
        # Mengemas data menjadi satu string JSON-like
        data_transaksi = f"Petani: {petani} | Panen: {jumlah_kopi} Kg | Lokasi: {lokasi}"
        
        # Memanggil method add_block dari Object yang ada di memori
        st.session_state.my_blockchain.add_block(data_transaksi)
        st.sidebar.success("Blok berhasil ditambahkan!")
    else:
        st.sidebar.error("Lengkapi semua data!")

# --- MAIN AREA: VISUALISASI RANTAI ---
st.subheader("📦 Blockchain Ledger (Buku Besar)")

# Status Validitas Rantai
is_valid = st.session_state.my_blockchain.is_chain_valid()
if is_valid:
    st.success("✔ Status Jaringan: Rantai Valid (Aman)")
else:
    st.error("❌ PERINGATAN: Integritas Rantai Rusak (Telah Dimanipulasi!)")

# Menampilkan semua blok dengan Looping
for block in st.session_state.my_blockchain.chain:
    with st.expander(f"Blok #{block.index} | Hash: {block.hash[:15]}..."):
        # Membuat 2 kolom untuk rapi
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Payload:**")
            st.info(block.data)
            st.write(f"**Timestamp:** {block.timestamp_readable}")
            
        with col2:
            st.write("**Kriptografi:**")
            st.write("**Hash Saat Ini:**")
            st.code(block.hash, language='python')
            st.write("**Hash Sebelumnya (Pointer):**")
            st.code(block.prev_hash, language='python')