"""はむ鯖 専用画面のパネル画像（2倍解像度）を作る。

出力（assets/hamu/textures/font/ に置く）:
  panel_buy_0..3.png  … 市場の「買う」画面   (U+E020〜E023)
  panel_sell_0..3.png … 市場の「売る」画面   (U+E024〜E027)
  panel_list_0..3.png … 市場の一覧画面       (U+E028〜E02B)

絵は 352x444 で描き、4枚（176x222）に分けて保存する。Minecraft はフォントの1文字を 256px までしか
描けないため（v4 で 352x444 を1枚にしたら表示されなかった）。ゲーム内では合わせて 176x222
（チェスト6段の画面と同じ大きさ）になる。
座標はすべてゲーム内の 1 倍の値で書き、描くときに 2 倍する。
スロット (列 c, 段 r) の枠は x=7+18c, y=17+18r から 18x18。持ち物欄は y=139 から、ホットバーは y=197 から。

使い方: python tools/gen_panels.py <出力フォルダ>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2  # 解像度の倍率
W, H = 176, 222
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"

NAVY = (22, 24, 38, 255)        # 地の色（Nozk の #161826 に近い濃紺）
BAR = (31, 34, 53, 255)         # タイトル帯・下段
CELL = (34, 38, 58, 255)        # スロットの枠
CELL_EDGE = (52, 57, 84, 255)
GOLD = (201, 162, 39, 255)
BOX = (6, 7, 12, 255)           # 数字の黒い枠
BOX_EDGE = (58, 63, 90, 255)
WHITE = (240, 240, 245, 255)


def font(px):
    return ImageFont.truetype(FONT, px * S, index=0)


def rect(d, x, y, w, h, fill, edge=None, width=1, radius=2):
    d.rounded_rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], radius=radius * S, fill=fill,
                        outline=edge, width=width * S if edge else 0)


def text(d, cx, cy, s, px, fill):
    f = font(px)
    d.text((cx * S, cy * S), s, font=f, fill=fill, anchor="mm")


def slot(c, r):
    return 7 + 18 * c, 17 + 18 * r


def base():
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rect(d, 0, 0, W, H, NAVY, GOLD, 1, 4)
    rect(d, 2, 2, W - 4, 13, BAR, None, radius=2)                 # タイトル帯
    d.line([(4 * S, 128 * S), ((W - 4) * S, 128 * S)], fill=GOLD, width=S)  # 持ち物欄との境目
    for r in range(3):
        for c in range(9):
            rect(d, 7 + 18 * c, 139 + 18 * r, 18, 18, CELL, CELL_EDGE, 1, 1)
    for c in range(9):
        rect(d, 7 + 18 * c, 197, 18, 18, CELL, CELL_EDGE, 1, 1)
    return im, d


def button(d, c, r, label, fill, edge, px=7, fg=WHITE, span=1):
    x, y = slot(c, r)
    rect(d, x + 0.5, y + 0.5, 18 * span - 1, 17, fill, edge, 1, 2)
    text(d, x + 18 * span / 2, y + 9, label, px, fg)


def trade(sell):
    im, d = base()
    # 品物の枠（スロット4）
    x, y = slot(4, 0)
    rect(d, x - 1, y - 1, 20, 20, CELL, GOLD, 1, 2)
    # 買う／売るの切り替え（スロット0）
    button(d, 0, 0, "買う" if sell else "売る", (40, 44, 70, 255), (120, 130, 180, 255), 7)
    # 現在価格・数量の黒い枠
    rect(d, 100, 24, 71, 33, BOX, BOX_EDGE, 1, 2)
    rect(d, 100, 60, 71, 29, BOX, BOX_EDGE, 1, 2)
    # 数量のボタン（段4）
    red, red_e = (122, 42, 42, 255), (205, 90, 90, 255)
    green, green_e = (42, 92, 46, 255), (110, 200, 110, 255)
    for c, s in zip((0, 1, 2), ("-64", "-10", "-1")):
        button(d, c, 4, s, red, red_e)
    for c, s in zip((6, 7, 8), ("+1", "+10", "+64")):
        button(d, c, 4, s, green, green_e)
    button(d, 4, 4, "入力", GOLD, (255, 220, 120, 255), 7, (30, 24, 8, 255))
    # 下段：戻る・全部・合計・決定・閉じる
    button(d, 0, 5, "◀", (60, 64, 90, 255), (150, 156, 190, 255), 8)
    button(d, 2, 5, "全部", (30, 60, 70, 255), (90, 200, 220, 255), 7)
    rect(d, 61, 108, 54, 17, BOX, BOX_EDGE, 1, 2)                 # 合計の枠（スロット48〜50）
    if sell:
        button(d, 6, 5, "売却する", (150, 82, 20, 255), (240, 160, 70, 255), 7, span=2)
    else:
        button(d, 6, 5, "購入する", (44, 110, 50, 255), (120, 220, 120, 255), 7, span=2)
    button(d, 8, 5, "×", (122, 42, 42, 255), (205, 90, 90, 255), 8)
    return im


def listing():
    im, d = base()
    for r in range(5):
        for c in range(9):
            rect(d, 7 + 18 * c, 17 + 18 * r, 18, 18, CELL, CELL_EDGE, 1, 1)
    rect(d, 3, 107, W - 6, 19, BAR, None, radius=2)               # 下段（戻る・ページ・閉じる）
    for c in (0, 3, 4, 5, 8):
        rect(d, 7 + 18 * c, 107, 18, 18, CELL, CELL_EDGE, 1, 1)
    return im


def save_tiles(im, out, name):
    """Minecraft はフォントの1文字を 256px までしか描けないので、352x444 を 176x222 の4枚に分ける。
    並び：_0 左上、_1 右上、_2 左下、_3 右下。gui.json では高さ 111（上段 ascent 13・下段 ascent -98）で使う。"""
    w, h = im.width // 2, im.height // 2
    for i, (x, y) in enumerate(((0, 0), (w, 0), (0, h), (w, h))):
        im.crop((x, y, x + w, y + h)).save(out / f"{name}_{i}.png")


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    save_tiles(trade(False), out, "panel_buy")
    save_tiles(trade(True), out, "panel_sell")
    save_tiles(listing(), out, "panel_list")


if __name__ == "__main__":
    main()
