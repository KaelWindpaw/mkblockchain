# Logika Smart Contract Lanjutan (Struct, Mapping, Events, dan Error Handling (Require/Revert) #

A. Tujuan Praktikum
1. Mahasiswa mampu memahami dan menerapkan Event pada Solidity untuk mencatat riwayat transaksi secara efisien.
2. Mahasiswa mampu menggunakan Require untuk membangun sistem kontrol akses (Access Control) yang aman.
3. Mahasiswa mampu mengimplementasikan logika pemindahan hak milik (Transfer Ownership) atas suatu aset digital.
4. Mahasiswa mulai merancang dan menulis kode Smart Contract (Versi 1) sesuai dengan studi kasus proyek kelompok masing-masing.


## Tahapan Praktikum ##

1. Buka Remix dan login
2. Sesuaikan File SupplyChainKopi.sol dengan modul
3. Membuat event untuk StatusBerubah dan KepemilikanBerpindah
![alt text](image.png)
4. Membuat Pemicu / emit untuk event-event tersebut pada setiap perubahan status
![alt text](image-1.png)
5. Membuat function updateStatus dan transferKopi
![alt text](image-2.png)
6. Uji coba konsep
- Daftar Panen Baru
![alt text](image-3.png)
- Transfer Kopi Akun 1 (Petani) ke Akun 2 (Distributor)
![alt text](image-4.png)
- Tranfer Kopi Gagal Akun 1 (Petani) ke Akun 2 (Distributor)
![alt text](image-5.png)
- Tranfer Kopi dari Akun 2 (Distributor) ke Akun 1
![alt text](image-6.png)