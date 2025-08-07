import os
import pickle
import time
import psutil
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from colorama import Fore, init

init(autoreset=True)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "client_secrets.json"  # Memperbaiki nama file
ACCOUNTS_FOLDER = "accounts"
MAX_VIDEOS_PER_ACCOUNT = 3
UPLOADED_VIDEOS_LOG = "uploaded_videos.log"  # File untuk logging video yang sudah diupload

# Hashtag umum untuk video short
COMMON_HASHTAGS = ["#shorts", "#viral", "#trending", "#fyp", "#foryou", "#foryoupage"]

def authenticate(token_path):
    """Autentikasi dengan penanganan error yang lebih baik"""
    creds = None
    try:
        if os.path.exists(token_path):
            print(Fore.CYAN + f"🔐 Memuat token dari: {token_path}")
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        else:
            print(Fore.CYAN + f"🔐 Token tidak ditemukan, memulai proses autentikasi baru...")
            if not os.path.exists(CREDENTIALS_FILE):
                print(Fore.RED + f"❌ File kredensial tidak ditemukan: {CREDENTIALS_FILE}")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            # Buat direktori jika belum ada
            os.makedirs(os.path.dirname(token_path) if os.path.dirname(token_path) else ".", exist_ok=True)
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
            print(Fore.GREEN + f"✅ Token disimpan di: {token_path}")
        
        # Bangun service YouTube
        service = build("youtube", "v3", credentials=creds)
        return service
    except Exception as e:
        print(Fore.RED + f"❌ Error saat autentikasi: {str(e)}")
        return None
                
