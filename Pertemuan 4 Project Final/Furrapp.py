import base64
import hashlib
import sqlite3
import time
from contextlib import closing
from datetime import datetime
from pathlib import Path

import streamlit as st
from databasecore import Blockchain 

KATEGORI_PRODUK = {
    "Motherboard": {
        "AMD AM4 - B550": 1750000,
        "AMD AM5 - B650": 2850000,
        "AMD AM5 - X870E": 4900000,
        "Intel LGA1200 - B560": 1650000,
        "Intel LGA1700 - B760": 2350000,
        "Intel LGA1700 - Z790": 4900000,
    },
    "CPU": {
        "AMD Ryzen 5 5600": 1850000,
        "AMD Ryzen 7 5700X": 2850000,
        "AMD Ryzen 5 7600": 3450000,
        "AMD Ryzen 9 7950X": 4900000,
        "AMD Ryzen 7 9800X3D": 750000,
        "Intel Core i3-10100F": 850000,
        "Intel Core i3-12100F": 1450000,
        "Intel Core i5-12400F": 2350000,
        "Intel Core i5-14400F": 3550000,
        "Intel Core i7-14700K": 6850000,
    },
    "RAM": {
        "DDR4 8GB": 350000,
        "DDR4 16GB": 650000,
        "DDR4 32GB Kit": 1250000,
        "DDR5 16GB": 850000,
        "DDR5 32GB Kit": 1650000,
        "DDR5 64GB Kit": 3200000,
    },
    "GPU": {
        "NVIDIA RTX 3050 (30 Series)": 3500000,
        "NVIDIA RTX 3060 (30 Series)": 4800000,
        "NVIDIA RTX 3070 (30 Series)": 7200000,
        "NVIDIA RTX 4060 (40 Series)": 5200000,
        "NVIDIA RTX 4070 (40 Series)": 9500000,
        "NVIDIA RTX 4080 (40 Series)": 18500000,
        "NVIDIA RTX 5060 (50 Series)": 6500000,
        "NVIDIA RTX 5070 (50 Series)": 10500000,
        "NVIDIA RTX 5080 (50 Series)": 19500000,
        "NVIDIA RTX 5090 (50 Series)": 67500000,
        "AMD Radeon RX 6600": 3500000,
        "AMD Radeon RX 7600": 4900000,
        "AMD Radeon RX 7800 XT": 8500000,
    },
    "PSU": {
        "550W 80+ Bronze": 750000,
        "650W 80+ Bronze": 950000,
        "750W 80+ Gold": 1450000,
        "850W 80+ Gold": 1950000,
        "1000W 80+ Gold": 3250000,
        "1200W 80+ Platinum": 4500000,
    },
    "CPU Cooler": {
        "Air Cooler Tower 120mm": 450000,
        "Air Cooler Dual Fan": 750000,
        "AIO Liquid Cooler 240mm": 1250000,
        "AIO Liquid Cooler 360mm": 1850000,
    },
    "Case PC": {
        "Casing ATX Airflow": 850000,
        "Casing Tempered Glass": 1250000,
        "Casing Mini ITX": 1450000,
        "Casing Full Tower": 2350000,
        "Casing Micro ATX Aesthetic White": 3250000,
    },
    "Storage": {
        "SSD SATA 512GB": 650000,
        "SSD NVMe Gen5 1TB": 1150000,
        "SSD NVMe Gen4 2TB": 2250000,
        "SSD NVMe Gen4 4TB": 4250000,
        "HDD 1TB": 750000,
        "HDD 2TB": 1050000,
    },
    "Monitor": {
        "Monitor IPS 24 inci 100Hz": 1850000,
        "Monitor Gaming 27 inci 165Hz": 3250000,
        "Monitor Ultrawide 34 inci": 6500000,
    },
    "Periferal": {
        "Keyboard Mechanical": 650000,
        "Mouse Wireless": 250000,
        "Headset Gaming": 550000,
        "Webcam Full HD": 450000,
    },
}
AKSESORI = {
    "Kabel HDMI": 100000,
    "Mousepad": 75000,
    "Flashdisk 64GB": 90000,
    "Thermal Paste": 75000,
    "Kabel Power": 50000,
}

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Computer Store Blockchain", page_icon="🔗", layout="wide")


