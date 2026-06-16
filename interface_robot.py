import time
import math
import random  # Mengaktifkan library pengacak bawaan Python
import google.generativeai as genai
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# =====================================================================
# CONFIGURATION & INITIALIZATION
# =====================================================================
GEMINI_API_KEY = "AQ.Ab8RN6LfU3Zr6F--Bf8XWzhMi1PoAuWGWYoJ7prhT9GGk_DfWQ"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

try:
    sim_client = RemoteAPIClient()
    sim = sim_client.getObject('sim')
    print("Inisialisasi Remote API CoppeliaSim Sukses!")
except Exception as e:
    print(f"Gagal terhubung ke aplikasi CoppeliaSim. Detail: {e}")

def hitung_jarak(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# PEMETAAN TARGET BARU UNTUK LABIRIN SALIB & TIANG (image_eab54a.jpg)
MAP_WARNA = {
    "/Goal[0]": "Target Ruang 1 (Goal 0)",
    "/Goal[1]": "Target Ruang 2 (Goal 1)",
    "/Goal[2]": "Target Ruang 3 (Goal 2)",
    "/Goal[3]": "Target Ruang 4 (Goal 3)"
}

# =====================================================================
# BRAIN ENGINE: SUPER CHAOS EDITION (BENAR-BENAR ACAK TOTAL & SUSAH DITEBAK)
# =====================================================================
def ai_pilih_target_warna(daftar_pilihan, warna_tereksekusi):
    # SUNTIKAN KEACAKAN 1: Mengacak urutan list pilihan di Python sebelum dikirim ke AI
    pilihan_diacak = list(daftar_pilihan)
    random.shuffle(pilihan_diacak)
    
    teks_pilihan = ""
    for nama, pos, jarak in pilihan_diacak:
        nama_warna = MAP_WARNA.get(nama, "Tidak Diketahui")
        teks_pilihan += f"- {nama_warna} (ID: {nama}): Jarak saat ini={jarak:.2f}m\n"

    # SUNTIKAN KEACAKAN 2: Mengubah kepribadian AI menjadi penjelajah impulsif
    prompt_misi = f"""
    Kamu adalah otak robot penjelajah yang memiliki kepribadian impulsif, tidak terduga, dan berjiwa seni bebas.
    Kamu sedang berada di labirin salib. 

    Target ruang yang tersedia di sekitarmu (urutannya sudah diacak oleh takdir):
    {teks_pilihan}
    
    Target yang sudah sukses kamu kunjungi sebelumnya: {warna_tereksekusi}

    PERINTAH MUTLAK:
    1. Pilih satu ID target berikutnya yang belum dikunjungi.
    2. JANGAN PERNAH gunakan logika jarak terdekat! Pilihlah secara acak, spontan, berdasarkan mood emosional instan, atau pilih yang paling jauh sekaligus.
    3. Manusia yang sedang menontonmu ingin melihat robot yang bergerak eksentrik dan tidak punya pola tetap. Buat mereka bingung dengan pilihanmu!

    Output harus berupa teks JSON mentah dengan format persis seperti ini:
    {{"target_terpilih": "ID_TARGET", "alasan": "ALASAN_KREATIF_DAN_IMPULSIF_KAMU"}}
    """
    try:
        # TEMPERATURE DISET MAKSIMAL KE 1.0 (TINGKAT KREATIF DAN ACAK TERTINGGI)
        response = model.generate_content(
            prompt_misi,
            generation_config={"response_mime_type": "application/json", "temperature": 1.0}
        )
        import json
        hasil = json.loads(response.text)
        return hasil.get("target_terpilih"), hasil.get("alasan", "Pilihan acak spontan AI.")
    except Exception as e:
        print(f"⚠️ [API ERROR] Gagal meminta keputusan AI: {e}. Menggunakan opsi cadangan.")
        # Jika API error, Python yang akan mengacak secara paksa sebagai backup darurat
        pilihan_darurat = random.choice(daftar_pilihan)
        return pilihan_darurat[0], "Sistem otomatis mengambil opsi acak darurat akibat gangguan jaringan."

# =====================================================================
# MAIN LOOP NAVIGASI LABIRIN DENGAN LOGIKA ANTI-MENTOK TOTAL
# =====================================================================
def jalankan_misi_pilihan_ai():
    try:
        robot_handle = sim.getObject('/PioneerP3DX')
        left_motor = sim.getObject('/PioneerP3DX/leftMotor')
        right_motor = sim.getObject('/PioneerP3DX/rightMotor')
        
        # Inisialisasi 16 sensor ultrasonik Pioneer P3DX (image_ea44c5.jpg)
        sensor_handles = [sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]') for i in range(16)]
        
        # -----------------------------------------------------------------
        # BRUTE-FORCE PATH DETECTION UNTUK ARENA BARU (ANTI-0 GOAL)
        # -----------------------------------------------------------------
        daftar_objek_warna = {}
        for i in range(4):
            variasi_path = [f'/Goal[{i}]', f'Goal[{i}]', f'./Goal[{i}]']
            handle_ketemu = None
            
            for path in variasi_path:
                try:
                    handle = sim.getObject(path)
                    if handle != -1:
                        handle_ketemu = handle
                        break
                except Exception:
                    continue
            
            if handle_ketemu is not None:
                daftar_objek_warna[f'/Goal[{i}]'] = handle_ketemu

        print(f"Sukses mendeteksi {len(daftar_objek_warna)} target objek Goal di arena!")
        
        if len(daftar_objek_warna) == 0:
            print("\n❌ [ERROR] Target tetap terbaca 0! Pastikan nama di simulator adalah Goal[0] sampai Goal[3]")
            return

    except Exception as e:
        print(f"Error inisialisasi hardware simulator: {e}")
        return

    sim.startSimulation()
    print("Simulasi Dimulai! Sistem Navigasi Cerdas Aktif...")

    warna_tereksekusi = []
    
    try:
        while len(warna_tereksekusi) < len(daftar_objek_warna):
            pos_robot = sim.getObjectPosition(robot_handle, -1)
            pilihan_tersedia = []
            
            for nama, handle in daftar_objek_warna.items():
                if MAP_WARNA.get(nama) not in warna_tereksekusi:
                    pos_objek = sim.getObjectPosition(handle, -1)
                    jarak_ke_objek = hitung_jarak(pos_robot, pos_objek)
                    pilihan_tersedia.append((nama, pos_objek, jarak_ke_objek))
            
            if not pilihan_tersedia:
                break
                
            print("\n" + "="*60)
            print("🎲 AI Gemini sedang menentukan rute acak otonom...")
            id_target_terpilih, alasan_ai = ai_pilih_target_warna(pilihan_tersedia, warna_tereksekusi)
            
            warna_aktif = MAP_WARNA.get(id_target_terpilih, "Misteri")
            handle_target_aktif = daftar_objek_warna[id_target_terpilih]
            
            print(f"🎯 TARGET PILIHAN ACAK AI: {warna_aktif} ({id_target_terpilih})")
            print(f"💡 ALASAN EMOSIONAL AI: \"{alasan_ai}\"")
            print("="*60)
            
            while True:
                # 1. BACA SELURUH 16 INDEKS SENSOR ULTRASONIK PIONEER
                distansi = [99.0] * 16
                for i in range(16):
                    res, dist, _, _, _ = sim.readProximitySensor(sensor_handles[i])
                    if res > 0:
                        distansi[i] = dist

                # Kelompokkan area pembacaan sensor secara presisi (image_ea44c5.jpg)
                jarak_depan = min(distansi[2], distansi[3], distansi[4], distansi[5])  
                jarak_serong_kiri = min(distansi[1], distansi[2])                   
                jarak_serong_kanan = min(distansi[5], distansi[6])                  
                jarak_samping_kiri = min(distansi[0], distansi[15])                 
                jarak_samping_kanan = min(distansi[7], distansi[8])                 

                # 2. HITUNG GEOMETRI KORDINAT KE TARGET
                pos_robot = sim.getObjectPosition(robot_handle, -1)
                pos_goal = sim.getObjectPosition(handle_target_aktif, -1)
                orientasi_robot = sim.getObjectOrientation(robot_handle, -1)
                
                sudut_robot_sekarang = orientasi_robot[2]
                jarak_ke_goal = hitung_jarak(pos_robot, pos_goal)
                
                sudut_ke_goal = math.atan2(pos_goal[1] - pos_robot[1], pos_goal[0] - pos_robot[0])
                error_sudut = math.atan2(math.sin(sudut_ke_goal - sudut_robot_sekarang), math.cos(sudut_ke_goal - sudut_robot_sekarang))

                # KONDISI SUKSES MENYENTUH TARGET
                if jarak_ke_goal < 0.45: 
                    print(f"💥 SUCCESS: Target {warna_aktif} berhasil dicapai!")
                    warna_tereksekusi.append(warna_aktif)
                    sim.setJointTargetVelocity(left_motor, 0)
                    sim.setJointTargetVelocity(right_motor, 0)
                    time.sleep(1.0)
                    break

                # 3. HIERARKI KONTROL: JIKA SEKAT TEMBOK DEPAN SANGAT DEKAT (< 0.52m)
                if jarak_depan < 0.52 or jarak_serong_kiri < 0.42 or jarak_serong_kanan < 0.42:
                    print(f"⚠️ [WALL BLOCK] Depan: {jarak_depan:.2f}m. Abaikan target, paksa banting setir!")
                    
                    if jarak_depan < 0.28: 
                        v_kiri, v_kanan = -1.0, -1.0
                    elif jarak_serong_kiri < jarak_serong_kanan or jarak_samping_kiri < jarak_samping_kanan:
                        v_kiri, v_kanan = 1.8, -1.2
                    else:
                        v_kiri, v_kanan = -1.2, 1.8

                # JIKA DI SAMPING KANAN/KIRI MASIH ADA SEKAT DEKAT
                elif jarak_samping_kiri < 0.45:
                    print("⚠️ [SIDE WALL LEFT] Menjaga jarak lambung kiri...")
                    v_kiri, v_kanan = 1.4, 0.8 
                elif jarak_samping_kanan < 0.45:
                    print("⚠️ [SIDE WALL RIGHT] Menjaga jarak lambung kanan...")
                    v_kiri, v_kanan = 0.8, 1.4 

                # KONDISI JALUR BENAR-BENAR BERSIH DAN AMAN: KEJAR TARGET
                else:
                    kp = 1.6          
                    v_dasar = 1.4     
                    kontrol_kemudi = kp * error_sudut
                    
                    v_kiri = max(-3.0, min(3.0, v_dasar - kontrol_kemudi))
                    v_kanan = max(-3.0, min(3.0, v_dasar + kontrol_kemudi))
                    print(f"🏃 [NAVIGASI] Bebas sekat, memburu {warna_aktif} | Jarak: {jarak_ke_goal:.2f}m")

                # Terapkan kecepatan ke motor roda simulator
                sim.setJointTargetVelocity(left_motor, v_kiri)
                sim.setJointTargetVelocity(right_motor, v_kanan)
                time.sleep(0.02) 

        print("\n🏆 FINISH SUKSES! Semua target pilihan acak AI berhasil dijalajahi!")

    except KeyboardInterrupt:
        print("\nSimulasi dihentikan manual.")
    finallys:
        sim.setJointTargetVelocity(left_motor, 0)
        sim.setJointTargetVelocity(right_motor, 0)
        sim.stopSimulation()

if __name__ == "__main__":
    jalankan_misi_pilihan_ai()