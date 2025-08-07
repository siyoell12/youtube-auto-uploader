# 🚀 YouTube Auto Short Uploader v2.0

**Otomatisasi Upload Video Short ke YouTube dengan Multi-Akun Support**

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![YouTube API](https://img.shields.io/badge/YouTube%20API-v3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fitur Utama

- ✅ **Multi-Akun Support** - Upload ke beberapa akun YouTube secara otomatis
- ✅ **Auto Hashtag** - Menghasilkan hashtag otomatis berdasarkan konten video
- ✅ **Anti Duplikat** - Tidak akan upload video yang sudah pernah diupload
- ✅ **Auto Hapus** - Menghapus video lokal setelah upload berhasil
- ✅ **Rate Limit Protection** - Delay otomatis untuk menghindari limit API
- ✅ **Target Audience** - Pilih apakah video untuk anak-anak atau tidak
- ✅ **Colorful CLI** - Tampilan terminal yang menarik dan informatif

## 🚀 Cara Pakai

### Quick Start (5 Menit)

1. **Download & Setup**
   ```bash
   git clone https://github.com/siyoell12/youtube-auto-short-uploader.git
   cd youtube-auto-short-uploader
   pip install -r requirements.txt
   ```

2. **Setup Google API**
   - Download `client_secrets.json` dari [Google Cloud Console](https://console.cloud.google.com)
   - Letakkan di root folder project

3. **Upload Video**
   ```bash
   python uploader.py
   ```

### Struktur Folder
```
youtube-auto-short-uploader/
├── uploader.py              # Main script
├── requirements.txt         # Dependencies
├── client_secrets.json      # Google API credentials
├── accounts/
│   ├── akun1/
│   │   ├── token.pkl       # Auto-generated
│   │   └── *.mp4           # Video files
│   ├── akun2/
│   └── akun3/
└── uploaded_videos.log     # Upload history
```

## 📋 Persyaratan
- Python 3.7+
- Google Cloud Console account
- YouTube channel yang sudah diverifikasi

## 🎯 Langkah Setup Google API

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Buat project baru
3. Enable **YouTube Data API v3**
4. Buat **OAuth 2.0 credentials** (Desktop App)
5. Download JSON → rename ke `client_secrets.json`

## 📖 Cara Penggunaan

### 1. Persiapan Video
- Pastikan video dalam format `.mp4`
- Letakkan video di folder akun yang sesuai
- Contoh: `accounts/akun1/video-anda.mp4`

### 2. Jalankan Script
```bash
python uploader.py
```

### 3. Ikuti Panduan CLI
```
╔═══════════════════════════════════════╗
║   YOUTUBE AUTO SHORT v.02             ║
╠═══════════════════════════════════════╣
║ 1. AKUN TUYUL SATU                    ║
║ 2. AKUN TUYUL DUA                     ║
║ 3. AKUN TUYUL TIGA                    ║
║ 4. PILIH AKUN                         ║
╚═══════════════════════════════════════╝
```

### 4. Pilih Target Audience
```
╔═════════════════════════╗
║ 👥 TARGET AUDIENCE     ║   
╠═════════════════════════╣
║ 1. Untuk Anak-Anak      ║
║ 2. Bukan Untuk Anak     ║
╚═════════════════════════╝
```

## 🔧 Troubleshooting

### Error: "client_secrets.json tidak ditemukan"
**Solusi**: Pastikan file `client_secrets.json` ada di root folder

### Error: "Quota exceeded"
**Solusi**: Tunggu 24 jam untuk reset quota

### Error: "Invalid credentials"
**Solusi**: Hapus file `token.pkl` di folder akun & ulang login

## 📊 Monitoring

### Check Upload History
```bash
type uploaded_videos.log  # Windows
cat uploaded_videos.log   # Linux/Mac
```

## 🌐 Komunitas & Sosial Media

Ingin berdiskusi, bertanya, atau berbagi ide? Bergabunglah dengan komunitas kami!

💬 Telegram Group: [t.me/airdropindependen](https://t.me/independendropers)

🐦 Twitter/X: [twitter.com/deasaputra12](https://x.com/Deasaputra_12)

🎮 Discord Server: [discord.gg/airdropindependen](https://discord.gg/Tuy2bR6CkU)


## Buy Me a Coffee

- **EVM:** 0x905d0505Ec007C9aDb5CF005535bfcC5E43c0B66
- **TON:** UQCFO7vVP0N8_K4JUCfqlK6tsofOF4KEhpahEEdXBMQ-MVQL
- **SOL:** BmqfjRHAKXUSKATuhbjPZfcNciN3J2DA1tqMgw9aGMdj

Thank you for visiting this repository, don't forget to contribute in the form of follows and stars.
If you have questions, find an issue, or have suggestions for improvement, feel free to contact me or open an *issue* in this GitHub repository.

**deasaputra**