def terapkan_tema():
    background_image = ""
    background_path = next(
        (
            Path(__file__).with_name(filename)
            for filename in [
                "wolf_background.png",
                "wolf_background.jpg",
                "wolf_background.jpeg",
                "wolf_background.webp",
            ]
            if Path(__file__).with_name(filename).exists()
        ),
        None,
    )
    if background_path:
        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }[background_path.suffix.lower()]
        background_image = (
            "url('data:"
            + mime_type
            + ";base64,"
            + base64.b64encode(background_path.read_bytes()).decode()
            + "')"
        )

    background_css = (
        f"background-image: linear-gradient(135deg, rgba(5, 12, 22, .94), "
        f"rgba(13, 31, 43, .72)), {background_image};"
        if background_image
        else "background-image: radial-gradient(circle at 80% 10%, rgba(105, 173, 182, .28), transparent 34%), linear-gradient(135deg, #07111d, #102b35 55%, #17212b);"
    )
    st.markdown(
        f"""
        <style>
        :root {{
            --wolf-ice: #a8e6e1;
            --wolf-mint: #62d4c8;
            --wolf-night: #07111d;
            --wolf-panel: rgba(12, 29, 40, .82);
            --wolf-line: rgba(168, 230, 225, .2);
        }}
        .stApp {{
            {background_css}
            background-attachment: fixed;
            background-size: cover;
            color: #edf9f7;
        }}
        .stApp::before {{
            content: "🐺";
            position: fixed;
            right: 3vw;
            bottom: -2rem;
            z-index: 0;
            opacity: .09;
            font-size: clamp(12rem, 28vw, 28rem);
            filter: grayscale(1) drop-shadow(0 0 2rem var(--wolf-mint));
            pointer-events: none;
        }}
        .stApp::after {{
            content: "";
            position: fixed;
            inset: 0;
            z-index: 2;
            pointer-events: none;
            background-image:
                radial-gradient(1.5px 1.5px at 24px 35px, rgba(255, 255, 255, .65) 99%, transparent),
                radial-gradient(1.2px 1.2px at 110px 80px, rgba(210, 245, 255, .48) 99%, transparent),
                radial-gradient(2px 2px at 75px 140px, rgba(255, 255, 255, .35) 99%, transparent);
            background-size: 320px 320px, 460px 460px, 620px 620px;
            animation: snowfall 28s linear infinite;
        }}
        [data-testid="stMain"] {{
            position: relative;
            z-index: 1;
            animation: page-in .65s ease-out both;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(4, 15, 25, .9);
            border-right: 1px solid var(--wolf-line);
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--wolf-panel);
            border-color: var(--wolf-line);
            backdrop-filter: blur(16px);
        }}
        [data-testid="stMetric"] {{
            background: var(--wolf-panel);
            border: 1px solid var(--wolf-line);
            border-radius: 14px;
            padding: 1rem;
            animation: float-in .55s ease-out both;
        }}
        [data-testid="stMain"] h1 {{
            animation: text-launch 1.15s cubic-bezier(.2, .75, .25, 1) .05s both;
        }}
        [data-testid="stMain"] h2 {{
            animation: text-launch 1.15s cubic-bezier(.2, .75, .25, 1) .16s both;
        }}
        [data-testid="stMain"] h3 {{
            animation: text-launch 1.15s cubic-bezier(.2, .75, .25, 1) .25s both;
        }}
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p {{
            animation: text-launch 1.15s cubic-bezier(.2, .75, .25, 1) .32s both;
        }}
        .stButton > button, .stFormSubmitButton > button {{
            border: 1px solid rgba(168, 230, 225, .42);
            border-radius: 10px;
            background: linear-gradient(135deg, #1d766f, #2b9c91);
            color: white;
            font-weight: 700;
            transition: transform .16s ease, box-shadow .16s ease, filter .16s ease;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 9px 24px rgba(98, 212, 200, .25);
            filter: brightness(1.12);
        }}
        .stButton > button:active, .stFormSubmitButton > button:active {{
            transform: scale(.96);
            box-shadow: 0 0 0 6px rgba(98, 212, 200, .12);
        }}
        .stTabs [data-baseweb="tab-highlight"] {{ background: var(--wolf-mint); }}
        .stTabs [data-baseweb="tab"] {{ color: var(--wolf-ice); }}
        @keyframes page-in {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes float-in {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes snowfall {{
            to {{ background-position: 0 320px, 0 460px, 0 620px; }}
        }}
        @keyframes text-launch {{
            from {{ opacity: 0; transform: translate3d(-12px, 14px, 0); }}
            to {{ opacity: 1; transform: translate3d(0, 0, 0); }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .stApp::after,
            [data-testid="stMain"] h1,
            [data-testid="stMain"] h2,
            [data-testid="stMain"] h3,
            [data-testid="stMain"] [data-testid="stMarkdownContainer"] p {{
                animation: none;
            }}
        }}
        .wolf-login-loader {{
            position: fixed;
            inset: 0;
            z-index: 9999;
            display: grid;
            place-items: center;
            background: rgba(5, 15, 24, .96);
            backdrop-filter: blur(10px);
        }}
        .wolf-loader-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.25rem;
            color: var(--wolf-ice);
        }}
        .wolf-howling-logo {{
            position: relative;
            display: grid;
            width: 132px;
            height: 132px;
            place-items: center;
            border: 1px solid var(--wolf-line);
            border-radius: 50%;
            background: rgba(12, 29, 40, .72);
            box-shadow: 0 0 42px rgba(98, 212, 200, .16);
        }}
        .wolf-howling-logo::before, .wolf-howling-logo::after {{
            content: "";
            position: absolute;
            inset: -9px;
            border: 1px solid rgba(168, 230, 225, .5);
            border-radius: 50%;
            animation: howl-wave 1.8s ease-out infinite;
            opacity: 0;
        }}
        .wolf-howling-logo::after {{ animation-delay: .9s; }}
        .wolf-howling-logo span {{
            font-size: 4.5rem;
            animation: wolf-howl 1.8s ease-in-out infinite;
            transform-origin: 50% 72%;
        }}
        .wolf-loader-caption {{
            margin: 0;
            font-size: .85rem;
            font-weight: 700;
            letter-spacing: .12em;
        }}
        @keyframes wolf-howl {{
            0%, 100% {{ transform: rotate(0) translateY(0); }}
            22% {{ transform: rotate(-12deg) translateY(-4px); }}
            48% {{ transform: rotate(-8deg) translateY(-2px); }}
            72% {{ transform: rotate(2deg) translateY(0); }}
        }}
        @keyframes howl-wave {{
            0% {{ transform: scale(.82); opacity: 0; }}
            28% {{ opacity: .65; }}
            100% {{ transform: scale(1.35); opacity: 0; }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .wolf-howling-logo::before, .wolf-howling-logo::after,
            .wolf-howling-logo span {{ animation: none; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def buka_database_pengguna():
    return sqlite3.connect(Path(__file__).with_name("users.db"))


def inisialisasi_database_pengguna():
    akun_demo = {
        "admin": {"password": hash_password("admin123"), "role": "Admin"},
        "penjual": {"password": hash_password("jual123"), "role": "Penjual"},
        "pembeli": {"password": hash_password("beli123"), "role": "Pembeli"},
    }
    with closing(buka_database_pengguna()) as database:
        with database:
            database.execute(
                "CREATE TABLE IF NOT EXISTS users ("
                "username TEXT PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL)"
            )
            database.executemany(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                [
                    (username, akun["password"], akun["role"])
                    for username, akun in akun_demo.items()
                ],
            )


def muat_pengguna():
    with closing(buka_database_pengguna()) as database:
        rows = database.execute("SELECT username, password, role FROM users").fetchall()
    return {
        username: {"password": password, "role": role}
        for username, password, role in rows
    }


def simpan_pengguna(username, password, role):
    try:
        with closing(buka_database_pengguna()) as database:
            with database:
                database.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role),
                )
    except sqlite3.IntegrityError:
        return False
    return True


def rupiah(value):
    return f"Rp{value:,}".replace(",", ".")


def catat_audit(aksi, detail):
    st.session_state.audit_events.append(
        {
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pengguna": st.session_state.get("current_user", "system"),
            "aksi": aksi,
            "detail": detail,
        }
    )


def inisialisasi_state():
    if "my_blockchain" not in st.session_state:
        st.session_state.my_blockchain = Blockchain()
    if "stok_produk" not in st.session_state:
        st.session_state.stok_produk = {
            produk: 10
            for daftar_produk in KATEGORI_PRODUK.values()
            for produk in daftar_produk
        }
    if "transaction_records" not in st.session_state:
        st.session_state.transaction_records = []
    if "audit_events" not in st.session_state:
        st.session_state.audit_events = []
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "Admin Penjual",
                "message": "Halo! Ada yang bisa kami bantu terkait kebutuhan komputer Anda?",
            }
        ]
    inisialisasi_database_pengguna()
    st.session_state.users = muat_pengguna()


def tampilkan_login():
    st.title("🔐 Login Computer Store")
    st.caption("Masuk atau buat akun baru untuk mengakses aplikasi.")
    login_tab, register_tab = st.tabs(["Masuk", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            masuk = st.form_submit_button("Masuk", type="primary")
        if masuk:
            akun = st.session_state.users.get(username.strip())
            if akun and akun["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.login_loading = True
                st.session_state.current_user = username.strip()
                st.session_state.current_role = akun["role"]
                catat_audit("Login", f"Login berhasil sebagai {akun['role']}")
                st.rerun()
            else:
                st.error("Username atau password tidak valid.")
        st.info("Demo: admin/admin123, penjual/jual123, pembeli/beli123")

    with register_tab:
        st.write("Buat akun baru sebagai **Pembeli**.")
        with st.form("register_form"):
            username_baru = st.text_input("Username baru", key="register_username")
            password_baru = st.text_input(
                "Password baru", type="password", key="register_password"
            )
            konfirmasi_password = st.text_input(
                "Konfirmasi password", type="password", key="register_password_confirmation"
            )
            daftar = st.form_submit_button("Daftar", type="primary")
        if daftar:
            username_baru = username_baru.strip()
            if not username_baru or not password_baru or not konfirmasi_password:
                st.error("Username dan password wajib diisi.")
            elif len(username_baru) < 3:
                st.error("Username minimal terdiri dari 3 karakter.")
            elif len(password_baru) < 6:
                st.error("Password minimal terdiri dari 6 karakter.")
            elif password_baru != konfirmasi_password:
                st.error("Konfirmasi password tidak sama.")
            elif not simpan_pengguna(
                username_baru, hash_password(password_baru), "Pembeli"
            ):
                st.error("Username sudah digunakan. Silakan pilih username lain.")
            else:
                st.session_state.users[username_baru] = {
                    "password": hash_password(password_baru), "role": "Pembeli"
                }
                catat_audit("Register", f"Akun pembeli baru: {username_baru}")
                st.success("Registrasi berhasil. Silakan masuk menggunakan akun baru.")


def tampilkan_chat():
    st.subheader("💬 Chat dengan Penjual")
    st.caption("Chat bersifat sementara dan hanya tersedia selama sesi aplikasi.")
    if st.button("Hapus Riwayat Chat", key="clear_chat"):
        st.session_state.chat_messages = []
        st.rerun()
    peran_pengirim = st.radio(
        "Kirim sebagai:",
        ["User", "Admin Penjual"],
        horizontal=True,
        key="chat_sender_role",
    )
    chat_container = st.container(height=430, border=True)
    with chat_container:
        for chat in st.session_state.chat_messages:
            with st.chat_message("assistant" if chat["role"] == "Admin Penjual" else "user"):
                st.caption(chat["role"])
                st.write(chat["message"])
    pesan_baru = st.chat_input("Tulis pesan untuk penjual...", key="chat_input")
    if pesan_baru and pesan_baru.strip():
        st.session_state.chat_messages.append(
            {"role": peran_pengirim, "message": pesan_baru.strip()}
        )
        st.rerun()


def tampilkan_toko():
    st.sidebar.header("➕ Tambah Transaksi Toko Komputer")
    nama_pemesan = st.sidebar.text_input("Nama Pembeli:")
    kategori = st.sidebar.selectbox("Pilih Kategori Komponen:", list(KATEGORI_PRODUK))
    produk_kategori = KATEGORI_PRODUK[kategori]
    produk = st.sidebar.selectbox(
        "Pilih Produk:",
        list(produk_kategori),
        format_func=lambda nama: f"{nama} - {rupiah(produk_kategori[nama])}",
    )
    jumlah_produk = st.sidebar.number_input("Jumlah Produk:", min_value=1, step=1)
    stok_tersedia = st.session_state.stok_produk[produk]
    st.sidebar.info(f"Stok tersedia: {stok_tersedia} unit")
    aksesori = st.sidebar.multiselect(
        "Pilih Aksesori (opsional):",
        list(AKSESORI),
        format_func=lambda nama: f"{nama} - {rupiah(AKSESORI[nama])}",
    )
    nama_penjual = st.sidebar.text_input("Nama Penjual/Admin:")
    lokasi = st.sidebar.text_input("Lokasi Toko:")

    if st.sidebar.button("Tambahkan ke Blockchain"):
        if not nama_pemesan or not nama_penjual or not lokasi:
            st.sidebar.error("Lengkapi nama pembeli, penjual/admin, dan lokasi toko!")
        elif jumlah_produk > stok_tersedia:
            st.sidebar.error(f"Stok tidak cukup. Tersedia hanya {stok_tersedia} unit.")
        else:
            harga_aksesori = sum(AKSESORI[nama] for nama in aksesori)
            harga_satuan = produk_kategori[produk] + harga_aksesori
            total_harga = harga_satuan * jumlah_produk
            stok_setelah = stok_tersedia - jumlah_produk
            daftar_aksesori = ", ".join(aksesori) if aksesori else "Tidak ada"
            data_transaksi = (
                f"Pembeli: {nama_pemesan} | Kategori: {kategori} | Produk: {produk} | "
                f"Jumlah: {jumlah_produk} Unit | Aksesori: {daftar_aksesori} | "
                f"Total: Rp{total_harga:,} | Penjual/Admin: {nama_penjual} | "
                f"Stok Sebelum: {stok_tersedia} Unit | Stok Sesudah: {stok_setelah} Unit | "
                f"Lokasi Toko: {lokasi}"
            ).replace(",", ".")
            st.session_state.my_blockchain.add_block(data_transaksi)
            st.session_state.stok_produk[produk] = stok_setelah
            st.session_state.transaction_records.append(
                {
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pembeli": nama_pemesan,
                    "kategori": kategori,
                    "produk": produk,
                    "jumlah": jumlah_produk,
                    "total": total_harga,
                    "pengguna": st.session_state.current_user,
                }
            )
            catat_audit("Transaksi", f"{produk} x{jumlah_produk}, total {rupiah(total_harga)}")
            st.sidebar.success(f"Blok berhasil ditambahkan. Stok tersisa: {stok_setelah} unit.")

    st.subheader("📦 Blockchain Ledger (Buku Besar)")
    if st.session_state.my_blockchain.is_chain_valid():
        st.success("✔ Status Jaringan: Rantai Valid (Aman)")
    else:
        st.error("❌ PERINGATAN: Integritas Rantai Rusak!")
    for block in st.session_state.my_blockchain.chain:
        with st.expander(f"Blok #{block.index} | Hash: {block.hash[:15]}..."):
            st.info(block.data)
            st.write(f"Timestamp: {block.timestamp_readable} | Nonce: {block.nonce}")


def tampilkan_inventory():
    st.subheader("📋 Katalog & Stok Produk")
    rows = []
    for kategori, daftar_produk in KATEGORI_PRODUK.items():
        for produk, harga in daftar_produk.items():
            rows.append({
                "Kategori": kategori,
                "Produk": produk,
                "Harga": rupiah(harga),
                "Stok": st.session_state.stok_produk[produk],
                "Status": "Habis" if st.session_state.stok_produk[produk] == 0 else "Tersedia",
            })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if st.session_state.current_role in ["Admin", "Penjual"]:
        st.subheader("Penyesuaian Stok")
        kategori_stok = st.selectbox("Kategori", list(KATEGORI_PRODUK), key="stock_category")
        produk_stok = st.selectbox("Produk", list(KATEGORI_PRODUK[kategori_stok]), key="stock_product")
        perubahan = st.number_input("Perubahan stok (+/- unit)", value=0, step=1, key="stock_delta")
        if st.button("Simpan Perubahan Stok"):
            stok_baru = st.session_state.stok_produk[produk_stok] + perubahan
            if stok_baru < 0:
                st.error("Stok tidak boleh menjadi negatif.")
            else:
                st.session_state.stok_produk[produk_stok] = stok_baru
                catat_audit("Perubahan Stok", f"{produk_stok}: stok menjadi {stok_baru}")
                st.success(f"Stok {produk_stok} sekarang {stok_baru} unit.")


def tampilkan_audit():
    st.subheader("🔍 Verifikasi Blok & Audit Keamanan")
    chain_valid = st.session_state.my_blockchain.is_chain_valid()
    st.metric("Status Rantai", "VALID" if chain_valid else "TIDAK VALID")
    st.write(f"Jumlah blok: {len(st.session_state.my_blockchain.chain)}")
    audit_rows = []
    for block in st.session_state.my_blockchain.chain:
        hash_valid = block.hash == block.calculate_hash()
        pow_valid = block.hash.startswith("0" * block.difficulty)
        pointer_valid = block.index == 1 or block.prev_hash == st.session_state.my_blockchain.chain[block.index - 2].hash
        audit_rows.append({
            "Blok": block.index,
            "Hash valid": hash_valid,
            "PoW valid": pow_valid,
            "Pointer valid": pointer_valid,
            "Nonce": block.nonce,
            "Hash": block.hash,
        })
    st.dataframe(audit_rows, use_container_width=True, hide_index=True)
    if len(st.session_state.my_blockchain.chain) > 1:
        st.subheader("🧪 Simulasi Perusakan Data")
        blok_tamper = st.selectbox(
            "Pilih blok transaksi",
            [block.index for block in st.session_state.my_blockchain.chain[1:]],
            key="tamper_block_index",
        )
        if st.button("Simulasikan Perusakan Data", type="secondary"):
            st.session_state.my_blockchain.tamper_block(blok_tamper, "DATA TRANSAKSI TELAH DIMANIPULASI")
            catat_audit("Tamper Test", f"Payload blok #{blok_tamper} diubah")
            st.rerun()
    st.subheader("Audit Trail Aktivitas")
    st.dataframe(st.session_state.audit_events, use_container_width=True, hide_index=True)


def tampilkan_analytics():
    st.subheader("📊 Dashboard / Statistik Penjualan")
    records = st.session_state.transaction_records
    total_transaksi = len(records)
    total_pendapatan = sum(item["total"] for item in records)
    total_unit = sum(item["jumlah"] for item in records)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transaksi", total_transaksi)
    col2.metric("Total Pendapatan", rupiah(total_pendapatan))
    col3.metric("Unit Terjual", total_unit)
    if not records:
        st.info("Belum ada transaksi untuk dianalisis.")
        return
    kategori_sales = {}
    produk_sales = {}
    for item in records:
        kategori_sales[item["kategori"]] = kategori_sales.get(item["kategori"], 0) + item["jumlah"]
        produk_sales[item["produk"]] = produk_sales.get(item["produk"], 0) + item["jumlah"]
    st.write("**Penjualan per kategori**")
    st.bar_chart(kategori_sales)
    st.write("**Produk terlaris**")
    st.dataframe(
        [{"Produk": produk, "Unit Terjual": jumlah} for produk, jumlah in sorted(produk_sales.items(), key=lambda item: item[1], reverse=True)],
        use_container_width=True,
        hide_index=True,
    )


def tampilkan_pengguna():
    st.subheader("👥 Manajemen Pengguna & Peran")
    st.caption("Halaman ini hanya dapat diakses oleh Admin.")
    st.dataframe(
        [{"Username": username, "Peran": akun["role"]} for username, akun in st.session_state.users.items()],
        use_container_width=True,
        hide_index=True,
    )
    with st.form("new_user_form"):
        username_baru = st.text_input("Username baru")
        password_baru = st.text_input("Password baru", type="password")
        role_baru = st.selectbox("Peran", ["Admin", "Penjual", "Pembeli"])
        simpan_user = st.form_submit_button("Tambah Pengguna")
    if simpan_user:
        if not username_baru.strip() or not password_baru:
            st.error("Username dan password wajib diisi.")
        elif not simpan_pengguna(
            username_baru.strip(), hash_password(password_baru), role_baru
        ):
            st.error("Username sudah digunakan.")
        else:
            st.session_state.users[username_baru.strip()] = {
                "password": hash_password(password_baru), "role": role_baru
            }
            catat_audit("Pengguna Baru", f"{username_baru.strip()} dibuat sebagai {role_baru}")
            st.success("Pengguna berhasil ditambahkan.")


inisialisasi_state()
terapkan_tema()
if not st.session_state.get("logged_in", False):
    tampilkan_login()
    st.stop()

if st.session_state.pop("login_loading", False):
    st.markdown(
        """
        <div class="wolf-login-loader">
            <div class="wolf-loader-content">
                <div class="wolf-howling-logo"><span>🐺</span></div>
                <p class="wolf-loader-caption">MEMUAT TOKO</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.6)
    st.rerun()

