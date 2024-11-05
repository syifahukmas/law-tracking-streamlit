# Law Tracking Dashboard

Proyek ini membuat sebuah dashboard interaktif yang dikembangkan dengan Streamlit untuk memvisualisasikan perubahan dalam peraturan perundang-undangan (UU) yang terdapat di JDIH Kementerian Energi dan Sumber Daya Mineral (KESDM). Dashboard ini menampilkan alur perubahan UU menggunakan diagram Sankey yang intuitif, memungkinkan user untuk melihat alur revisi atau pencabutan UU dari waktu ke waktu.

## Daftar Isi
- [Tentang Proyek](#tentang-proyek)
- [Fitur](#fitur)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Struktur Proyek](#struktur-proyek)
- [Contoh Penggunaan](#contoh-penggunaan)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)
- [Kontak](#kontak)

---

## Tentang Proyek

Jelaskan tentang proyek secara lebih rinci, seperti:
- Latar belakang proyek
- Masalah yang diselesaikan
- Solusi yang diberikan oleh proyek ini

## Fitur

- **Filter Data Berupa Bentuk Peraturan dan Nomor UU** - Pengguna dapat memilih bentuk peraturan tertentu untuk memfilter UU yang ingin ditampilkan seperti Keputusan Menteri (KEPMEN), Peraturan Menteri (PERMEN), Peraturan Presiden (PERPRES), dll. Selain itu, pengguna juga dapat memilih nomor UU berdasarkan bentuk peraturan yang sudah dipilih.
- - **Diagram Sankey untuk Alur Perubahan UU** - Diagram Sankey memperlihatkan aliran perubahan peraturan berdasarkan status seperti Dicabut, Diubah, Mencabut, dan Mengubah. Pengguna dapat melihat Diagram Sankey perubahan regulasi terhadap UU yang telah dipilih berdasarkan filter yang diterapkan.
- **Tabel Data UU** -  Tabel data memberikan informasi utama dari setiap UU, seperti Judul, Nomor Peraturan, Tahun Terbit, Tipe Dokumen, Status Perubahan, dll.

## Persyaratan Sistem

Daftar kebutuhan sistem untuk menjalankan proyek ini:
- Python versi x.x atau lebih tinggi (untuk proyek Python)
- Paket-paket tambahan yang diperlukan
- Persyaratan lain yang relevan

## Instalasi

Langkah-langkah instalasi proyek:
1. Clone repositori:
    ```bash
    git clone https://github.com/username/nama-proyek.git
    ```
2. Masuk ke direktori proyek:
    ```bash
    cd nama-proyek
    ```
3. Install dependensi yang diperlukan:
    ```bash
    pip install -r requirements.txt
    ```

## Penggunaan

To run the dashboard:
```bash
streamlit run app.py
```

## Struktur Proyek

├── data/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── README.md
└── requirements.txt
