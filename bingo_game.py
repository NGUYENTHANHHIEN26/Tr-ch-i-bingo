import os
import random
import re
import sys
WIDTH = 72
USE_COLOR = sys.stdout.isatty()

COLORS = {
    "reset": "\033[0m",
    "title": "\033[95m",
    "primary": "\033[96m",
    "success": "\033[92m",
    "danger": "\033[91m",
    "warning": "\033[93m",
    "muted": "\033[90m",
    "bold": "\033[1m"}
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def styled_input(prompt, color="primary"):
    return input(colorize(prompt, color))


def colorize(text, color):
    if not USE_COLOR:
        return text
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def money_text(amount):
    return f"{amount:,.2f}"


def fit_ansi_text(text, max_visible, continuation_color=None):
    """continuation_color: after inner RESET codes, re-apply so padding stays colored (no black border glitch)."""
    cont = COLORS.get(continuation_color, "") if continuation_color and USE_COLOR else ""
    plain = ANSI_RE.sub("", text)
    if len(plain) <= max_visible:
        pad_len = max_visible - len(plain)
        pad = (cont + " " * pad_len + COLORS["reset"]) if cont and pad_len else (" " * pad_len)
        return text + pad

    out = []
    i = 0
    visible = 0
    while i < len(text) and visible < max_visible:
        if text[i] == "\033":
            m = ANSI_RE.match(text, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
        out.append(text[i])
        visible += 1
        i += 1

    if cont:
        out.append(cont)
    out.append(COLORS["reset"])
    return "".join(out)


def print_box(lines, width=WIDTH, color=None):
    top = "╔" + "═" * width + "╗"
    bottom = "╚" + "═" * width + "╝"
    separator = "╟" + "─" * width + "╢"
    if color:
        top = colorize(top, color)
        bottom = colorize(bottom, color)
        separator = colorize(separator, color)
    border_on = COLORS.get(color, "") if color and USE_COLOR else ""
    border_off = COLORS["reset"] if border_on else ""
    print(top)
    for line in lines:
        if line is None:
            print(separator)
            continue
        inner = fit_ansi_text(line, width - 1, continuation_color=color)
        if border_on:
            print(border_on + "║ " + inner + border_on + "║" + border_off)
        else:
            print(f"║ {inner}║")
    print(bottom)


def print_title(text, width=WIDTH):
    title_line = colorize(text.center(width - 1), "title")
    print_box([title_line], width=width, color="primary")


def show_result(title, message):
    print()
    t = title.lower()
    theme = "success" if "thang" in t else "danger" if "thua" in t else "warning"
    print_box(
        [colorize(title.upper(), "bold"), "", message],
        width=WIDTH,
        color=theme)


def pause():
    styled_input("\nNhấn Enter để tiếp tục...", "muted")


def nhap_so_tien_ban_dau():
    while True:
        try:
            so_tien = float(styled_input("Nhập số tiền ban đầu trong tài khoản: "))
            if so_tien > 0:
                return so_tien
            print("Số tiền phải lớn hơn 0. Vui lòng nhập lại.")
        except ValueError:
            print("Dữ liệu không hợp lệ. Vui lòng nhập một số.")


def quay_so_bingo():
    return [random.randint(0, 9) for _ in range(3)]


def format_bingo_result(ket_qua):
    balls = [f"[ {num} ]" for num in ket_qua]
    return " ".join(balls)


def print_ket_qua_bingo(ket_qua, tong=None, ket_luan=None):
    s = f"\nKết quả bingo: {format_bingo_result(ket_qua)}"
    if tong is not None and ket_luan is not None:
        s += f" -> Tổng = {tong} ({ket_luan.upper()})"
    print(colorize(s, "primary"))


def nhap_so_chon():
    while True:
        try:
            so = int(styled_input("Nhập số bạn muốn chọn (0-9): "))
            if 0 <= so <= 9:
                return so
            print("Số phải nằm trong khoảng từ 0 đến 9.")
        except ValueError:
            print("Dữ liệu không hợp lệ. Vui lòng nhập số nguyên.")


def nhap_tien_cuoc(so_du):
    if so_du <= 0:
        show_result(
            "Số dư không đủ",
            "Tài khoản của bạn đã hết tiền. Vui lòng quay lại menu để thoát hoặc xem số dư.")
        return None
    while True:
        try:
            t = float(styled_input("Nhập số tiền đặt cược: "))
            if t <= 0:
                print("Số tiền cược phải lớn hơn 0.")
            elif t > so_du:
                print("Số tiền cược vượt qua số dư hiện tại.")
            else:
                return t
        except ValueError:
            print("Dữ liệu không hợp lệ. Vui lòng nhập một số.")


def choi_bingo_1_so(so_du):
    so_chon = nhap_so_chon()
    tien_cuoc = nhap_tien_cuoc(so_du)
    if tien_cuoc is None:
        return so_du
    ket_qua = quay_so_bingo()
    print_ket_qua_bingo(ket_qua)

    if so_chon in ket_qua:
        tien_thang = tien_cuoc * 2
        so_du += tien_thang
        show_result("Thắng cược", f"Trúng Bingo 1 số! Bạn nhận được {money_text(tien_thang)}")
    else:
        so_du -= tien_cuoc
        show_result("Thua cược", f"Không trúng. Bạn bị trừ {money_text(tien_cuoc)}")

    return so_du


def choi_chon_2_so_trung_nhau(so_du):
    so_chon = nhap_so_chon()
    tien_cuoc = nhap_tien_cuoc(so_du)
    if tien_cuoc is None:
        return so_du
    ket_qua = quay_so_bingo()
    print_ket_qua_bingo(ket_qua)

    so_lan_trung = ket_qua.count(so_chon)
    if so_lan_trung >= 2:
        tien_thang = tien_cuoc * 3
        so_du += tien_thang
        show_result("Thắng cược", f"Có {so_lan_trung} số trúng! Bạn nhận được {money_text(tien_thang)}")
    else:
        so_du -= tien_cuoc
        show_result("Thua cược", f"Không đạt điều kiện 2 số giống nhau. Bạn bị trừ {money_text(tien_cuoc)}")

    return so_du


def xac_dinh_tai_xiu_hoa(tong):
    return ("xiu" if tong <= 8 else "hoa") if tong <= 18 else "tai"


def nhap_lua_chon_tai_xiu_hoa():
    lua_chon_hop_le = {"tai", "xiu", "hoa"}
    while True:
        lua_chon = styled_input("Chọn kết quả (tai/xiu/hoa): ").strip().lower()
        if lua_chon in lua_chon_hop_le:
            return lua_chon
        print("Lựa chọn không hợp lệ. Vui lòng nhập tai, xiu hoặc hoa.")


def choi_lon_nho_hoa(so_du):
    lua_chon = nhap_lua_chon_tai_xiu_hoa()
    tien_cuoc = nhap_tien_cuoc(so_du)
    if tien_cuoc is None:
        return so_du
    ket_qua = quay_so_bingo()
    tong = sum(ket_qua)
    ket_luan = xac_dinh_tai_xiu_hoa(tong)
    print_ket_qua_bingo(ket_qua, tong=tong, ket_luan=ket_luan)

    if lua_chon == ket_luan:
        tien_thang = tien_cuoc * 0.5
        so_du += tien_thang
        show_result("Thắng cược", f"Bạn thắng {money_text(tien_thang)} (50% tiền cược)")
    else:
        so_du -= tien_cuoc
        show_result("Thua cược", f"Không trúng. Bạn bị trừ {money_text(tien_cuoc)}")

    return so_du


def in_so_du(so_du):
    show_result("Số dư tài khoản", f"Số tiền hiện tại: {money_text(so_du)}")


def ghi_so_du_ra_file(so_du):
    ten_file = styled_input("Nhập tên file text để lưu (ví dụ: sodu.txt): ").strip() or "so_du_tai_khoan.txt"
    if not ten_file.lower().endswith(".txt"):
        ten_file += ".txt"

    with open(ten_file, "w", encoding="utf-8") as f:
        f.write(f"Số dư tài khoản còn lại: {money_text(so_du)}\n")

    show_result("Lưu file thành công", f"Đã ghi số dư vào file: {ten_file}")


def hien_thi_menu(so_du):
    clear_screen()
    print_title("TRÒ CHƠI BINGO", width=WIDTH)
    menu_lines = [
        colorize(f"Số dư hiện tại: {money_text(so_du)}", "bold"),
        "",
        None,
        colorize("[1]", "success") + "  Bingo 1 số (trúng 1 trong 3 số)",
        colorize("[2]", "success") + "  Chọn 2 số trùng nhau",
        colorize("[3]", "success") + "  Lớn / Nhỏ / Hòa",
        None,
        "",
        colorize("[4]", "warning") + "  Xem số dư tài khoản",
        colorize("[5]", "warning") + "  Lưu số dư ra file text",
        None,
        colorize("[0]", "danger") + "  Thoát game",
    ]
    print_box(menu_lines, width=WIDTH, color="primary")


def main():
    so_du = nhap_so_tien_ban_dau()
    games = {
        "1": choi_bingo_1_so,
        "2": choi_chon_2_so_trung_nhau,
        "3": choi_lon_nho_hoa,
    }
    while True:
        hien_thi_menu(so_du)
        chon = styled_input("Nhập lựa chọn của bạn: ").strip()

        if chon in games:
            so_du = games[chon](so_du)
            pause()
        elif chon == "4":
            in_so_du(so_du)
            pause()
        elif chon == "5":
            ghi_so_du_ra_file(so_du)
            pause()
        elif chon == "0":
            print(colorize("Cảm ơn bạn đã chơi. Tạm biệt!", "muted"))
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            pause()


if __name__ == "__main__":
    main()
