# LAPORAN PRAKTIKUM
## Implementasi Konsep Blockchain pada Aplikasi Toko Komputer Berbasis Streamlit
### (Studi Kasus: `Furrapp.py` dan `databasecore.py`)

---

## 1. Tujuan Praktikum

1. Memahami konsep dasar teknologi *blockchain*, meliputi struktur blok, *hashing*, *Proof of Work* (PoW), dan mekanisme *chaining* antar blok.
2. Mengimplementasikan struktur data blok dan rantai blok (`Block` dan `Blockchain`) menggunakan bahasa pemrograman Python.
3. Mengintegrasikan struktur blockchain sederhana ke dalam sebuah aplikasi web interaktif menggunakan *framework* **Streamlit**, dalam bentuk studi kasus sistem pencatatan transaksi toko komputer.
4. Memahami penerapan fungsi *hash* (SHA-256) sebagai mekanisme penjamin integritas data pada setiap blok.
5. Memahami dan mengimplementasikan sistem autentikasi pengguna (*login* dan *register*) dengan basis data **SQLite** serta manajemen peran (*role-based access*: Admin, Penjual, Pembeli).
6. Melakukan simulasi serangan terhadap integritas data (*tampering*) dan menguji mekanisme verifikasi rantai blok (*chain validation*) untuk membuktikan sifat *immutability* blockchain.
7. Menganalisis alur data transaksi mulai dari input pengguna, penyimpanan ke dalam blok, hingga proses audit dan visualisasi statistik penjualan.

---

## 2. Dasar Teori Singkat

**Blockchain** adalah struktur data berupa rantai blok yang saling terhubung melalui nilai *hash*, di mana setiap blok menyimpan data, *timestamp*, dan *hash* dari blok sebelumnya (`prev_hash`). Karakteristik utama blockchain adalah:

- **Immutability**: data yang telah tercatat sangat sulit diubah karena perubahan pada satu blok akan mengubah nilai *hash*-nya dan merusak keterkaitan dengan blok berikutnya.
- **Proof of Work (PoW)**: mekanisme "penambangan" (*mining*) di mana sebuah blok baru dianggap valid apabila nilai *hash*-nya memenuhi syarat tertentu (misalnya diawali oleh sejumlah digit nol) yang dicapai dengan mengubah nilai `nonce` secara berulang.
- **Hash Function (SHA-256)**: fungsi satu arah yang mengubah data input menjadi nilai keluaran (*digest*) dengan panjang tetap, bersifat unik dan sensitif terhadap perubahan sekecil apapun pada data masukan.

---

## 3. Deskripsi Program

### 3.1 `databasecore.py` — Inti Logika Blockchain

File ini berisi dua kelas utama yang membentuk logika inti blockchain:

**a. Kelas `Block`**
Merepresentasikan satu blok data tunggal dengan atribut:
- `index` — nomor urut blok dalam rantai.
- `timestamp` — waktu pembuatan blok (disimpan dalam format UNIX time, dan dapat ditampilkan dalam format `%Y-%m-%d %H:%M:%S` melalui *property* `timestamp_readable`).
- `data` — payload atau isi data blok (dalam konteks aplikasi ini berupa string detail transaksi).
- `prev_hash` — nilai hash dari blok sebelumnya, berfungsi sebagai *pointer* penghubung antar blok.
- `nonce` — angka yang diubah-ubah selama proses *mining* untuk memenuhi syarat *Proof of Work*.
- `difficulty` — tingkat kesulitan *mining*, menentukan jumlah angka nol di awal hash yang harus dipenuhi.
- `hash` — hasil akhir dari fungsi `mine_block()`.

Fungsi penting pada kelas ini:
- `calculate_hash()` — menggabungkan seluruh atribut blok menjadi satu *string*, kemudian menghitung nilai SHA-256-nya.
- `mine_block()` — melakukan iterasi (*brute force*) terhadap nilai `nonce` hingga hash yang dihasilkan memenuhi target *difficulty* (diawali oleh `"0" * difficulty`).

