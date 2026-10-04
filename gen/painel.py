"""Painel (dashboard) pessoal + helpers de cartões KPI reutilizados nos painéis do negócio."""
from lib import *
from ctx import *
from personal import month_dv, cf_pos_neg

CELL_PX = px(11)          # largura em pixels de uma coluna de 11 caracteres
ROW_PX = 22               # altura da linha padrão (16,5 pt)


def kpi_card(ctx, ws, r, c0, c1, label, value, vnum, sub, snum, accent, vsize=20, v_align="center"):
    """Cartão com 3 linhas: rótulo / valor / subtexto. value/sub podem ser fórmulas ('=...')."""
    B = ctx.book
    gap = T["bg"]
    lab = B.fmt(bg_color="#FFFFFF", font_size=8, bold=True, font_color=T["muted"], align="center",
                top=2, top_color=accent, left=5, left_color=gap, right=5, right_color=gap)
    val = B.fmt(bg_color="#FFFFFF", font_size=vsize, bold=True, font_color=T["ink"], align=v_align,
                num_format=vnum or "General", left=5, left_color=gap, right=5, right_color=gap, shrink=True)
    sub_f = B.fmt(bg_color="#FFFFFF", font_size=9, font_color=T["muted"], align="center",
                  num_format=snum or "General", bottom=5, bottom_color=gap, left=5, left_color=gap,
                  right=5, right_color=gap)
    B.merge(ws, r, c0, r, c1, label, lab)
    B.merge(ws, r + 1, c0, r + 1, c1, value, val)
    B.merge(ws, r + 2, c0, r + 2, c1, sub, sub_f)


def section_bar(ctx, ws, r, c0, c1, text, color):
    ctx.book.merge(ws, r, c0, r, c1, text, ctx.fmt(bg_color=color, font_color="#FFFFFF", bold=True, indent=1,
                                                     font_size=10))
    ws.set_row(r - 1, 22)


def chart_pos(ws, chart, row, left=True, span=6, h=320, w_cols=6):
    """Posiciona gráfico ocupando 6 colunas (L: B..G, R: H..M)."""
    w = CELL_PX * span - 8
    chart.set_size({"width": w, "height": h})
    ws.insert_chart(row - 1, 1 if left else 7, chart, {"x_offset": 4, "y_offset": 4, "object_position": 1})


