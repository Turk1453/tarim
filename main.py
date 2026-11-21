import os
from datetime import date
import flet as ft
from database import TarlaDatabase

PRIMARY_DARK = "#173c2b"
PRIMARY_GREEN = "#24633d"
ACCENT_GREEN = "#438653"
BG_LIGHT = "#f1f5f0"
CARD_BG = "#ffffff"
SOFT_GREEN = "#edf5ee"
DANGER_RED = "#b83b35"
TEXT_DARK = "#26352b"
TEXT_MUTED = "#718071"


def tl_fmt(val: float) -> str:
    return f"{val:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def num_fmt(val: float) -> str:
    s = f"{val:,.3f}".rstrip("0").rstrip(".")
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def parse_num(raw: str | None, default: float = 0.0) -> float:
    if not raw:
        return default
    try:
        return float(str(raw).strip().replace(",", "."))
    except ValueError:
        return default


def main(page: ft.Page):
    page.title = "Tarla Masraf & Kâr Hesaplama Sistemi"
    page.bgcolor = BG_LIGHT
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    app_data_dir = os.getenv("FLET_APP_STORAGE_DATA") or os.path.dirname(os.path.abspath(__file__))
    os.makedirs(app_data_dir, exist_ok=True)
    db = TarlaDatabase(os.path.join(app_data_dir, "tarla_verileri.db"))

    def show_snack(msg: str, is_error: bool = False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=DANGER_RED if is_error else PRIMARY_GREEN,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def stat_card(title: str, value: str, border_color: str = ACCENT_GREEN):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=12, color=TEXT_MUTED),
                    ft.Text(value, size=17, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                ],
                spacing=4,
            ),
            bgcolor=CARD_BG,
            padding=12,
            border_radius=12,
            border=ft.border.only(left=ft.BorderSide(5, border_color)),
            shadow=ft.BoxShadow(blur_radius=6, color="#12000000", offset=ft.Offset(0, 2)),
            expand=True,
        )

    def section_panel(title: str, controls: list):
        return ft.Container(
            content=ft.Column(
                [ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN), *controls],
                spacing=10,
            ),
            bgcolor=CARD_BG,
            padding=14,
            border_radius=12,
            border=ft.border.all(1, "#dce6dc"),
            margin=ft.margin.only(bottom=8),
        )

    body_container = ft.Container(expand=True, padding=12)

    header = ft.Container(
        content=ft.Column(
            [
                ft.Text("🌾 ŞABAN GÖK VE OĞULLARI", size=19, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("TARLA MASRAF & KÂR DURUMU", size=13, color="#e1f0e4", weight=ft.FontWeight.W_600),
                ft.Text("Tarım İşletmesi Takip ve Hesaplama Sistemi", size=11, color="#c7dfce"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        bgcolor=PRIMARY_DARK,
        padding=ft.padding.symmetric(vertical=12, horizontal=12),
        alignment=ft.alignment.center,
    )

    # --- SAYFA 0: ANA SAYFA & TARLALARIM ---
    def build_ana_sayfa():
        rapor = db.get_genel_rapor()
        net_renk = PRIMARY_GREEN if rapor["net_kar"] >= 0 else DANGER_RED

        tarla_kartlari = []
        for ozet in rapor["tarla_ozetleri"]:
            t = ozet["tarla"]
            t_net = ozet["net"]
            tarla_kartlari.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(f"🌱 {t['ad']}", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                                    ft.Container(
                                        content=ft.Text(t["urun"] or "Henüz girilmedi", size=12, color=PRIMARY_DARK),
                                        bgcolor=SOFT_GREEN,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=6,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Dönüm: {num_fmt(t['donum'])} ({num_fmt(t['donum']*2500)} m²)", size=13, color=TEXT_MUTED),
                            ft.Row(
                                [
                                    ft.Text(f"Gider: {tl_fmt(ozet['toplam_gider'])}", size=13, weight=ft.FontWeight.W_600),
                                    ft.Text(f"Gelir: {tl_fmt(ozet['gelir'])}", size=13, weight=ft.FontWeight.W_600, color=PRIMARY_GREEN),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"Net: {tl_fmt(t_net)}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=PRIMARY_GREEN if t_net >= 0 else DANGER_RED,
                                    ),
                                    ft.ElevatedButton(
                                        "Tarlayı Aç & Düzenle",
                                        bgcolor=PRIMARY_GREEN,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, tid=t["id"]: open_tarla_editor(tid),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=6,
                    ),
                    bgcolor=CARD_BG,
                    padding=14,
                    border_radius=12,
                    border=ft.border.all(1, "#dce6dc"),
                )
            )

        return ft.ListView(
            [
                ft.Text("Genel Durum", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                ft.Row([stat_card("Toplam Tarla", str(rapor["tarla_sayisi"])), stat_card("Toplam Dönüm", num_fmt(rapor["toplam_donum"]))], spacing=10),
                ft.Row([stat_card("Toplam Gelir", tl_fmt(rapor["toplam_gelir"]), PRIMARY_GREEN), stat_card("Toplam Gider", tl_fmt(rapor["toplam_gider"]), DANGER_RED)], spacing=10),
                ft.Row([stat_card("Net Kâr / Zarar", tl_fmt(rapor["net_kar"]), net_renk), stat_card("Toplam Hasat", f"{num_fmt(rapor['toplam_hasat'])} Ton")], spacing=10),
                ft.Row([stat_card("Ortak Gider", tl_fmt(rapor["ortak_gider"])), stat_card("Toplam Alan", f"{num_fmt(rapor['toplam_alan'])} m²")], spacing=10),
                ft.Divider(height=10, color="transparent"),
                ft.Text("🌱 Tarlalarım (10 Tarla)", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                *tarla_kartlari,
            ],
            spacing=8,
            expand=True,
        )

    # --- TARLA DÜZENLEME EKRANI ---
    def open_tarla_editor(tarla_id: int):
        ozet = db.get_tarla_finans_ozeti(tarla_id)
        if not ozet:
            return
        t = ozet["tarla"]

        ad_tf = ft.TextField(label="Tarla Adı", value=t["ad"])
        urun_tf = ft.TextField(label="Ekili Ürün", value=t["urun"], hint_text="Buğday, arpa, mısır")
        donum_tf = ft.TextField(label="Tarla Dönümü", value=str(t["donum"]), keyboard_type=ft.KeyboardType.NUMBER)
        m2_txt = ft.Text(f"Metrekare: {num_fmt(t['donum']*2500)} m² (1 dönüm = 2.500 m²)", size=12, color=TEXT_MUTED)

        def on_donum_change(e):
            d = max(0.0, parse_num(donum_tf.value))
            m2_txt.value = f"Metrekare: {num_fmt(d*2500)} m² (1 dönüm = 2.500 m²)"
            page.update()

        donum_tf.on_change = on_donum_change

        tohum_tf = ft.TextField(label="Tohum Gideri (TL)", value=str(t["tohum_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        mazot_tf = ft.TextField(label="Doğrudan Mazot Gideri (TL)", value=str(t["mazot_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        su_tf = ft.TextField(label="Su Gideri (TL)", value=str(t["su_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        malzeme_tf = ft.TextField(label="Malzeme Gideri (TL)", value=str(t["malzeme_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        hasat_tf = ft.TextField(label="Hasat Ücreti (TL)", value=str(t["hasat_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        diger_tf = ft.TextField(label="Diğer Giderler (TL)", value=str(t["diger_gider"]), keyboard_type=ft.KeyboardType.NUMBER)

        def save_tarla(e):
            db.update_tarla(
                tarla_id,
                ad_tf.value.strip() or f"Tarla {tarla_id}",
                urun_tf.value.strip(),
                max(0.0, parse_num(donum_tf.value)),
                {
                    "tohum_gider": max(0.0, parse_num(tohum_tf.value)),
                    "mazot_gider": max(0.0, parse_num(mazot_tf.value)),
                    "su_gider": max(0.0, parse_num(su_tf.value)),
                    "malzeme_gider": max(0.0, parse_num(malzeme_tf.value)),
                    "hasat_gider": max(0.0, parse_num(hasat_tf.value)),
                    "diger_gider": max(0.0, parse_num(diger_tf.value)),
                },
            )
            show_snack("Tarla bilgileri kaydedildi.")
            open_tarla_editor(tarla_id)

        detay_satirlari = [
            ft.Text("📋 Bu Tarlanın Kapsamlı Finansal Dökümü", weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
            ft.Text(f"1. Sabit/Temel Giderler: {tl_fmt(ozet['temel'])}", size=13),
            ft.Text(f"2. Tarla Gider Girişi (Su, Elektrik vb.): {tl_fmt(ozet['ek_gider'])}", size=13),
        ]
        for eg in ozet["ek_liste"]:
            detay_satirlari.append(ft.Text(f"   • {eg['tur']} ({eg['aciklama'] or 'Açıklamasız'}): {tl_fmt(eg['tutar'])}", size=12, color=TEXT_MUTED))

        detay_satirlari.append(ft.Text(f"3. İlaç & Gübre Deposu Maliyeti: {tl_fmt(ozet['ilac_gubre'])}", size=13))
        for il in ozet["ilac_liste"]:
            detay_satirlari.append(ft.Text(f"   • {il['urun_ad'] or 'Ürün'} ({num_fmt(il['miktar'])} {il['temel_birim'] or ''}): {tl_fmt(il['maliyet'])}", size=12, color=TEXT_MUTED))

        detay_satirlari.append(ft.Text(f"4. Mazot Deposu Maliyeti: {tl_fmt(ozet['mazot_depo'])}", size=13))
        for mz in ozet["mazot_liste"]:
            detay_satirlari.append(ft.Text(f"   • {num_fmt(mz['miktar'])} L Mazot Çıkışı: {tl_fmt(mz['maliyet'])}", size=12, color=TEXT_MUTED))

        detay_satirlari.extend([
            ft.Text(f"5. Ortak Gider Payı: {tl_fmt(ozet['ortak_pay'])}", size=13),
            ft.Divider(height=6),
            ft.Text(f"Toplam Gider: {tl_fmt(ozet['toplam_gider'])}", weight=ft.FontWeight.BOLD),
            ft.Text(f"Toplam Gelir: {tl_fmt(ozet['gelir'])}", weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
        ])
        for hs in ozet["hasat_liste"]:
            detay_satirlari.append(ft.Text(f"   • {hs['urun']}: {num_fmt(hs['miktar'])} Ton - Gelir: {tl_fmt(hs['gelir'])} (Alıcı: {hs['alici'] or '-'})", size=12, color=TEXT_MUTED))

        detay_satirlari.extend([
            ft.Divider(height=6),
            ft.Text(
                f"Net Kâr / Zarar: {tl_fmt(ozet['net'])}",
                weight=ft.FontWeight.BOLD,
                size=15,
                color=PRIMARY_GREEN if ozet["net"] >= 0 else DANGER_RED,
            ),
        ])

        body_container.content = ft.ListView(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate_to(0)),
                        ft.Text(f"{t['ad']} - Düzenleme", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                    ]
                ),
                section_panel("Tarla Bilgileri", [ad_tf, urun_tf, donum_tf, m2_txt]),
                section_panel("Sabit / Doğrudan Tarla Giderleri", [tohum_tf, mazot_tf, su_tf, malzeme_tf, hasat_tf, diger_tf]),
                ft.Container(content=ft.Column(detay_satirlari, spacing=3), bgcolor=SOFT_GREEN, padding=12, border_radius=8, border=ft.border.all(1, "#c0d8c3")),
                ft.Row(
                    [
                        ft.ElevatedButton("💾 Tarla Bilgilerini Kaydet", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, expand=True, on_click=save_tarla),
                        ft.OutlinedButton("Geri Dön", expand=True, on_click=lambda e: navigate_to(0)),
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
            expand=True,
        )
        page.update()

    # --- SAYFA 1: İLAÇ & GÜBRE DEPOSU ---
    def build_depo_sayfa():
        tarlalar = db.get_tarlalar()
        urunler = db.get_depo_urunler()
        kullanimlar = db.get_kullanimlar()

        tur_dd = ft.Dropdown(label="Ürün Türü", value="Gübre", options=[ft.dropdown.Option("Gübre"), ft.dropdown.Option("İlaç")])
        ad_tf = ft.TextField(label="Ürün Adı", hint_text="Örnek: DAP Gübre")
        miktar_tf = ft.TextField(label="Alınan Miktar", hint_text="Örnek: 5000", keyboard_type=ft.KeyboardType.NUMBER)
        birim_dd = ft.Dropdown(
            label="Birim",
            value="kg",
            options=[
                ft.dropdown.Option("kg", "Kilogram"),
                ft.dropdown.Option("ton", "Ton"),
                ft.dropdown.Option("litre", "Litre"),
                ft.dropdown.Option("ml", "Mililitre"),
                ft.dropdown.Option("gram", "Gram"),
            ],
        )
        fiyat_tf = ft.TextField(label="Toplam Alış Fiyatı (TL)", hint_text="Örnek: 100000", keyboard_type=ft.KeyboardType.NUMBER)
        tarih_tf = ft.TextField(label="Alış Tarihi", value=str(date.today()))

        def alis_kaydet(e):
            m = parse_num(miktar_tf.value)
            f = parse_num(fiyat_tf.value, -1.0)
            if not ad_tf.value.strip() or m <= 0 or f < 0:
                show_snack("Ürün adı, miktar ve fiyat bilgilerini kontrol et.", True)
                return
            if tur_dd.value == "Gübre" and birim_dd.value not in ("kg", "ton", "gram"):
                show_snack("Gübre için kg, gram veya ton seçmelisin.", True)
                return
            db.add_depo_urun(tur_dd.value, ad_tf.value.strip(), m, birim_dd.value, f, tarih_tf.value)
            show_snack("Ürün depoya kaydedildi.")
            navigate_to(1)

        k_tarla_dd = ft.Dropdown(label="Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        k_urun_dd = ft.Dropdown(
            label="Depodan Ürün Seç",
            options=[ft.dropdown.Option(str(u["id"]), f"{u['ad']} - {num_fmt(u['kalan'])} {u['temel_birim']}") for u in urunler],
        )
        k_miktar_tf = ft.TextField(label="Kullanılan Miktar", hint_text="Örnek: 200", keyboard_type=ft.KeyboardType.NUMBER)
        k_birim_dd = ft.Dropdown(
            label="Çıkış Ölçü Birimi",
            value="kg",
            options=[
                ft.dropdown.Option("kg", "Kilogram"),
                ft.dropdown.Option("ton", "Ton"),
                ft.dropdown.Option("litre", "Litre"),
                ft.dropdown.Option("ml", "Mililitre"),
                ft.dropdown.Option("gram", "Gram"),
            ],
        )
        k_tarih_tf = ft.TextField(label="Kullanım Tarihi", value=str(date.today()))

        def urun_kullan_click(e):
            if not k_tarla_dd.value or not k_urun_dd.value:
                show_snack("Tarla, ürün ve miktar bilgilerini kontrol et.", True)
                return
            m = parse_num(k_miktar_tf.value)
            if m <= 0:
                show_snack("Tarla, ürün ve miktar bilgilerini kontrol et.", True)
                return
            ok, msg = db.add_urun_kullanim(int(k_tarla_dd.value), int(k_urun_dd.value), m, k_birim_dd.value, k_tarih_tf.value)
            show_snack(msg, not ok)
            if ok:
                navigate_to(1)

        def try_delete_urun(uid: int):
            ok, msg = db.delete_depo_urun(uid)
            show_snack(msg, not ok)
            if ok:
                navigate_to(1)

        stok_kartlari = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{u['ad']} ({u['tur']})", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Alınan: {num_fmt(u['miktar'])} {u['temel_birim']} | Kullanılan: {num_fmt(u['kullanilan'])} {u['temel_birim']} | Kalan: {num_fmt(u['kalan'])} {u['temel_birim']}", size=12, color=TEXT_MUTED),
                                ft.Text(f"Birim Fiyat: {tl_fmt(u['birim_fiyat'])} | Stok Değeri: {tl_fmt(u['stok_degeri'])}", size=12, color=PRIMARY_GREEN),
                            ],
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, uid=u["id"]: try_delete_urun(uid)),
                    ]
                ),
                padding=10,
                bgcolor=SOFT_GREEN,
                border_radius=8,
            )
            for u in urunler
        ]

        kullanim_kartlari = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{k['tarla_ad']} → {k['urun_ad'] or '-'}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{num_fmt(k['miktar'])} {k['temel_birim'] or ''} | Maliyet: {tl_fmt(k['maliyet'])} | {k['tarih'] or '-'}", size=12, color=TEXT_MUTED),
                            ],
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, kid=k["id"]: (db.delete_kullanim(kid), show_snack("Kullanım kaydı silindi, stok geri eklendi."), navigate_to(1))),
                    ]
                ),
                padding=10,
                bgcolor="#f9fbf9",
                border=ft.border.all(1, "#dce6dc"),
                border_radius=8,
            )
            for k in kullanimlar
        ]

        return ft.ListView(
            [
                section_panel("Yeni Ürün Alışı (İlaç / Gübre)", [tur_dd, ad_tf, miktar_tf, birim_dd, fiyat_tf, tarih_tf, ft.ElevatedButton("+ Ürünü Depoya Ekle", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=alis_kaydet)]),
                section_panel("📋 Depodaki Ürünler", stok_kartlari or [ft.Text("Henüz depo ürünü yok.", color=TEXT_MUTED)]),
                section_panel("🌱 Ürünü Tarlada Kullan", [k_tarla_dd, k_urun_dd, k_miktar_tf, k_birim_dd, k_tarih_tf, ft.ElevatedButton("Tarlaya Ürün Kullan", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=urun_kullan_click)]),
                section_panel("📊 Tarlalara Gönderilen Ürünler", kullanim_kartlari or [ft.Text("Henüz kullanım kaydı yok.", color=TEXT_MUTED)]),
            ],
            spacing=8,
            expand=True,
        )

    # --- SAYFA 2: MAZOT DEPOSU ---
    def build_mazot_sayfa():
        tarlalar = db.get_tarlalar()
        alislar = db.get_mazot_alislar()
        cikislar = db.get_mazot_cikislar()

        toplam_l = sum(a["miktar"] for a in alislar)
        kull_l = sum(a["kullanilan"] for a in alislar)
        kalan_l = toplam_l - kull_l
        stok_val = sum(a["stok_degeri"] for a in alislar)

        m_miktar = ft.TextField(label="Alınan Mazot (Litre)", keyboard_type=ft.KeyboardType.NUMBER)
        m_fiyat = ft.TextField(label="Toplam Alış Fiyatı (TL)", keyboard_type=ft.KeyboardType.NUMBER)
        m_tarih = ft.TextField(label="Alış Tarihi", value=str(date.today()))

        def mazot_alis_ekle(e):
            mk = parse_num(m_miktar.value)
            fy = parse_num(m_fiyat.value, -1.0)
            if mk <= 0 or fy < 0:
                show_snack("Litre ve fiyat bilgilerini kontrol et.", True)
                return
            db.add_mazot_alis(mk, fy, m_tarih.value)
            show_snack("Mazot depoya eklendi.")
            navigate_to(2)

        c_tarla = ft.Dropdown(label="Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        c_alis = ft.Dropdown(
            label="Mazot Alış Kaydı Seç",
            options=[
                ft.dropdown.Option(str(a["id"]), f"{a['tarih'] or '-'} | {num_fmt(a['kalan'])} L - {tl_fmt(a['birim_fiyat'])}/L")
                for a in alislar
                if a["kalan"] > 0
            ],
        )
        c_miktar = ft.TextField(label="Çıkış Miktarı (Litre)", keyboard_type=ft.KeyboardType.NUMBER)
        c_tarih = ft.TextField(label="Çıkış Tarihi", value=str(date.today()))

        def mazot_cikis_ekle(e):
            if not c_tarla.value or not c_alis.value:
                show_snack("Tarla, mazot ve miktar bilgilerini kontrol et.", True)
                return
            mk = parse_num(c_miktar.value)
            if mk <= 0:
                show_snack("Tarla, mazot ve miktar bilgilerini kontrol et.", True)
                return
            ok, msg = db.add_mazot_cikis(int(c_tarla.value), int(c_alis.value), mk, c_tarih.value)
            show_snack(msg, not ok)
            if ok:
                navigate_to(2)

        def try_delete_alis(aid: int):
            ok, msg = db.delete_mazot_alis(aid)
            show_snack(msg, not ok)
            if ok:
                navigate_to(2)

        alis_kartlari = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"Alış ({a['tarih'] or '-'}) — Alınan: {num_fmt(a['miktar'])} L", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Kalan: {num_fmt(a['kalan'])} L | Birim: {tl_fmt(a['birim_fiyat'])}/L | Stok Değeri: {tl_fmt(a['stok_degeri'])}", size=12, color=TEXT_MUTED),
                            ],
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, aid=a["id"]: try_delete_alis(aid)),
                    ]
                ),
                padding=10,
                bgcolor="#f9fbf9",
                border=ft.border.all(1, "#dce6dc"),
                border_radius=8,
            )
            for a in alislar
        ]

        cikis_kartlari = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{c['tarla_ad'] or '-'} — {num_fmt(c['miktar'])} L", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Litre Fiyatı: {tl_fmt(c['birim_fiyat'])} | Maliyet: {tl_fmt(c['maliyet'])} | {c['tarih'] or '-'}", size=12, color=TEXT_MUTED),
                            ],
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, cid=c["id"]: (db.delete_mazot_cikis(cid), show_snack("Mazot çıkışı silindi, stok geri eklendi."), navigate_to(2))),
                    ]
                ),
                padding=10,
                bgcolor=SOFT_GREEN,
                border_radius=8,
            )
            for c in cikislar
        ]

        return ft.ListView(
            [
                ft.Row([stat_card("Toplam Alınan", f"{num_fmt(toplam_l)} L"), stat_card("Toplam Kullanılan", f"{num_fmt(kull_l)} L")], spacing=10),
                ft.Row([stat_card("Kalan Mazot", f"{num_fmt(kalan_l)} L"), stat_card("Stok Değeri", tl_fmt(stok_val))], spacing=10),
                section_panel("Yeni Mazot Alışı", [m_miktar, m_fiyat, m_tarih, ft.ElevatedButton("+ Mazot Depoya Ekle", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=mazot_alis_ekle)]),
                section_panel("📋 Mazot Alış Kayıtları", alis_kartlari or [ft.Text("Henüz mazot alışı yok.", color=TEXT_MUTED)]),
                section_panel("🌱 Tarlaya Mazot Çıkışı", [c_tarla, c_alis, c_miktar, c_tarih, ft.ElevatedButton("Mazotu Tarlaya Gönder", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=mazot_cikis_ekle)]),
                section_panel("📋 Mazot Çıkış Geçmişi", cikis_kartlari or [ft.Text("Henüz mazot çıkışı yok.", color=TEXT_MUTED)]),
            ],
            spacing=8,
            expand=True,
        )

    # --- SAYFA 3: TARLA GİDER GİRİŞİ, HASAT VE ORTAK GİDERLER ---
    def build_islemler_sayfa():
        tarlalar = db.get_tarlalar()
        ek_giderler = db.get_ek_giderler()
        hasatlar = db.get_hasatlar()
        ortaklar = db.get_ortak_giderler()
        rapor = db.get_genel_rapor()

        # Tarla Ek Gider
        eg_tarla = ft.Dropdown(label="Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        eg_tur = ft.Dropdown(label="Gider Türü", value="Su", options=[ft.dropdown.Option(x) for x in ["Su", "Elektrik", "İşçilik", "Tamir", "Nakliye", "Diğer"]])
        eg_aciklama = ft.TextField(label="Açıklama (İsteğe Bağlı)", hint_text="Örnek: Sulama motoru arızası")
        eg_tutar = ft.TextField(label="Gider Tutarı (TL)", keyboard_type=ft.KeyboardType.NUMBER)
        eg_tarih = ft.TextField(label="Gider Tarihi", value=str(date.today()))

        def eg_kaydet(e):
            if not eg_tarla.value:
                show_snack("Lütfen tarla seç ve geçerli bir gider tutarı gir.", True)
                return
            tutar = parse_num(eg_tutar.value)
            if tutar <= 0:
                show_snack("Lütfen tarla seç ve geçerli bir gider tutarı gir.", True)
                return
            db.add_ek_gider(int(eg_tarla.value), eg_tur.value, eg_aciklama.value.strip(), tutar, eg_tarih.value)
            show_snack("Tarla gideri kaydedildi.")
            navigate_to(3)

        # Hasat & Satış
        h_tarla = ft.Dropdown(label="Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        h_urun = ft.TextField(label="Hasat Edilen Ürün", hint_text="Buğday, arpa, mısır")
        h_miktar = ft.TextField(label="Hasat Miktarı (Ton)", keyboard_type=ft.KeyboardType.NUMBER)
        h_fiyat = ft.TextField(label="Satış Fiyatı (Ton Başına TL)", keyboard_type=ft.KeyboardType.NUMBER)
        h_tarih = ft.TextField(label="Hasat Tarihi", value=str(date.today()))
        h_alici = ft.TextField(label="Alıcı / Firma", hint_text="Alıcı adı")

        def h_kaydet(e):
            if not h_tarla.value or not h_urun.value.strip():
                show_snack("Hasat bilgilerini kontrol et.", True)
                return
            mk = parse_num(h_miktar.value)
            fy = parse_num(h_fiyat.value, -1.0)
            if mk <= 0 or fy < 0:
                show_snack("Hasat bilgilerini kontrol et.", True)
                return
            db.add_hasat(int(h_tarla.value), h_urun.value.strip(), mk, fy, h_tarih.value, h_alici.value.strip())
            show_snack("Hasat ve satış kaydı oluşturuldu.")
            navigate_to(3)

        # Ortak Gider
        o_aciklama = ft.TextField(label="Gider Açıklaması", hint_text="Örnek: Traktör tamiri")
        o_kat = ft.Dropdown(label="Gider Kategorisi", value="Mazot", options=[ft.dropdown.Option(x) for x in ["Mazot", "İşçilik", "Makine", "Nakliye", "Bakım", "Elektrik", "Diğer"]])
        o_tutar = ft.TextField(label="Gider Tutarı (TL)", keyboard_type=ft.KeyboardType.NUMBER)
        o_tarih = ft.TextField(label="Gider Tarihi", value=str(date.today()))
        o_paylasim = ft.Dropdown(
            label="Gideri Paylaştırma Şekli",
            value="donum",
            options=[ft.dropdown.Option("donum", "Dönüme Göre"), ft.dropdown.Option("esit", "Tarlalara Eşit")],
        )

        def o_kaydet(e):
            if not o_aciklama.value.strip():
                show_snack("Açıklama ve geçerli bir gider tutarı gir.", True)
                return
            tt = parse_num(o_tutar.value)
            if tt <= 0:
                show_snack("Açıklama ve geçerli bir gider tutarı gir.", True)
                return
            db.add_ortak_gider(o_aciklama.value.strip(), o_kat.value, tt, o_tarih.value, o_paylasim.value)
            show_snack("Ortak gider kaydedildi.")
            navigate_to(3)

        ek_list_ui = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column([ft.Text(f"{g['tarla_ad'] or '-'} — {g['tur']} ({tl_fmt(g['tutar'])})", weight=ft.FontWeight.BOLD), ft.Text(f"{g['aciklama'] or '-'} | {g['tarih'] or '-'}", size=12, color=TEXT_MUTED)], expand=True),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, gid=g["id"]: (db.delete_ek_gider(gid), show_snack("Tarla gideri silindi."), navigate_to(3))),
                    ]
                ),
                padding=8,
                bgcolor="#fff8f8",
                border_radius=8,
            )
            for g in ek_giderler
        ]

        hasat_list_ui = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column([ft.Text(f"{h['tarla_ad'] or '-'} — {h['urun']} ({num_fmt(h['miktar'])} Ton)", weight=ft.FontWeight.BOLD), ft.Text(f"Birim: {tl_fmt(h['fiyat'])} | Gelir: {tl_fmt(h['gelir'])} | Alıcı: {h['alici'] or '-'} | {h['tarih'] or '-'}", size=12, color=PRIMARY_GREEN)], expand=True),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, hid=h["id"]: (db.delete_hasat(hid), show_snack("Hasat kaydı silindi."), navigate_to(3))),
                    ]
                ),
                padding=8,
                bgcolor=SOFT_GREEN,
                border_radius=8,
            )
            for h in hasatlar
        ]

        ortak_list_ui = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column([ft.Text(f"{o['aciklama']} ({o['kategori']}) — {tl_fmt(o['tutar'])}", weight=ft.FontWeight.BOLD), ft.Text(f"Paylaşım: {'Dönüme Göre' if o['paylasim']=='donum' else 'Eşit'} | {o['tarih'] or '-'}", size=12, color=TEXT_MUTED)], expand=True),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, oid=o["id"]: (db.delete_ortak_gider(oid), show_snack("Ortak gider silindi."), navigate_to(3))),
                    ]
                ),
                padding=8,
                bgcolor="#f9fbf9",
                border=ft.border.all(1, "#dce6dc"),
                border_radius=8,
            )
            for o in ortaklar
        ]

        dagitim_ui = [
            ft.Text(f"• {oz['tarla']['ad']}: {tl_fmt(oz['ortak_pay'])}", size=13)
            for oz in rapor["tarla_ozetleri"]
        ]

        return ft.ListView(
            [
                section_panel("🧾 Yeni Tarla Gideri Ekle", [eg_tarla, eg_tur, eg_aciklama, eg_tutar, eg_tarih, ft.ElevatedButton("💾 Gideri Kaydet", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=eg_kaydet)]),
                section_panel("📋 Eklenen Tarla Giderleri", ek_list_ui or [ft.Text("Henüz ek tarla gideri yok.", color=TEXT_MUTED)]),
                section_panel("🚜 Yeni Hasat ve Satış Kaydı", [h_tarla, h_urun, h_miktar, h_fiyat, h_tarih, h_alici, ft.ElevatedButton("Hasat ve Satışı Kaydet", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=h_kaydet)]),
                section_panel("📋 Hasat ve Satış Geçmişi", hasat_list_ui or [ft.Text("Henüz hasat kaydı yok.", color=TEXT_MUTED)]),
                section_panel("💰 Yeni Ortak Gider Ekle", [o_aciklama, o_kat, o_tutar, o_tarih, o_paylasim, ft.ElevatedButton("+ Ortak Gider Kaydet", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=o_kaydet)]),
                section_panel("📋 Ortak Gider Listesi", ortak_list_ui or [ft.Text("Henüz ortak gider yok.", color=TEXT_MUTED)]),
                section_panel("🌱 Tarlalara Dağıtılan Ortak Giderler", dagitim_ui),
            ],
            spacing=8,
            expand=True,
        )

    # --- SAYFA 4: GENEL RAPOR & YEDEKLEME ---
    def build_rapor_sayfa():
        r = db.get_genel_rapor()
        urunler = db.get_depo_urunler()
        mazot_alislar = db.get_mazot_alislar()

        tarla_satirlari = []
        for o in r["tarla_ozetleri"]:
            t = o["tarla"]
            net_c = PRIMARY_GREEN if o["net"] >= 0 else DANGER_RED
            tarla_satirlari.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(f"{t['ad']} ({t['urun'] or '-'})", weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{num_fmt(t['donum'])} Dönüm", size=12, color=TEXT_MUTED),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                f"Tarla+Ek: {tl_fmt(o['temel']+o['ek_gider'])} | İlaç-Gübre: {tl_fmt(o['ilac_gubre'])} | Mazot: {tl_fmt(o['mazot_depo'])} | Ortak: {tl_fmt(o['ortak_pay'])}",
                                size=11,
                                color=TEXT_MUTED,
                            ),
                            ft.Row(
                                [
                                    ft.Text(f"Gider: {tl_fmt(o['toplam_gider'])}", size=12),
                                    ft.Text(f"Gelir: {tl_fmt(o['gelir'])}", size=12, color=PRIMARY_GREEN),
                                    ft.Text(f"Net: {tl_fmt(o['net'])}", size=13, weight=ft.FontWeight.BOLD, color=net_c),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=10,
                    bgcolor=SOFT_GREEN,
                    border_radius=8,
                )
            )

        depo_durum_ui = [
            ft.Text(f"• {u['ad']} ({u['tur']}): Kalan {num_fmt(u['kalan'])} {u['temel_birim']} | Değer: {tl_fmt(u['stok_degeri'])}", size=12)
            for u in urunler
        ]
        if mazot_alislar:
            m_kalan = sum(a["kalan"] for a in mazot_alislar)
            m_deger = sum(a["stok_degeri"] for a in mazot_alislar)
            depo_durum_ui.append(ft.Text(f"• Mazot (Toplam Stok): Kalan {num_fmt(m_kalan)} L | Değer: {tl_fmt(m_deger)}", size=12, weight=ft.FontWeight.BOLD))

        json_yedek_tf = ft.TextField(label="Yedek JSON Metni (Kopyala veya Yapıştır)", multiline=True, min_lines=3, max_lines=6)

        def yedek_disa_aktar(e):
            json_yedek_tf.value = db.export_json()
            backup_path = os.path.join(app_data_dir, f"tarla-takip-yedek-{date.today()}.json")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(json_yedek_tf.value)
            show_snack(f"Yedek oluşturuldu ve kaydedildi: {backup_path}")
            page.update()

        def yedek_ice_aktar(e):
            if not json_yedek_tf.value.strip():
                show_snack("Geri yüklenecek JSON verisini alana yapıştırın.", True)
                return
            ok, msg = db.import_json(json_yedek_tf.value)
            show_snack(msg, not ok)
            if ok:
                navigate_to(4)

        def csv_disa_aktar(e):
            csv_path = os.path.join(app_data_dir, f"tarla-genel-rapor-{date.today()}.csv")
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(db.export_csv())
            show_snack(f"CSV raporu kaydedildi: {csv_path}")

        def tumunu_sil(e):
            db.reset_all()
            show_snack("Bütün kayıtlar silindi ve 10 boş tarla oluşturuldu.")
            navigate_to(4)

        return ft.ListView(
            [
                ft.Text("📊 Genel Tarım İşletmesi Raporu", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                ft.Row([stat_card("Toplam Gelir", tl_fmt(r["toplam_gelir"]), PRIMARY_GREEN), stat_card("Sabit & Ek Tarla Gideri", tl_fmt(r["tarla_sabit_ek"]))], spacing=10),
                ft.Row([stat_card("Depo Giderleri", tl_fmt(r["depo_toplam"])), stat_card("Ortak Giderler", tl_fmt(r["ortak_gider"]))], spacing=10),
                ft.Row([stat_card("Toplam Gider", tl_fmt(r["toplam_gider"]), DANGER_RED), stat_card("Net Kâr / Zarar", tl_fmt(r["net_kar"]), PRIMARY_GREEN if r["net_kar"] >= 0 else DANGER_RED)], spacing=10),
                ft.Row([stat_card("Toplam Hasat", f"{num_fmt(r['toplam_hasat'])} Ton"), stat_card("Tarla Sayısı", str(r["tarla_sayisi"]))], spacing=10),
                section_panel(
                    "💰 Gider Dağılımı",
                    [
                        ft.Text(f"• Sabit ve Ek Tarla Giderleri: {tl_fmt(r['tarla_sabit_ek'])}"),
                        ft.Text(f"• İlaç ve Gübre (Depo Kullanımı): {tl_fmt(r['ilac_gubre'])}"),
                        ft.Text(f"• Mazot (Depo Çıkışı): {tl_fmt(r['mazot_depo'])}"),
                        ft.Text(f"• Ortak Giderler: {tl_fmt(r['ortak_gider'])}"),
                    ],
                ),
                section_panel("📦 Depo Durumu", depo_durum_ui or [ft.Text("Depoda kayıtlı ürün yok.", color=TEXT_MUTED)]),
                section_panel("🌱 Tarla Bazlı Kâr-Zarar Raporu", tarla_satirlari),
                section_panel("📄 Rapor Dışa Aktarma", [ft.ElevatedButton("📥 Raporu CSV Kaydet", bgcolor="#68766a", color=ft.Colors.WHITE, on_click=csv_disa_aktar)]),
                section_panel(
                    "💾 Veri Güvenliği ve Yedekleme",
                    [
                        ft.Text("Kayıtların cihaz veritabanında saklanır. Düzenli olarak yedek almanı öneririm.", size=12, color=TEXT_MUTED),
                        ft.ElevatedButton("📥 Bütün Verileri Yedekle (JSON)", bgcolor=PRIMARY_GREEN, color=ft.Colors.WHITE, on_click=yedek_disa_aktar),
                        json_yedek_tf,
                        ft.ElevatedButton("📤 JSON Yedeğinden Geri Yükle", bgcolor=ACCENT_GREEN, color=ft.Colors.WHITE, on_click=yedek_ice_aktar),
                        ft.ElevatedButton("🗑️ Bütün Verileri Sil", bgcolor=DANGER_RED, color=ft.Colors.WHITE, on_click=tumunu_sil),
                    ],
                ),
            ],
            spacing=8,
            expand=True,
        )

    def navigate_to(idx: int):
        nav_bar.selected_index = idx
        if idx == 0:
            body_container.content = build_ana_sayfa()
        elif idx == 1:
            body_container.content = build_depo_sayfa()
        elif idx == 2:
            body_container.content = build_mazot_sayfa()
        elif idx == 3:
            body_container.content = build_islemler_sayfa()
        elif idx == 4:
            body_container.content = build_rapor_sayfa()
        page.update()

    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor=CARD_BG,
        indicator_color="#d5e8d8",
        on_change=lambda e: navigate_to(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Tarlalar"),
            ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="İlaç/Gübre"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCAL_GAS_STATION_OUTLINED, selected_icon=ft.Icons.LOCAL_GAS_STATION, label="Mazot"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.Icons.RECEIPT_LONG, label="Gider/Hasat"),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS_OUTLINED, selected_icon=ft.Icons.ANALYTICS, label="Rapor"),
        ],
    )

    page.add(ft.Column([header, body_container, nav_bar], spacing=0, expand=True))
    navigate_to(0)


if __name__ == "__main__":
    ft.app(target=main)
