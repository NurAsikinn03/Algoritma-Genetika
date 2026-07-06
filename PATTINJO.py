import random

# =====================================================================
# 1. DATASET / DATABASE KAMUS BAHASA DAERAH PATTINJO
#    (Suku Pattinjo, Kec. Lembang, Kab. Pinrang, Sulawesi Selatan)

#   Nama: Nur Asikin
#   Nim: 105841104524
#   Kelas: 4B
# =====================================================================
kamus = [
    ("CAMMIN",   "cermin"),
    ("MEJA",     "meja"),
    ("KASE",     "kaset"),
    ("PAMMUTTU", "wajan"),
    ("PATTAPI",  "nyiru"),
    ("PANTENG",  "ember"),
    ("KACA",     "gelas"),
    ("GOLO",     "bola"),
    ("GOLI",     "kelereng"),
    ("KASORO",   "kasur"),
    ("ESBO",     "kulkas"),
    ("BATTOA",   "besar"),
    ("MALAMPE",  "panjang"),
    ("MALEBU",   "bulat"),
    ("SAPULO",   "sepuluh"),
]


# 2. STATE / VARIABEL GLOBAL UNTUK PROSES ALGORITMA GENETIKA

POP_SIZE = 6
MUTATION_RATE = 0.2
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# --- BARU: batas maksimal generasi supaya loop otomatis tidak berjalan
#     selamanya kalau target sulit ditemukan (misal huruf langka / typo).
MAX_GENERASI = 100

target_word = None
generasi_ke = 0
population = []
fitness_values = []
probabilities = []
intervals = []
parents = []
children_crossover = []
children_mutasi = []

# --- BARU: menyimpan histori individu terbaik tiap generasi, dipakai
#     untuk menampilkan grafik/ringkasan perkembangan fitness di menu 11.
riwayat_terbaik = []   # list of tuple (generasi_ke, individu_terbaik, fitness_terbaik)


# 3. MENU 1: TAMPILKAN KAMUS

def tampilkan_kamus():
    print("\n=== KAMUS BAHASA DAERAH PATTINJO ===")
    print(f"{'No':<4}{'Kata Pattinjo':<15}{'Arti (Indonesia)':<20}")
    print("-" * 39)
    for i, (kata, arti) in enumerate(kamus, start=1):
        print(f"{i:<4}{kata:<15}{arti:<20}")


# 4. MENU 2: CARI KATA (dua arah: Pattinjo -> Indonesia / sebaliknya)

def cari_kata():
    kunci = input("Masukkan kata (Pattinjo atau Indonesia) yang dicari: ").strip().lower()
    ditemukan = False
    for kata, arti in kamus:
        if kunci == kata.lower():
            print(f"'{kata}' (Pattinjo) artinya -> '{arti}' (Indonesia)")
            ditemukan = True
        elif kunci == arti.lower():
            print(f"'{arti}' (Indonesia) dalam bahasa Pattinjo -> '{kata}'")
            ditemukan = True
    if not ditemukan:
        print("Kata tidak ditemukan dalam kamus.")


# FUNGSI BANTU: pilih kata target dari kamus & bangkitkan populasi awal

def pilih_target():
    global target_word
    tampilkan_kamus()
    try:
        no = int(input("\nPilih nomor kata sebagai TARGET pencarian GA: "))
        target_word = kamus[no - 1][0].upper()
        print(f"Kata target terpilih: {target_word}")
    except (ValueError, IndexError):
        print("Nomor tidak valid, target di-set default ke kata pertama.")
        target_word = kamus[0][0].upper()