def painel_pessoal(ctx):
    k, ws, B = "PAINEL", ctx.ws["PAINEL"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("pessoal")
    ra = N["RESUMO"]
    nome = ctx.cfg("cfg_nome")
    title = f'="📊 Painel — "&{nome}' if not ctx.aut else f'="👤 Painel Pessoal — "&{nome}'
    ctx.page(k, [11] * 12, title,
             "Escolha o mês no menu suspenso: cartões, gráficos e alertas se atualizam sozinhos.", bg=True, landscape=False, one_page=True)
    wb = B.wb

    # --- seletor de mês
    ws.set_row(CS - 1, 28)
    ws.merge_range(CS - 1, 1, CS - 1, 2, "📅 Mês de análise", B.fmt(bold=True, font_size=11, align="right", bg_color=T["bg"]))
    sf = ctx.f_input(align="center", bold=True, font_size=12)
    ws.merge_range(CS - 1, 3, CS - 1, 4, "", sf)
    if ctx.demo:
        ws.write(CS - 1, 3, "Setembro", sf)
    else:
        B.f(ws, A(CS, 4), f"=INDEX({ctx.cfg_list('c_mes', 12)},MAX(1,{ctx.dados('d_R')}))", sf)
    month_dv(ctx, ws, A(CS, 4))
    B.merge(ws, CS, 7, CS, 8, "Ano de referência", B.fmt(bold=True, align="right", bg_color=T["bg"], font_color=T["muted"]))
    B.merge(ws, CS, 9, CS, 9, f"={ctx.cfg('cfg_ano')}", B.fmt(bold=True, align="center", bg_color="#FFFFFF", num_format="0",
                                                              border=1, border_color=T["line2"]))
    B.merge(ws, CS, 10, CS, 13, "← o ano e a meta de poupança ficam na aba Config",
            B.fmt(italic=True, font_size=8, font_color=T["muted"], bg_color=T["bg"], indent=1))
    ws.set_row(CS, 8)

    m = ctx.dados("d_mpainel")
    ix = lambda row: f"INDEX({X(ra, RNG(row, 3, row, 14))},{m})"
    ixp = lambda row: f"INDEX({X(ra, RNG(row, 3, row, 14))},{m}-1)"
    ent, sai, acum, taxa = L["ra_enttot"], L["ra_saitot"], L["ra_acum"], L["ra_taxa"]
    r = CS + 2
    ws.set_row(r - 1, 18)
    ws.set_row(r, 36)
    ws.set_row(r + 1, 20)

    def delta(row):
        return (f'=IF({m}=1,"—",IF({ixp(row)}=0,"—",IF({ix(row)}>={ixp(row)},"▲ ","▼ ")&'
                f'TEXT(ABS({ix(row)}/{ixp(row)}-1),"0%")&" vs mês anterior"))')

    kpi_card(ctx, ws, r, 2, 3, "ENTRADAS DO MÊS", f"={ix(ent)}", MONEY_INT, delta(ent), None, T["ent"])
    kpi_card(ctx, ws, r, 4, 5, "SAÍDAS DO MÊS", f"={ix(sai)}", MONEY_INT, delta(sai), None, T["sai"])
    kpi_card(ctx, ws, r, 6, 7, "SALDO DO MÊS", f"={ix(ent)}-{ix(sai)}", MONEY_INT,
             f'=IF({ix(ent)}-{ix(sai)}>=0,"Sobrou dinheiro ✓","Gastou mais do que ganhou")', None, T["saldo"])
    kpi_card(ctx, ws, r, 8, 9, "TAXA DE POUPANÇA", f'=IF({ix(ent)}=0,0,{ix(taxa)})', "0%",
             f'="Meta: "&TEXT({ctx.cfg("cfg_meta")},"0%")', None, "#7C3AED")
    kpi_card(ctx, ws, r, 10, 11, "SALDO ACUMULADO", f"={ix(acum)}", MONEY_INT, "no ano, até o mês escolhido", None, "#0891B2")
    rk = L["d_rank_r0"]
    kpi_card(ctx, ws, r, 12, 13, "MAIOR GASTO DO MÊS", f"={X(N['DADOS'], AA(rk, 10))}", None,
             f"={X(N['DADOS'], AA(rk, 11))}", '"R$" #,##0.00', "#F59E0B", vsize=12)
    # cores condicionais
    sv = A(r + 1, 6)
    ws.conditional_format(sv, {"type": "cell", "criteria": "<", "value": 0, "format": B.fmt(font_color=T["neg"])})
    ws.conditional_format(sv, {"type": "cell", "criteria": ">=", "value": 0, "format": B.fmt(font_color=T["pos"])})
    pv = A(r + 1, 8)
    meta = ctx.cfg("cfg_meta")
    ws.conditional_format(pv, {"type": "formula", "criteria": f"={pv}>={meta}", "format": B.fmt(font_color=T["pos"])})
    ws.conditional_format(pv, {"type": "formula", "criteria": f"={pv}<0", "format": B.fmt(font_color=T["neg"])})
    av = A(r + 1, 10)
    ws.conditional_format(av, {"type": "cell", "criteria": "<", "value": 0, "format": B.fmt(font_color=T["neg"])})
    for c, up_bad in ((2, False), (4, True)):
        sc = A(r + 2, c)
        up, dn = (T["neg"], T["pos"]) if up_bad else (T["pos"], T["neg"])
        ws.conditional_format(sc, {"type": "text", "criteria": "begins with", "value": "▲", "format": B.fmt(font_color=up)})
        ws.conditional_format(sc, {"type": "text", "criteria": "begins with", "value": "▼", "format": B.fmt(font_color=dn)})
    ws.conditional_format(A(r + 2, 6), {"type": "text", "criteria": "begins with", "value": "Gastou",
                                        "format": B.fmt(font_color=T["neg"])})

    # --- gráficos (linha 1)
    r1 = CS + 6
    hdr = L["ra_hdr"]
    cats = f"={X(ra, RNG(hdr, 3, hdr, 14))}"
    col = wb.add_chart({"type": "column"})
    col.add_series({"name": "Entradas", "categories": cats, "values": f"={X(ra, RNG(ent, 3, ent, 14))}",
                    "fill": {"color": T["ent"]}, "gap": 70, "overlap": -5})
    col.add_series({"name": "Saídas", "categories": cats, "values": f"={X(ra, RNG(sai, 3, sai, 14))}",
                    "fill": {"color": T["sai"]}})
    ln = wb.add_chart({"type": "line"})
    sd = L["ra_saldo"]
    ln.add_series({"name": "Saldo do mês", "categories": cats, "values": f"={X(ra, RNG(sd, 3, sd, 14))}",
                   "line": {"color": T["saldo"], "width": 2.25},
                   "marker": {"type": "circle", "size": 6, "fill": {"color": "#FFFFFF"}, "border": {"color": T["saldo"], "width": 1.5}}})
    col.combine(ln)
    style_chart(col, "Entradas × Saídas × Saldo — mês a mês", 484, 320)
    chart_pos(ws, col, r1, True)

    dn = wb.add_chart({"type": "doughnut"})
    dr = L["d_don_r0"]
    dd = N["DADOS"]
    dn.add_series({"name": "Saídas do mês", "categories": f"={X(dd, RNG(dr, 13, dr + 7, 13))}",
                   "values": f"={X(dd, RNG(dr, 14, dr + 7, 14))}",
                   "points": [{"fill": {"color": c}} for c in PALETTE],
                   "data_labels": {"percentage": True, "font": {"name": FONT, "size": 8, "color": "#FFFFFF", "bold": True}}})
    dn.set_hole_size(52)
    style_chart(dn, "Para onde foi o dinheiro", 484, 320, legend="right")
    dn.set_title({"name": f"={X(dd, AA(*L['d_title_don']))}", "name_font": {"name": FONT, "size": 11, "bold": True, "color": T["ink"]}})
    chart_pos(ws, dn, r1, False)

    # --- gráficos (linha 2)
    r2 = r1 + 16
    ac = wb.add_chart({"type": "area"})
    ac.add_series({"name": "Saldo acumulado", "categories": cats, "values": f"={X(ra, RNG(acum, 3, acum, 14))}",
                   "fill": {"color": "#BFDBFE", "transparency": 25}, "line": {"color": T["saldo"], "width": 2.25}})
    style_chart(ac, "Saldo acumulado ao longo do ano", 484, 320, legend=None)
    chart_pos(ws, ac, r2, True)

    bar = wb.add_chart({"type": "bar"})
    rkr = L["d_rank_r0"]
    bar.add_series({"name": "Realizado", "categories": f"={X(dd, RNG(rkr, 10, rkr + 7, 10))}",
                    "values": f"={X(dd, RNG(rkr, 11, rkr + 7, 11))}", "fill": {"color": T["teal"]}, "gap": 45, "overlap": -5})
    bar.add_series({"name": "Planejado", "categories": f"={X(dd, RNG(rkr, 10, rkr + 7, 10))}",
                    "values": f"={X(dd, RNG(rkr, 12, rkr + 7, 12))}", "fill": {"color": "#CBD5E1"}})
    style_chart(bar, "Top 8 categorias: realizado × planejado", 484, 320, reverse_x=True, horizontal=True)
    chart_pos(ws, bar, r2, False)

    # --- metas
    r3 = r2 + 16
    section_bar(ctx, ws, r3, 2, 13, "🎯  METAS DE ECONOMIA", th["mid"])
    hd = ctx.f_head(th, font_size=9)
    heads = [(2, 4, "Meta"), (5, 6, "Guardado"), (7, 8, "Valor alvo"), (9, 9, "%"), (10, 12, "Progresso"), (13, 13, "Situação")]
    for c0, c1, t in heads:
        B.merge(ws, r3 + 1, c0, r3 + 1, c1, t, hd)
    mt = N["METAS"]
    wh = lambda **kw: B.fmt(bg_color="#FFFFFF", bottom=1, bottom_color=T["line"], **kw)
    for i in range(5):
        rr = r3 + 2 + i
        mr = L["m_r0"] + i
        g = lambda c: X(mt, AA(mr, c))
        B.merge(ws, rr, 2, rr, 4, f'=IF({g(2)}="","",{g(2)})', wh(indent=1, bold=True))
        B.merge(ws, rr, 5, rr, 6, f'=IF({g(2)}="","",{g(7)})', wh(num_format=MONEY_INT, align="center"))
        B.merge(ws, rr, 7, rr, 8, f'=IF({g(2)}="","",{g(3)})', wh(num_format=MONEY_INT, align="center"))
        B.merge(ws, rr, 9, rr, 9, f'=IF({g(8)}="","",{g(8)})', wh(num_format="0%", align="center", bold=True))
        B.merge(ws, rr, 10, rr, 12, f'=IF({g(9)}="","",{g(9)})', wh(font_color=T["teal_mid"], font_size=9))
        B.merge(ws, rr, 13, rr, 13, f'=IF({g(2)}="","",{g(13)})', wh(align="center", font_size=8, bold=True))
    rg = f"{A(r3 + 2, 13)}:{A(r3 + 6, 13)}"
    for txt, fc, bg in [("Concluída", T["pos"], T["pos_bg"]), ("Atrasada", T["neg"], T["neg_bg"]),
                        ("No prazo", T["saldo"], T["navy_light"])]:
        ws.conditional_format(rg, {"type": "text", "criteria": "containing", "value": txt,
                                   "format": B.fmt(font_color=fc, bg_color=bg)})
    ws.write(r3 + 7 - 1 + 1, 1, "Veja todas as metas e o simulador de aportes na aba Metas.",
             B.fmt(italic=True, font_size=8, font_color=T["muted"], bg_color=T["bg"], indent=1))

    # --- alertas
    r4 = r3 + 9
    section_bar(ctx, ws, r4, 2, 13, "🔔  ALERTAS E INSIGHTS DO MÊS", th["mid"])
    nover, planned = ctx.dados("d_nover"), X(N["ORC"], AA(L["o_tot"], 3))
    saldo = f"({ix(ent)}-{ix(sai)})"
    msgs = [
        f'=IF(AND({ix(ent)}=0,{ix(sai)}=0),"ℹ Ainda não há lançamentos neste mês.",IF({saldo}<0,'
        f'"⚠ Você gastou R$ "&FIXED(-{saldo},2)&" a mais do que ganhou neste mês.",'
        f'"✓ Mês no azul: sobraram R$ "&FIXED({saldo},2)&" depois de todas as saídas."))',
        f'=IF({planned}=0,"ℹ Defina o orçamento por categoria na aba Orçamento para receber alertas de gastos.",'
        f'IF({nover}=0,"✓ Nenhuma categoria acima do orçamento neste mês.",'
        f'"⚠ "&{nover}&" categoria(s) acima do orçamento planejado — veja a aba Orçamento."))',
        f'=IF({ix(ent)}=0,"ℹ Registre suas entradas do mês para calcular a taxa de poupança.",'
        f'IF({ix(taxa)}>={meta},"✓ Meta de poupança atingida: "&TEXT({ix(taxa)},"0%")&" (meta "&TEXT({meta},"0%")&").",'
        f'"⚠ Taxa de poupança de "&TEXT({ix(taxa)},"0%")&", abaixo da meta de "&TEXT({meta},"0%")&"."))',
    ]
    for i, f in enumerate(msgs):
        rr = r4 + 1 + i
        ws.set_row(rr - 1, 24)
        B.merge(ws, rr, 2, rr, 13, f, B.fmt(bg_color="#FFFFFF", indent=1, bottom=1, bottom_color=T["line"], font_size=10))
    ar = f"{A(r4 + 1, 2)}:{A(r4 + 3, 13)}"
    for ch, fc, bg in [("⚠", T["warn"], T["warn_bg"]), ("✓", T["pos"], T["pos_bg"]), ("ℹ", T["saldo"], T["navy_light"])]:
        ws.conditional_format(ar, {"type": "text", "criteria": "begins with", "value": ch,
                                   "format": B.fmt(font_color=fc, bg_color=bg, bold=True)})
    ctx.painel_last_row = r4 + 4