def upload_video(youtube, video_path, made_for_kids=False):
    """Upload video dengan penanganan error dan logging yang lebih baik"""
    try:
        # Periksa apakah video sudah pernah diupload
        if is_video_already_uploaded(video_path):
            print(Fore.YELLOW + f"⚠️  Video sudah pernah diupload: {video_path}")
            print(Fore.BLUE + f"ℹ️  Melewati upload: {video_path}")
            # Hapus video yang sudah diupload
            try:
                os.remove(video_path)
                print(Fore.RED + f"🗑️  Video dihapus: {video_path}")
            except PermissionError as e:
                if e.winerror == 32:  # File sedang digunakan oleh proses lain
                    print(Fore.LIGHTRED_EX + f"⚠️ Gagal menghapus: {e}")
                    print(Fore.YELLOW + f"ℹ️  File sedang digunakan oleh proses lain. Coba tutup aplikasi yang menggunakan file ini, lalu hapus secara manual: {video_path}")
                else:
                    print(Fore.LIGHTRED_EX + f"⚠️ Gagal menghapus: {e}")
                    print(Fore.YELLOW + f"ℹ️  Pastikan untuk menghapus video secara manual: {video_path}")
            except Exception as e:
                print(Fore.LIGHTRED_EX + f"⚠️ Gagal menghapus: {e}")
                print(Fore.YELLOW + f"ℹ️  Pastikan untuk menghapus video secara manual: {video_path}")
            return True
            
        title = os.path.splitext(os.path.basename(video_path))[0]
        # Bersihkan judul dari spasi di awal/akhir dan hapus trailing underscore
        title = title.strip().rstrip('_')
        # Validasi judul agar tidak kosong atau hanya spasi
        if not title:
            title = "Untitled Video"
        # Tambahkan auto hashtag ke judul
        hashtags = generate_hashtags(title)
        
        # Sanitasi judul: ganti karakter & dengan 'dan', hapus karakter tidak valid lainnya
        import re
        sanitized_title = title.replace("&", "dan")
        sanitized_title = re.sub(r"[^a-zA-Z0-9\s\-_,.!?']", "", sanitized_title)
        sanitized_title = sanitized_title.strip()
        if not sanitized_title:
            sanitized_title = "Untitled Video"
        
        # Batasi panjang judul agar tidak melebihi 100 karakter
        if len(sanitized_title) > 100:
            sanitized_title = sanitized_title[:100].rstrip()
        
        # Kembalikan hashtag ke judul agar tetap terlihat
        # Pastikan hashtag juga sudah disanitasi agar tidak menyebabkan error
        import re
        sanitized_hashtags = " ".join([re.sub(r'[^a-zA-Z0-9#]', '', tag) for tag in hashtags.split()])
        title_with_hashtags = f"{sanitized_title} {sanitized_hashtags}".strip()
        # Batasi panjang judul termasuk hashtag agar tidak melebihi 100 karakter
        if len(title_with_hashtags) > 100:
            # Potong di spasi terakhir sebelum batas 100 karakter agar tidak memotong hashtag
            cut_pos = title_with_hashtags.rfind(' ', 0, 100)
            if cut_pos == -1:
                cut_pos = 100
            title_with_hashtags = title_with_hashtags[:cut_pos].rstrip()
        if not title_with_hashtags or title_with_hashtags.isspace():
            title_with_hashtags = "Untitled Video"
        description = f"Uploaded by DEA SAPUTRA AUTO SHORT - {sanitized_title}"
        
        print(Fore.CYAN + f"Judul final untuk upload: '{title_with_hashtags}'")
        print(Fore.CYAN + f"Deskripsi final untuk upload: '{description}'")

        # Pastikan tags juga mencakup hashtag tanpa tanda #
        tags = title.split()
        hashtag_tags = [tag.lstrip('#') for tag in hashtags.split()]
        tags = list(set(tags + hashtag_tags))

        # Remove redundant assignment to tags
        # tags = title.split()

        print(Fore.CYAN + f"Nilai made_for_kids: {made_for_kids}")
        request_body = {
            "snippet": {
                "title": title_with_hashtags,
                "description": description,
                "tags": tags,
                "categoryId": "22",
                "defaultLanguage": "id",
                "defaultAudioLanguage": "id",
                "audience": {
                    "madeForKids": made_for_kids
                }
            },
            "status": {
                "privacyStatus": "public",
                "madeForKids": made_for_kids,
                "selfDeclaredMadeForKids": made_for_kids
            },
        }
        print(Fore.CYAN + f"Request body status: {request_body['status']}")

        media = MediaFileUpload(video_path, resumable=True, mimetype="video/*")

        print(Fore.YELLOW + f"🚀 Mengupload: {title_with_hashtags} ...")
        
        # Coba upload dengan penanganan rate limit
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response_upload = youtube.videos().insert(
                    part="snippet,status",
                    body=request_body,
                    media_body=media
                ).execute()
                
                print(Fore.GREEN + f"✅ Upload selesai: {response_upload['id']}")
                
                # Logging video yang berhasil diupload
                log_uploaded_video(video_path, response_upload['id'], title)
                
                # Hapus video secara otomatis setelah upload berhasil
                import time
                max_delete_retries = 5

                def kill_process_using_file(file_path):
                    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                        try:
                            if proc.info['open_files']:
                                for opened_file in proc.info['open_files']:
                                    if opened_file.path == file_path:
                                        proc.kill()
                                        print(Fore.MAGENTA + f"🛑 Proses {proc.pid} ({proc.name()}) yang menggunakan file telah dihentikan.")
                                        return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    return False

                for attempt in range(max_delete_retries):
                    try:
                        os.remove(video_path)
                        print(Fore.RED + f"🗑️  Video dihapus: {video_path}")
                        break
                    except PermissionError as e:
                        if e.winerror == 32:  # File sedang digunakan oleh proses lain
                            print(Fore.LIGHTRED_EX + f"⚠️ Gagal menghapus (percobaan {attempt+1}): {e}")
                            killed = kill_process_using_file(video_path)
                            if not killed:
                                time.sleep(1)
                        else:
                            print(Fore.LIGHTRED_EX + f"⚠️ Gagal menghapus: {e}")
                            print(Fore.YELLOW + f"ℹ️  Pastikan untuk menghapus video secara manual: {video_path}")
                            break
                    except Exception as e:
                        print(Fore.LIGHTRED_EX + f"⚠️ Gagal menghapus: {e}")
                        print(Fore.YELLOW + f"ℹ️  Pastikan untuk menghapus video secara manual: {video_path}")
                        break
                else:
                    print(Fore.YELLOW + f"ℹ️  Gagal menghapus video setelah {max_delete_retries} percobaan. Harap hapus secara manual: {video_path}")
                        
                return True
                
            except Exception as e:
                # Cek jika error karena rate limit
                if "rateLimitExceeded" in str(e) or "quotaExceeded" in str(e) or (hasattr(e, 'resp') and e.resp.status == 429):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt * 60  # Eksponensial backoff: 1 menit, 2 menit, 4 menit
                        print(Fore.YELLOW + f"⏳ Rate limit tercapai. Menunggu {wait_time} detik sebelum mencoba lagi...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(Fore.RED + f"❌ Rate limit masih tercapai setelah {max_retries} percobaan.")
                        raise e
                else:
                    # Error lainnya, langsung raise
                    raise e
                    
    except Exception as e:
        print(Fore.RED + f"❌ Error saat upload video {video_path}: {str(e)}")
        return False
                        
def is_video_already_uploaded(video_path):
    """Periksa apakah video sudah pernah diupload sebelumnya"""
    try:
        if not os.path.exists(UPLOADED_VIDEOS_LOG):
            return False
            
        with open(UPLOADED_VIDEOS_LOG, "r", encoding="utf-8") as log_file:
            for line in log_file:
                if video_path in line:
                    return True
        return False
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"⚠️ Gagal memeriksa log: {e}")
        return False

