"""Biblioteca base para gerar as planilhas (xlsxwriter).

Convenções: linhas/colunas 1-indexadas nos helpers (A, AA, RNG); fórmulas sempre em
inglês com vírgulas (o Excel/Sheets traduzem para o idioma do usuário ao abrir).
"""
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name

FONT = "Arial"

# ---------------------------------------------------------------- endereços
def col(c):
    return xl_col_to_name(c - 1)


def A(r, c, ra=False, ca=False):
    return xl_rowcol_to_cell(r - 1, c - 1, row_abs=ra, col_abs=ca)


def AA(r, c):
    return A(r, c, True, True)


def RNG(r1, c1, r2, c2, absolute=True):
    f = AA if absolute else A
    return f"{f(r1, c1)}:{f(r2, c2)}"


def S(sheet):
    return "'" + sheet.replace("'", "''") + "'"


def X(sheet, ref):
    return f"{S(sheet)}!{ref}"


# ---------------------------------------------------------------- tema
T = dict(
    ink="#0F172A", text="#334155", muted="#64748B", line="#E2E8F0", line2="#CBD5E1",
    bg="#F1F5F9", white="#FFFFFF", zebra="#F8FAFC",
    input_bg="#FFF9DB", input_fg="#1D4ED8", input_line="#E7D98B",
    pos="#15803D", pos_bg="#DCFCE7", neg="#B91C1C", neg_bg="#FEE2E2",
    warn="#B45309", warn_bg="#FEF3C7",
    teal="#0F766E", teal_dark="#115E59", teal_light="#CCFBF1", teal_mid="#14B8A6",
    navy="#1E3A8A", navy_dark="#172554", navy_light="#DBEAFE",
    orange="#C2410C", orange_mid="#EA580C", orange_light="#FFEDD5",
    ent="#10B981", sai="#F43F5E", saldo="#2563EB", plan="#94A3B8",
)
PALETTE = ["#0F766E", "#2563EB", "#F59E0B", "#E11D48", "#7C3AED", "#0891B2", "#65A30D", "#94A3B8"]

MONEY = '"R$" #,##0.00;-"R$" #,##0.00'
MONEY0 = '"R$" #,##0.00;-"R$" #,##0.00;"–"'
MONEY_INT = '"R$" #,##0;-"R$" #,##0'
PCT = "0%"
PCT1 = "0.0%"
DATE = "dd/mm/yyyy"


class Book:
    """Envolve o Workbook: cache de formatos + gravação de fórmulas com valor em cache."""

    def __init__(self, path, cache=None):
        self.wb = xlsxwriter.Workbook(path)
        self.cache = cache or {}
        self._fmts = {}

    def fmt(self, **kw):
        base = {"font_name": FONT, "font_size": 10, "valign": "vcenter", "font_color": T["text"]}
        base.update(kw)
        key = tuple(sorted(base.items()))
        if key not in self._fmts:
            self._fmts[key] = self.wb.add_format(base)
        return self._fmts[key]

    def f(self, ws, a1, formula, fmt=None):
        """Grava fórmula; no 2º passe usa o valor calculado pelo LibreOffice como cache."""
        v = self.cache.get((ws.get_name(), a1), "")
        if v is None:
            v = ""
        ws.write_formula(a1, formula, fmt, v)

    def merge(self, ws, r1, c1, r2, c2, value, fmt):
        """Mescla; value pode ser texto, número ou fórmula (str iniciando com '=')."""
        rng = f"{A(r1, c1)}:{A(r2, c2)}"
        if (r1, c1) == (r2, c2):
            if isinstance(value, str) and value.startswith("="):
                self.f(ws, A(r1, c1), value, fmt)
            else:
                ws.write(r1 - 1, c1 - 1, value, fmt)
            return
        if isinstance(value, str) and value.startswith("="):
            ws.merge_range(rng, "", fmt)
            self.f(ws, A(r1, c1), value, fmt)
        else:
            ws.merge_range(rng, value, fmt)

    def close(self):
        self.wb.close()


