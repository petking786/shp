import requests                                   import json
import time
import os                                         import re

BOT_TOKEN = "8795407763:AAH95WgvA4Qqna5MwSfLawuLZ4z5XsQvAsc"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
DATA_FILE = "akun_data.json"

# === DATA ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"akun": [], "riwayat": []}            
def save_data(data):                                  with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === KIRIM PESAN ===
def kirim_pesan(chat_id, teks, keyboard=None):
    data = {"chat_id": chat_id, "text": teks, "parse_mode": "Markdown"}
    if keyboard:
        data["reply_markup"] = json.dumps({"keyboard": keyboard, "resize_keyboard": True})
    try:
        requests.post(f"{API_URL}/sendMessage", data=data)
    except Exception as e:
        print(f"❌ Error kirim pesan: {e}")
                                                  # === MENU UTAMA ===
def menu_utama(chat_id, nama):                        keyboard = [
        [{"text": "📋 Tambah Akun"}],
        [{"text": "👤 Daftar Akun"}],                     [{"text": "🛒 Checkout Barang"}, {"text": "⚡ Token PLN"}],
        [{"text": "📊 Riwayat Pesanan"}]
    ]
    kirim_pesan(chat_id,
        f"🛒 Halo {nama}! Selamat datang di Shopee Bot Gratis\n\n"
        "✅ 100% Gratis — Tanpa Langganan\n"
        "✅ Simpan Banyak Akun\n"
        "✅ Checkout Barang & Token PLN\n\n"
        "Pilih menu di bawah 👇", keyboard)

# === TAMBAH AKUN ===
def tambah_akun(chat_id, teks):
    if not teks or teks in ["📋 Tambah Akun", "/batal"]:
        kirim_pesan(chat_id, "📋 Tempel cookies Shopee di bawah:\nKetik /batal untuk membatalkan.")
        return "tambah_akun"

    data = load_data()
    data["akun"].append({
        "id": len(data["akun"])+1,
        "nama": f"Akun {len(data['akun'])+1}",
        "cookies": teks,                                  "fp": ""
    })                                                save_data(data)                                   kirim_pesan(chat_id, "✅ *AKUN BERHASIL DITAMBAHKAN!*")
    return "menu"                                 
# === DAFTAR AKUN ===
def daftar_akun(chat_id):                             data = load_data()
    if not data["akun"]:                                  kirim_pesan(chat_id, "⚠️ Belum ada akun. Tekan 📋 Tambah Akun dulu.")
        return                                        teks = "👤 *DAFTAR AKUN:*\n\n"
    for a in data["akun"]:
        status = "✅ FP Lengkap" if a.get("fp") else "⚠️ FP Belum Diisi"
        teks += f"🆔 ID {a['id']} — {a['nama']}\n{status}\n\n"                                          kirim_pesan(chat_id, teks)
                                                  # === CHECKOUT BARANG ===
def proses_checkout(chat_id, teks, state_data):       if teks == "/batal":
        kirim_pesan(chat_id, "❌ Dibatalkan.")            return "menu", {}
                                                      if state_data.get("langkah") == "link":
        state_data["link"] = teks                         kirim_pesan(chat_id, "✅ Link diterima!\n 📦 Masukkan jumlah:")                                     state_data["langkah"] = "jumlah"
        return "checkout", state_data             
    if state_data.get("langkah") == "jumlah":             jml = teks if teks.isdigit() else "1"
        state_data["jumlah"] = jml                        data = load_data()
        data["riwayat"].append({                              "tipe": "barang",
            "link": state_data["link"],                       "jumlah": jml,
            "waktu": time.strftime('%d-%m-%Y %H:%M:%S')                                                     })
        save_data(data)                                   kirim_pesan(chat_id, f"✅ *CHECKOUT DIPROSES!*\n📦 Jumlah: {jml}")
        return "menu", {}                                                                               # Mulai baru
    kirim_pesan(chat_id, "🛒 Masukkan link produk Shopee:")                                             state_data["langkah"] = "link"
    return "checkout", state_data
                                                  # === TOKEN PLN ===