st.title("💻 Blockchain for Computer Store")
st.sidebar.write(f"Login: **{st.session_state.current_user}** ({st.session_state.current_role})")
if st.sidebar.button("Logout"):
    catat_audit("Logout", "Sesi pengguna berakhir")
    st.session_state.logged_in = False
    st.session_state.pop("current_user", None)
    st.session_state.pop("current_role", None)
    st.rerun()

role = st.session_state.current_role
menu_by_role = {
    "Admin": ["Toko Komputer", "Katalog & Stok", "Verifikasi & Audit", "Analytics", "Chat Penjual", "Manajemen Pengguna"],
    "Penjual": ["Toko Komputer", "Katalog & Stok", "Verifikasi & Audit", "Analytics", "Chat Penjual"],
    "Pembeli": ["Toko Komputer", "Analytics", "Chat Penjual"],
}
menu = st.sidebar.radio("Menu Utama", menu_by_role[role], key="main_menu")

if menu == "Toko Komputer":
    tampilkan_toko()
elif menu == "Katalog & Stok":
    tampilkan_inventory()
elif menu == "Verifikasi & Audit":
    tampilkan_audit()
elif menu == "Analytics":
    tampilkan_analytics()
elif menu == "Chat Penjual":
    tampilkan_chat()
elif menu == "Manajemen Pengguna":
    tampilkan_pengguna()