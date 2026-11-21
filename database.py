import csv
import io
import json
import sqlite3


class TarlaDatabase:
    def __init__(self, db_path="tarla_verileri.db"):
        self.db_path = db_path
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS tarlalar (
                    id INTEGER PRIMARY KEY,
                    ad TEXT NOT NULL,
                    urun TEXT DEFAULT '',
                    donum REAL DEFAULT 0,
                    tohum_gider REAL DEFAULT 0,
                    mazot_gider REAL DEFAULT 0,
                    su_gider REAL DEFAULT 0,
                    malzeme_gider REAL DEFAULT 0,
                    hasat_gider REAL DEFAULT 0,
                    diger_gider REAL DEFAULT 0
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS depo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tur TEXT NOT NULL,
                    ad TEXT NOT NULL,
                    birim TEXT NOT NULL,
                    temel_birim TEXT NOT NULL,
                    miktar REAL NOT NULL,
                    fiyat REAL NOT NULL,
                    birim_fiyat REAL NOT NULL,
                    tarih TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS kullanimlar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarla_id INTEGER NOT NULL,
                    urun_id INTEGER NOT NULL,
                    miktar REAL NOT NULL,
                    maliyet REAL NOT NULL,
                    tarih TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS mazot_alis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    miktar REAL NOT NULL,
                    fiyat REAL NOT NULL,
                    birim_fiyat REAL NOT NULL,
                    tarih TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS mazot_cikis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarla_id INTEGER NOT NULL,
                    alis_id INTEGER NOT NULL,
                    miktar REAL NOT NULL,
                    birim_fiyat REAL NOT NULL,
                    maliyet REAL NOT NULL,
                    tarih TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS ek_tarla_gider (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarla_id INTEGER NOT NULL,
                    tur TEXT NOT NULL,
                    aciklama TEXT,
                    tutar REAL NOT NULL,
                    tarih TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS hasat_satis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarla_id INTEGER NOT NULL,
                    urun TEXT NOT NULL,
                    miktar REAL NOT NULL,
                    fiyat REAL NOT NULL,
                    gelir REAL NOT NULL,
                    tarih TEXT,
                    alici TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS ortak_giderler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aciklama TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    tutar REAL NOT NULL,
                    tarih TEXT,
                    paylasim TEXT NOT NULL
                )
            """)

            c.execute("SELECT COUNT(*) as cnt FROM tarlalar")
            if c.fetchone()["cnt"] == 0:
                for i in range(1, 11):
                    c.execute("INSERT INTO tarlalar (id, ad) VALUES (?, ?)", (i, f"Tarla {i}"))
            conn.commit()

    @staticmethod
    def birim_donustur(miktar: float, birim: str) -> float:
        if birim == "ton":
            return miktar * 1000.0
        if birim in ("ml", "gram"):
            return miktar / 1000.0
        return miktar

    @staticmethod
    def temel_birim_adi(birim: str) -> str:
        if birim in ("kg", "ton", "gram"):
            return "kg"
        if birim in ("litre", "ml"):
            return "litre"
        return "birim"

    # --- TARLALAR ---
    def get_tarlalar(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM tarlalar ORDER BY id").fetchall()]

    def update_tarla(self, tarla_id: int, ad: str, urun: str, donum: float, giderler: dict):
        with self.get_conn() as conn:
            conn.execute("""
                UPDATE tarlalar SET
                    ad = ?, urun = ?, donum = ?,
                    tohum_gider = ?, mazot_gider = ?, su_gider = ?,
                    malzeme_gider = ?, hasat_gider = ?, diger_gider = ?
                WHERE id = ?
            """, (
                ad, urun, donum,
                giderler.get("tohum_gider", 0.0),
                giderler.get("mazot_gider", 0.0),
                giderler.get("su_gider", 0.0),
                giderler.get("malzeme_gider", 0.0),
                giderler.get("hasat_gider", 0.0),
                giderler.get("diger_gider", 0.0),
                tarla_id,
            ))
            conn.commit()

    # --- EK TARLA GİDERİ ---
    def add_ek_gider(self, tarla_id: int, tur: str, aciklama: str, tutar: float, tarih: str):
        with self.get_conn() as conn:
            conn.execute(
                "INSERT INTO ek_tarla_gider (tarla_id, tur, aciklama, tutar, tarih) VALUES (?, ?, ?, ?, ?)",
                (tarla_id, tur, aciklama, tutar, tarih),
            )
            conn.commit()

    def get_ek_giderler(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT e.*, t.ad as tarla_ad FROM ek_tarla_gider e
                LEFT JOIN tarlalar t ON e.tarla_id = t.id ORDER BY e.id DESC
            """).fetchall()]

    def delete_ek_gider(self, gider_id: int):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM ek_tarla_gider WHERE id = ?", (gider_id,))
            conn.commit()

    # --- İLAÇ VE GÜBRE DEPOSU ---
    def add_depo_urun(self, tur: str, ad: str, miktar: float, birim: str, fiyat: float, tarih: str):
        temel_miktar = self.birim_donustur(miktar, birim)
        temel_birim = self.temel_birim_adi(birim)
        birim_fiyat = fiyat / temel_miktar if temel_miktar > 0 else 0.0
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO depo (tur, ad, birim, temel_birim, miktar, fiyat, birim_fiyat, tarih)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tur, ad, birim, temel_birim, temel_miktar, fiyat, birim_fiyat, tarih))
            conn.commit()

    def get_depo_urunler(self):
        with self.get_conn() as conn:
            urunler = [dict(r) for r in conn.execute("SELECT * FROM depo ORDER BY id DESC").fetchall()]
            for u in urunler:
                row = conn.execute(
                    "SELECT COALESCE(SUM(miktar), 0) as kull FROM kullanimlar WHERE urun_id = ?",
                    (u["id"],),
                ).fetchone()
                u["kullanilan"] = float(row["kull"])
                u["kalan"] = max(0.0, float(u["miktar"]) - u["kullanilan"])
                u["stok_degeri"] = u["kalan"] * float(u["birim_fiyat"])
            return urunler

    def delete_depo_urun(self, urun_id: int) -> tuple[bool, str]:
        with self.get_conn() as conn:
            cnt = conn.execute("SELECT COUNT(*) as c FROM kullanimlar WHERE urun_id = ?", (urun_id,)).fetchone()["c"]
            if cnt > 0:
                return False, "Bu üründen tarlalara çıkış yapılmış. Önce kullanım kayıtlarını silmelisin."
            conn.execute("DELETE FROM depo WHERE id = ?", (urun_id,))
            conn.commit()
            return True, "Ürün kaydı depodan silindi."

    def add_urun_kullanim(
        self, tarla_id: int, urun_id: int, girilen_miktar: float, cikis_birim: str, tarih: str
    ) -> tuple[bool, str]:
        urunler = self.get_depo_urunler()
        urun = next((x for x in urunler if x["id"] == urun_id), None)
        if not urun:
            return False, "Ürün bulunamadı."
        if urun["temel_birim"] != self.temel_birim_adi(cikis_birim):
            return False, f"Birim uyumsuzluğu! Bu ürün '{urun['temel_birim']}' bazlıdır."
        kullanilan = self.birim_donustur(girilen_miktar, cikis_birim)
        if kullanilan > urun["kalan"] + 1e-7:
            return False, f"Depoda yeterli ürün bulunmuyor. Kalan stok: {urun['kalan']:.3f} {urun['temel_birim']}"
        maliyet = kullanilan * float(urun["birim_fiyat"])
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO kullanimlar (tarla_id, urun_id, miktar, maliyet, tarih)
                VALUES (?, ?, ?, ?, ?)
            """, (tarla_id, urun_id, kullanilan, maliyet, tarih))
            conn.commit()
        return True, f"Ürün tarlaya kaydedildi. Maliyet: {maliyet:,.2f} TL"

    def get_kullanimlar(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT k.*, t.ad as tarla_ad, d.ad as urun_ad, d.temel_birim
                FROM kullanimlar k
                LEFT JOIN tarlalar t ON k.tarla_id = t.id
                LEFT JOIN depo d ON k.urun_id = d.id
                ORDER BY k.id DESC
            """).fetchall()]

    def delete_kullanim(self, kullanim_id: int):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM kullanimlar WHERE id = ?", (kullanim_id,))
            conn.commit()

    # --- MAZOT DEPOSU ---
    def add_mazot_alis(self, miktar: float, fiyat: float, tarih: str):
        birim_fiyat = fiyat / miktar if miktar > 0 else 0.0
        with self.get_conn() as conn:
            conn.execute(
                "INSERT INTO mazot_alis (miktar, fiyat, birim_fiyat, tarih) VALUES (?, ?, ?, ?)",
                (miktar, fiyat, birim_fiyat, tarih),
            )
            conn.commit()

    def get_mazot_alislar(self):
        with self.get_conn() as conn:
            alislar = [dict(r) for r in conn.execute("SELECT * FROM mazot_alis ORDER BY id DESC").fetchall()]
            for a in alislar:
                kull = conn.execute(
                    "SELECT COALESCE(SUM(miktar), 0) as k FROM mazot_cikis WHERE alis_id = ?",
                    (a["id"],),
                ).fetchone()["k"]
                a["kullanilan"] = float(kull)
                a["kalan"] = max(0.0, float(a["miktar"]) - a["kullanilan"])
                a["stok_degeri"] = a["kalan"] * float(a["birim_fiyat"])
            return alislar

    def delete_mazot_alis(self, alis_id: int) -> tuple[bool, str]:
        with self.get_conn() as conn:
            cnt = conn.execute("SELECT COUNT(*) as c FROM mazot_cikis WHERE alis_id = ?", (alis_id,)).fetchone()["c"]
            if cnt > 0:
                return False, "Bu mazot alışından çıkış yapılmış. Önce çıkış kayıtlarını silmelisin."
            conn.execute("DELETE FROM mazot_alis WHERE id = ?", (alis_id,))
            conn.commit()
            return True, "Mazot alış kaydı silindi."

    def add_mazot_cikis(self, tarla_id: int, alis_id: int, miktar: float, tarih: str) -> tuple[bool, str]:
        alislar = self.get_mazot_alislar()
        alis = next((x for x in alislar if x["id"] == alis_id), None)
        if not alis:
            return False, "Mazot alış kaydı bulunamadı."
        if miktar > alis["kalan"] + 1e-7:
            return False, f"Depoda yeterli mazot bulunmuyor. Kalan: {alis['kalan']:.2f} L"
        maliyet = miktar * float(alis["birim_fiyat"])
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO mazot_cikis (tarla_id, alis_id, miktar, birim_fiyat, maliyet, tarih)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (tarla_id, alis_id, miktar, alis["birim_fiyat"], maliyet, tarih))
            conn.commit()
        return True, f"Mazot tarlaya gönderildi. Maliyet: {maliyet:,.2f} TL"

    def get_mazot_cikislar(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT m.*, t.ad as tarla_ad FROM mazot_cikis m
                LEFT JOIN tarlalar t ON m.tarla_id = t.id ORDER BY m.id DESC
            """).fetchall()]

    def delete_mazot_cikis(self, cikis_id: int):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM mazot_cikis WHERE id = ?", (cikis_id,))
            conn.commit()

    # --- HASAT VE SATIŞ ---
    def add_hasat(self, tarla_id: int, urun: str, miktar: float, fiyat: float, tarih: str, alici: str):
        gelir = miktar * fiyat
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO hasat_satis (tarla_id, urun, miktar, fiyat, gelir, tarih, alici)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tarla_id, urun, miktar, fiyat, gelir, tarih, alici))
            conn.commit()

    def get_hasatlar(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute("""
                SELECT h.*, t.ad as tarla_ad FROM hasat_satis h
                LEFT JOIN tarlalar t ON h.tarla_id = t.id ORDER BY h.id DESC
            """).fetchall()]

    def delete_hasat(self, hasat_id: int):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM hasat_satis WHERE id = ?", (hasat_id,))
            conn.commit()

    # --- ORTAK GİDERLER ---
    def add_ortak_gider(self, aciklama: str, kategori: str, tutar: float, tarih: str, paylasim: str):
        with self.get_conn() as conn:
            conn.execute("""
                INSERT INTO ortak_giderler (aciklama, kategori, tutar, tarih, paylasim)
                VALUES (?, ?, ?, ?, ?)
            """, (aciklama, kategori, tutar, tarih, paylasim))
            conn.commit()

    def get_ortak_giderler(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM ortak_giderler ORDER BY id DESC").fetchall()]

    def delete_ortak_gider(self, gider_id: int):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM ortak_giderler WHERE id = ?", (gider_id,))
            conn.commit()

    # --- KAPSAMLI FİNANSAL HESAPLAMALAR ---
    def get_tarla_finans_ozeti(self, tarla_id: int) -> dict:
        tarlalar = self.get_tarlalar()
        tarla = next((t for t in tarlalar if t["id"] == tarla_id), None)
        if not tarla:
            return {}

        temel = float(
            tarla["tohum_gider"]
            + tarla["mazot_gider"]
            + tarla["su_gider"]
            + tarla["malzeme_gider"]
            + tarla["hasat_gider"]
            + tarla["diger_gider"]
        )
        with self.get_conn() as conn:
            ek_gider = float(conn.execute("SELECT COALESCE(SUM(tutar), 0) as s FROM ek_tarla_gider WHERE tarla_id = ?", (tarla_id,)).fetchone()["s"])
            ilac_gubre = float(conn.execute("SELECT COALESCE(SUM(maliyet), 0) as s FROM kullanimlar WHERE tarla_id = ?", (tarla_id,)).fetchone()["s"])
            mazot_depo = float(conn.execute("SELECT COALESCE(SUM(maliyet), 0) as s FROM mazot_cikis WHERE tarla_id = ?", (tarla_id,)).fetchone()["s"])
            gelir = float(conn.execute("SELECT COALESCE(SUM(gelir), 0) as s FROM hasat_satis WHERE tarla_id = ?", (tarla_id,)).fetchone()["s"])

            ek_liste = [dict(r) for r in conn.execute("SELECT * FROM ek_tarla_gider WHERE tarla_id = ? ORDER BY id DESC", (tarla_id,)).fetchall()]
            mazot_liste = [dict(r) for r in conn.execute("SELECT * FROM mazot_cikis WHERE tarla_id = ? ORDER BY id DESC", (tarla_id,)).fetchall()]
            ilac_liste = [dict(r) for r in conn.execute("""
                SELECT k.*, d.ad as urun_ad, d.temel_birim
                FROM kullanimlar k LEFT JOIN depo d ON k.urun_id = d.id
                WHERE k.tarla_id = ? ORDER BY k.id DESC
            """, (tarla_id,)).fetchall()]
            hasat_liste = [dict(r) for r in conn.execute("SELECT * FROM hasat_satis WHERE tarla_id = ? ORDER BY id DESC", (tarla_id,)).fetchall()]

        toplam_donum = sum(float(t["donum"]) for t in tarlalar)
        tarla_sayisi = len(tarlalar)
        ortak_giderler = self.get_ortak_giderler()
        ortak_pay = 0.0
        for g in ortak_giderler:
            tutar = float(g["tutar"])
            if g["paylasim"] == "esit":
                ortak_pay += (tutar / tarla_sayisi) if tarla_sayisi > 0 else 0.0
            else:
                if toplam_donum > 0:
                    ortak_pay += tutar * (float(tarla["donum"]) / toplam_donum)

        toplam_gider = temel + ek_gider + ilac_gubre + mazot_depo + ortak_pay
        net = gelir - toplam_gider

        return {
            "tarla": tarla,
            "temel": temel,
            "ek_gider": ek_gider,
            "ilac_gubre": ilac_gubre,
            "mazot_depo": mazot_depo,
            "ortak_pay": ortak_pay,
            "toplam_gider": toplam_gider,
            "gelir": gelir,
            "net": net,
            "ek_liste": ek_liste,
            "mazot_liste": mazot_liste,
            "ilac_liste": ilac_liste,
            "hasat_liste": hasat_liste,
        }

    def get_genel_rapor(self) -> dict:
        tarlalar = self.get_tarlalar()
        ozetler = [self.get_tarla_finans_ozeti(t["id"]) for t in tarlalar]
        toplam_donum = sum(float(t["donum"]) for t in tarlalar)
        toplam_gelir = sum(o["gelir"] for o in ozetler)
        tarla_sabit_ek = sum(o["temel"] + o["ek_gider"] for o in ozetler)
        ilac_gubre = sum(o["ilac_gubre"] for o in ozetler)
        mazot_depo = sum(o["mazot_depo"] for o in ozetler)
        ortak_gider = sum(float(g["tutar"]) for g in self.get_ortak_giderler())
        toplam_gider = tarla_sabit_ek + ilac_gubre + mazot_depo + ortak_gider
        net_kar = toplam_gelir - toplam_gider
        toplam_hasat = sum(float(h["miktar"]) for h in self.get_hasatlar())

        return {
            "tarla_sayisi": len(tarlalar),
            "toplam_donum": toplam_donum,
            "toplam_alan": toplam_donum * 2500.0,
            "toplam_gelir": toplam_gelir,
            "tarla_sabit_ek": tarla_sabit_ek,
            "ilac_gubre": ilac_gubre,
            "mazot_depo": mazot_depo,
            "depo_toplam": ilac_gubre + mazot_depo,
            "ortak_gider": ortak_gider,
            "toplam_gider": toplam_gider,
            "net_kar": net_kar,
            "toplam_hasat": toplam_hasat,
            "tarla_ozetleri": ozetler,
        }

    def export_csv(self) -> str:
        r = self.get_genel_rapor()
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow([
            "Tarla", "Ürün", "Dönüm", "Tarla ve Ek Gider", "İlaç Gübre",
            "Mazot (Depo)", "Ortak Gider", "Toplam Gider", "Gelir", "Net Kar",
        ])
        for o in r["tarla_ozetleri"]:
            t = o["tarla"]
            writer.writerow([
                t["ad"], t["urun"], t["donum"],
                round(o["temel"] + o["ek_gider"], 2),
                round(o["ilac_gubre"], 2),
                round(o["mazot_depo"], 2),
                round(o["ortak_pay"], 2),
                round(o["toplam_gider"], 2),
                round(o["gelir"], 2),
                round(o["net"], 2),
            ])
        return "﻿" + buf.getvalue()

    def export_json(self) -> str:
        with self.get_conn() as conn:
            data = {
                "tarlalar": [dict(r) for r in conn.execute("SELECT * FROM tarlalar").fetchall()],
                "depo": [dict(r) for r in conn.execute("SELECT * FROM depo").fetchall()],
                "kullanimlar": [dict(r) for r in conn.execute("SELECT * FROM kullanimlar").fetchall()],
                "mazot_alis": [dict(r) for r in conn.execute("SELECT * FROM mazot_alis").fetchall()],
                "mazot_cikis": [dict(r) for r in conn.execute("SELECT * FROM mazot_cikis").fetchall()],
                "ek_tarla_gider": [dict(r) for r in conn.execute("SELECT * FROM ek_tarla_gider").fetchall()],
                "hasat_satis": [dict(r) for r in conn.execute("SELECT * FROM hasat_satis").fetchall()],
                "ortak_giderler": [dict(r) for r in conn.execute("SELECT * FROM ortak_giderler").fetchall()],
            }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def import_json(self, json_str: str) -> tuple[bool, str]:
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                return False, "Geçersiz yedek formatı."
            required = ["tarlalar", "depo", "kullanimlar", "hasat_satis", "ortak_giderler"]
            if not all(isinstance(data.get(k), list) for k in required):
                return False, "Eksik veya hatalı yedek verisi."

            with self.get_conn() as conn:
                for tbl in ["tarlalar", "depo", "kullanimlar", "mazot_alis", "mazot_cikis", "ek_tarla_gider", "hasat_satis", "ortak_giderler"]:
                    conn.execute(f"DELETE FROM {tbl}")

                for t in data["tarlalar"]:
                    conn.execute("""
                        INSERT INTO tarlalar (id, ad, urun, donum, tohum_gider, mazot_gider, su_gider, malzeme_gider, hasat_gider, diger_gider)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        t.get("id", 1), t.get("ad", "Tarla"), t.get("urun", ""), float(t.get("donum", 0)),
                        float(t.get("tohum_gider", 0)), float(t.get("mazot_gider", 0)), float(t.get("su_gider", 0)),
                        float(t.get("malzeme_gider", 0)), float(t.get("hasat_gider", 0)), float(t.get("diger_gider", 0)),
                    ))

                for d in data["depo"]:
                    conn.execute("""
                        INSERT INTO depo (id, tur, ad, birim, temel_birim, miktar, fiyat, birim_fiyat, tarih)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        d.get("id"), d.get("tur", "Gübre"), d.get("ad", "Ürün"), d.get("birim", "kg"),
                        d.get("temel_birim", "kg"), float(d.get("miktar", 0)), float(d.get("fiyat", 0)),
                        float(d.get("birim_fiyat", 0)), d.get("tarih", ""),
                    ))

                for k in data["kullanimlar"]:
                    conn.execute("""
                        INSERT INTO kullanimlar (id, tarla_id, urun_id, miktar, maliyet, tarih)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        k.get("id"), k.get("tarla_id"), k.get("urun_id"),
                        float(k.get("miktar", 0)), float(k.get("maliyet", 0)), k.get("tarih", ""),
                    ))

                for a in data.get("mazot_alis", []):
                    conn.execute("""
                        INSERT INTO mazot_alis (id, miktar, fiyat, birim_fiyat, tarih)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        a.get("id"), float(a.get("miktar", 0)), float(a.get("fiyat", 0)),
                        float(a.get("birim_fiyat", 0)), a.get("tarih", ""),
                    ))

                for c_row in data.get("mazot_cikis", []):
                    conn.execute("""
                        INSERT INTO mazot_cikis (id, tarla_id, alis_id, miktar, birim_fiyat, maliyet, tarih)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        c_row.get("id"), c_row.get("tarla_id"), c_row.get("alis_id"),
                        float(c_row.get("miktar", 0)), float(c_row.get("birim_fiyat", 0)),
                        float(c_row.get("maliyet", 0)), c_row.get("tarih", ""),
                    ))

                for e_row in data.get("ek_tarla_gider", []):
                    conn.execute("""
                        INSERT INTO ek_tarla_gider (id, tarla_id, tur, aciklama, tutar, tarih)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        e_row.get("id"), e_row.get("tarla_id"), e_row.get("tur", "Diğer"),
                        e_row.get("aciklama", ""), float(e_row.get("tutar", 0)), e_row.get("tarih", ""),
                    ))

                for h in data["hasat_satis"]:
                    conn.execute("""
                        INSERT INTO hasat_satis (id, tarla_id, urun, miktar, fiyat, gelir, tarih, alici)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        h.get("id"), h.get("tarla_id"), h.get("urun", ""), float(h.get("miktar", 0)),
                        float(h.get("fiyat", 0)), float(h.get("gelir", 0)), h.get("tarih", ""), h.get("alici", ""),
                    ))

                for o in data["ortak_giderler"]:
                    conn.execute("""
                        INSERT INTO ortak_giderler (id, aciklama, kategori, tutar, tarih, paylasim)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        o.get("id"), o.get("aciklama", ""), o.get("kategori", "Diğer"),
                        float(o.get("tutar", 0)), o.get("tarih", ""), o.get("paylasim", "donum"),
                    ))

                conn.commit()
            return True, "Yedek başarıyla geri yüklendi."
        except Exception as exc:
            return False, f"Yedek okunamadı: {exc}"

    def reset_all(self):
        with self.get_conn() as conn:
            for tbl in ["tarlalar", "depo", "kullanimlar", "mazot_alis", "mazot_cikis", "ek_tarla_gider", "hasat_satis", "ortak_giderler"]:
                conn.execute(f"DELETE FROM {tbl}")
            for i in range(1, 11):
                conn.execute("INSERT INTO tarlalar (id, ad) VALUES (?, ?)", (i, f"Tarla {i}"))
            conn.commit()