**b. Kelas `Blockchain`**
Merepresentasikan kumpulan blok (rantai) dengan fungsi:
- `create_genesis_block()` — membuat blok pertama (*genesis block*) secara *hardcoded* dengan `prev_hash = "0"`.
- `add_block(data)` — menambahkan blok baru dengan merujuk hash dari blok terakhir sebagai `prev_hash`, lalu melakukan proses *mining*.
- `tamper_block(index, tampered_data)` — fungsi simulasi serangan yang mengubah data pada blok tertentu **tanpa** melakukan *mining* ulang, sehingga hash blok tersebut menjadi tidak valid lagi.
- `is_chain_valid()` — memverifikasi keabsahan seluruh rantai dengan tiga pemeriksaan pada setiap blok: kesesuaian hash tersimpan dengan hash hasil perhitungan ulang, pemenuhan syarat *Proof of Work*, dan kesesuaian `prev_hash` dengan hash blok sebelumnya.

### 3.2 `Furrapp.py` — Aplikasi Antarmuka (Front-End Streamlit)

File ini merupakan aplikasi web yang dibangun dengan **Streamlit**, mengimplementasikan studi kasus **"Blockchain for Computer Store"**, yaitu sistem pencatatan transaksi penjualan komponen komputer (motherboard, CPU, RAM, GPU, PSU, dan lain-lain) yang setiap transaksinya dicatat sebagai satu blok pada blockchain.

Komponen utama aplikasi:

