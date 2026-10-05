import time
from datetime import datetime

import streamlit as st
from core import Block, Blockchain  

PRODUK = {
    "Kopi Arabika Gayo": 28000,
    "Kopi Robusta Temanggung": 22000,
    "Kopi Liberika Rangsang Meranti": 25000,
    "Kopi Susu Gula Aren": 18000,
    "Cappuccino": 20000,
    "Americano": 15000,
    "Cold Brew": 23000,
}
PELENGKAP = {
    "Extra shot espresso": 5000,
    "Susu oat": 6000,
    "Gula aren": 3000,
    "Sirup vanila": 4000,
    "Es batu tambahan": 0,
    "Croissant": 14000,
    "Pisang goreng": 12000,
}


def rupiah(nilai):
    return f"Rp{nilai:,}".replace(",", ".")


def waktu_terbaca(block):
    """Ubah timestamp (float) menjadi teks tanggal yang mudah dibaca."""
    return datetime.fromtimestamp(block.timestamp).strftime("%d-%m-%Y %H:%M:%S")



st.set_page_config(page_title="Blockchain Explorer", page_icon="🐺", layout="wide")
st.title("☕ Blockchain for Halal Coffee Supply Chain")


if "kopi_chain" not in st.session_state:
    st.session_state.kopi_chain = Blockchain()
if "waktu_mining" not in st.session_state:
    st.session_state.waktu_mining = None

kopi_chain = st.session_state.kopi_chain


st.sidebar.header("➕ Tambah Data Baru")

nama_pemesan = st.sidebar.text_input("Nama Pemesan:")
produk = st.sidebar.selectbox(
    "Pilih Produk:",
    list(PRODUK),
    format_func=lambda nama: f"{nama} - {rupiah(PRODUK[nama])}",
)
jumlah_produk = st.sidebar.number_input("Jumlah Produk:", min_value=1, step=1)
pelengkap = st.sidebar.multiselect(
    "Pilih Pelengkap (opsional):",
    list(PELENGKAP),
    format_func=lambda nama: f"{nama} - {rupiah(PELENGKAP[nama])}",
)

petani = st.sidebar.text_input("Nama Petani/Aktor:")
jumlah_kopi = st.sidebar.number_input("Jumlah Panen (Kg):", min_value=1, step=1)
lokasi = st.sidebar.text_input("Lokasi Kebun:")

if st.sidebar.button("⛏️ Mine Block (Tambah Data)"):
    if nama_pemesan and petani and lokasi:
        harga_pelengkap = sum(PELENGKAP[nama] for nama in pelengkap)
        harga_satuan = PRODUK[produk] + harga_pelengkap
        total_harga = harga_satuan * jumlah_produk
        daftar_pelengkap = ", ".join(pelengkap) if pelengkap else "Tidak ada"

        data_transaksi = (
            f"Pemesan: {nama_pemesan} | Produk: {produk} | Jumlah: {jumlah_produk} | "
            f"Pelengkap: {daftar_pelengkap} | Total: {rupiah(total_harga)} | "
            f"Petani: {petani} | Panen: {jumlah_kopi} Kg | Lokasi: {lokasi}"
        )

        new_index = len(kopi_chain.chain)
        new_block = Block(new_index, data_transaksi, "")

        with st.spinner("Sedang mencari Hash yang tepat (Mining)..."):
            mulai = time.perf_counter()
            kopi_chain.add_block(new_block)
            st.session_state.waktu_mining = time.perf_counter() - mulai

        st.sidebar.success("Blok berhasil ditambang dan diamankan ke dalam rantai!")
    else:
        st.sidebar.error("Lengkapi nama pemesan, petani, dan lokasi!")


st.sidebar.markdown("---")
st.sidebar.header("☠️ Simulasi Serangan")
if st.sidebar.button("HACK BLOK 1"):
    if len(kopi_chain.chain) > 1:
        st.session_state.kopi_chain.chain[1].data = "DATA PALSU!"
        st.sidebar.warning("Data Blok #1 telah diubah paksa! Klik '🛡️ Cek Integritas Rantai'.")
    else:
        st.sidebar.info("Belum ada Blok #1. Tambahkan minimal satu blok dulu.")


prefix_target = "0" * kopi_chain.difficulty
col_a, col_b, col_c = st.columns(3)
col_a.metric("Difficulty", kopi_chain.difficulty)
col_b.metric("Target Hash", f"{prefix_target}...")
if st.session_state.waktu_mining is not None:
    col_c.metric("Waktu Mining Terakhir", f"{st.session_state.waktu_mining:.3f} detik")
else:
    col_c.metric("Waktu Mining Terakhir", "-")

st.markdown("---")
if st.button("🛡️ Cek Integritas Rantai"):
    if kopi_chain.is_chain_valid():
        st.success("✔ Status Jaringan: AMAN (Rantai Valid)")
    else:
        st.error("❌ Status Jaringan: BAHAYA (Data telah dimanipulasi!)")
st.markdown("---")

st.subheader("📜 Blockchain Ledger (Buku Besar)")

for block in kopi_chain.chain:
    with st.expander(f"Blok #{block.index} | Nonce: {block.nonce} | Hash: {block.hash[:15]}..."):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Data Payload:**")
            st.info(block.data)
            st.write(f"**Timestamp:** {waktu_terbaca(block)}")
            st.write(f"**Nonce (Tebakan):** {block.nonce}")

        with col2:
            st.write("**Kriptografi:**")
            st.write("**Hash Saat Ini:**")
            st.code(block.hash, language="python")
            if block.hash.startswith(prefix_target):
                st.caption(f"✅ Hash diawali {prefix_target} (memenuhi Difficulty)")
            st.write("**Hash Sebelumnya (Pointer):**")
            st.code(block.previous_hash, language="python")
