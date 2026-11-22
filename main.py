import os
from datetime import date
import flet as ft
from database import TarlaDatabase

# --- KURUMSAL RENK PALETİ ---
PRIMARY_DARK = "#143626"
PRIMARY_GREEN = "#1e5638"
ACCENT_GREEN = "#2e7d4f"
BG_LIGHT = "#f4f7f4"
CARD_BG = "#ffffff"
SOFT_GREEN = "#eaf3ec"
SOFT_RED = "#fdf0ef"
DANGER_RED = "#c0392b"
TEXT_DARK = "#1c2b22"
TEXT_MUTED = "#637368"
BORDER_COLOR = "#dce5de"


def tl_fmt(val: float) -> str:
    return f"{val:,.2f} ₺".replace(",", "X").replace(".", ",").replace("X", ".")


def num_fmt(val: float) -> str:
    s = f"{val:,.3f}".rstrip("0").rstrip(".")
    if not s:
        return "0"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def parse_num(raw: str | None, default: float = 0.0) -> float:
    if not raw:
        return default
    try:
        return float(str(raw).strip().replace(",", "."))
    except ValueError:
        return default


def main(page: ft.Page):
    page.title = "Şaban Gök ve Oğulları - Tarla Takip"
    page.bgcolor = BG_LIGHT
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY_GREEN,
        font_family="Roboto",
    )

    app_data_dir = os.getenv("FLET_APP_STORAGE_DATA") or os.path.dirname(os.path.abspath(__file__))
    os.makedirs(app_data_dir, exist_ok=True)
    db = TarlaDatabase(os.path.join(app_data_dir, "tarla_verileri.db"))

    def show_snack(msg: str, is_error: bool = False):
        page.snack_bar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.ERROR_OUTLINE if is_error else ft.Icons.CHECK_CIRCLE_OUTLINE,
                        color=ft.Colors.WHITE,
                        size=20,
                    ),
                    ft.Text(
                        msg,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=DANGER_RED if is_error else PRIMARY_GREEN,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.margin.all(12),
            shape=ft.RoundedRectangleBorder(radius=10),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    # --- STANDART FORM VE UI BİLEŞENLERİ (TÜM FLET SÜRÜMLERİYLE UYUMLU) ---
    def styled_tf(label: str, value: str = "", hint_text: str | None = None, keyboard_type=None, multiline: bool = False, min_lines: int = 1, max_lines: int = 1):
        return ft.TextField(
            label=label,
            value=value,
            hint_text=hint_text,
            keyboard_type=keyboard_type,
            multiline=multiline,
            min_lines=min_lines,
            max_lines=max_lines,
            border_radius=10,
            filled=True,
            fill_color="#f9fbf9",
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY_GREEN,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            label_style=ft.TextStyle(color=TEXT_MUTED, size=13),
        )

    def styled_dd(label: str, options: list, value: str | None = None):
        return ft.Dropdown(
            label=label,
            value=value,
            options=options,
            expand=True,
            border_radius=10,
            filled=True,
            fill_color="#f9fbf9",
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY_GREEN,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            label_style=ft.TextStyle(color=TEXT_MUTED, size=13),
        )

    def stat_card(title: str, value: str, icon: str, color: str = ACCENT_GREEN):
        return ft.Container(
            col={"xs": 6, "sm": 6, "md": 3},
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, size=16, color=color),
                                bgcolor=f"{color}18",
                                padding=6,
                                border_radius=8,
                            ),
                            ft.Text(
                                title,
                                size=12,
                                color=TEXT_MUTED,
                                weight=ft.FontWeight.W_500,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_DARK,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=CARD_BG,
            padding=12,
            border_radius=14,
            border=ft.border.all(1, BORDER_COLOR),
            shadow=ft.BoxShadow(blur_radius=8, color="#0d000000", offset=ft.Offset(0, 2)),
        )

    def section_panel(title: str, controls: list, icon: str | None = None):
        header_row = [
            ft.Text(
                title,
                size=15,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY_DARK,
                expand=True,
            )
        ]
        if icon:
            header_row.insert(0, ft.Icon(icon, size=19, color=PRIMARY_GREEN))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(header_row, spacing=8),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    *controls,
                ],
                spacing=12,
            ),
            bgcolor=CARD_BG,
            padding=16,
            border_radius=14,
            border=ft.border.all(1, BORDER_COLOR),
            shadow=ft.BoxShadow(blur_radius=6, color="#08000000", offset=ft.Offset(0, 2)),
        )

    def primary_btn(text: str, icon: str, on_click, bg: str = PRIMARY_GREEN):
        return ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=ft.Colors.WHITE),
                    ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=bg,
            height=46,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=1,
            ),
            on_click=on_click,
        )

    body_container = ft.Container(expand=True)

    # Çentik (Notch) ve durum çubuğu uyumlu üst başlık
    header = ft.Container(
        content=ft.SafeArea(
            bottom=False,
            content=ft.Container(
                padding=ft.padding.symmetric(vertical=12, horizontal=16),
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.AGRICULTURE_ROUNDED, color=PRIMARY_DARK, size=24),
                            bgcolor="#d7eadc",
                            padding=10,
                            border_radius=12,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "ŞABAN GÖK VE OĞULLARI",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    "Tarla Masraf & Kâr Yönetim Sistemi",
                                    size=12,
                                    color="#c5e0cd",
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
            ),
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[PRIMARY_DARK, PRIMARY_GREEN],
        ),
    )

    # --- SAYFA 0: ANA SAYFA & TARLALARIM ---
    def build_ana_sayfa():
        rapor = db.get_genel_rapor()
        net_renk = PRIMARY_GREEN if rapor["net_kar"] >= 0 else DANGER_RED

        tarla_kartlari = []
        for ozet in rapor["tarla_ozetleri"]:
            t = ozet["tarla"]
            t_net = ozet["net"]
            is_profit = t_net >= 0
            tarla_kartlari.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.ECO_ROUNDED, color=PRIMARY_GREEN, size=20),
                                            ft.Text(
                                                t["ad"],
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXT_DARK,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                        ],
                                        spacing=6,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            t["urun"] or "Ürün Yok",
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color=PRIMARY_DARK if t["urun"] else TEXT_MUTED,
                                        ),
                                        bgcolor=SOFT_GREEN if t["urun"] else "#eef1ee",
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=20,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                f"Alan: {num_fmt(t['donum'])} Dönüm ({num_fmt(t['donum']*2500)} m²)",
                                size=12,
                                color=TEXT_MUTED,
                            ),
                            ft.Container(
                                bgcolor="#f8faf8",
                                padding=10,
                                border_radius=10,
                                content=ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                ft.Text("Toplam Gider", size=11, color=TEXT_MUTED),
                                                ft.Text(
                                                    tl_fmt(ozet["toplam_gider"]),
                                                    size=13,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=DANGER_RED,
                                                ),
                                            ],
                                            spacing=2,
                                            expand=True,
                                        ),
                                        ft.Container(width=1, height=28, bgcolor=BORDER_COLOR),
                                        ft.Column(
                                            [
                                                ft.Text("Toplam Gelir", size=11, color=TEXT_MUTED),
                                                ft.Text(
                                                    tl_fmt(ozet["gelir"]),
                                                    size=13,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=PRIMARY_GREEN,
                                                ),
                                            ],
                                            spacing=2,
                                            expand=True,
                                            horizontal_alignment=ft.CrossAxisAlignment.END,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        bgcolor=SOFT_GREEN if is_profit else SOFT_RED,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                        border_radius=8,
                                        content=ft.Text(
                                            f"Net: {tl_fmt(t_net)}",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_GREEN if is_profit else DANGER_RED,
                                        ),
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Row(
                                            [
                                                ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=18),
                                                ft.Text("Düzenle", size=13, weight=ft.FontWeight.W_600),
                                            ],
                                            spacing=4,
                                        ),
                                        style=ft.ButtonStyle(
                                            color=PRIMARY_GREEN,
                                            side=ft.BorderSide(1.2, PRIMARY_GREEN),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda e, tid=t["id"]: open_tarla_editor(tid),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=CARD_BG,
                    padding=14,
                    border_radius=14,
                    border=ft.border.all(1, BORDER_COLOR),
                    shadow=ft.BoxShadow(blur_radius=6, color="#08000000", offset=ft.Offset(0, 2)),
                )
            )

        return ft.ListView(
            padding=14,
            spacing=12,
            expand=True,
            controls=[
                ft.Text("İşletme Özeti", size=17, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.ResponsiveRow(
                    spacing=10,
                    run_spacing=10,
                    controls=[
                        stat_card("Toplam Tarla", f"{rapor['tarla_sayisi']} Adet", ft.Icons.GRID_VIEW_ROUNDED),
                        stat_card("Toplam Dönüm", f"{num_fmt(rapor['toplam_donum'])} Dönüm", ft.Icons.SQUARE_FOOT_ROUNDED),
                        stat_card("Toplam Gelir", tl_fmt(rapor["toplam_gelir"]), ft.Icons.TRENDING_UP_ROUNDED, PRIMARY_GREEN),
                        stat_card("Toplam Gider", tl_fmt(rapor["toplam_gider"]), ft.Icons.TRENDING_DOWN_ROUNDED, DANGER_RED),
                        stat_card("Net Kâr / Zarar", tl_fmt(rapor["net_kar"]), ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, net_renk),
                        stat_card("Toplam Hasat", f"{num_fmt(rapor['toplam_hasat'])} Ton", ft.Icons.AGRICULTURE_ROUNDED),
                        stat_card("Ortak Gider", tl_fmt(rapor["ortak_gider"]), ft.Icons.PIE_CHART_ROUNDED),
                        stat_card("Toplam Alan", f"{num_fmt(rapor['toplam_alan'])} m²", ft.Icons.MAP_OUTLINED),
                    ],
                ),
                ft.Divider(height=4, color="transparent"),
                ft.Text("Tarlalarım (10 Tarla)", size=17, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                *tarla_kartlari,
            ],
        )

    # --- TARLA DÜZENLEME EKRANI ---
    def open_tarla_editor(tarla_id: int):
        ozet = db.get_tarla_finans_ozeti(tarla_id)
        if not ozet:
            return
        t = ozet["tarla"]

        ad_tf = styled_tf("Tarla Adı", value=t["ad"])
        urun_tf = styled_tf("Ekili Ürün", value=t["urun"], hint_text="Buğday, arpa, mısır")
        donum_tf = styled_tf("Tarla Dönümü", value=str(t["donum"]), keyboard_type=ft.KeyboardType.NUMBER)
        m2_txt = ft.Text(f"Metrekare: {num_fmt(t['donum']*2500)} m² (1 dönüm = 2.500 m²)", size=12, color=TEXT_MUTED)

        def on_donum_change(e):
            d = max(0.0, parse_num(donum_tf.value))
            m2_txt.value = f"Metrekare: {num_fmt(d*2500)} m² (1 dönüm = 2.500 m²)"
            page.update()

        donum_tf.on_change = on_donum_change

        tohum_tf = styled_tf("Tohum Gideri (₺)", value=str(t["tohum_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        mazot_tf = styled_tf("Doğrudan Mazot Gideri (₺)", value=str(t["mazot_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        su_tf = styled_tf("Su Gideri (₺)", value=str(t["su_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        malzeme_tf = styled_tf("Malzeme Gideri (₺)", value=str(t["malzeme_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        hasat_tf = styled_tf("Hasat Ücreti (₺)", value=str(t["hasat_gider"]), keyboard_type=ft.KeyboardType.NUMBER)
        diger_tf = styled_tf("Diğer Giderler (₺)", value=str(t["diger_gider"]), keyboard_type=ft.KeyboardType.NUMBER)

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
            ft.Text("Kapsamlı Finansal Döküm", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
            ft.Divider(height=1, color="#c0d8c3"),
            ft.Text(f"1. Sabit/Temel Giderler: {tl_fmt(ozet['temel'])}", size=13),
            ft.Text(f"2. Tarla Ek Giderleri: {tl_fmt(ozet['ek_gider'])}", size=13),
        ]
        for eg in ozet["ek_liste"]:
            detay_satirlari.append(
                ft.Text(f"   • {eg['tur']} ({eg['aciklama'] or 'Açıklamasız'}): {tl_fmt(eg['tutar'])}", size=12, color=TEXT_MUTED)
            )

        detay_satirlari.append(ft.Text(f"3. İlaç & Gübre Maliyeti: {tl_fmt(ozet['ilac_gubre'])}", size=13))
        for il in ozet["ilac_liste"]:
            detay_satirlari.append(
                ft.Text(f"   • {il['urun_ad'] or 'Ürün'} ({num_fmt(il['miktar'])} {il['temel_birim'] or ''}): {tl_fmt(il['maliyet'])}", size=12, color=TEXT_MUTED)
            )

        detay_satirlari.append(ft.Text(f"4. Mazot Deposu Maliyeti: {tl_fmt(ozet['mazot_depo'])}", size=13))
        for mz in ozet["mazot_liste"]:
            detay_satirlari.append(
                ft.Text(f"   • {num_fmt(mz['miktar'])} L Mazot Çıkışı: {tl_fmt(mz['maliyet'])}", size=12, color=TEXT_MUTED)
            )

        detay_satirlari.extend([
            ft.Text(f"5. Ortak Gider Payı: {tl_fmt(ozet['ortak_pay'])}", size=13),
            ft.Divider(height=6, color="#c0d8c3"),
            ft.Text(f"Toplam Gider: {tl_fmt(ozet['toplam_gider'])}", weight=ft.FontWeight.BOLD, color=DANGER_RED),
            ft.Text(f"Toplam Gelir: {tl_fmt(ozet['gelir'])}", weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
        ])
        for hs in ozet["hasat_liste"]:
            detay_satirlari.append(
                ft.Text(f"   • {hs['urun']}: {num_fmt(hs['miktar'])} Ton - Gelir: {tl_fmt(hs['gelir'])} (Alıcı: {hs['alici'] or '-'})", size=12, color=TEXT_MUTED)
            )

        detay_satirlari.extend([
            ft.Divider(height=6, color="#c0d8c3"),
            ft.Text(
                f"Net Kâr / Zarar: {tl_fmt(ozet['net'])}",
                weight=ft.FontWeight.BOLD,
                size=16,
                color=PRIMARY_GREEN if ozet["net"] >= 0 else DANGER_RED,
            ),
        ])

        body_container.content = ft.ListView(
            padding=14,
            spacing=12,
            expand=True,
            controls=[
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                            icon_color=PRIMARY_DARK,
                            bgcolor=CARD_BG,
                            on_click=lambda e: navigate_to(0),
                        ),
                        ft.Text(f"{t['ad']} Düzenle", size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK, expand=True),
                    ],
                    spacing=10,
                ),
                section_panel("Temel Bilgiler", [ad_tf, urun_tf, donum_tf, m2_txt], ft.Icons.INFO_OUTLINE),
                section_panel("Sabit / Doğrudan Tarla Giderleri", [tohum_tf, mazot_tf, su_tf, malzeme_tf, hasat_tf, diger_tf], ft.Icons.PAYMENTS_OUTLINED),
                ft.Container(
                    content=ft.Column(detay_satirlari, spacing=5),
                    bgcolor=SOFT_GREEN,
                    padding=14,
                    border_radius=14,
                    border=ft.border.all(1, "#c0d8c3"),
                ),
                primary_btn("Değişiklikleri Kaydet", ft.Icons.SAVE_ROUNDED, save_tarla),
                ft.OutlinedButton(
                    "Listeye Geri Dön",
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=lambda e: navigate_to(0),
                ),
            ],
        )
        page.update()

    # --- SAYFA 1: İLAÇ & GÜBRE DEPOSU (SEKMELİ YAPIDA) ---
    def build_depo_sayfa():
        tarlalar = db.get_tarlalar()
        urunler = db.get_depo_urunler()
        kullanimlar = db.get_kullanimlar()

        tur_dd = styled_dd("Ürün Türü", value="Gübre", options=[ft.dropdown.Option("Gübre"), ft.dropdown.Option("İlaç")])
        ad_tf = styled_tf("Ürün Adı", hint_text="Örnek: DAP Gübre")
        miktar_tf = styled_tf("Alınan Miktar", hint_text="Örnek: 5000", keyboard_type=ft.KeyboardType.NUMBER)
        birim_dd = styled_dd(
            "Birim",
            value="kg",
            options=[
                ft.dropdown.Option("kg", "Kilogram"),
                ft.dropdown.Option("ton", "Ton"),
                ft.dropdown.Option("litre", "Litre"),
                ft.dropdown.Option("ml", "Mililitre"),
                ft.dropdown.Option("gram", "Gram"),
            ],
        )
        fiyat_tf = styled_tf("Toplam Alış Fiyatı (₺)", hint_text="Örnek: 100000", keyboard_type=ft.KeyboardType.NUMBER)
        tarih_tf = styled_tf("Alış Tarihi", value=str(date.today()))

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

        k_tarla_dd = styled_dd("Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        k_urun_dd = styled_dd(
            "Depodan Ürün Seç",
            options=[ft.dropdown.Option(str(u["id"]), f"{u['ad']} ({num_fmt(u['kalan'])} {u['temel_birim']})") for u in urunler],
        )
        k_miktar_tf = styled_tf("Kullanılan Miktar", hint_text="Örnek: 200", keyboard_type=ft.KeyboardType.NUMBER)
        k_birim_dd = styled_dd(
            "Çıkış Ölçü Birimi",
            value="kg",
            options=[
                ft.dropdown.Option("kg", "Kilogram"),
                ft.dropdown.Option("ton", "Ton"),
                ft.dropdown.Option("litre", "Litre"),
                ft.dropdown.Option("ml", "Mililitre"),
                ft.dropdown.Option("gram", "Gram"),
            ],
        )
        k_tarih_tf = styled_tf("Kullanım Tarihi", value=str(date.today()))

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
                                ft.Text(f"{u['ad']} ({u['tur']})", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"Kalan: {num_fmt(u['kalan'])} / {num_fmt(u['miktar'])} {u['temel_birim']}", size=12, color=TEXT_MUTED),
                                ft.Text(f"Birim: {tl_fmt(u['birim_fiyat'])} | Stok Değeri: {tl_fmt(u['stok_degeri'])}", size=12, color=PRIMARY_GREEN, weight=ft.FontWeight.W_600),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, uid=u["id"]: try_delete_urun(uid)),
                    ]
                ),
                padding=12,
                bgcolor=SOFT_GREEN,
                border_radius=10,
            )
            for u in urunler
        ]

        kullanim_kartlari = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{k['tarla_ad']} → {k['urun_ad'] or '-'}", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"{num_fmt(k['miktar'])} {k['temel_birim'] or ''} | {tl_fmt(k['maliyet'])} | {k['tarih'] or '-'}", size=12, color=TEXT_MUTED),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            icon_color=DANGER_RED,
                            on_click=lambda e, kid=k["id"]: (db.delete_kullanim(kid), show_snack("Kullanım kaydı silindi, stok geri eklendi."), navigate_to(1)),
                        ),
                    ]
                ),
                padding=12,
                bgcolor="#f9fbf9",
                border=ft.border.all(1, BORDER_COLOR),
                border_radius=10,
            )
            for k in kullanimlar
        ]

        return ft.Tabs(
            selected_index=0,
            animation_duration=200,
            indicator_color=PRIMARY_GREEN,
            label_color=PRIMARY_GREEN,
            unselected_label_color=TEXT_MUTED,
            expand=True,
            tabs=[
                ft.Tab(
                    text="Tarlada Kullan",
                    icon=ft.Icons.AGRICULTURE_OUTLINED,
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            section_panel("Ürünü Tarlada Kullan", [k_tarla_dd, k_urun_dd, k_miktar_tf, k_birim_dd, k_tarih_tf, primary_btn("Tarlaya Çıkış Yap", ft.Icons.CHECK_ROUNDED, urun_kullan_click)]),
                            section_panel("Son Kullanımlar", kullanim_kartlari or [ft.Text("Henüz kullanım kaydı yok.", color=TEXT_MUTED)]),
                        ],
                    ),
                ),
                ft.Tab(
                    text="Depo & Alış",
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            section_panel("Yeni Ürün Alışı", [tur_dd, ad_tf, miktar_tf, birim_dd, fiyat_tf, tarih_tf, primary_btn("Depoya Ekle", ft.Icons.ADD_ROUNDED, alis_kaydet)]),
                            section_panel("Mevcut Stoklar", stok_kartlari or [ft.Text("Henüz depo ürünü yok.", color=TEXT_MUTED)]),
                        ],
                    ),
                ),
            ],
        )

    # --- SAYFA 2: MAZOT DEPOSU (SEKMELİ YAPIDA) ---
    def build_mazot_sayfa():
        tarlalar = db.get_tarlalar()
        alislar = db.get_mazot_alislar()
        cikislar = db.get_mazot_cikislar()

        toplam_l = sum(a["miktar"] for a in alislar)
        kull_l = sum(a["kullanilan"] for a in alislar)
        kalan_l = toplam_l - kull_l
        stok_val = sum(a["stok_degeri"] for a in alislar)

        m_miktar = styled_tf("Alınan Mazot (Litre)", keyboard_type=ft.KeyboardType.NUMBER)
        m_fiyat = styled_tf("Toplam Alış Fiyatı (₺)", keyboard_type=ft.KeyboardType.NUMBER)
        m_tarih = styled_tf("Alış Tarihi", value=str(date.today()))

        def mazot_alis_ekle(e):
            mk = parse_num(m_miktar.value)
            fy = parse_num(m_fiyat.value, -1.0)
            if mk <= 0 or fy < 0:
                show_snack("Litre ve fiyat bilgilerini kontrol et.", True)
                return
            db.add_mazot_alis(mk, fy, m_tarih.value)
            show_snack("Mazot depoya eklendi.")
            navigate_to(2)

        c_tarla = styled_dd("Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        c_alis = styled_dd(
            "Mazot Alış Kaydı Seç",
            options=[
                ft.dropdown.Option(str(a["id"]), f"{a['tarih'] or '-'} | {num_fmt(a['kalan'])} L ({tl_fmt(a['birim_fiyat'])}/L)")
                for a in alislar
                if a["kalan"] > 0
            ],
        )
        c_miktar = styled_tf("Çıkış Miktarı (Litre)", keyboard_type=ft.KeyboardType.NUMBER)
        c_tarih = styled_tf("Çıkış Tarihi", value=str(date.today()))

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
                                ft.Text(f"Alış ({a['tarih'] or '-'}) — {num_fmt(a['miktar'])} L", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"Kalan: {num_fmt(a['kalan'])} L | {tl_fmt(a['birim_fiyat'])}/L | Değer: {tl_fmt(a['stok_degeri'])}", size=12, color=TEXT_MUTED),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, aid=a["id"]: try_delete_alis(aid)),
                    ]
                ),
                padding=12,
                bgcolor="#f9fbf9",
                border=ft.border.all(1, BORDER_COLOR),
                border_radius=10,
            )
            for a in alislar
        ]

        cikis_kartlari = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{c['tarla_ad'] or '-'} — {num_fmt(c['miktar'])} L", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"Maliyet: {tl_fmt(c['maliyet'])} ({tl_fmt(c['birim_fiyat'])}/L) | {c['tarih'] or '-'}", size=12, color=TEXT_MUTED),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            icon_color=DANGER_RED,
                            on_click=lambda e, cid=c["id"]: (db.delete_mazot_cikis(cid), show_snack("Mazot çıkışı silindi, stok geri eklendi."), navigate_to(2)),
                        ),
                    ]
                ),
                padding=12,
                bgcolor=SOFT_GREEN,
                border_radius=10,
            )
            for c in cikislar
        ]

        ozet_row = ft.ResponsiveRow(
            spacing=10,
            run_spacing=10,
            controls=[
                stat_card("Kalan Mazot", f"{num_fmt(kalan_l)} L", ft.Icons.LOCAL_GAS_STATION_ROUNDED, PRIMARY_GREEN),
                stat_card("Stok Değeri", tl_fmt(stok_val), ft.Icons.PAYMENTS_ROUNDED),
                stat_card("Toplam Alınan", f"{num_fmt(toplam_l)} L", ft.Icons.ADD_CIRCLE_OUTLINE),
                stat_card("Kullanılan", f"{num_fmt(kull_l)} L", ft.Icons.REMOVE_CIRCLE_OUTLINE, DANGER_RED),
            ],
        )

        return ft.Tabs(
            selected_index=0,
            animation_duration=200,
            indicator_color=PRIMARY_GREEN,
            label_color=PRIMARY_GREEN,
            unselected_label_color=TEXT_MUTED,
            expand=True,
            tabs=[
                ft.Tab(
                    text="Mazot Çıkışı",
                    icon=ft.Icons.LOCAL_GAS_STATION_OUTLINED,
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            ozet_row,
                            section_panel("Tarlaya Mazot Gönder", [c_tarla, c_alis, c_miktar, c_tarih, primary_btn("Mazotu Gönder", ft.Icons.SEND_ROUNDED, mazot_cikis_ekle)]),
                            section_panel("Son Mazot Çıkışları", cikis_kartlari or [ft.Text("Henüz mazot çıkışı yok.", color=TEXT_MUTED)]),
                        ],
                    ),
                ),
                ft.Tab(
                    text="Mazot Alışı",
                    icon=ft.Icons.ADD_SHOPPING_CART_OUTLINED,
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            section_panel("Yeni Mazot Alışı", [m_miktar, m_fiyat, m_tarih, primary_btn("Mazot Depoya Ekle", ft.Icons.ADD_ROUNDED, mazot_alis_ekle)]),
                            section_panel("Alış Kayıtları", alis_kartlari or [ft.Text("Henüz mazot alışı yok.", color=TEXT_MUTED)]),
                        ],
                    ),
                ),
            ],
        )

    # --- SAYFA 3: TARLA GİDERİ, HASAT VE ORTAK GİDERLER (SEKMELİ YAPIDA) ---
    def build_islemler_sayfa():
        tarlalar = db.get_tarlalar()
        ek_giderler = db.get_ek_giderler()
        hasatlar = db.get_hasatlar()
        ortaklar = db.get_ortak_giderler()
        rapor = db.get_genel_rapor()

        eg_tarla = styled_dd("Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        eg_tur = styled_dd("Gider Türü", value="Su", options=[ft.dropdown.Option(x) for x in ["Su", "Elektrik", "İşçilik", "Tamir", "Nakliye", "Diğer"]])
        eg_aciklama = styled_tf("Açıklama (İsteğe Bağlı)", hint_text="Örnek: Sulama motoru arızası")
        eg_tutar = styled_tf("Gider Tutarı (₺)", keyboard_type=ft.KeyboardType.NUMBER)
        eg_tarih = styled_tf("Gider Tarihi", value=str(date.today()))

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

        h_tarla = styled_dd("Tarla Seç", options=[ft.dropdown.Option(str(t["id"]), t["ad"]) for t in tarlalar])
        h_urun = styled_tf("Hasat Edilen Ürün", hint_text="Buğday, arpa, mısır")
        h_miktar = styled_tf("Hasat Miktarı (Ton)", keyboard_type=ft.KeyboardType.NUMBER)
        h_fiyat = styled_tf("Satış Fiyatı (Ton Başına ₺)", keyboard_type=ft.KeyboardType.NUMBER)
        h_tarih = styled_tf("Hasat Tarihi", value=str(date.today()))
        h_alici = styled_tf("Alıcı / Firma", hint_text="Alıcı adı")

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

        o_aciklama = styled_tf("Gider Açıklaması", hint_text="Örnek: Traktör tamiri")
        o_kat = styled_dd("Gider Kategorisi", value="Mazot", options=[ft.dropdown.Option(x) for x in ["Mazot", "İşçilik", "Makine", "Nakliye", "Bakım", "Elektrik", "Diğer"]])
        o_tutar = styled_tf("Gider Tutarı (₺)", keyboard_type=ft.KeyboardType.NUMBER)
        o_tarih = styled_tf("Gider Tarihi", value=str(date.today()))
        o_paylasim = styled_dd(
            "Paylaştırma Şekli",
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
                        ft.Column(
                            [
                                ft.Text(f"{g['tarla_ad'] or '-'} — {g['tur']} ({tl_fmt(g['tutar'])})", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"{g['aciklama'] or '-'} | {g['tarih'] or '-'}", size=12, color=TEXT_MUTED),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, gid=g["id"]: (db.delete_ek_gider(gid), show_snack("Tarla gideri silindi."), navigate_to(3))),
                    ]
                ),
                padding=12,
                bgcolor=SOFT_RED,
                border_radius=10,
            )
            for g in ek_giderler
        ]

        hasat_list_ui = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{h['tarla_ad'] or '-'} — {h['urun']} ({num_fmt(h['miktar'])} Ton)", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"Gelir: {tl_fmt(h['gelir'])} ({tl_fmt(h['fiyat'])}/Ton) | {h['alici'] or '-'}", size=12, color=PRIMARY_GREEN, weight=ft.FontWeight.W_600),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, hid=h["id"]: (db.delete_hasat(hid), show_snack("Hasat kaydı silindi."), navigate_to(3))),
                    ]
                ),
                padding=12,
                bgcolor=SOFT_GREEN,
                border_radius=10,
            )
            for h in hasatlar
        ]

        ortak_list_ui = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(f"{o['aciklama']} ({o['kategori']}) — {tl_fmt(o['tutar'])}", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text(f"Paylaşım: {'Dönüme Göre' if o['paylasim']=='donum' else 'Eşit'} | {o['tarih'] or '-'}", size=12, color=TEXT_MUTED),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_RED, on_click=lambda e, oid=o["id"]: (db.delete_ortak_gider(oid), show_snack("Ortak gider silindi."), navigate_to(3))),
                    ]
                ),
                padding=12,
                bgcolor="#f9fbf9",
                border=ft.border.all(1, BORDER_COLOR),
                border_radius=10,
            )
            for o in ortaklar
        ]

        dagitim_ui = [
            ft.Row(
                [
                    ft.Text(oz["tarla"]["ad"], size=13, color=TEXT_DARK, expand=True),
                    ft.Text(tl_fmt(oz["ortak_pay"]), size=13, weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                ]
            )
            for oz in rapor["tarla_ozetleri"]
        ]

        return ft.Tabs(
            selected_index=0,
            animation_duration=200,
            indicator_color=PRIMARY_GREEN,
            label_color=PRIMARY_GREEN,
            unselected_label_color=TEXT_MUTED,
            expand=True,
            tabs=[
                ft.Tab(
                    text="Tarla Gideri",
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            section_panel("Yeni Tarla Gideri", [eg_tarla, eg_tur, eg_aciklama, eg_tutar, eg_tarih, primary_btn("Gideri Kaydet", ft.Icons.SAVE_ROUNDED, eg_kaydet)]),
                            section_panel("Kayıtlı Tarla Giderleri", ek_list_ui or [ft.Text("Henüz ek tarla gideri yok.", color=TEXT_MUTED)]),
                        ],
                    ),
                ),
                ft.Tab(
                    text="Hasat & Satış",
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            section_panel("Yeni Hasat / Satış", [h_tarla, h_urun, h_miktar, h_fiyat, h_tarih, h_alici, primary_btn("Hasat ve Satışı Kaydet", ft.Icons.CHECK_ROUNDED, h_kaydet)]),
                            section_panel("Hasat Geçmişi", hasat_list_ui or [ft.Text("Henüz hasat kaydı yok.", color=TEXT_MUTED)]),
                        ],
                    ),
                ),
                ft.Tab(
                    text="Ortak Gider",
                    content=ft.ListView(
                        padding=14,
                        spacing=12,
                        controls=[
                            section_panel("Yeni Ortak Gider", [o_aciklama, o_kat, o_tutar, o_tarih, o_paylasim, primary_btn("Ortak Gider Kaydet", ft.Icons.ADD_ROUNDED, o_kaydet)]),
                            section_panel("Ortak Gider Listesi", ortak_list_ui or [ft.Text("Henüz ortak gider yok.", color=TEXT_MUTED)]),
                            section_panel("Tarlalara Dağıtım", dagitim_ui),
                        ],
                    ),
                ),
            ],
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
                                    ft.Text(f"{t['ad']} ({t['urun'] or '-'})", weight=ft.FontWeight.BOLD, color=TEXT_DARK, expand=True),
                                    ft.Text(f"{num_fmt(t['donum'])} Dönüm", size=12, color=TEXT_MUTED),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                f"Sabit+Ek: {tl_fmt(o['temel']+o['ek_gider'])} • İlaç/Gübre: {tl_fmt(o['ilac_gubre'])} • Mazot: {tl_fmt(o['mazot_depo'])} • Ortak: {tl_fmt(o['ortak_pay'])}",
                                size=11,
                                color=TEXT_MUTED,
                            ),
                            ft.Divider(height=1, color="#c8decb"),
                            ft.Row(
                                [
                                    ft.Text(f"Gider: {tl_fmt(o['toplam_gider'])}", size=12, color=DANGER_RED),
                                    ft.Text(f"Gelir: {tl_fmt(o['gelir'])}", size=12, color=PRIMARY_GREEN),
                                    ft.Text(f"Net: {tl_fmt(o['net'])}", size=13, weight=ft.FontWeight.BOLD, color=net_c),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=12,
                    bgcolor=SOFT_GREEN,
                    border_radius=10,
                )
            )

        depo_durum_ui = [
            ft.Text(f"• {u['ad']} ({u['tur']}): Kalan {num_fmt(u['kalan'])} {u['temel_birim']} ({tl_fmt(u['stok_degeri'])})", size=12)
            for u in urunler
        ]
        if mazot_alislar:
            m_kalan = sum(a["kalan"] for a in mazot_alislar)
            m_deger = sum(a["stok_degeri"] for a in mazot_alislar)
            depo_durum_ui.append(
                ft.Text(f"• Mazot (Toplam): Kalan {num_fmt(m_kalan)} L ({tl_fmt(m_deger)})", size=12, weight=ft.FontWeight.BOLD)
            )

        json_yedek_tf = styled_tf("Yedek JSON Metni", multiline=True, min_lines=3, max_lines=5)

        def yedek_disa_aktar(e):
            json_yedek_tf.value = db.export_json()
            backup_path = os.path.join(app_data_dir, f"tarla-takip-yedek-{date.today()}.json")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(json_yedek_tf.value)
            show_snack(f"Yedek kaydedildi: {os.path.basename(backup_path)}")
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
            show_snack(f"CSV raporu kaydedildi: {os.path.basename(csv_path)}")

        def confirm_reset_dialog(e):
            def close_dlg(ev):
                dlg.open = False
                page.update()

            def do_reset(ev):
                dlg.open = False
                db.reset_all()
                show_snack("Bütün kayıtlar sıfırlandı ve 10 boş tarla oluşturuldu.")
                navigate_to(4)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Tüm Verileri Sil?", weight=ft.FontWeight.BOLD),
                content=ft.Text("Tüm tarla, depo, mazot ve hasat kayıtları kalıcı olarak silinecek. Emin misiniz?"),
                actions=[
                    ft.TextButton("İptal", on_click=close_dlg),
                    ft.ElevatedButton("Evet, Sil", bgcolor=DANGER_RED, color=ft.Colors.WHITE, on_click=do_reset),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        return ft.ListView(
            padding=14,
            spacing=12,
            expand=True,
            controls=[
                ft.Text("Genel İşletme Raporu", size=17, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.ResponsiveRow(
                    spacing=10,
                    run_spacing=10,
                    controls=[
                        stat_card("Toplam Gelir", tl_fmt(r["toplam_gelir"]), ft.Icons.TRENDING_UP_ROUNDED, PRIMARY_GREEN),
                        stat_card("Toplam Gider", tl_fmt(r["toplam_gider"]), ft.Icons.TRENDING_DOWN_ROUNDED, DANGER_RED),
                        stat_card("Net Kâr / Zarar", tl_fmt(r["net_kar"]), ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, PRIMARY_GREEN if r["net_kar"] >= 0 else DANGER_RED),
                        stat_card("Depo Giderleri", tl_fmt(r["depo_toplam"]), ft.Icons.INVENTORY_2_OUTLINED),
                    ],
                ),
                section_panel(
                    "Gider Dağılımı",
                    [
                        ft.Text(f"• Sabit ve Ek Tarla Giderleri: {tl_fmt(r['tarla_sabit_ek'])}", size=13),
                        ft.Text(f"• İlaç ve Gübre Kullanımı: {tl_fmt(r['ilac_gubre'])}", size=13),
                        ft.Text(f"• Mazot Çıkışları: {tl_fmt(r['mazot_depo'])}", size=13),
                        ft.Text(f"• Ortak Giderler: {tl_fmt(r['ortak_gider'])}", size=13),
                    ],
                    ft.Icons.PIE_CHART_OUTLINE,
                ),
                section_panel("Depo Stok Durumu", depo_durum_ui or [ft.Text("Depoda kayıtlı ürün yok.", color=TEXT_MUTED)], ft.Icons.WAREHOUSE_OUTLINED),
                section_panel("Tarla Bazlı Kâr-Zarar", tarla_satirlari, ft.Icons.ANALYTICS_OUTLINED),
                section_panel(
                    "Rapor ve Yedekleme",
                    [
                        primary_btn("CSV Raporu Dışa Aktar", ft.Icons.TABLE_VIEW_ROUNDED, csv_disa_aktar, "#4a5d50"),
                        primary_btn("JSON Yedek Oluştur", ft.Icons.DOWNLOAD_ROUNDED, yedek_disa_aktar, PRIMARY_GREEN),
                        json_yedek_tf,
                        primary_btn("JSON Yedeğinden Geri Yükle", ft.Icons.UPLOAD_ROUNDED, yedek_ice_aktar, ACCENT_GREEN),
                        primary_btn("Bütün Verileri Sıfırla", ft.Icons.DELETE_FOREVER_ROUNDED, confirm_reset_dialog, DANGER_RED),
                    ],
                    ft.Icons.BACKUP_OUTLINED,
                ),
            ],
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
        elevation=8,
        indicator_color="#d5e8d8",
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        on_change=lambda e: navigate_to(e.control.selected_index),
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME_ROUNDED, label="Tarlalar"),
            ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2_ROUNDED, label="İlaç/Gübre"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCAL_GAS_STATION_OUTLINED, selected_icon=ft.Icons.LOCAL_GAS_STATION_ROUNDED, label="Mazot"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.Icons.RECEIPT_LONG_ROUNDED, label="İşlemler"),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS_OUTLINED, selected_icon=ft.Icons.ANALYTICS_ROUNDED, label="Rapor"),
        ],
    )

    page.add(ft.Column([header, body_container, nav_bar], spacing=0, expand=True))
    navigate_to(0)


if __name__ == "__main__":
    ft.app(target=main)