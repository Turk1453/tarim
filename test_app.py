import os
from database import TarlaDatabase


def run_tests():
    test_db = "test_tarla_v3.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    db = TarlaDatabase(test_db)
    assert len(db.get_tarlalar()) == 10

    db.update_tarla(1, "Köy Tarla", "Buğday", 10.0, {"tohum_gider": 5000.0})
    db.update_tarla(2, "Dere Tarla", "Arpa", 30.0, {})

    db.add_depo_urun("Gübre", "DAP Gübre", 2.0, "ton", 40000.0, "2026-11-20")
    urun = db.get_depo_urunler()[0]
    assert urun["miktar"] == 2000.0
    assert urun["birim_fiyat"] == 20.0

    # Birim uyumsuzluğu kontrolü
    ok_bad, _ = db.add_urun_kullanim(1, urun["id"], 10.0, "litre", "2026-11-20")
    assert not ok_bad

    # Geçerli kullanım: 250 kg -> 5.000 TL
    ok, msg = db.add_urun_kullanim(1, urun["id"], 250.0, "kg", "2026-11-20")
    assert ok, msg

    # Mazot alışı & çıkışı
    db.add_mazot_alis(500.0, 20000.0, "2026-11-20")
    alis_id = db.get_mazot_alislar()[0]["id"]
    ok_m, msg_m = db.add_mazot_cikis(1, alis_id, 100.0, "2026-11-20")
    assert ok_m, msg_m

    # Ek gider + Ortak gider + Hasat
    db.add_ek_gider(1, "Su", "Sulama", 1000.0, "2026-11-20")
    db.add_ortak_gider("Traktör Bakım", "Bakım", 4000.0, "2026-11-20", "donum")
    db.add_hasat(1, "Buğday", 5.0, 10000.0, "2026-11-20", "TMO")

    ozet = db.get_tarla_finans_ozeti(1)
    assert ozet["toplam_gider"] == 16000.0
    assert ozet["gelir"] == 50000.0
    assert ozet["net"] == 34000.0

    # Yedek dışa/içe aktarım ve CSV testi
    yedek = db.export_json()
    csv_out = db.export_csv()
    assert "Köy Tarla" in csv_out

    db.reset_all()
    assert db.get_genel_rapor()["toplam_gelir"] == 0.0

    ok_imp, msg_imp = db.import_json(yedek)
    assert ok_imp, msg_imp
    assert db.get_tarla_finans_ozeti(1)["net"] == 34000.0

    os.remove(test_db)
    print("TÜM DENETİM VE HESAPLAMA TESTLERİ BAŞARILI!")


if __name__ == "__main__":
    run_tests()