| Komponen | Deskripsi |
|---|---|
| **Data Produk** | `KATEGORI_PRODUK` dan `AKSESORI` berupa dictionary berisi daftar kategori, nama produk, dan harga komponen PC. |
| **Tema Visual** | Fungsi `terapkan_tema()` menyuntikkan CSS kustom (tema gelap bernuansa "wolf/ice") beserta animasi transisi halaman dan efek salju. |
| **Autentikasi Pengguna** | Fungsi `hash_password()` (SHA-256), `buka_database_pengguna()`, `inisialisasi_database_pengguna()`, `muat_pengguna()`, dan `simpan_pengguna()` mengelola akun pengguna pada basis data **SQLite (`users.db`)**, dengan tiga peran demo: `admin`, `penjual`, `pembeli`. |
| **Halaman Login/Register** | `tampilkan_login()` menyediakan formulir masuk dan pendaftaran akun baru (akun baru otomatis berperan sebagai *Pembeli*), lengkap dengan validasi panjang *username*/*password*. |
| **Manajemen State** | `inisialisasi_state()` menyiapkan objek `Blockchain`, stok produk, riwayat transaksi, log audit, dan riwayat obrolan pada `st.session_state` agar tetap konsisten antar-*rerun* Streamlit. |
| **Toko Komputer** | `tampilkan_toko()` merupakan halaman utama transaksi: pengguna memilih kategori, produk, jumlah, aksesori, lalu sistem menghitung total harga, memvalidasi ketersediaan stok, dan memanggil `add_block()` untuk mencatat transaksi ke blockchain. Riwayat blok ditampilkan dalam bentuk *expander* berisi data, hash, timestamp, dan nonce. |
| **Katalog & Stok** | `tampilkan_inventory()` menampilkan tabel seluruh produk beserta harga dan status stok, serta formulir penyesuaian stok bagi Admin/Penjual. |
| **Verifikasi & Audit** | `tampilkan_audit()` menampilkan status validitas rantai (`is_chain_valid()`), tabel audit tiap blok (validitas hash, PoW, dan pointer), fitur **simulasi perusakan data** (`tamper_block()`) untuk menguji ketahanan sistem, serta log audit aktivitas pengguna (`catat_audit()`). |
| **Analytics** | `tampilkan_analytics()` menyajikan statistik total transaksi, total pendapatan, unit terjual, grafik batang penjualan per kategori, dan daftar produk terlaris. |
| **Chat Penjual** | `tampilkan_chat()` menyediakan fitur obrolan sederhana (sementara, hanya berlaku selama sesi) antara pembeli dan admin/penjual. |
| **Manajemen Pengguna** | `tampilkan_pengguna()` (khusus Admin) menampilkan daftar pengguna dan formulir penambahan akun baru dengan peran tertentu. |
| **Kontrol Akses Berbasis Peran** | Variabel `menu_by_role` membatasi menu yang dapat diakses sesuai peran pengguna: Admin memiliki akses penuh, Penjual tanpa Manajemen Pengguna, dan Pembeli hanya mengakses Toko, Analytics, dan Chat. |

### 3.3 Alur Kerja Aplikasi (Ringkas)

1. Pengguna login/registrasi → diverifikasi terhadap tabel `users` pada `users.db`.
2. Pengguna memilih menu sesuai peran yang dimiliki.
3. Saat transaksi dibuat pada menu "Toko Komputer", data transaksi disusun menjadi satu string dan dikirim ke `Blockchain.add_block()`.
4. Objek `Block` baru melakukan proses *mining* (mencari `nonce` yang menghasilkan hash sesuai *difficulty*) sebelum ditambahkan ke rantai.
5. Pada menu "Verifikasi & Audit", sistem memeriksa validitas seluruh rantai dan menyediakan simulasi perusakan data untuk menunjukkan bagaimana blockchain mendeteksi manipulasi.

---

## 4. Hasil dan Pembahasan

- Setiap transaksi yang dicatat berhasil membentuk satu blok baru dengan hash unik yang memenuhi syarat *Proof of Work* (`difficulty = 3`, yaitu hash diawali tiga digit nol).
- Ketika fitur **simulasi perusakan data** dijalankan pada suatu blok, nilai `data` blok tersebut berubah tanpa dilakukan *mining* ulang. Akibatnya, `calculate_hash()` menghasilkan nilai berbeda dari `hash` yang tersimpan, sehingga `is_chain_valid()` mengembalikan `False` dan sistem menampilkan peringatan **"Integritas Rantai Rusak!"**.
- Hal ini membuktikan sifat *immutability* blockchain: data yang telah tercatat tidak dapat diubah tanpa terdeteksi, karena perubahan data akan merusak kecocokan hash dan pointer antar blok.
- Sistem autentikasi berbasis SQLite serta pembatasan menu berdasarkan peran (*role-based access control*) berhasil membedakan hak akses antara Admin, Penjual, dan Pembeli.

---

## 5. Kesimpulan

Melalui praktikum ini, konsep dasar blockchain — meliputi *hashing*, *Proof of Work*, dan *chaining* antar blok — berhasil diimplementasikan dan diintegrasikan ke dalam sebuah aplikasi web nyata menggunakan Streamlit. Studi kasus sistem toko komputer menunjukkan bagaimana blockchain dapat dimanfaatkan sebagai mekanisme pencatatan transaksi yang transparan dan tahan terhadap manipulasi data, di mana setiap upaya perubahan data pada blok lama akan segera terdeteksi melalui proses verifikasi rantai (`is_chain_valid()`). Selain itu, praktikum ini juga memperkuat pemahaman mengenai integrasi basis data (SQLite) untuk autentikasi pengguna serta penerapan kontrol akses berbasis peran dalam sebuah aplikasi.

---

Laporan ini disusun berdasarkan hasil analisis dari kode `Furrapp.py` dan `databasecore.py`. 

Laporan Keberhasilan

![Halaman Awal.png](Halaman-Awal.png)
![Halaman awal saat user menambahkan hash.png](Halaman-awal-saat-user-menambahkan-hash.png)
![Halaman Verifikasi.png](Halaman-Verifikasi.png)
![Katalog and Stok.png](Katalog-and-Stok.png)
![Analytic Page.png](Analytic-Page.png)
![manajemen-page.png](manajemen-page.png)
![chat.png](chat.png)
![login reg.png](login-reg.png)