# ---------------------------------------------------------------- navegação
def partition(widths, n):
    """Divide colunas contíguas em n grupos com larguras o mais parecidas possível (índices 0-based)."""
    m = len(widths)
    n = min(n, m)
    ideal = sum(widths) / n
    pre = [0.0]
    for w in widths:
        pre.append(pre[-1] + w)
    INF = float("inf")
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for g in range(1, n + 1):
        for j in range(g, m + 1):
            for i in range(g - 1, j):
                c = cost[g - 1][i] + (pre[j] - pre[i] - ideal) ** 2
                if c < cost[g][j]:
                    cost[g][j], back[g][j] = c, i
    groups, j = [], m
    for g in range(n, 0, -1):
        i = back[g][j]
        groups.append((i, j - 1))
        j = i
    return groups[::-1]


def nav_bar(book, ws, widths, rows, current, row0=1, first_col=2):
    """rows: lista de dicts {color, light, tag, items:[(rótulo, aba)]}.
    Cada botão é um hiperlink interno (funciona no Excel e no Google Sheets)."""
    for ri, spec in enumerate(rows):
        r = row0 + ri
        ws.set_row(r - 1, 22)
        items = list(spec["items"])
        cells = ([("__tag__", spec["tag"])] if spec.get("tag") else []) + items
        groups = partition(widths, len(cells))
        for (label, target), (g0, g1) in zip(cells, groups):
            c0, c1 = first_col + g0, first_col + g1
            if label == "__tag__":
                f = book.fmt(bg_color=spec["color"], font_color="#FFFFFF", bold=True, font_size=8,
                             align="center", border=1, border_color="#FFFFFF")
                book.merge(ws, r, c0, r, c1, target, f)
                continue
            is_cur = target == current
            f = book.fmt(bg_color="#FFFFFF" if is_cur else spec["color"],
                         font_color=spec["color"] if is_cur else "#FFFFFF",
                         bold=True, font_size=9, align="center",
                         border=1, border_color="#FFFFFF" if not is_cur else spec["color"],
                         underline=0)
            if c0 != c1:
                ws.merge_range(r - 1, c0 - 1, r - 1, c1 - 1, "", f)
            ws.write_url(r - 1, c0 - 1, f"internal:{S(target)}!A1", f, label)
    return row0 + len(rows)


# ---------------------------------------------------------------- gráficos
def style_chart(ch, title, w, h, legend="bottom", y_fmt=MONEY_INT, y_title=None, x_font=9,
                gridlines=True, reverse_x=False, horizontal=False):
    ch.set_title({"name": title, "name_font": {"name": FONT, "size": 11, "bold": True, "color": T["ink"]},
                  "overlay": False})
    ch.set_size({"width": w, "height": h})
    ch.set_chartarea({"border": {"color": T["line"], "width": 0.75}, "fill": {"color": "#FFFFFF"}})
    ch.set_plotarea({"fill": {"none": True}, "border": {"none": True}})
    if legend:
        ch.set_legend({"position": legend, "font": {"name": FONT, "size": 9, "color": T["text"]}})
    else:
        ch.set_legend({"none": True})
    xa = {"num_font": {"name": FONT, "size": x_font, "color": T["muted"]}, "line": {"color": T["line2"]},
          "major_tick_mark": "none"}
    if reverse_x:
        xa["reverse"] = True
        xa["crossing"] = "max" if horizontal else "min"
    ya = {"num_font": {"name": FONT, "size": 9, "color": T["muted"]}, "num_format": y_fmt,
          "line": {"none": True}, "major_tick_mark": "none"}
    if gridlines:
        ya["major_gridlines"] = {"visible": True, "line": {"color": T["line"], "width": 0.75}}
    else:
        ya["major_gridlines"] = {"visible": False}
    if y_title:
        ya["name"] = y_title
        ya["name_font"] = {"name": FONT, "size": 9, "color": T["muted"]}
    if horizontal:   # em gráficos de barras o eixo de categorias é o 'y' do xlsxwriter
        ch.set_y_axis(xa)
        ch.set_x_axis(ya)
    else:
        ch.set_x_axis(xa)
        ch.set_y_axis(ya)


def px(width_chars):
    return int(width_chars * 7 + 5)