def bangkitkan_populasi_awal():
    """
    Populasi awal dibentuk dengan mengacak 1-2 posisi huruf dari kata
    target, sehingga awalnya populasi memiliki variasi tingkat
    kecocokan (fitness) terhadap target, persis seperti ilustrasi
    pada materi (I1: KOTA, I2: KITA, I3: DATA, I4: KASA, dst).
    """
    global population
    population = []
    n = len(target_word)
    for _ in range(POP_SIZE):
        individu = list(target_word)
        jumlah_acak = random.randint(1, max(1, n // 2))
        posisi_acak = random.sample(range(n), jumlah_acak)
        for pos in posisi_acak:
            huruf_baru = random.choice(ALPHABET)
            individu[pos] = huruf_baru
        population.append("".join(individu))


# 5. MENU 4: TAMPILKAN POPULASI

def tampilkan_populasi():
    if not population:
        print("Populasi belum dibuat. Jalankan menu 3 terlebih dahulu.")
        return
    print(f"\n=== POPULASI GENERASI KE-{generasi_ke} (Target: {target_word}) ===")
    for i, ind in enumerate(population, start=1):
        print(f"Individu {i}: {ind}")


# 6. MENU 5: HASIL FITNESS
#    fitness = (jumlah huruf yang cocok posisinya) / (panjang kata)

def hitung_fitness(individu):
    cocok = sum(1 for a, b in zip(individu, target_word) if a == b)
    return cocok / len(target_word)


def hasil_fitness():
    global fitness_values
    if not population:
        print("Populasi belum dibuat. Jalankan menu 3 terlebih dahulu.")
        return
    fitness_values = []
    print(f"\n=== PERHITUNGAN FITNESS (Target: {target_word}) ===")
    print(f"{'Individu':<12}{'Kromosom':<12}{'Huruf Cocok':<14}{'Fitness':<10}")
    print("-" * 48)
    for i, ind in enumerate(population, start=1):
        cocok = sum(1 for a, b in zip(ind, target_word) if a == b)
        fit = cocok / len(target_word)
        fitness_values.append(fit)
        print(f"I{i:<11}{ind:<12}{cocok:<14}{fit:<10.2f}")
    print(f"Total fitness populasi : {sum(fitness_values):.2f}")


# 7. MENU 6: SELEKSI ROULETTE (Roulette Wheel Selection)

def seleksi_roulette():
    global probabilities, intervals, parents
    if not fitness_values:
        print("Fitness belum dihitung. Jalankan menu 5 terlebih dahulu.")
        return

    total_fitness = sum(fitness_values)
    print(f"\n=== PERHITUNGAN PROBABILITAS & INTERVAL SELEKSI ROULETTE ===")
    if total_fitness == 0:
        print("Total fitness = 0, seleksi dilakukan acak merata.")
        probabilities = [1 / len(population)] * len(population)
    else:
        probabilities = [f / total_fitness for f in fitness_values]

    intervals = []
    batas_bawah = 0.0
    print(f"{'Individu':<10}{'Fitness':<10}{'Probabilitas':<14}{'Interval':<20}")
    print("-" * 54)
    for i, (fit, prob) in enumerate(zip(fitness_values, probabilities), start=1):
        batas_atas = batas_bawah + prob
        intervals.append((batas_bawah, batas_atas))
        print(f"I{i:<9}{fit:<10.2f}{prob:<14.3f}{batas_bawah:.3f} - {batas_atas:.3f}")
        batas_bawah = batas_atas

    # proses "putaran roda roulette" sebanyak POP_SIZE kali
    parents = []
    print("\nProses Pemutaran Roulette Wheel:")
    for putaran in range(1, POP_SIZE + 1):
        r = random.random()
        for i, (bawah, atas) in enumerate(intervals):
            if bawah <= r < atas or (i == len(intervals) - 1 and r == 1.0):
                terpilih = population[i]
                parents.append(terpilih)
                print(f"Putaran {putaran}: angka acak r = {r:.3f} -> jatuh di interval "
                      f"I{i+1} ({bawah:.3f}-{atas:.3f}) -> terpilih {terpilih}")
                break

    print("\nIndukan (parents) hasil seleksi:", parents)


# 8. MENU 7: CROSS OVER (Pindah Silang satu titik)

def cross_over():
    global children_crossover
    if not parents:
        print("Belum ada hasil seleksi. Jalankan menu 6 terlebih dahulu.")
        return

    print("\n=== PERHITUNGAN CROSS OVER (Pindah Silang 1 Titik) ===")
    children_crossover = []
    pasangan_parents = list(parents)
    if len(pasangan_parents) % 2 != 0:
        pasangan_parents.append(random.choice(parents))  # genapkan jika ganjil

    n = len(target_word)
    for i in range(0, len(pasangan_parents), 2):
        p1 = pasangan_parents[i]
        p2 = pasangan_parents[i + 1]
        titik = random.randint(1, n - 1) if n > 1 else 1
        anak1 = p1[:titik] + p2[titik:]
        anak2 = p2[:titik] + p1[titik:]
        children_crossover.extend([anak1, anak2])
        print(f"Parent A = {p1} | Parent B = {p2} | Titik potong = {titik}")
        print(f"  -> Child 1 = {p1[:titik]} + {p2[titik:]} = {anak1}")
        print(f"  -> Child 2 = {p2[:titik]} + {p1[titik:]} = {anak2}")

    children_crossover = children_crossover[:POP_SIZE]
    print("\nHasil populasi anak (setelah crossover):", children_crossover)


# 9. MENU 8: MUTASI

def mutasi():
    global children_mutasi
    if not children_crossover:
        print("Belum ada hasil crossover. Jalankan menu 7 terlebih dahulu.")
        return

    print(f"\n=== PERHITUNGAN MUTASI (peluang mutasi = {MUTATION_RATE:.0%} per gen) ===")
    children_mutasi = []
    for idx, anak in enumerate(children_crossover, start=1):
        anak_list = list(anak)
        termutasi = False
        for pos in range(len(anak_list)):
            r = random.random()
            if r < MUTATION_RATE:
                huruf_lama = anak_list[pos]
                huruf_baru = random.choice([c for c in ALPHABET if c != huruf_lama])
                anak_list[pos] = huruf_baru
                print(f"Child {idx} ({anak}): posisi {pos+1} r={r:.3f} < {MUTATION_RATE} "
                      f"-> gen '{huruf_lama}' bermutasi jadi '{huruf_baru}'")
                termutasi = True
        hasil = "".join(anak_list)
        if not termutasi:
            print(f"Child {idx} ({anak}): tidak ada gen yang bermutasi.")
        children_mutasi.append(hasil)

    print("\nPopulasi anak setelah mutasi:", children_mutasi)


# 10. MENU 9: GENERASI BARU (regenerasi populasi + evaluasi)
#     --- DIKEMBANGKAN: sekarang mengembalikan (individu_terbaik, fitness_terbaik,
#         status_ketemu) supaya bisa dipakai oleh loop otomatis di menu 11,
#         dan mencatat riwayat setiap generasi ke `riwayat_terbaik`.

def generasi_baru():
    global population, generasi_ke
    if not children_mutasi:
        print("Belum ada hasil mutasi. Jalankan menu 8 terlebih dahulu.")
        return None, None, False

    population = list(children_mutasi)
    generasi_ke += 1

    print(f"\n=== POPULASI BARU - GENERASI KE-{generasi_ke} ===")
    best_ind, best_fit = None, -1
    for i, ind in enumerate(population, start=1):
        fit = hitung_fitness(ind)
        print(f"Individu {i}: {ind}  | fitness = {fit:.2f}")
        if fit > best_fit:
            best_fit, best_ind = fit, ind

    print(f"\nIndividu terbaik generasi ke-{generasi_ke}: {best_ind} "
          f"(fitness = {best_fit:.2f}) | Target: {target_word}")

    ketemu = (best_ind == target_word)
    riwayat_terbaik.append((generasi_ke, best_ind, best_fit))

    if ketemu:
        print(">> Kata target berhasil ditemukan!")

    return best_ind, best_fit, ketemu


# --- BARU: satu paket "siklus regenerasi" (seleksi -> crossover -> mutasi ->
#     generasi baru) yang dipanggil berulang oleh menu 11 tanpa perlu
#     interaksi input dari pengguna di setiap tahap.

def satu_siklus_regenerasi():
    hasil_fitness()
    seleksi_roulette()
    cross_over()
    mutasi()
    return generasi_baru()


# 11. MENU 3: JALANKAN ALGORITMA GENETIKA (pipeline 1 generasi awal, manual)

def jalankan_algoritma_genetika():
    global generasi_ke, riwayat_terbaik
    generasi_ke = 0
    riwayat_terbaik = []
    pilih_target()
    bangkitkan_populasi_awal()
    tampilkan_populasi()
    hasil_fitness()
    seleksi_roulette()
    cross_over()
    mutasi()
    generasi_baru()
    print("\n(Jika kata target belum ditemukan, gunakan menu 11 untuk "
          "melanjutkan otomatis ke generasi-generasi berikutnya, "
          "atau tekan menu 6-7-8-9 secara manual satu per satu.)")


# --- BARU: MENU 11 - LANJUTKAN OTOMATIS SAMPAI KETEMU / GENERASI MAKSIMAL
#     Ini jawaban untuk kasus seperti kata "PAMMUTTU" yang di Generasi ke-1
#     baru mencapai fitness 0.62 (belum sama persis). Fungsi ini akan terus
#     mengulang siklus regenerasi (seleksi-crossover-mutasi-generasi baru)
#     secara otomatis, generasi demi generasi, sampai:
#       a) individu terbaik == target_word (fitness sempurna 1.00), atau
#       b) jumlah generasi mencapai MAX_GENERASI (supaya tidak infinite loop).

def lanjutkan_otomatis():
    if target_word is None or not population:
        print("Belum ada proses GA yang berjalan. Jalankan menu 3 terlebih dahulu.")
        return

    print(f"\n=== MELANJUTKAN OTOMATIS DARI GENERASI KE-{generasi_ke} "
          f"(Target: {target_word}, Maks. {MAX_GENERASI} generasi) ===")

    ketemu = False
    while generasi_ke < MAX_GENERASI and not ketemu:
        best_ind, best_fit, ketemu = satu_siklus_regenerasi()

    print("\n--- RINGKASAN PERKEMBANGAN FITNESS TIAP GENERASI ---")
    for gen, ind, fit in riwayat_terbaik:
        tanda = "  <-- TARGET DITEMUKAN" if ind == target_word else ""
        print(f"Generasi ke-{gen}: individu terbaik = {ind} (fitness = {fit:.2f}){tanda}")

    if ketemu:
        print(f"\n>> Kata target '{target_word}' berhasil ditemukan pada "
              f"Generasi ke-{generasi_ke}.")
    else:
        print(f"\n>> Kata target belum ditemukan hingga batas {MAX_GENERASI} 3generasi. "
              f"Individu terbaik terakhir: {population[0] if population else '-'}.")


# MENU UTAMA (MAIN PROGRAM)

def main():
    while True:
        print("\n=== Kamus Bahasa Daerah Pattinjo ===")
        print("1. Tampilkan Kamus")
        print("2. Cari Kata")
        print("3. Jalankan Algoritma Genetika (Generasi ke-1)")
        print("4. Tampilkan Populasi")
        print("5. Hasil Fitness")
        print("6. Seleksi Roulette")
        print("7. Cross Over")
        print("8. Mutasi")
        print("9. Generasi Baru (1 langkah manual)")
        print("10. Keluar")
        print("11. Lanjutkan Otomatis Hingga Ketemu / Generasi Maksimal")

        pilihan = input("Pilih menu (1-11): ").strip()

        if pilihan == "1":
            tampilkan_kamus()
        elif pilihan == "2":
            cari_kata()
        elif pilihan == "3":
            jalankan_algoritma_genetika()
        elif pilihan == "4":
            tampilkan_populasi()
        elif pilihan == "5":
            hasil_fitness()
        elif pilihan == "6":
            seleksi_roulette()
        elif pilihan == "7":
            cross_over()
        elif pilihan == "8":
            mutasi()
        elif pilihan == "9":
            generasi_baru()
        elif pilihan == "10":
            print("Terima kasih. Program selesai.")
            break
        elif pilihan == "11":
            lanjutkan_otomatis()
        else:
            print("Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main()