def proses_token(chat_id, teks, state_data):
    if teks == "/batal":                                  kirim_pesan(chat_id, "❌ Dibatalkan.")
        return "menu", {}
                                                      if state_data.get("langkah") == "meter":
        state_data["meter"] = teks
        kirim_pesan(chat_id, f"✅ Nomor Meter: {teks}\n💰 Masukkan nominal:")
        state_data["langkah"] = "nominal"
        return "token", state_data                
    if state_data.get("langkah") == "nominal":
        data = load_data()                                data["riwayat"].append({
            "tipe": "token-pln",
            "meter": state_data["meter"],                     "nominal": teks,
            "waktu": time.strftime('%d-%m-%Y %H:%M:%S')
        })                                                save_data(data)
        kirim_pesan(chat_id, f"✅ *TOKEN PLN DIPROSES!*\n🔢 Meter: {state_data['meter']}\n💰 Rp{teks}")                                                       return "menu", {}
                                                      kirim_pesan(chat_id, "⚡ Masukkan nomor meter:")                                                    state_data["langkah"] = "meter"
    return "token", state_data                    
# === RIWAYAT ===
def riwayat(chat_id):                                 data = load_data()
    if not data["riwayat"]:                               kirim_pesan(chat_id, "📊 Belum ada riwayat pesanan.")                                               return
    teks = "📊 *RIWAYAT PESANAN:*\n\n"
    for i, r in enumerate(reversed(data["riwayat"][-10:]), 1):
        icon = "🛒" if r["tipe"] == "barang" else "⚡"
        teks += f"{icon} {i}. {r['tipe'].upper()}\n🕐 {r['waktu']}\n"
        if r["tipe"] == "barang":                             teks += f"📦 Jumlah: {r['jumlah']}\n"
        else:                                                 teks += f"🔢 Meter: {r['meter']} — Rp{r['nominal']}\n"                                          teks += "─────────────\n"
    kirim_pesan(chat_id, teks)                    
# === MAIN LOOP ===
def main():                                           print("🔄 Memulai bot...")                        offset = 0
    state = {}  # {chat_id: {status, data}}           print("✅ BOT BERJALAN! 🤖")                      print("👉 Buka Telegram → cari bot kamu → ketik /start")
    print("⏹️  Tekan Ctrl+C untuk berhenti\n")                                                           while True:
        try:                                                  res = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 15}, timeout=20)                                                     data = res.json()                                 if not data.get("ok"):
                time.sleep(2)                                     continue                                                                                        for upd in data.get("result", []):                    offset = upd["update_id"] + 1                     msg = upd.get("message", {})                      chat_id = msg.get("chat", {}).get("id")
                teks = msg.get("text", "")
                nama = msg.get("from", {}).get("first_name", "Pengguna")

                if not chat_id:
                    continue                      
                # Ambil status saat ini
                curr_state = state.get(chat_id, {"status": "menu", "data": {}})
                status = curr_state["status"]
                sdata = curr_state["data"]        
                # === PERINTAH ===                                if teks == "/start":
                    menu_utama(chat_id, nama)
                    state[chat_id] = {"status": "menu", "data": {}}                                 
                elif teks == "📋 Tambah Akun" or status == "tambah_akun":
                    new_status, _ = tambah_akun(chat_id, teks)
                    state[chat_id] = {"status": new_status, "data": {}}                             
                elif teks == "👤 Daftar Akun":
                    daftar_akun(chat_id)

                elif teks == "🛒 Checkout Barang" or status == "checkout":
                    new_status, new_data = proses_checkout(chat_id, teks, sdata)
                    state[chat_id] = {"status": new_status, "data": new_data}

                elif teks == "⚡ Token PLN" or status == "token":
                    new_status, new_data = proses_token(chat_id, teks, sdata)
                    state[chat_id] = {"status": new_status, "data": new_data}                       
                elif teks == "📊 Riwayat Pesanan":
                    riwayat(chat_id)

                time.sleep(0.1)                   
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Bot dihentikan.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")                            time.sleep(3)

if __name__ == "__main__":
    main()
