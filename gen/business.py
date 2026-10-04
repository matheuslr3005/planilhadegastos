"""Abas do NEGÓCIO (versão Autônomo/MEI): A Receber, Impostos, Fluxo de Caixa,
Painel Negócio, Painel Geral e blocos auxiliares em Dados."""
import datetime as dt
from lib import *
from ctx import *
from personal import (MESES, cf_pos_neg, month_dv, lancamentos, NENT_L, NSAI_L)
from painel import kpi_card, section_bar, chart_pos
import demo


def reg(ctx, sheet, r0, c, n=None, r1=None):
    r1 = r1 or r0 + n - 1
    return X(ctx.N[sheet], RNG(r0, c, r1, c))


def selector(ctx, ws, sel_rc, key_hint):
    B, CS = ctx.book, ctx.CS
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
    B.merge(ws, CS, 10, CS, 13, key_hint, B.fmt(italic=True, font_size=8, font_color=T["muted"], bg_color=T["bg"], indent=1))
    ws.set_row(CS, 8)


# ===================================================================== A RECEBER
def recebimentos(ctx):
    k, ws, B = "REC", ctx.ws["REC"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("negocio")
    widths = [12, 26, 34, 14, 13, 13, 17, 12, 9, 14, 14, 9]
    ctx.page(k, widths, "💰 A Receber — vendas a prazo e cobranças",
             "Vendeu fiado ou combinou prazo? Registre aqui com o vencimento. Quando o cliente pagar, preencha a data do pagamento: o status é automático.",
             area="negocio")
    hr, r0, r1 = L["r_hr"], L["r_r0"], L["r_r1"]
    ano, hoje = ctx.cfg("cfg_ano"), ctx.cfg("cfg_hoje")
    cr = lambda c: X(N[k], RNG(r0, c, r1, c))
    EMI, CLI, VAL, VEN, PAG, STA, ABE, ATR = cr(2), cr(3), cr(5), cr(6), cr(7), cr(9), cr(11), cr(12)
    inyear = lambda rng: f'{rng},">="&DATE({ano},1,1),{rng},"<"&DATE({ano}+1,1,1)'
    # colunas
    fi = dict(font_color=T["input_fg"])
    ws.set_column(1, 1, 12, B.fmt(num_format=DATE, align="center", **fi))
    ws.set_column(2, 2, 26, B.fmt(**fi))
    ws.set_column(3, 3, 34, B.fmt(**fi))
    ws.set_column(4, 4, 14, B.fmt(num_format=MONEY, **fi))
    ws.set_column(5, 6, 13, B.fmt(num_format=DATE, align="center", **fi))
    ws.set_column(7, 7, 17, B.fmt(**fi))
    ws.set_column(8, 8, 12, B.fmt(align="center", bold=True, font_size=9))
    ws.set_column(9, 9, 9, B.fmt(align="center", num_format="0"))
    ws.set_column(10, 11, 14, B.fmt(num_format=MONEY0, font_color=T["muted"]))
    ws.set_column(12, 12, 9, B.fmt(font_color="#CBD5E1", font_size=7, num_format="0.0"), {"hidden": True})
    # faixa
    ws.set_row(CS - 1, 16)
    ws.set_row(CS, 26)
    ws.set_row(CS + 1, 6)
    lab = lambda: B.fmt(font_size=8, font_color=T["muted"], bg_color=T["bg"], bold=True, indent=1, top=2, top_color=th["mid"])
    val = lambda num, color=T["ink"]: B.fmt(font_size=14, bold=True, bg_color=T["bg"], num_format=num, indent=1, font_color=color, align="left")
    cards = [(2, 3, "EM ABERTO (A RECEBER)", f"=SUM({ABE})", MONEY, T["saldo"]),
             (4, 4, "EM ATRASO", f"=SUM({ATR})", MONEY, T["neg"]),
             (5, 6, "RECEBIDO NO ANO", f"=SUMIFS({VAL},{inyear(PAG)})", MONEY, T["pos"])]
    for c0, c1, label, fml, num, color in cards:
        B.merge(ws, CS, c0, CS, c1, label, lab())
        B.merge(ws, CS + 1, c0, CS + 1, c1, fml, val(num, color))
    n_nocli = f'SUMPRODUCT(({VAL}>0)*({CLI}=""))'
    n_novenc = f'SUMPRODUCT(({VAL}>0)*({VEN}="")*({PAG}=""))'
    chk = (f'=IF({n_nocli}>0,"⚠ "&{n_nocli}&" cobrança(s) sem cliente",'
           f'IF({n_novenc}>0,"⚠ "&{n_novenc}&" cobrança(s) em aberto sem vencimento — informe para projetar o caixa",'
           f'"✓ Tudo certo: "&COUNT({VAL})&" cobrança(s) registradas"))')
    B.merge(ws, CS, 7, CS, 12, "VERIFICAÇÃO AUTOMÁTICA", lab())
    B.merge(ws, CS + 1, 7, CS + 1, 12, chk, B.fmt(font_size=9, bold=True, bg_color=T["bg"], indent=1, font_color=T["pos"]))
    ws.conditional_format(f"{A(CS + 1, 7)}:{A(CS + 1, 12)}", {"type": "text", "criteria": "begins with", "value": "⚠",
                                                              "format": B.fmt(font_color=T["warn"])})
    heads = ["Data da venda", "Cliente", "Descrição", "Valor (R$)", "Vencimento", "Data do pagamento",
             "Forma", "Status", "Dias de atraso", "Em aberto", "Em atraso", "aux."]
    hf = ctx.f_head(th)
    ws.set_row(hr - 1, 30)
    for j, t in enumerate(heads):
        ws.write(hr - 1, 1 + j, t, hf)
    ws.write_comment(hr - 1, 6, "Preencha SÓ quando o cliente pagar. Vazio = ainda em aberto.", {"x_scale": 1.3})
    ws.write_comment(hr - 1, 2, "Digite o nome do cliente (texto livre).", {"x_scale": 1.2})
    tf = B.fmt(align="center", bold=True, font_size=9)
    for r in range(r0, r1 + 1):
        B.f(ws, A(r, 9), f'=IF($E{r}="","",IF($G{r}<>"","Pago",IF($F{r}="","Pendente",IF({hoje}>$F{r},"Atrasado","Pendente"))))', tf)
        B.f(ws, A(r, 10), f'=IF($I{r}="Atrasado",{hoje}-$F{r},"")', B.fmt(align="center", num_format="0"))
        B.f(ws, A(r, 11), f'=IF(AND($E{r}<>"",$G{r}=""),$E{r},0)', B.fmt(num_format=MONEY0, font_color=T["muted"]))
        B.f(ws, A(r, 12), f'=IF($I{r}="Atrasado",$E{r},0)', B.fmt(num_format=MONEY0, font_color=T["muted"]))
        B.f(ws, A(r, 13), f'=IF($I{r}="Atrasado",$J{r}+ROW()/1000000,0)', B.fmt(font_color="#CBD5E1", font_size=7, num_format="0.0"))
    if ctx.demo:
        rows, _ = demo.business_rows()
        d_f = B.fmt(num_format=DATE, align="center", **fi)
        t_f = B.fmt(**fi)
        m_f = B.fmt(num_format=MONEY, **fi)
        for i, (emi, cli, desc, valor, venc, pg, forma) in enumerate(rows):
            r = r0 + i
            ws.write_datetime(r - 1, 1, dt.datetime.combine(emi, dt.time()), d_f)
            ws.write(r - 1, 2, cli, t_f)
            ws.write(r - 1, 3, desc, t_f)
            ws.write_number(r - 1, 4, valor, m_f)
            ws.write_datetime(r - 1, 5, dt.datetime.combine(venc, dt.time()), d_f)
            if pg:
                ws.write_datetime(r - 1, 6, dt.datetime.combine(pg, dt.time()), d_f)
            ws.write(r - 1, 7, forma, t_f)
    # validações
    for c in (2, 6, 7):
        ws.data_validation(f"{A(r0, c)}:{A(r1, c)}", {"validate": "date", "criteria": "between", "minimum": dt.date(2000, 1, 1),
                                                      "maximum": dt.date(2100, 12, 31), "error_title": "Data inválida",
                                                      "error_message": "Use uma data válida, ex.: 15/03/2026.",
                                                      "input_title": "Data", "input_message": "Formato dd/mm/aaaa."})
    ws.data_validation(f"{A(r0, 5)}:{A(r1, 5)}", {"validate": "decimal", "criteria": ">", "value": 0,
                                                   "error_title": "Valor inválido", "error_message": "Digite um número maior que zero."})
    ws.data_validation(f"{A(r0, 8)}:{A(r1, 8)}", {"validate": "list", "source": "=" + ctx.cfg_list("c_forma", NFORMA), "ignore_blank": True})
    # formatação condicional
    for txt, fc, bg in [("Pago", T["pos"], T["pos_bg"]), ("Atrasado", T["neg"], T["neg_bg"]), ("Pendente", T["warn"], T["warn_bg"])]:
        ws.conditional_format(f"{A(r0, 9)}:{A(r1, 9)}", {"type": "cell", "criteria": "==", "value": f'"{txt}"',
                                                          "format": B.fmt(font_color=fc, bg_color=bg)})
    ws.conditional_format(f"{A(r0, 10)}:{A(r1, 10)}", {"type": "cell", "criteria": ">", "value": 30,
                                                       "format": B.fmt(font_color=T["neg"], bold=True)})
    full = f"{A(r0, 2)}:{A(r1, 13)}"
    ws.conditional_format(full, {"type": "formula", "criteria": "=MOD(ROW(),2)=0",
                                 "format": B.fmt(bg_color=T["zebra"], bottom=1, bottom_color=T["line"])})
    ws.conditional_format(full, {"type": "formula", "criteria": "=MOD(ROW(),2)=1", "format": B.fmt(bottom=1, bottom_color=T["line"])})
    ws.autofilter(hr - 1, 1, r1 - 1, 12)
    ws.freeze_panes(hr, 0)
    ws.repeat_rows(hr - 1)


# ===================================================================== IMPOSTOS
def impostos(ctx):
    k, ws, B = "IMP", ctx.ws["IMP"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("negocio")
    widths = [14, 16, 16, 13, 14, 14, 14, 14, 13, 26, 16, 16]
    ctx.page(k, widths, "🧾 Impostos — DAS do MEI, vencimentos e limite anual",
             "Escolha seu regime e confira os parâmetros (amarelo). A tabela mostra o imposto de cada mês, vencimento e status.",
             area="negocio")
    ano, hoje, R = ctx.cfg("cfg_ano"), ctx.cfg("cfg_hoje"), ctx.dados("d_R")
    p0 = L["i_p0"]
    sec = ctx.f_section(th)
    B.merge(ws, CS, 2, CS, 6, "PARÂMETROS", sec)
    params = [("Regime tributário", "MEI", None, ["MEI", "Simples Nacional", "Outro regime"]),
              ("Atividade do MEI", "Comércio e indústria" if ctx.demo else "Comércio e serviços", None, ["Comércio e indústria", "Serviços", "Comércio e serviços"]),
              ("Salário mínimo vigente (R$)", 1621, MONEY, None),
              ("% de INSS do MEI (sobre o salário mínimo)", 0.05, "0%", None),
              ("ICMS fixo — comércio/indústria (R$)", 1, MONEY, None),
              ("ISS fixo — serviços (R$)", 5, MONEY, None),
              ("Alíquota sobre a receita (Simples/outro)", 0.06, "0.0%", None),
              ("Limite anual de faturamento do MEI (R$)", 81000, MONEY, None),
              ("Início da atividade neste ano (mês 1-12)", 1, "0", None)]
    pr = {}
    for i, (label, v, num, lst) in enumerate(params):
        r = p0 + i
        B.merge(ws, r, 2, r, 4, label, B.fmt(indent=1, bottom=1, bottom_color=T["line"]))
        f = ctx.f_input(num, align="center")
        ws.merge_range(r - 1, 4, r - 1, 5, "", f)
        ws.write(r - 1, 4, v, f)
        pr[i] = X(N[k], AA(r, 5))
        if lst:
            ws.data_validation(A(r, 5), {"validate": "list", "source": lst, "error_message": "Escolha uma opção da lista."})
    ws.data_validation(A(p0 + 8, 5), {"validate": "integer", "criteria": "between", "minimum": 1, "maximum": 12,
                                      "error_message": "Digite um mês de 1 a 12."})
    regime, ativ, sm, inss, icms, iss, aliq, limite, inicio = (pr[i] for i in range(9))
    r = p0 + 9
    B.merge(ws, r, 2, r, 4, "Valor do DAS mensal (calculado)", B.fmt(bold=True, indent=1, bg_color=th["light"]))
    B.merge(ws, r, 5, r, 6, f'={sm}*{inss}+IF(OR({ativ}="Comércio e indústria",{ativ}="Comércio e serviços"),{icms},0)'
                           f'+IF(OR({ativ}="Serviços",{ativ}="Comércio e serviços"),{iss},0)',
            B.fmt(bold=True, num_format=MONEY, bg_color=th["light"], align="center", font_size=11))
    das = X(N[k], AA(r, 5))
    note = ("Valores de referência para 2026 (salário mínimo R$ 1.621; DAS-MEI = 5% do salário mínimo + ICMS/ISS fixos). "
            "Confirme sempre no Portal do Simples Nacional/Receita Federal, pois podem mudar. Para Simples Nacional ou outro "
            "regime, o imposto é estimado como % da receita recebida. Esta aba organiza — não substitui seu contador.")
    ws.merge_range(r, 1, r + 3, 5, note, B.fmt(italic=True, font_size=8, font_color=T["muted"], text_wrap=True, valign="top"))

    # tabela mensal
    hr, r0, tot = L["i_hdr"], L["i_r0"], L["i_tot"]
    lneg = N["LNEG"]
    ln = lambda c: X(lneg, RNG(L["l_r0"], c, L["l_r1"], c))
    rec = lambda c: X(N["REC"], RNG(L["r_r0"], c, L["r_r1"], c))
    slot1, slot2 = ctx.cfg_item("c_nent", 0), ctx.cfg_item("c_nent", 1)   # Vendas e Pagamento mensal = faturamento
    heads = ["Competência", "Receita recebida", "Imposto devido", "Vencimento", "Data do pagamento", "Valor pago (se diferente)",
             "Pago (R$)", "Status", "Em aberto", "Observação", "Receita acumulada", "Limite do período"]
    ws.set_row(hr - 1, 32)
    for j, t in enumerate(heads):
        ws.write(hr - 1, 1 + j, t, ctx.f_head(th))
    inp_d, inp_m = ctx.f_input(DATE, align="center"), ctx.f_input(MONEY)
    for i in range(12):
        r = r0 + i
        B.f(ws, A(r, 2), f"=DATE({ano},{i + 1},1)", ctx.f_calc("mmm/yyyy", align="center", bold=True))
        B.f(ws, A(r, 3), (f'=SUMIFS({rec(5)},{rec(7)},">="&$B{r},{rec(7)},"<"&EDATE($B{r},1))'
                          f'+IF({slot1}="",0,SUMIFS({ln(6)},{ln(4)},{slot1},{ln(2)},">="&$B{r},{ln(2)},"<"&EDATE($B{r},1)))'
                          f'+IF({slot2}="",0,SUMIFS({ln(6)},{ln(4)},{slot2},{ln(2)},">="&$B{r},{ln(2)},"<"&EDATE($B{r},1)))'),
            ctx.f_calc(MONEY0))
        B.f(ws, A(r, 4), f'=IF($B{r}<DATE({ano},{inicio},1),0,IF({regime}="MEI",{das},ROUND($C{r}*{aliq},2)))', ctx.f_calc(MONEY0, bold=True))
        B.f(ws, A(r, 5), f"=DATE(YEAR($B{r}),MONTH($B{r})+1,20)", ctx.f_calc(DATE, align="center"))
        pg = None
        if ctx.demo and i <= 7:
            pg = dt.datetime(2026, i + 2, 18 if i % 3 else 19)
        if pg:
            ws.write_datetime(r - 1, 5, pg, inp_d)
        else:
            ws.write_blank(r - 1, 5, None, inp_d)
        ws.write_blank(r - 1, 6, None, inp_m)
        B.f(ws, A(r, 8), f'=IF($F{r}="",0,IF($G{r}="",$D{r},$G{r}))', ctx.f_calc(MONEY0))
        B.f(ws, A(r, 9), f'=IF($D{r}=0,"—",IF($F{r}<>"","Pago",IF({hoje}>$E{r},"Atrasado",IF($B{r}>{hoje},"Futuro","A pagar"))))',
            ctx.f_calc(align="center", bold=True, font_size=9))
        B.f(ws, A(r, 10), f'=IF(AND($D{r}>0,$F{r}=""),$D{r},0)', ctx.f_calc(MONEY0, font_color=T["muted"]))
        ws.write_blank(r - 1, 10, None, ctx.f_input(align="left"))
        B.f(ws, A(r, 12), f"=SUM($C${r0}:C{r})", ctx.f_calc(MONEY0, font_color=T["muted"]))
        B.f(ws, A(r, 13), f"={limite}/12*(13-{inicio})",
            ctx.f_calc(MONEY0, font_color=T["muted"]))
    tf = lambda num=MONEY0: B.fmt(bold=True, bg_color=th["light"], top=1, top_color=th["mid"], num_format=num)
    ws.write(tot - 1, 1, "TOTAL", B.fmt(bold=True, bg_color=th["light"], indent=1, top=1, top_color=th["mid"]))
    for c in (5, 6, 7, 9, 11, 12, 13):
        ws.write(tot - 1, c - 1, "", tf())
    for c in (3, 4, 8, 10):
        B.f(ws, A(tot, c), f"=SUM({A(r0, c)}:{A(r0 + 11, c)})", tf())
    ws.data_validation(f"{A(r0, 6)}:{A(r0 + 11, 6)}", {"validate": "date", "criteria": "between", "minimum": dt.date(2000, 1, 1),
                                                        "maximum": dt.date(2100, 12, 31), "error_message": "Use uma data válida.",
                                                        "input_title": "Pagamento", "input_message": "Preencha a data em que pagou o DAS."})
    ws.data_validation(f"{A(r0, 7)}:{A(r0 + 11, 7)}", {"validate": "decimal", "criteria": ">=", "value": 0})
    for txt, fc, bg in [("Pago", T["pos"], T["pos_bg"]), ("Atrasado", T["neg"], T["neg_bg"]), ("A pagar", T["warn"], T["warn_bg"]),
                        ("Futuro", T["muted"], T["bg"])]:
        ws.conditional_format(f"{A(r0, 9)}:{A(r0 + 11, 9)}", {"type": "cell", "criteria": "==", "value": f'"{txt}"',
                                                               "format": B.fmt(font_color=fc, bg_color=bg)})
    ws.conditional_format(f"{A(r0, 10)}:{A(r0 + 11, 10)}", {"type": "cell", "criteria": ">", "value": 0, "format": B.fmt(font_color=T["warn"], bold=True)})

    # caixa do limite (à direita dos parâmetros)
    B.merge(ws, CS, 8, CS, 13, "LIMITE ANUAL DO MEI", ctx.f_section(th))
    acum = f"IF({R}=0,0,INDEX({RNG(r0, 12, r0 + 11, 12)},{R}))"
    prop = f"({limite}/12*(13-{inicio}))"
    items = [("Faturamento acumulado (até o mês de referência)", f"={acum}", MONEY),
             ("Limite proporcional ao período de atividade", f"={prop}", MONEY),
             ("% do limite utilizado", f"=IF({prop}=0,0,{acum}/{prop})", "0%"),
             ("Projeção de faturamento no ano (ritmo atual)", f"=IF({R}=0,0,{acum}/MAX(1,{R}-{inicio}+1)*(13-{inicio}))", MONEY),
             ("Projeção ÷ limite", f"=IF({prop}=0,0,{A(CS + 4, 12)}/{prop})", "0%")]
    for i, (label, f, num) in enumerate(items):
        r = CS + 1 + i
        B.merge(ws, r, 8, r, 11, label, B.fmt(indent=1, bottom=1, bottom_color=T["line"]))
        B.merge(ws, r, 12, r, 13, f, ctx.f_calc(num, bold=True, align="right"))
    r = CS + 6
    acc, pct, proj = AA(CS + 1, 12), AA(CS + 3, 12), AA(CS + 4, 12)
    msg = (f'=IF({regime}<>"MEI","ℹ Limite do MEI não se aplica ao regime selecionado.",'
           f'IF({acum}>{prop},"✖ Limite ultrapassado! Procure seu contador: o excesso pode exigir DAS complementar ou desenquadramento.",'
           f'IF({A(CS + 4, 12)}>{prop},"⚠ Pelo ritmo atual você ultrapassa o limite antes do fim do ano. Avalie com seu contador.",'
           f'IF({pct}>=0.8,"⚠ Atenção: mais de 80% do limite anual já foi utilizado.","✓ Dentro do limite anual do MEI."))))')
    ws.merge_range(r - 1, 7, r + 1, 12, "", B.fmt(text_wrap=True, bold=True, indent=1, valign="vcenter"))
    B.f(ws, A(r, 8), msg, B.fmt(text_wrap=True, bold=True, indent=1, valign="vcenter"))
    mrng = f"{A(r, 8)}:{A(r + 2, 13)}"
    for ch, fc, bg in [("✖", T["neg"], T["neg_bg"]), ("⚠", T["warn"], T["warn_bg"]), ("✓", T["pos"], T["pos_bg"]), ("ℹ", T["saldo"], T["navy_light"])]:
        ws.conditional_format(mrng, {"type": "text", "criteria": "begins with", "value": ch, "format": B.fmt(font_color=fc, bg_color=bg, bold=True)})
    B.merge(ws, r + 3, 8, r + 3, 13, "Até 20% acima do limite: DAS complementar. Acima de 20%: desenquadramento retroativo (consulte seu contador).",
            B.fmt(italic=True, font_size=8, font_color=T["muted"]))
    B.merge(ws, r + 4, 8, r + 4, 13, "Entrega da DASN-SIMEI (declaração anual): até 31 de maio do ano seguinte.",
            B.fmt(italic=True, font_size=8, font_color=T["muted"]))
    ctx.imp = dict(regime=regime, das=das, msg=X(N[k], AA(r, 8)), pct=X(N[k], AA(CS + 3, 12)), proj_ratio=X(N[k], AA(CS + 5, 12)),
                   acum=X(N[k], AA(CS + 1, 12)), prop=X(N[k], AA(CS + 2, 12)), r0=r0)
    # gráfico: faturamento acumulado × limite
    ch = ctx.book.wb.add_chart({"type": "line"})
    cats = f"={X(N[k], RNG(r0, 2, r0 + 11, 2))}"
    ch.add_series({"name": "Receita acumulada", "categories": cats, "values": f"={X(N[k], RNG(r0, 12, r0 + 11, 12))}",
                   "line": {"color": T["orange_mid"], "width": 2.75},
                   "marker": {"type": "circle", "size": 6, "fill": {"color": "#FFFFFF"}, "border": {"color": T["orange_mid"], "width": 1.5}}})
    ch.add_series({"name": "Limite do período", "categories": cats, "values": f"={X(N[k], RNG(r0, 13, r0 + 11, 13))}",
                   "line": {"color": T["sai"], "width": 2, "dash_type": "dash"}})
    style_chart(ch, "Faturamento acumulado × limite anual", 760, 300)
    ch.set_x_axis({"num_format": "mmm", "num_font": {"name": FONT, "size": 9, "color": T["muted"]}, "line": {"color": T["line2"]}, "text_axis": True})
    ws.insert_chart(tot + 1, 1, ch, {"x_offset": 4, "y_offset": 6})


# ===================================================================== FLUXO DE CAIXA
def fluxo(ctx):
    k, ws, B = "FLUXO", ctx.ws["FLUXO"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("negocio")
    widths = [40] + [12.5] * 12 + [15]
    ctx.page(k, widths, "📈 Fluxo de caixa do negócio — realizado e projetado",
             "Até o mês de referência os números são REALIZADOS; depois, PROJETADOS (a receber em aberto, DAS em aberto, "
             "média de despesas e retirada prevista).", area="negocio")
    ano, hoje, R = ctx.cfg("cfg_ano"), ctx.cfg("cfg_hoje"), "" + ctx.dados("d_R")
    sec = ctx.f_section(th)
    B.merge(ws, CS, 2, CS, 4, "PREMISSAS", sec)
    pr = L["f_prem"]
    lab = lambda: B.fmt(indent=1, bottom=1, bottom_color=T["line"])
    B.merge(ws, pr, 2, pr, 2, "Saldo do caixa em 1º de janeiro (R$)", lab())
    ws.merge_range(pr - 1, 2, pr - 1, 3, 4000 if ctx.demo else 0, ctx.f_input(MONEY, align="center"))
    B.merge(ws, pr + 1, 2, pr + 1, 2, "Retirada pessoal mensal prevista (R$)", lab())
    ws.merge_range(pr, 2, pr, 3, 3400 if ctx.demo else 0, ctx.f_input(MONEY, align="center"))
    B.merge(ws, pr + 2, 2, pr + 2, 2, "Despesa operacional média (R$)", lab())
    saldo0, prolab_prev, opex_avg = X(N[k], AA(pr, 3)), X(N[k], AA(pr + 1, 3)), X(N[k], AA(pr + 2, 3))
    B.merge(ws, pr + 3, 2, pr + 3, 2, "Mês de referência (último realizado)", lab())
    B.merge(ws, pr + 3, 3, pr + 3, 4, f'=IF({R}=0,"nenhum",INDEX({ctx.cfg_list("c_mes", 12)},{R}))',
            B.fmt(bold=True, align="center", bottom=1, bottom_color=T["line"], font_color=T["orange"]))
    B.merge(ws, pr + 4, 2, pr + 4, 2, "Receita média mensal realizada (R$)", lab())
    B.merge(ws, pr + 5, 2, pr + 5, 2, "% da receita média esperada nos meses futuros", lab())
    ws.merge_range(pr + 4, 2, pr + 4, 3, 0.8 if ctx.demo else 0.7, ctx.f_input("0%", align="center"))
    pct_new = X(N[k], AA(pr + 5, 3))
    rev_avg = X(N[k], AA(pr + 4, 3))
    dates, hdr, sit, f0 = L["f_dates"], L["f_hdr"], L["f_sit"], L["f_0"]
    ws.set_row(dates - 1, None, None, {"hidden": True})
    for m in range(1, 13):
        B.f(ws, A(dates, 2 + m), f"=DATE({ano},{m},1)", B.fmt(num_format=DATE))
    ws.set_row(hdr - 1, 24)
    ws.write(hdr - 1, 1, "Em R$", ctx.f_head(th, align="left", indent=1))
    for m in range(1, 13):
        B.f(ws, A(hdr, 2 + m), f"=INDEX({ctx.cfg_list('c_abrev', 12)},{m})", ctx.f_head(th))
    ws.write(hdr - 1, 14, "Ano", ctx.f_head(th))
    sf = B.fmt(font_size=8, bold=True, align="center", font_color=T["saldo"], bg_color=T["navy_light"])
    ws.write(sit - 1, 1, "", sf)
    for m in range(1, 13):
        B.f(ws, A(sit, 2 + m), f'=IF({m}<={R},"REALIZADO","PROJETADO")', sf)
    ws.write(sit - 1, 14, "", sf)
    ws.conditional_format(f"{A(sit, 3)}:{A(sit, 14)}", {"type": "cell", "criteria": "==", "value": '"PROJETADO"',
                                                         "format": B.fmt(font_color=T["warn"], bg_color=T["warn_bg"], italic=True)})
    ws.conditional_format(f"{A(hdr, 3)}:{A(hdr, 14)}", {"type": "formula", "criteria": f'={A(sit, 3, True)}="PROJETADO"',
                                                         "format": B.fmt(bg_color=T["warn_bg"], font_color=T["warn"])})

    # linhas do detalhe (realizado por categoria) — endereços
    e0, et, s0, st, ox = L["f_ent0"], L["f_enttot"], L["f_sai0"], L["f_saitot"], L["f_opex"]
    lneg = N["LNEG"]
    ln = lambda c: X(lneg, RNG(L["l_r0"], c, L["l_r1"], c))
    rc = lambda c: X(N["REC"], RNG(L["r_r0"], c, L["r_r1"], c))
    im = lambda c: X(N["IMP"], RNG(L["i_r0"], c, L["i_r0"] + 11, c))
    # linhas principais
    R_ = dict(ini=f0, rec=f0 + 1, ven=f0 + 2, men=f0 + 3, out=f0 + 4, nov=f0 + 5, ent=f0 + 6, dsp=f0 + 7, imp=f0 + 8,
              pro=f0 + 9, sai=f0 + 10, var=f0 + 11, fim=f0 + 12, res=f0 + 13, mar=f0 + 14)
    L["f_rows"] = R_
    labels = {"ini": ("Saldo inicial do mês", "n"), "rec": ("(+) Cobranças recebidas (A Receber)", "n"),
              "ven": ("(+) Vendas", "n"), "men": ("(+) Pagamento mensal", "n"), "out": ("(+) Outras entradas", "n"),
              "nov": ("(+) Receita nova prevista (média × %)", "n"),
              "ent": ("TOTAL DE ENTRADAS", "t+"), "dsp": ("(−) Despesas operacionais", "n"),
              "imp": ("(−) Impostos (DAS / %)", "n"), "pro": ("(−) Retirada pessoal", "n"),
              "sai": ("TOTAL DE SAÍDAS", "t-"), "var": ("Variação do caixa no mês", "b"),
              "fim": ("💰 SALDO FINAL DO MÊS", "big"), "res": ("Resultado operacional (lucro de caixa)", "b"),
              "mar": ("Margem de lucro", "p")}
    for key, (label, style) in labels.items():
        r = R_[key]
        if style == "t+":
            lf = B.fmt(bold=True, bg_color=T["pos_bg"], indent=1, top=1, top_color=T["pos"])
        elif style == "t-":
            lf = B.fmt(bold=True, bg_color=T["neg_bg"], indent=1, top=1, top_color=T["neg"])
        elif style == "big":
            lf = B.fmt(bold=True, font_size=11, indent=1, top=2, top_color=th["mid"], bottom=2, bottom_color=th["mid"], bg_color=th["light"])
        elif style in ("b", "p"):
            lf = B.fmt(bold=True, indent=1, bottom=1, bottom_color=T["line"])
        else:
            lf = B.fmt(indent=1, bottom=1, bottom_color=T["line"])
        ws.write(r - 1, 1, label, lf)
    D = lambda c: A(dates, c, True)
    nxt = lambda c: f"EDATE({D(c)},1)"
    for m in range(1, 13):
        c = 2 + m
        cell = lambda key: A(R_[key], c)
        det_e = lambda i: A(e0 + i, c)
        det_s = lambda i: A(s0 + i, c)
        plain = ctx.f_calc(MONEY0)
        # saldo inicial
        B.f(ws, A(R_["ini"], c), f"={saldo0}" if m == 1 else f"={A(R_['fim'], c - 1)}", ctx.f_calc(MONEY0, font_color=T["muted"]))
        B.f(ws, cell("rec"),
            f'=IF({m}<={R},SUMIFS({rc(5)},{rc(7)},">="&{D(c)},{rc(7)},"<"&{nxt(c)}),'
            f'IF({m}={R}+1,SUMIFS({rc(11)},{rc(6)},"<"&{nxt(c)}),SUMIFS({rc(11)},{rc(6)},">="&{D(c)},{rc(6)},"<"&{nxt(c)})))', plain)
        B.f(ws, cell("ven"), f"=IF({m}<={R},{det_e(0)},0)", plain)
        B.f(ws, cell("men"), f"=IF({m}<={R},{det_e(1)},0)", plain)
        B.f(ws, cell("out"), f"=IF({m}<={R},SUM({det_e(2)}:{det_e(NBENT - 1)}),0)", plain)
        B.f(ws, cell("nov"), f"=IF({m}<={R},0,{rev_avg}*{pct_new})", plain)
        B.f(ws, cell("ent"), f"=SUM({A(R_['rec'], c)}:{A(R_['nov'], c)})", B.fmt(bold=True, num_format=MONEY0, bg_color=T["pos_bg"], top=1, top_color=T["pos"]))
        B.f(ws, cell("dsp"), f"=IF({m}<={R},{A(ox, c)},{opex_avg})", plain)
        B.f(ws, cell("imp"),
            f'=IF({m}<={R},SUMIFS({im(8)},{im(6)},">="&{D(c)},{im(6)},"<"&{nxt(c)}),'
            f'IF({m}={R}+1,SUMIFS({im(10)},{im(5)},"<"&{nxt(c)}),SUMIFS({im(10)},{im(5)},">="&{D(c)},{im(5)},"<"&{nxt(c)})))', plain)
        B.f(ws, cell("pro"), f"=IF({m}<={R},{det_s(NBSAI - 1)},{prolab_prev})", plain)
        B.f(ws, cell("sai"), f"=SUM({A(R_['dsp'], c)}:{A(R_['pro'], c)})", B.fmt(bold=True, num_format=MONEY0, bg_color=T["neg_bg"], top=1, top_color=T["neg"]))
        B.f(ws, cell("var"), f"={A(R_['ent'], c)}-{A(R_['sai'], c)}", ctx.f_calc(MONEY0, bold=True))
        B.f(ws, cell("fim"), f"={A(R_['ini'], c)}+{A(R_['var'], c)}", B.fmt(bold=True, font_size=11, num_format=MONEY0, top=2, top_color=th["mid"], bottom=2, bottom_color=th["mid"], bg_color=th["light"]))
        B.f(ws, cell("res"), f"={A(R_['ent'], c)}-{A(R_['dsp'], c)}-{A(R_['imp'], c)}", ctx.f_calc(MONEY0, bold=True))
        B.f(ws, cell("mar"), f'=IF(({A(R_["rec"], c)}+{A(R_["ven"], c)}+{A(R_["men"], c)}+{A(R_["nov"], c)})=0,"",{A(R_["res"], c)}/({A(R_["rec"], c)}+{A(R_["ven"], c)}+{A(R_["men"], c)}+{A(R_["nov"], c)}))',
            ctx.f_calc(PCT, bold=True, align="right"))
    # coluna Ano
    cA = 15
    for key in ("rec", "ven", "men", "out", "nov", "dsp", "imp", "pro", "var", "res"):
        B.f(ws, A(R_[key], cA), f"=SUM({A(R_[key], 3)}:{A(R_[key], 14)})", ctx.f_calc(MONEY0, bold=True))
    B.f(ws, A(R_["ent"], cA), f"=SUM({A(R_['ent'], 3)}:{A(R_['ent'], 14)})", B.fmt(bold=True, num_format=MONEY0, bg_color=T["pos_bg"], top=1, top_color=T["pos"]))
    B.f(ws, A(R_["sai"], cA), f"=SUM({A(R_['sai'], 3)}:{A(R_['sai'], 14)})", B.fmt(bold=True, num_format=MONEY0, bg_color=T["neg_bg"], top=1, top_color=T["neg"]))
    B.f(ws, A(R_["ini"], cA), f"={A(R_['ini'], 3)}", ctx.f_calc(MONEY0, font_color=T["muted"]))
    B.f(ws, A(R_["fim"], cA), f"={A(R_['fim'], 14)}", B.fmt(bold=True, font_size=11, num_format=MONEY0, top=2, top_color=th["mid"], bottom=2, bottom_color=th["mid"], bg_color=th["light"]))
    B.f(ws, A(R_["mar"], cA), f'=IF(({A(R_["rec"], cA)}+{A(R_["ven"], cA)}+{A(R_["men"], cA)}+{A(R_["nov"], cA)})=0,"",{A(R_["res"], cA)}/({A(R_["rec"], cA)}+{A(R_["ven"], cA)}+{A(R_["men"], cA)}+{A(R_["nov"], cA)}))', ctx.f_calc(PCT, bold=True, align="right"))
    for key in ("var", "fim", "res"):
        cf_pos_neg(ws, B, f"{A(R_[key], 3)}:{A(R_[key], 15)}")
    mr = f"{A(R_['mar'], 3)}:{A(R_['mar'], 15)}"
    ws.conditional_format(mr, {"type": "formula", "criteria": f'=AND(ISNUMBER({A(R_["mar"], 3)}),{A(R_["mar"], 3)}<0)', "format": B.fmt(font_color=T["neg"], bg_color=T["neg_bg"])})
    ws.conditional_format(mr, {"type": "formula", "criteria": f'=AND(ISNUMBER({A(R_["mar"], 3)}),{A(R_["mar"], 3)}>=0.3)', "format": B.fmt(font_color=T["pos"], bg_color=T["pos_bg"])})
    ws.conditional_format(mr, {"type": "formula", "criteria": f'=AND(ISNUMBER({A(R_["mar"], 3)}),{A(R_["mar"], 3)}>=0,{A(R_["mar"], 3)}<0.3)', "format": B.fmt(font_color=T["warn"], bg_color=T["warn_bg"])})
    # média de despesas dos meses realizados
    rng_ox = f"{A(ox, 3, True, True)}:{A(ox, 14, True, True)}"
    B.merge(ws, pr + 2, 3, pr + 2, 4, f"=IF({R}=0,0,SUMPRODUCT((COLUMN({rng_ox})-2<={R})*{rng_ox})/{R})", B.fmt(num_format=MONEY, align="center", bottom=1, bottom_color=T["line"], bold=True))
    rr_rec = f"{A(R_['rec'], 3, True, True)}:{A(R_['rec'], 14, True, True)}"
    rr_avu = f"{A(R_['ven'], 3, True, True)}:{A(R_['ven'], 14, True, True)}"
    rr_men = f"{A(R_['men'], 3, True, True)}:{A(R_['men'], 14, True, True)}"
    B.merge(ws, pr + 4, 3, pr + 4, 4, f"=IF({R}=0,0,SUMPRODUCT((COLUMN({rr_rec})-2<={R})*({rr_rec}+{rr_avu}+{rr_men}))/{R})",
            B.fmt(num_format=MONEY, align="center", bottom=1, bottom_color=T["line"], bold=True))
    # DETALHE (realizado por categoria)
    B.merge(ws, L["f_detsec"], 2, L["f_detsec"], 15, "DETALHE REALIZADO POR CATEGORIA (lançamentos da aba Lanç. Negócio)", ctx.f_section(th))
    ws.write(L["f_dethdr"] - 1, 1, "Categoria", ctx.f_head(th, align="left", indent=1))
    for m in range(1, 13):
        B.f(ws, A(L["f_dethdr"], 2 + m), f"={A(hdr, 2 + m)}", ctx.f_head(th))
    ws.write(L["f_dethdr"] - 1, 14, "Ano", ctx.f_head(th))
    B.merge(ws, e0 - 1, 2, e0 - 1, 15, "▲ Entradas (vendas a prazo ficam na aba A Receber)", B.fmt(bold=True, bg_color=T["pos_bg"], font_color=T["pos"], indent=1))
    B.merge(ws, s0 - 1, 2, s0 - 1, 15, "▼ Saídas (a última categoria é a retirada pessoal)", B.fmt(bold=True, bg_color=T["neg_bg"], font_color=T["neg"], indent=1))

    def detail(first, n, ckey):
        for i in range(n):
            r = first + i
            B.f(ws, A(r, 2), f'=IF({ctx.cfg_item(ckey, i)}="","",{ctx.cfg_item(ckey, i)})', B.fmt(indent=1, bottom=1, bottom_color=T["line"]))
            for m in range(1, 13):
                c = 2 + m
                B.f(ws, A(r, c), f'=IF($B{r}="",0,SUMIFS({ln(6)},{ln(4)},$B{r},{ln(2)},">="&{D(c)},{ln(2)},"<"&{nxt(c)}))', ctx.f_calc(MONEY0))
            B.f(ws, A(r, 15), f"=SUM({A(r, 3)}:{A(r, 14)})", ctx.f_calc(MONEY0, bold=True))
    detail(e0, NBENT, "c_nent")
    detail(s0, NBSAI, "c_nsai")
    tf = lambda: B.fmt(bold=True, bg_color=T["bg"], num_format=MONEY0, top=1, top_color=T["line2"])
    for r, lbl, a, b in [(et, "Total de entradas lançadas", e0, e0 + NBENT - 1), (st, "Total de saídas (inclui retirada)", s0, s0 + NBSAI - 1),
                         (ox, "Despesas operacionais (sem retirada)", s0, s0 + NBSAI - 2)]:
        ws.write(r - 1, 1, lbl, B.fmt(bold=True, bg_color=T["bg"], indent=1, top=1, top_color=T["line2"]))
        for c in range(3, 16):
            B.f(ws, A(r, c), f"=SUM({A(a, c)}:{A(b, c)})", tf())
    # gráficos
    wb = ctx.book.wb
    cats = f"={X(N[k], RNG(hdr, 3, hdr, 14))}"
    col = wb.add_chart({"type": "column"})
    col.add_series({"name": "Entradas", "categories": cats, "values": f"={X(N[k], RNG(R_['ent'], 3, R_['ent'], 14))}", "fill": {"color": T["ent"]}, "gap": 70, "overlap": -5})
    col.add_series({"name": "Saídas", "categories": cats, "values": f"={X(N[k], RNG(R_['sai'], 3, R_['sai'], 14))}", "fill": {"color": T["sai"]}})
    ln_ = wb.add_chart({"type": "line"})
    ln_.add_series({"name": "Saldo final", "categories": cats, "values": f"={X(N[k], RNG(R_['fim'], 3, R_['fim'], 14))}",
                    "line": {"color": T["saldo"], "width": 2.25},
                    "marker": {"type": "circle", "size": 6, "fill": {"color": "#FFFFFF"}, "border": {"color": T["saldo"], "width": 1.5}}})
    col.combine(ln_)
    style_chart(col, "Entradas × Saídas × Saldo (meses futuros = projeção)", 700, 320)
    ws.insert_chart(L["f_chart"] - 1, 1, col, {"x_offset": 4, "y_offset": 4})
    ser = L["b_ser"]
    dd = N["DADOS"]
    hs = L["b_serh"]
    st_ = wb.add_chart({"type": "column", "subtype": "stacked"})
    st_.add_series({"name": "Saldo realizado", "categories": f"={X(dd, RNG(hs, 3, hs, 14))}", "values": f"={X(dd, RNG(ser['sreal'], 3, ser['sreal'], 14))}",
                    "fill": {"color": T["saldo"]}, "gap": 60})
    st_.add_series({"name": "Saldo projetado", "categories": f"={X(dd, RNG(hs, 3, hs, 14))}", "values": f"={X(dd, RNG(ser['sproj'], 3, ser['sproj'], 14))}",
                    "fill": {"color": "#FBBF24"}})
    style_chart(st_, "Saldo de caixa no fim de cada mês", 640, 320)
    ws.insert_chart(L["f_chart"] - 1, 7, st_, {"x_offset": 40, "y_offset": 4})
    ws.freeze_panes(hdr, 2)


# ===================================================================== DADOS (negócio)
def dados_biz(ctx):
    ws, B = ctx.ws["DADOS"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("negocio")
    sec = ctx.f_section(th)
    cf, num, mon = ctx.f_calc(), ctx.f_calc("0"), ctx.f_calc(MONEY)
    hd = ctx.f_head(th)
    b0 = L["b0"]
    R = ctx.dados("d_R")
    mn, mg = ctx.dados("d_mneg"), ctx.dados("d_mger")
    R_ = L["f_rows"]
    fl = lambda row: X(N["FLUXO"], RNG(row, 3, row, 14))
    B.merge(ws, b0, 2, b0, 3, "NEGÓCIO — PARÂMETROS", sec)
    mlist = ctx.cfg_list("c_mes", 12)
    ws.write(L["d_mneg"][0] - 1, 1, "Mês selecionado – Painel Negócio", cf)
    B.f(ws, A(*L["d_mneg"]), f"=IFERROR(MATCH({X(N['PNEG'], AA(*L['pn_sel']))},{mlist},0),1)", num)
    ws.write(L["d_mger"][0] - 1, 1, "Mês selecionado – Painel Geral", cf)
    B.f(ws, A(*L["d_mger"]), f"=IFERROR(MATCH({X(N['GERAL'], AA(*L['pg_sel']))},{mlist},0),1)", num)
    ser = L["b_ser"]
    ws.write(L["d_negm"][0] - 1, 1, "1º mês com caixa negativo (99 = nenhum)", cf)
    B.f(ws, A(*L["d_negm"]), f"=MIN({RNG(ser['neg'], 3, ser['neg'], 14)})", num)
    # lista combinada negócio
    cc, r0 = L["d_nall_c"], L["d_all_r0"]
    ws.write(CS - 1, cc - 1, "LISTA COMBINADA (negócio)", sec)
    for i in range(NBENT):
        B.f(ws, A(r0 + i, cc), f'=IF({ctx.cfg_item("c_nent", i)}="","",{ctx.cfg_item("c_nent", i)})', cf)
    for i in range(NBSAI):
        B.f(ws, A(r0 + NBENT + i, cc), f'=IF({ctx.cfg_item("c_nsai", i)}="","",{ctx.cfg_item("c_nsai", i)})', cf)
    # despesas do negócio no mês do Painel Negócio: categorias operacionais + DAS (rosca)
    h = L["b_cat0"] - 1
    for j, t in enumerate(["Despesa do negócio", "Valor no mês"]):
        ws.write(h - 1, 1 + j, t, hd)
    c0 = L["b_cat0"]
    nop = NBSAI - 1
    for i in range(nop):
        r = c0 + i
        B.f(ws, A(r, 2), f'=IF({ctx.cfg_item("c_nsai", i)}="","",{ctx.cfg_item("c_nsai", i)})', cf)
        B.f(ws, A(r, 3), f'=IF({A(r, 2)}="",0,IF({mn}<={R},INDEX({fl(L["f_sai0"] + i)},{mn}),0))', mon)
    r = c0 + nop
    ws.write(r - 1, 1, "Impostos (DAS)", cf)
    B.f(ws, A(r, 3), f'=IF({mn}<={R},INDEX({fl(R_["imp"])},{mn}),0)', mon)
    r, c = L["d_btot"]
    ws.write(r - 1, 1, "Total de despesas (mês do Painel Negócio)", cf)
    B.f(ws, A(r, c), f"=SUM({RNG(c0, 3, c0 + nop, 3)})", mon)
    r, c = L["d_btitle"]
    ws.write(r - 1, 1, "Título da rosca (negócio)", cf)
    B.f(ws, A(r, c), f'="Onde o negócio gastou — "&INDEX({mlist},{mn})', cf)
    # origem do faturamento no ano (até o mês de referência) — gráfico de barras
    o0 = L["b_orig0"]
    ws.write(o0 - 2, 1, "Origem do faturamento (ano)", hd)
    ws.write(o0 - 2, 2, "Valor", hd)
    ytd = lambda key: f"SUMPRODUCT((COLUMN({fl(R_[key])})-2<={R})*{fl(R_[key])})"
    ws.write(o0 - 1, 1, "Cobranças recebidas (A Receber)", cf)
    B.f(ws, A(o0, 3), f"={ytd('rec')}", mon)
    for i, key in enumerate(("ven", "men")):
        B.f(ws, A(o0 + 1 + i, 2), f'=IF({ctx.cfg_item("c_nent", i)}="","",{ctx.cfg_item("c_nent", i)})', cf)
        B.f(ws, A(o0 + 1 + i, 3), f"={ytd(key)}", mon)
    # cobranças em atraso (top 5)
    h3 = L["b_atr0"] - 1
    for j, t in enumerate(["#", "Posição", "Cliente", "Descrição", "Vencimento", "Dias", "Valor"]):
        ws.write(h3 - 1, 7 + j, t, hd)
    a0 = L["b_atr0"]
    rr = lambda c: X(N["REC"], RNG(L["r_r0"], c, L["r_r1"], c))
    for kx in range(5):
        r = a0 + kx
        ws.write(r - 1, 7, kx + 1, ctx.f_calc("0", align="center"))
        B.f(ws, A(r, 9), f"=IF(LARGE({rr(13)},{kx + 1})>0,MATCH(LARGE({rr(13)},{kx + 1}),{rr(13)},0),0)", num)
        B.f(ws, A(r, 10), f'=IF({A(r, 9)}>0,INDEX({rr(3)},{A(r, 9)}),"")', cf)
        B.f(ws, A(r, 11), f'=IF({A(r, 9)}>0,INDEX({rr(4)},{A(r, 9)}),"")', cf)
        B.f(ws, A(r, 12), f'=IF({A(r, 9)}>0,INDEX({rr(6)},{A(r, 9)}),"")', ctx.f_calc(DATE))
        B.f(ws, A(r, 13), f'=IF({A(r, 9)}>0,INDEX({rr(10)},{A(r, 9)}),"")', num)
        B.f(ws, A(r, 14), f'=IF({A(r, 9)}>0,INDEX({rr(5)},{A(r, 9)}),"")', mon)
    # séries mensais (12 colunas) — realizado (zero após o mês de referência)
    hs = L["b_serh"]
    ws.write(hs - 1, 1, "SÉRIES MENSAIS (realizado = 0 após o mês de referência)", hd)
    for m in range(1, 13):
        B.f(ws, A(hs, 2 + m), f"=INDEX({ctx.cfg_list('c_abrev', 12)},{m})", hd)
    ra = N["RESUMO"]
    rrow = lambda row, c: X(ra, AA(row, c))
    fx = lambda key, c: X(N["FLUXO"], AA(R_[key], c))
    defs = [
        ("rec", "Faturamento (A Receber + vendas + pagamento mensal)", lambda c, m: f"=IF({m}<={R},{fx('rec', c)}+{fx('ven', c)}+{fx('men', c)},0)"),
        ("desp", "Despesas + impostos", lambda c, m: f"=IF({m}<={R},{fx('dsp', c)}+{fx('imp', c)},0)"),
        ("lucro", "Lucro de caixa", lambda c, m: f"=IF({m}<={R},{fx('res', c)},0)"),
        ("sreal", "Saldo realizado", lambda c, m: f"=IF({m}<={R},{fx('fim', c)},0)"),
        ("sproj", "Saldo projetado", lambda c, m: f"=IF({m}>{R},{fx('fim', c)},0)"),
        ("cxp", "Caixa pessoal (acumulado)", lambda c, m: f"=IF({m}<={R},{rrow(L['ra_acum'], c)},0)"),
        ("cxn", "Caixa do negócio", lambda c, m: f"=IF({m}<={R},{fx('fim', c)},0)"),
        ("resp", "Resultado pessoal do mês", lambda c, m: f"=IF({m}<={R},{rrow(L['ra_saldo'], c)},0)"),
        ("prol", "Pró-labore recebido (pessoal)", lambda c, m: f"=IF({m}<={R},{rrow(L['ra_ent0'], c)},0)"),
        ("gasp", "Gastos pessoais", lambda c, m: f"=IF({m}<={R},{rrow(L['ra_saitot'], c)},0)"),
        ("neg", "Flag: saldo de caixa negativo", lambda c, m: f"=IF({fx('fim', c)}<0,{m},99)"),
        ("op", "Despesas operacionais", lambda c, m: f"=IF({m}<={R},{fx('dsp', c)},0)"),
        ("imp", "Impostos pagos", lambda c, m: f"=IF({m}<={R},{fx('imp', c)},0)"),
        ("pro", "Retirada pessoal paga", lambda c, m: f"=IF({m}<={R},{fx('pro', c)},0)"),
    ]
    for key, label, fn in defs:
        r = ser[key]
        ws.write(r - 1, 1, label, cf)
        for m in range(1, 13):
            B.f(ws, A(r, 2 + m), fn(2 + m, m), mon if key != "neg" else num)
    # distribuição da receita no ano (rosca)
    d0 = L["b_dist0"]
    ws.write(d0 - 2, 1, "Para onde vai a receita (ano, até o mês de referência)", hd)
    ws.write(d0 - 2, 2, "Valor", hd)
    sm = lambda key: f"SUM({RNG(ser[key], 3, ser[key], 14)})"
    rows = [("Despesas operacionais", f"={sm('op')}"), ("Impostos", f"={sm('imp')}"),
            ("Retirada pessoal (seu pró-labore)", f"={sm('pro')}"),
            ("Lucro retido no caixa", f"=MAX(0,{sm('rec')}-{sm('op')}-{sm('imp')}-{sm('pro')})")]
    for i, (lbl, f) in enumerate(rows):
        ws.write(d0 + i - 1, 1, lbl, cf)
        B.f(ws, A(d0 + i, 3), f, mon)


# ===================================================================== PAINEL NEGÓCIO
def painel_negocio(ctx):
    k, ws, B = "PNEG", ctx.ws["PNEG"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("negocio")
    nome = ctx.cfg("cfg_neg")
    ctx.page(k, [11] * 12, f'="💼 Painel Negócio — "&{nome}',
             "Faturamento, despesas, lucro, cobranças em atraso e limite do MEI — tudo do mês escolhido.", area="negocio", bg=True, landscape=False, one_page=True)
    selector(ctx, ws, L["pn_sel"], "← escolha o mês; os valores só aparecem até o mês de referência (hoje)")
    wb = ctx.book.wb
    m = ctx.dados("d_mneg")
    dd = N["DADOS"]
    ser = L["b_ser"]
    sx = lambda key: f"INDEX({X(dd, RNG(ser[key], 3, ser[key], 14))},{m})"
    sxp = lambda key: f"INDEX({X(dd, RNG(ser[key], 3, ser[key], 14))},{m}-1)"
    r = CS + 2
    ws.set_row(r - 1, 18)
    ws.set_row(r, 36)
    ws.set_row(r + 1, 20)

    def delta(key):
        return (f'=IF({m}=1,"—",IF({sxp(key)}=0,"—",IF({sx(key)}>={sxp(key)},"▲ ","▼ ")&'
                f'TEXT(ABS({sx(key)}/{sxp(key)}-1),"0%")&" vs mês anterior"))')

    kpi_card(ctx, ws, r, 2, 3, "FATURAMENTO DO MÊS", f"={sx('rec')}", MONEY_INT, delta("rec"), None, T["ent"])
    kpi_card(ctx, ws, r, 4, 5, "DESPESAS + IMPOSTOS", f"={sx('desp')}", MONEY_INT, delta("desp"), None, T["sai"])
    kpi_card(ctx, ws, r, 6, 7, "LUCRO DE CAIXA", f"={sx('lucro')}", MONEY_INT,
             f'=IF({sx("rec")}=0,"—","Margem de "&TEXT({sx("lucro")}/{sx("rec")},"0%"))', None, T["saldo"])
    rr = lambda c: X(N["REC"], RNG(L["r_r0"], c, L["r_r1"], c))
    kpi_card(ctx, ws, r, 8, 9, "A RECEBER (EM ABERTO)", f"=SUM({rr(11)})", MONEY_INT, f"=SUM({rr(12)})", '"Em atraso: R$" #,##0', "#7C3AED")
    imp = ctx.imp
    kpi_card(ctx, ws, r, 10, 11, "LIMITE DO MEI USADO", f'=IF({imp["regime"]}<>"MEI","n/a",{imp["pct"]})', "0%",
             f'=IF({imp["regime"]}<>"MEI","regime sem limite MEI","Projeção: "&TEXT({imp["proj_ratio"]},"0%")&" do limite")', None, "#0891B2")
    ir = lambda c: X(N["IMP"], RNG(L["i_r0"], c, L["i_r0"] + 11, c))
    kpi_card(ctx, ws, r, 12, 13, "IMPOSTO DO MÊS (DAS)", f"=INDEX({ir(4)},{m})", MONEY, f"=INDEX({ir(9)},{m})", None, "#F59E0B")
    # condicionais
    ws.conditional_format(A(r + 1, 6), {"type": "cell", "criteria": "<", "value": 0, "format": B.fmt(font_color=T["neg"])})
    ws.conditional_format(A(r + 1, 6), {"type": "cell", "criteria": ">=", "value": 0, "format": B.fmt(font_color=T["pos"])})
    pv = A(r + 1, 10)
    ws.conditional_format(pv, {"type": "formula", "criteria": f"=AND(ISNUMBER({pv}),{pv}>=1)", "format": B.fmt(font_color=T["neg"])})
    ws.conditional_format(pv, {"type": "formula", "criteria": f"=AND(ISNUMBER({pv}),{pv}>=0.8)", "format": B.fmt(font_color=T["warn"])})
    for c, up_bad in ((2, False), (4, True)):
        sc = A(r + 2, c)
        up, dn_ = (T["neg"], T["pos"]) if up_bad else (T["pos"], T["neg"])
        ws.conditional_format(sc, {"type": "text", "criteria": "begins with", "value": "▲", "format": B.fmt(font_color=up)})
        ws.conditional_format(sc, {"type": "text", "criteria": "begins with", "value": "▼", "format": B.fmt(font_color=dn_)})
    ws.conditional_format(A(r + 2, 8), {"type": "cell", "criteria": ">", "value": 0, "format": B.fmt(font_color=T["neg"])})
    ws.conditional_format(A(r + 1, 12), {"type": "cell", "criteria": ">", "value": 0, "format": B.fmt(font_color=T["ink"])})
    stt = A(r + 2, 12)
    ws.conditional_format(stt, {"type": "text", "criteria": "containing", "value": "Atrasado", "format": B.fmt(font_color=T["neg"], bold=True)})
    ws.conditional_format(stt, {"type": "text", "criteria": "containing", "value": "Pago", "format": B.fmt(font_color=T["pos"], bold=True)})
    # gráficos
    r1 = CS + 6
    hs = L["b_serh"]
    cats = f"={X(dd, RNG(hs, 3, hs, 14))}"
    col = wb.add_chart({"type": "column"})
    col.add_series({"name": "Faturamento", "categories": cats, "values": f"={X(dd, RNG(ser['rec'], 3, ser['rec'], 14))}", "fill": {"color": T["ent"]}, "gap": 70, "overlap": -5})
    col.add_series({"name": "Despesas + impostos", "categories": cats, "values": f"={X(dd, RNG(ser['desp'], 3, ser['desp'], 14))}", "fill": {"color": T["sai"]}})
    col.add_series({"name": "Lucro de caixa", "categories": cats, "values": f"={X(dd, RNG(ser['lucro'], 3, ser['lucro'], 14))}", "fill": {"color": T["saldo"]}})
    style_chart(col, "Faturamento × Despesas × Lucro — mês a mês", 484, 320)
    chart_pos(ws, col, r1, True)
    dn = wb.add_chart({"type": "doughnut"})
    c0 = L["b_cat0"]
    dn.add_series({"name": "Despesas do mês", "categories": f"={X(dd, RNG(c0, 2, c0 + NBSAI - 1, 2))}", "values": f"={X(dd, RNG(c0, 3, c0 + NBSAI - 1, 3))}",
                   "points": [{"fill": {"color": c}} for c in PALETTE],
                   "data_labels": {"percentage": True, "font": {"name": FONT, "size": 8, "color": "#FFFFFF", "bold": True}}})
    dn.set_hole_size(52)
    style_chart(dn, "Onde o negócio gastou", 484, 320, legend="right")
    dn.set_title({"name": f"={X(dd, AA(*L['d_btitle']))}", "name_font": {"name": FONT, "size": 11, "bold": True, "color": T["ink"]}})
    chart_pos(ws, dn, r1, False)
    r2 = r1 + 16
    bar = wb.add_chart({"type": "bar"})
    k0 = L["b_orig0"]
    bar.add_series({"name": "Faturamento no ano", "categories": f"={X(dd, RNG(k0, 2, k0 + 2, 2))}", "values": f"={X(dd, RNG(k0, 3, k0 + 2, 3))}",
                    "fill": {"color": T["orange_mid"]}, "gap": 45,
                    "data_labels": {"value": True, "num_format": "#,##0", "font": {"name": FONT, "size": 8}}})
    style_chart(bar, "De onde vem o faturamento (ano)", 484, 320, legend=None, reverse_x=True, horizontal=True)
    chart_pos(ws, bar, r2, True)
    ln_ = wb.add_chart({"type": "line"})
    i0 = L["i_r0"]
    icats = f"={X(dd, RNG(hs, 3, hs, 14))}"
    ln_.add_series({"name": "Receita acumulada", "categories": icats, "values": f"={X(N['IMP'], RNG(i0, 12, i0 + 11, 12))}",
                    "line": {"color": T["orange_mid"], "width": 2.75},
                    "marker": {"type": "circle", "size": 6, "fill": {"color": "#FFFFFF"}, "border": {"color": T["orange_mid"], "width": 1.5}}})
    ln_.add_series({"name": "Limite do período", "categories": icats, "values": f"={X(N['IMP'], RNG(i0, 13, i0 + 11, 13))}",
                    "line": {"color": T["sai"], "width": 2, "dash_type": "dash"}})
    style_chart(ln_, "Faturamento acumulado × limite MEI", 484, 320)
    chart_pos(ws, ln_, r2, False)
    # cobranças em atraso
    r3 = r2 + 16
    section_bar(ctx, ws, r3, 2, 13, "⏰  COBRANÇAS EM ATRASO (as 5 mais antigas)", th["mid"])
    hd = ctx.f_head(th, font_size=9)
    for c0_, c1_, t in [(2, 4, "Cliente"), (5, 8, "Descrição"), (9, 10, "Vencimento"), (11, 11, "Dias"), (12, 13, "Valor")]:
        B.merge(ws, r3 + 1, c0_, r3 + 1, c1_, t, hd)
    a0 = L["b_atr0"]
    wh = lambda **kw: B.fmt(bg_color="#FFFFFF", bottom=1, bottom_color=T["line"], **kw)
    for i in range(5):
        rr_ = r3 + 2 + i
        dr = a0 + i
        g = lambda c: X(dd, AA(dr, c))
        first = f'IF({g(9)}=0,"✓ Nenhuma cobrança em atraso","")' if i == 0 else '""'
        B.merge(ws, rr_, 2, rr_, 4, f'=IF({g(9)}>0,{g(10)},{first})', wh(indent=1, bold=True))
        B.merge(ws, rr_, 5, rr_, 8, f'={g(11)}', wh(indent=1, font_size=9))
        B.merge(ws, rr_, 9, rr_, 10, f'={g(12)}', wh(num_format=DATE, align="center"))
        B.merge(ws, rr_, 11, rr_, 11, f'={g(13)}', wh(num_format="0", align="center", bold=True, font_color=T["neg"]))
        B.merge(ws, rr_, 12, rr_, 13, f'={g(14)}', wh(num_format=MONEY, align="center", bold=True))
    ws.conditional_format(A(r3 + 2, 2), {"type": "text", "criteria": "begins with", "value": "✓", "format": B.fmt(font_color=T["pos"])})
    # alertas
    r4 = r3 + 8
    section_bar(ctx, ws, r4, 2, 13, "🔔  ALERTAS E INSIGHTS", th["mid"])
    negm = ctx.dados("d_negm")
    msgs = [f"={imp['msg']}",
            f'=IF(SUM({rr(12)})=0,"✓ Nenhuma cobrança em atraso.","⚠ Você tem R$ "&FIXED(SUM({rr(12)}),2)&" em cobranças atrasadas — veja a aba A Receber.")',
            f'=IF({negm}=99,"✓ O caixa do negócio não fica negativo em nenhum mês do ano (incluindo a projeção).",'
            f'"⚠ O caixa projetado fica negativo a partir de "&INDEX({ctx.cfg_list("c_mes", 12)},{negm})&". Antecipe recebimentos ou reduza despesas.")']
    for i, f in enumerate(msgs):
        rr_ = r4 + 1 + i
        ws.set_row(rr_ - 1, 24)
        B.merge(ws, rr_, 2, rr_, 13, f, B.fmt(bg_color="#FFFFFF", indent=1, bottom=1, bottom_color=T["line"], font_size=10))
    ar = f"{A(r4 + 1, 2)}:{A(r4 + 3, 13)}"
    for ch, fc, bg in [("✖", T["neg"], T["neg_bg"]), ("⚠", T["warn"], T["warn_bg"]), ("✓", T["pos"], T["pos_bg"]), ("ℹ", T["saldo"], T["navy_light"])]:
        ws.conditional_format(ar, {"type": "text", "criteria": "begins with", "value": ch, "format": B.fmt(font_color=fc, bg_color=bg, bold=True)})


# ===================================================================== PAINEL GERAL
def painel_geral(ctx):
    k, ws, B = "GERAL", ctx.ws["GERAL"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("geral")
    nome = ctx.cfg("cfg_nome")
    ctx.page(k, [11] * 12, f'="📊 Painel Geral — "&{nome}',
             "Visão consolidada: vida pessoal + negócio. O negócio sustenta o seu custo de vida?", area="geral", bg=True, landscape=False, one_page=True)
    selector(ctx, ws, L["pg_sel"], "← escolha o mês; a aba Config guarda ano e metas")
    wb = ctx.book.wb
    m = ctx.dados("d_mger")
    dd, ra = N["DADOS"], N["RESUMO"]
    ser = L["b_ser"]
    R = ctx.dados("d_R")
    sx = lambda key: f"INDEX({X(dd, RNG(ser[key], 3, ser[key], 14))},{m})"
    acum = f"INDEX({X(ra, RNG(L['ra_acum'], 3, L['ra_acum'], 14))},{m})"
    fim = f"INDEX({X(N['FLUXO'], RNG(L['f_rows']['fim'], 3, L['f_rows']['fim'], 14))},{m})"
    r = CS + 2
    ws.set_row(r - 1, 18)
    ws.set_row(r, 36)
    ws.set_row(r + 1, 20)
    kpi_card(ctx, ws, r, 2, 3, "SALDO PESSOAL ACUMULADO", f"={acum}", MONEY_INT, "pessoal, no fim do mês", None, T["teal"])
    kpi_card(ctx, ws, r, 4, 5, "CAIXA DO NEGÓCIO", f"={fim}", MONEY_INT, f'=IF({m}<={R},"realizado","projetado")', None, T["orange_mid"])
    kpi_card(ctx, ws, r, 6, 7, "CAIXA TOTAL", f"={acum}+{fim}", MONEY_INT, "pessoal + negócio", None, T["navy"])
    kpi_card(ctx, ws, r, 8, 9, "RESULTADO PESSOAL (MÊS)", f"={sx('resp')}", MONEY_INT, "entradas − saídas pessoais", None, "#7C3AED")
    kpi_card(ctx, ws, r, 10, 11, "LUCRO DO NEGÓCIO (MÊS)", f"={sx('lucro')}", MONEY_INT, "receita − despesas − impostos", None, "#0891B2")
    kpi_card(ctx, ws, r, 12, 13, "PRÓ-LABORE ÷ GASTOS PESSOAIS", f'=IF({sx("gasp")}=0,0,{sx("prol")}/{sx("gasp")})', "0%",
             "cobertura do custo de vida", None, "#F59E0B")
    for c in (2, 4, 6, 8, 10):
        a = A(r + 1, c)
        ws.conditional_format(a, {"type": "cell", "criteria": "<", "value": 0, "format": B.fmt(font_color=T["neg"])})
    for c in (8, 10):
        ws.conditional_format(A(r + 1, c), {"type": "cell", "criteria": ">", "value": 0, "format": B.fmt(font_color=T["pos"])})
    cv = A(r + 1, 12)
    ws.conditional_format(cv, {"type": "cell", "criteria": ">=", "value": 1, "format": B.fmt(font_color=T["pos"])})
    ws.conditional_format(cv, {"type": "cell", "criteria": "<", "value": 1, "format": B.fmt(font_color=T["warn"])})
    r1 = CS + 6
    hs = L["b_serh"]
    cats = f"={X(dd, RNG(hs, 3, hs, 14))}"
    st = wb.add_chart({"type": "column", "subtype": "stacked"})
    st.add_series({"name": "Caixa pessoal", "categories": cats, "values": f"={X(dd, RNG(ser['cxp'], 3, ser['cxp'], 14))}", "fill": {"color": T["teal"]}, "gap": 60})
    st.add_series({"name": "Caixa do negócio", "categories": cats, "values": f"={X(dd, RNG(ser['cxn'], 3, ser['cxn'], 14))}", "fill": {"color": T["orange_mid"]}})
    style_chart(st, "Caixa no fim de cada mês — pessoal + negócio", 484, 320)
    chart_pos(ws, st, r1, True)
    cl = wb.add_chart({"type": "column"})
    cl.add_series({"name": "Pessoal (saldo)", "categories": cats, "values": f"={X(dd, RNG(ser['resp'], 3, ser['resp'], 14))}", "fill": {"color": T["teal"]}, "gap": 70, "overlap": -5})
    cl.add_series({"name": "Negócio (lucro)", "categories": cats, "values": f"={X(dd, RNG(ser['lucro'], 3, ser['lucro'], 14))}", "fill": {"color": T["orange_mid"]}})
    style_chart(cl, "Resultado do mês: pessoal × negócio", 484, 320)
    chart_pos(ws, cl, r1, False)
    r2 = r1 + 16
    cv_ = wb.add_chart({"type": "column"})
    cv_.add_series({"name": "Pró-labore recebido", "categories": cats, "values": f"={X(dd, RNG(ser['prol'], 3, ser['prol'], 14))}", "fill": {"color": T["ent"]}, "gap": 70, "overlap": -5})
    cv_.add_series({"name": "Gastos pessoais", "categories": cats, "values": f"={X(dd, RNG(ser['gasp'], 3, ser['gasp'], 14))}", "fill": {"color": T["sai"]}})
    style_chart(cv_, "O pró-labore cobre o seu custo de vida?", 484, 320)
    chart_pos(ws, cv_, r2, True)
    dn = wb.add_chart({"type": "doughnut"})
    d0 = L["b_dist0"]
    dn.add_series({"name": "Receita do ano", "categories": f"={X(dd, RNG(d0, 2, d0 + 3, 2))}", "values": f"={X(dd, RNG(d0, 3, d0 + 3, 3))}",
                   "points": [{"fill": {"color": c}} for c in [T["sai"], "#F59E0B", T["teal"], T["ent"]]],
                   "data_labels": {"percentage": True, "font": {"name": FONT, "size": 9, "color": "#FFFFFF", "bold": True}}})
    dn.set_hole_size(52)
    style_chart(dn, "Para onde vai a receita do negócio (ano)", 484, 320, legend="right")
    chart_pos(ws, dn, r2, False)
    r3 = r2 + 16
    section_bar(ctx, ws, r3, 2, 13, "🔔  ALERTAS E INSIGHTS", th["mid"])
    imp = ctx.imp
    rr = lambda c: X(N["REC"], RNG(L["r_r0"], c, L["r_r1"], c))
    atraso = f"SUM({rr(12)})"
    negm = ctx.dados("d_negm")
    cov = f'IF({sx("gasp")}=0,0,{sx("prol")}/{sx("gasp")})'
    msgs = [f"={imp['msg']}",
            f'=IF({atraso}=0,"✓ Nenhuma cobrança em atraso.","⚠ Você tem R$ "&FIXED({atraso},2)&" em cobranças atrasadas — veja a aba A Receber.")',
            f'=IF({negm}=99,"✓ O caixa do negócio permanece positivo no ano (incluindo a projeção).","⚠ O caixa do negócio projetado fica negativo a partir de "&INDEX({ctx.cfg_list("c_mes", 12)},{negm})&".")',
            f'=IF({sx("gasp")}=0,"ℹ Registre os gastos pessoais do mês para medir a cobertura do custo de vida.",IF({cov}>=1,"✓ O pró-labore do mês cobre "&TEXT({cov},"0%")&" dos seus gastos pessoais.","⚠ O pró-labore cobre só "&TEXT({cov},"0%")&" dos gastos pessoais do mês — o restante saiu de reservas."))']
    for i, f in enumerate(msgs):
        rr_ = r3 + 1 + i
        ws.set_row(rr_ - 1, 24)
        B.merge(ws, rr_, 2, rr_, 13, f, B.fmt(bg_color="#FFFFFF", indent=1, bottom=1, bottom_color=T["line"], font_size=10))
    ar = f"{A(r3 + 1, 2)}:{A(r3 + 4, 13)}"
    for ch, fc, bg in [("✖", T["neg"], T["neg_bg"]), ("⚠", T["warn"], T["warn_bg"]), ("✓", T["pos"], T["pos_bg"]), ("ℹ", T["saldo"], T["navy_light"])]:
        ws.conditional_format(ar, {"type": "text", "criteria": "begins with", "value": ch, "format": B.fmt(font_color=fc, bg_color=bg, bold=True)})


# ===================================================================== orquestração
def build_all(ctx):
    L, N = ctx.L, ctx.N
    rows = None
    if ctx.demo:
        _, rows = demo.business_rows()
    lancamentos(ctx, "LNEG", area="negocio", title="📝 Lançamentos do negócio — entradas e saídas do dia a dia",
                subtitle="Vendas à vista, pagamentos mensais, compras e despesas. Vendas a prazo vão na aba A Receber (não duplique aqui).",
                ent_key="c_nent", sai_key="c_nsai", all_col_key="d_nall_c", extra_label="Cliente (opcional)",
                extra_list_ref=None, demo_rows=rows, extra_width=24, mode="negocio", n_ent=NBENT, n_sai=NBSAI)
    recebimentos(ctx)
    impostos(ctx)
    fluxo(ctx)
    dados_biz(ctx)
    painel_negocio(ctx)
    painel_geral(ctx)