def log_uploaded_video(video_path, video_id, title):
    """Logging video yang sudah diupload"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {video_id} | {title} | {video_path}\n"
        
        with open(UPLOADED_VIDEOS_LOG, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"⚠️ Gagal membuat log: {e}")
        
def generate_hashtags(title):
    """Menghasilkan hashtag otomatis berdasarkan judul video"""
    # Hashtag umum
    hashtags = COMMON_HASHTAGS.copy()
    
    # Tambahkan hashtag berdasarkan kata kunci dalam judul
    keywords = title.lower().split()
    
    # Beberapa kata kunci umum dan hashtag terkait
    keyword_hashtags = {
        "rahasia": ["#rahasia", "#misteri", "#terlarang"],
        "tips": ["#tips", "#trik", "#cara"],
        "cara": ["#tips", "#trik", "#cara"],
        "sukses": ["#sukses", "#motivasi", "#inspirasi"],
        "motivasi": ["#motivasi", "#inspirasi", "#semangat"],
        "inspirasi": ["#inspirasi", "#motivasi", "#semangat"],
        "kisah": ["#kisah", "#cerita", "#pengalaman"],
        "pengalaman": ["#pengalaman", "#kisah", "#cerita"],
        "edukasi": ["#edukasi", "#belajar", "#ilmu"],
        "belajar": ["#belajar", "#edukasi", "#ilmu"],
        "pembelajaran": ["#belajar", "#edukasi", "#ilmu"],
        "adhd": ["#adhd", "#neurodivergensi", "#kesehatanmental"],
        "neurodivergensi": ["#neurodivergensi", "#adhd", "#kesehatanmental"],
        "kripto": ["#kripto", "#cryptocurrency", "#investasi"],
        "investasi": ["#investasi", "#keuangan", "#finansial"],
        "keuangan": ["#keuangan", "#finansial", "#investasi"],
        "seo": ["#seo", "#marketing", "#digitalmarketing"],
        "marketing": ["#marketing", "#digitalmarketing", "#seo"],
        "storytelling": ["#storytelling", "#cerita", "#narasi"],
        "narasi": ["#narasi", "#storytelling", "#cerita"],
        "kontroversi": ["#kontroversi", "#debat", "#diskusi"],
        "debat": ["#debat", "#kontroversi", "#diskusi"],
        "psikologi": ["#psikologi", "#mindset", "#kesehatanmental"],
        "kesehatanmental": ["#kesehatanmental", "#psikologi", "#mindset"],
        "trading": ["#trading", "#investasi", "#keuangan"],
        "bitcoin": ["#bitcoin", "#cryptocurrency", "#kripto"],
    }
    
    # Tambahkan hashtag berdasarkan kata kunci
    for keyword, tags in keyword_hashtags.items():
        if any(keyword in word for word in keywords):
            hashtags.extend(tags)
    
    # Hapus duplikat dan kembalikan sebagai string
    unique_hashtags = list(set(hashtags))
    return " ".join(unique_hashtags[:10])  # Batasi maksimal 10 hashtag

def banner():
    print(Fore.RED + " _     _  _____  _   _  _____  _   _  ___    ___       _____  _   _  _____  _____     ___    _   _  _____  ___   _____ ")
    print(Fore.YELLOW + "( )   ( )(  _  )( ) ( )(_   _)( ) ( )(  _`\\ (  _`\\    (  _  )( ) ( )(_   _)(  _  )   (  _`\\ ( ) ( )(  _  )|  _`\\(_   _)")
    print(Fore.GREEN + "`\\`\\_/'/'| ( ) || | | |  | |  | | | || (_) )| (_(_)   | (_) || | | |  | |  | ( ) |   | (_(_)| |_| || ( ) || (_) ) | |  ")
    print(Fore.CYAN + "  `\\ /'  | | | || | | |  | |  | | | ||  _ <'|  _)_    |  _  || | | |  | |  | | | |   `\\__ \\ |  _  || | | || ,  /  | |  ")
    print(Fore.BLUE + "   | |   | (_) || (_) |  | |  | (_) || (_) )| (_( )   | | | || (_) |  | |  | (_) |   ( )_) || | | || (_) || |\\ \\  | |  ")
    print(Fore.MAGENTA + "   (_)   (_____)(_____)  (_)  (_____)(____/'(____/'   (_) (_)(_____)  (_)  (_____)   `\\____)(_) (_)(_____)(_) (_) (_)  ")
    print()
                                                                                                                       
                                                                                                                       



def select_account():
    # Tampilkan banner
    banner()

    accounts = [f for f in os.listdir(ACCOUNTS_FOLDER) if os.path.isdir(os.path.join(ACCOUNTS_FOLDER, f))]
    if not accounts:
        print(Fore.RED + "❌ Tidak ada akun ditemukan di folder 'accounts'.")
        return None

    # Mapping nama akun yang lebih menarik
    account_names = {
           "akun1": "AKUN TUYUL SATU       ",
           "akun2": "AKUN TUYUL DUA        ", 
           "akun3": "AKUN TUYUL TIGA       "
    }
    
    # Banner ASCII kecil dan berwarna yang terintegrasi dengan daftar akun
    print(Fore.CYAN + "\n ╭─────────────────────────────╮")
    print(Fore.CYAN + " │" + Fore.YELLOW +    "   YOUTUBE AUTO SHORT v.02   " + Fore.CYAN + "│")
    print(Fore.CYAN + " ├─────────────────────────────┤")
    # Hitung panjang maksimum nama akun untuk padding
    max_length = max(len(name) for name in account_names.values())
    for idx, acc in enumerate(accounts, start=1):
        display_name = account_names.get(acc, acc.upper())
        padding = max_length - len(display_name) + 3  # +3 untuk nomor dan spasi
        print(Fore.CYAN +  " │" + Fore.GREEN + f" {idx}. {display_name}" + " " * padding + Fore.CYAN + "│")
        print(Fore.CYAN +  " ├" +    "─" * (max_length + 5) + "──┤")
    print(Fore.CYAN + " │ " + Fore.YELLOW + "4. PILIH AKUN               " + Fore.CYAN + "│")
    print(Fore.CYAN + " ╰─────────────────────────────╯")
    print(
        Fore.CYAN + "  Masukkan nomor: ",
        end=""
    )
    choice = input()
    try:
        selected = int(choice) - 1
        if 0 <= selected < len(accounts):
            return accounts[selected]
        else:
            print(Fore.RED + "❌ Pilihan tidak valid. Silakan pilih nomor yang tersedia.")
            return None
    except ValueError:
        print(Fore.RED + "❌ Input harus berupa angka.")
        return None
            
def select_made_for_kids():
    """Memilih apakah video ditujukan untuk anak-anak atau tidak"""
    print(Fore.CYAN + "\n  ╭─────────────────────────╮")
    print(Fore.CYAN + "  │" + Fore.YELLOW + " 👥 TARGET AUDIENCE      " + Fore.CYAN + "│")
    print(Fore.CYAN + "  ├─────────────────────────┤")
    print(Fore.CYAN + "  │" + Fore.GREEN + " 1. Untuk Anak-Anak      " + Fore.CYAN + "│")
    print(Fore.CYAN + "  ├─────────────────────────┤")
    print(Fore.CYAN + "  │" + Fore.GREEN + " 2. Bukan Untuk Anak     " + Fore.CYAN + "│")
    print(Fore.CYAN + "  ╰─────────────────────────╯")
    
    choice = input(Fore.GREEN + "\n🔢 Pilih target audience (1/2): ")
    if choice == "1":
        return True
    elif choice == "2":
        return False
    else:
        print(Fore.RED + "❌ Pilihan tidak valid. Default ke 'Bukan untuk Anak-anak'.")
        return False
            
def main():
    try:
        account = select_account()
        if not account:
            return

        # Pilih apakah video untuk anak-anak atau tidak
        made_for_kids = select_made_for_kids()

        account_path = os.path.join(ACCOUNTS_FOLDER, account)
        token_path = os.path.join(account_path, "token.pkl")
        print(Fore.CYAN + f"\n🔑 Akun: {account}")
        youtube = authenticate(token_path)
        
        if not youtube:
            print(Fore.RED + "❌ Gagal melakukan autentikasi.")
            return

        # Coba memuat video files dengan penanganan error
        try:
            video_files = [f for f in os.listdir(account_path) if f.lower().endswith(".mp4")]
            video_files = video_files[:MAX_VIDEOS_PER_ACCOUNT]
        except Exception as e:
            print(Fore.RED + f"❌ Error saat memuat video files: {str(e)}")
            return

        if not video_files:
            print("📭 Tidak ada video ditemukan.")
            return

        print(Fore.YELLOW + f"🎬 Menemukan {len(video_files)} video untuk diupload")
        
        for i, video in enumerate(video_files):
            video_path = os.path.join(account_path, video)
            print(Fore.CYAN + f"\n📝 Memproses video {i+1}/{len(video_files)}: {video}")
            
            # Upload video dengan pengaturan madeForKids
            success = upload_video(youtube, video_path, made_for_kids)
            
            # Tambahkan delay untuk menghindari rate limit
            if success and i < len(video_files) - 1:  # Jangan delay setelah video terakhir
                print(Fore.MAGENTA + "⏳ Menunggu 5 detik sebelum upload berikutnya (rate limit protection)...")
                time.sleep(5)
                
    except Exception as e:
        print(Fore.RED + f"❌ Error tidak terduga dalam fungsi main: {str(e)}")
            
if __name__ == "__main__":
    main()
