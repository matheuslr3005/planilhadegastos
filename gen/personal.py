"""Abas de finanças pessoais (usadas nas duas versões) + Config e Dados."""
import datetime as dt
from lib import *
from ctx import *

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro",
         "Outubro", "Novembro", "Dezembro"]
ABREV = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

ENT_PF = ["Salário", "Renda extra", "Rendimentos de investimentos", "13º e bônus", "Reembolsos",
          "Aluguéis recebidos", "Presentes recebidos", "Outras entradas"]
ENT_AUT = ["Pró-labore / Retirada do negócio", "Salário / Renda fixa", "Renda extra",
           "Rendimentos de investimentos", "Reembolsos", "Aluguéis recebidos", "Presentes recebidos",
           "Outras entradas"]
SAI = ["Moradia", "Contas da casa", "Alimentação", "Transporte", "Saúde", "Educação", "Lazer", "Vestuário",
       "Assinaturas", "Cuidados pessoais", "Pets", "Presentes e doações", "Dívidas e financiamentos",
       "Reserva e Metas", "Impostos pessoais", "Outros"]
FORMAS = ["Pix", "Cartão de débito", "Cartão de crédito", "Dinheiro", "Boleto", "Transferência",
          "Débito automático", "Outro"]
# Negócio (lista curta, pensada para MEI que vende produtos ou serviços)
# entradas: as 2 primeiras contam como FATURAMENTO; saídas: a ÚLTIMA é a retirada pessoal (pró-labore)
NENT_L = ["Vendas", "Pagamento mensal", "Outras entradas"]
NSAI_L = ["Compras (mercadoria e materiais)", "Despesas", "Outros impostos e taxas", "Retirada pessoal (pró-labore)"]

STATUS_CF = {  # texto contido -> (fonte, fundo)
    "Estourou": (T["neg"], T["neg_bg"]), "Atenção": (T["warn"], T["warn_bg"]), "OK": (T["pos"], T["pos_bg"]),
}


def cf_pos_neg(ws, book, rng, zero_green=True):
    ws.conditional_format(rng, {"type": "cell", "criteria": "<", "value": 0,
                                "format": book.fmt(font_color=T["neg"], bg_color=T["neg_bg"], bold=True)})
    ws.conditional_format(rng, {"type": "cell", "criteria": ">", "value": 0,
                                "format": book.fmt(font_color=T["pos"], bg_color=T["pos_bg"], bold=True)})


def month_dv(ctx, ws, cell):
    ws.data_validation(cell, {"validate": "list", "source": "=" + ctx.cfg_list("c_mes", 12).replace("'", "'"),
                              "input_title": "Escolha o mês", "input_message": "Selecione no menu suspenso.",
                              "error_title": "Mês inválido", "error_message": "Escolha um mês da lista."})


# ===================================================================== CONFIG
def config(ctx):
    k, ws, B = "CONFIG", ctx.ws["CONFIG"], ctx.book
    L, CS = ctx.L, ctx.CS
    th = ctx.theme("geral" if ctx.aut else "pessoal")
    widths = [38, 18, 3, 32, 3, 32, 3, 22, 3, 14, 10]
    if ctx.aut:
        widths += [3, 34, 3, 34]
    ctx.page(k, widths, "⚙ Configurações", "Personalize categorias, ano e parâmetros — tudo nas células amarelas. "
             "As mudanças se refletem em todas as abas.", area="geral" if ctx.aut else "pessoal")
    sec = ctx.f_section(th)
    B.merge(ws, CS, 2, CS, 3, "PARÂMETROS GERAIS", sec)
    lab = ctx.fmt(bottom=1, bottom_color=T["line"])
    rows = [("cfg_ano", "Ano de referência", 2026, "0", "Define o ano que os painéis e resumos analisam."),
            ("cfg_hoje", "Data de hoje (referência)", None, DATE, "Deixe =HOJE() ou fixe uma data."),
            ("cfg_nome", "Seu nome / título nos painéis", "Minhas Finanças" if not ctx.aut else "Meu Controle Financeiro",
             None, ""),
            ("cfg_meta", "Meta de taxa de poupança", 0.20, "0%", "% da renda que você quer guardar por mês."),
            ("cfg_saldo0", "Saldo pessoal em 1º de janeiro", 2500 if ctx.demo else 0, MONEY, "Dinheiro que você já tinha no início do ano.")]
    if ctx.aut:
        rows.append(("cfg_neg", "Nome do negócio", "Loja Exemplo" if ctx.demo else "Meu Negócio", None, ""))
    for key, label, val, num, hint in rows:
        r, c = L[key]
        ws.write(r - 1, 1, label, lab)
        f = ctx.f_input(num, align="left" if isinstance(val, str) else "right")
        if key == "cfg_hoje":
            if ctx.demo:
                ws.write_datetime(r - 1, c - 1, dt.datetime(2026, 9, 30), f)
            else:
                B.f(ws, A(r, c), "=TODAY()", f)
        else:
            ws.write(r - 1, c - 1, val, f)
    ws.data_validation(A(*L["cfg_ano"]), {"validate": "integer", "criteria": "between", "minimum": 2000,
                                          "maximum": 2100, "error_message": "Digite um ano entre 2000 e 2100."})
    ws.data_validation(A(*L["cfg_meta"]), {"validate": "decimal", "criteria": "between", "minimum": 0, "maximum": 1,
                                           "error_message": "Digite um percentual entre 0% e 100%."})
    hint = ctx.fmt(italic=True, font_size=8, font_color=T["muted"], text_wrap=True, valign="top")
    nr = L["cfg_saldo0"][0] + (2 if ctx.aut else 1)
    note = ("💡 Células AMARELAS são suas: edite à vontade. A data de hoje usa =HOJE(); se quiser congelar uma data "
            "(por exemplo para estudar um mês passado), digite-a.\n"
            "💡 Renomeie as categorias ao lado como preferir — os painéis acompanham. Evite deixar vazio e "
            "evite nomes repetidos.\n"
            "💡 A 14ª categoria de SAÍDA ('Reserva e Metas') é tratada como poupança, não como gasto, no cálculo da taxa de poupança.\n"
            "⚠ Renomeie as categorias ANTES de começar a lançar. Se renomear depois, use Localizar e Substituir na coluna "
            "Categoria dos lançamentos (senão eles ficam como 'Verificar').")
    ws.merge_range(nr - 1, 1, nr + 12, 2, note, hint)

    LS = L["ls"]
    headers = [(L["c_ent"], "CATEGORIAS DE ENTRADA", NENT, ENT_AUT if ctx.aut else ENT_PF),
               (L["c_sai"], "CATEGORIAS DE SAÍDA", NSAI, SAI),
               (L["c_forma"], "FORMAS DE PAGAMENTO", NFORMA, FORMAS)]
    if ctx.aut:
        headers[0] = (L["c_ent"], "ENTRADAS PESSOAIS", NENT, ENT_AUT)
        headers[1] = (L["c_sai"], "SAÍDAS PESSOAIS", NSAI, SAI)
        headers += [(L["c_nent"], "NEGÓCIO — ENTRADAS", NBENT, NENT_L), (L["c_nsai"], "NEGÓCIO — SAÍDAS", NBSAI, NSAI_L)]
    cell_f = ctx.f_input(align="left")
    for c, title, n, items in headers:
        ws.write(LS - 1, c - 1, title, sec)
        for i, v in enumerate(items):
            ws.write(LS + i, c - 1, v, cell_f)
    ws.write(LS - 1, L["c_mes"] - 1, "MÊS", sec)
    ws.write(LS - 1, L["c_abrev"] - 1, "ABREV.", sec)
    fixed = ctx.fmt(bottom=1, bottom_color=T["line"], font_color=T["muted"])
    for i in range(12):
        ws.write(LS + i, L["c_mes"] - 1, MESES[i], fixed)
        ws.write(LS + i, L["c_abrev"] - 1, ABREV[i], fixed)
    # dicas sob a lista de meses
    ws.set_column(L["c_ent"] - 1, L["c_ent"] - 1, 32)
    if ctx.aut:
        tip = ctx.fmt(italic=True, font_size=8, font_color=T["muted"], text_wrap=True, valign="top")
        r = LS + 18
        ws.merge_range(r - 1, L["c_nsai"] - 1, r + 5, L["c_nsai"] - 1,
                       "⚠ Regras do negócio: as 2 primeiras ENTRADAS (Vendas e Pagamento mensal) contam como faturamento "
                       "(limite do MEI). A última SAÍDA (Retirada pessoal) é o seu pró-labore: lance a MESMA retirada em Lanç. "
                       "Pessoal, como entrada 'Pró-labore'. Vendas a prazo ficam só na aba A Receber (não duplique).", tip)
    ws.freeze_panes(CS - 1, 0)


# ===================================================================== DADOS (auxiliar)
def dados(ctx):
    k, ws, B = "DADOS", ctx.ws["DADOS"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    widths = [34, 14, 14, 14, 14, 4, 6, 8, 28, 14, 14, 4, 26, 14, 4, 30, 4, 30]
    ctx.page(k, widths, "🧮 Dados auxiliares", "Cálculos que alimentam os gráficos e painéis. Não edite esta aba.",
             area="geral", nav=True)
    ws.set_tab_color("#CBD5E1")
    th = ctx.theme("geral")
    sec = ctx.f_section(th)
    cf = ctx.f_calc()
    num = ctx.f_calc("0")
    mon = ctx.f_calc(MONEY)
    a = lambda key: A(*L[key], True, True)
    ra = N["RESUMO"]
    sai_r0, enttot, saitot = L["ra_sai0"], L["ra_enttot"], L["ra_saitot"]
    mrow = lambda r: X(ra, RNG(r, 3, r, 14))

    B.merge(ws, CS, 2, CS, 3, "PARÂMETROS CALCULADOS", sec)
    items = [
        ("d_mpainel", "Mês selecionado – Painel (1-12)",
         f"=IFERROR(MATCH({X(N['PAINEL'], AA(*L['p_sel']))},{ctx.cfg_list('c_mes', 12)},0),1)", num),
        ("d_morc", "Mês selecionado – Orçamento (1-12)",
         f"=IFERROR(MATCH({X(N['ORC'], AA(*L['o_sel']))},{ctx.cfg_list('c_mes', 12)},0),1)", num),
        ("d_R", "Meses decorridos no ano (pela data de hoje)",
         f"=IF(YEAR({ctx.cfg('cfg_hoje')})<{ctx.cfg('cfg_ano')},0,IF(YEAR({ctx.cfg('cfg_hoje')})>{ctx.cfg('cfg_ano')},12,"
         f"MONTH({ctx.cfg('cfg_hoje')})))", num),
        ("d_nact", "Meses com movimento (pessoal)",
         f"=MAX(1,SUMPRODUCT(--(({mrow(enttot)}+{mrow(saitot)})>0)))", num),
        ("d_totsai", "Total de saídas no mês do Painel", f"=INDEX({mrow(saitot)},{a('d_mpainel')})", mon),
    ]
    for key, label, fml, f in items:
        r, c = L[key]
        ws.write(r - 1, 1, label, cf)
        B.f(ws, A(r, c), fml, f)

    # lista combinada de categorias (pessoal) – alimenta a validação da coluna Categoria
    cc, r0 = L["d_all_c"], L["d_all_r0"]
    ws.write(CS - 1, cc - 1, "LISTA COMBINADA (pessoal)", sec)
    for i in range(NENT):
        B.f(ws, A(r0 + i, cc), f'=IF({ctx.cfg_item("c_ent", i)}="","",{ctx.cfg_item("c_ent", i)})', cf)
    for i in range(NSAI):
        B.f(ws, A(r0 + NENT + i, cc), f'=IF({ctx.cfg_item("c_sai", i)}="","",{ctx.cfg_item("c_sai", i)})', cf)

    # tabela de categorias de saída no mês do Painel
    hr = L["d_cat_r0"] - 1
    hd = ctx.f_head(th)
    for j, t in enumerate(["Categoria de saída", "Valor no mês", "Planejado", "Chave (aux)", "Acima?"]):
        ws.write(hr - 1, 1 + j, t, hd)
    c0 = L["d_cat_r0"]
    for i in range(NSAI):
        r = c0 + i
        B.f(ws, A(r, 2), f'=IF({ctx.cfg_item("c_sai", i)}="","",{ctx.cfg_item("c_sai", i)})', cf)
        B.f(ws, A(r, 3), f'=IF({A(r, 2)}="",0,INDEX({mrow(sai_r0 + i)},{a("d_mpainel")}))', mon)
        B.f(ws, A(r, 4), f'=IF({A(r, 2)}="",0,{X(N["ORC"], AA(L["o_c0"] + i, 3))})', mon)
        B.f(ws, A(r, 5), f"=IF({A(r, 3)}>0,{A(r, 3)}+ROW()/1000000,0)", ctx.f_calc("0.000000"))
        B.f(ws, A(r, 6), f"=IF(AND({A(r, 4)}>0,{A(r, 3)}>{A(r, 4)}),1,0)" if i != 13 else "=0", num)
    c1 = c0 + NSAI - 1
    rng = lambda c: RNG(c0, c, c1, c)
    r, c = L["d_nover"]
    ws.write(r - 1, 1, "Categorias acima do orçamento (mês do Painel)", cf)
    B.f(ws, A(r, c), f"=SUM({rng(6)})", num)

    # ranking top 8 (H..L)
    ws.write(hr - 1, 7, "#", hd)
    for j, t in enumerate(["Posição na lista", "Categoria", "Realizado", "Planejado"]):
        ws.write(hr - 1, 8 + j, t, hd)
    rr = L["d_rank_r0"]
    for kx in range(8):
        r = rr + kx
        ws.write(r - 1, 7, kx + 1, ctx.f_calc("0", align="center"))
        B.f(ws, A(r, 9), f"=IF(LARGE({rng(5)},{kx + 1})>0,MATCH(LARGE({rng(5)},{kx + 1}),{rng(5)},0),0)", num)
        B.f(ws, A(r, 10), f'=IF({A(r, 9)}>0,INDEX({rng(2)},{A(r, 9)}),"—")', cf)
        B.f(ws, A(r, 11), f"=IF({A(r, 9)}>0,INDEX({rng(3)},{A(r, 9)}),0)", mon)
        B.f(ws, A(r, 12), f"=IF({A(r, 9)}>0,INDEX({rng(4)},{A(r, 9)}),0)", mon)

    # rosca: top 7 + outras  (nomes na coluna M=13, valores na N=14)
    ws.write(hr - 1, 12, "Rosca – categoria", hd)
    ws.write(hr - 1, 13, "Valor", hd)
    dr = L["d_don_r0"]
    for kx in range(7):
        B.f(ws, A(dr + kx, 13), f"={A(rr + kx, 10)}", cf)
        B.f(ws, A(dr + kx, 14), f"={A(rr + kx, 11)}", mon)
    ws.write(dr + 6, 12, "Outras categorias", cf)          # 0-based => linha dr+7
    B.f(ws, A(dr + 7, 14), f"=MAX(0,{a('d_totsai')}-SUM({A(dr, 14)}:{A(dr + 6, 14)}))", mon)
    r, c = L["d_title_don"]
    ws.write(r - 1, 1, "Título do gráfico de rosca", cf)
    B.f(ws, A(r, c), f'="Para onde foi o dinheiro — "&INDEX({ctx.cfg_list("c_mes", 12)},{a("d_mpainel")})', cf)


# ===================================================================== LANÇAMENTOS (genérico)
def lancamentos(ctx, key, *, area, title, subtitle, ent_key, sai_key, all_col_key, extra_label, extra_list_ref,
                demo_rows=None, extra_width=22, mode="pessoal", n_ent=NENT, n_sai=NSAI):
    ws, B = ctx.ws[key], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme(area)
    widths = [12, 36, 28, 19, 15, 11, extra_width, 32]
    ctx.page(key, widths, title, subtitle, area=area)
    hr, r0, r1 = L["l_hr"], L["l_r0"], L["l_r1"]
    ano = ctx.cfg("cfg_ano")
    colrng = lambda c: X(N[key], RNG(r0, c, r1, c))
    D_, CAT, FORMA, VAL, TIPO, EXTRA = colrng(2), colrng(4), colrng(5), colrng(6), colrng(7), colrng(8)
    start, end = f"DATE({ano},1,1)", f"DATE({ano}+1,1,1)"
    inyear = f'{D_},">="&{start},{D_},"<"&{end}'

    # colunas pré-formatadas
    ws.set_column(1, 1, 12, B.fmt(num_format=DATE, align="center", font_color=T["input_fg"]))
    ws.set_column(2, 2, 36, B.fmt(font_color=T["input_fg"]))
    ws.set_column(3, 3, 28, B.fmt(font_color=T["input_fg"]))
    ws.set_column(4, 4, 19, B.fmt(font_color=T["input_fg"]))
    ws.set_column(5, 5, 15, B.fmt(num_format=MONEY, font_color=T["input_fg"]))
    ws.set_column(6, 6, 11, B.fmt(align="center", bold=True, font_size=9))
    ws.set_column(7, 7, extra_width, B.fmt(font_color=T["input_fg"]))
    ws.set_column(8, 8, 32, B.fmt(font_color=T["input_fg"]))

    # faixa de indicadores
    ws.set_row(CS - 1, 16)
    ws.set_row(CS, 26)
    ws.set_row(CS + 1, 6)
    lab = lambda: B.fmt(font_size=8, font_color=T["muted"], bg_color=T["bg"], bold=True, indent=1,
                        top=2, top_color=th["mid"])
    val = lambda num, color=T["ink"]: B.fmt(font_size=14, bold=True, bg_color=T["bg"], num_format=num, indent=1,
                                            font_color=color, align="left")
    if mode == "negocio":
        pro = f'SUMIFS({VAL},{CAT},{ctx.cfg_item("c_nsai", NBSAI - 1)},{inyear})'
        cards = [(2, 3, "ENTRADAS NO ANO", f'=SUMIFS({VAL},{TIPO},"Entrada",{inyear})', MONEY, T["pos"]),
                 (4, 4, "DESPESAS NO ANO (SEM RETIRADA)", f'=SUMIFS({VAL},{TIPO},"Saída",{inyear})-{pro}', MONEY, T["neg"]),
                 (5, 6, "RETIRADA PESSOAL NO ANO", f"={pro}", MONEY, T["ink"])]
    else:
        cards = [(2, 3, "ENTRADAS NO ANO", f'=SUMIFS({VAL},{TIPO},"Entrada",{inyear})', MONEY, T["pos"]),
                 (4, 4, "SAÍDAS NO ANO", f'=SUMIFS({VAL},{TIPO},"Saída",{inyear})', MONEY, T["neg"]),
                 (5, 6, "SALDO DO ANO", None, MONEY, T["ink"])]
    for c0, c1, label, fml, num, color in cards:
        B.merge(ws, CS, c0, CS, c1, label, lab())
        if fml is None:
            fml = f"={A(CS + 1, 2)}-{A(CS + 1, 4)}"
        B.merge(ws, CS + 1, c0, CS + 1, c1, fml, val(num, color))
    if mode != "negocio":
        ws.conditional_format(f"{A(CS + 1, 5)}:{A(CS + 1, 6)}", {"type": "cell", "criteria": "<", "value": 0,
                                                                  "format": B.fmt(font_color=T["neg"])})
    n_nocat = f'SUMPRODUCT(({VAL}>0)*({CAT}=""))'
    n_bad = f'COUNTIF({TIPO},"Verificar")'
    n_out = f'(COUNT({VAL})-COUNTIFS({inyear},{VAL},">0"))'
    chk = (f'=IF({n_nocat}>0,"⚠ "&{n_nocat}&" lançamento(s) sem categoria — não entram nos painéis",'
           f'IF({n_bad}>0,"⚠ "&{n_bad}&" lançamento(s) com categoria inválida (coluna Tipo = Verificar)",'
           f'IF({n_out}>0,"⚠ "&{n_out}&" lançamento(s) sem data ou fora de "&{ano}&" — não entram nos painéis",'
           f'"✓ Tudo certo: "&COUNT({VAL})&" lançamento(s) registrados")))')
    B.merge(ws, CS, 7, CS, 9, "VERIFICAÇÃO AUTOMÁTICA", lab())
    B.merge(ws, CS + 1, 7, CS + 1, 9, chk, B.fmt(font_size=9, bold=True, bg_color=T["bg"], indent=1, text_wrap=True,
                                                 font_color=T["pos"]))
    ws.conditional_format(f"{A(CS + 1, 7)}:{A(CS + 1, 9)}",
                          {"type": "text", "criteria": "begins with", "value": "⚠",
                           "format": B.fmt(font_color=T["warn"])})

    # cabeçalho
    heads = ["Data", "Descrição", "Categoria", "Forma de pagamento", "Valor (R$)", "Tipo", extra_label, "Observação"]
    hf = ctx.f_head(th)
    ws.set_row(hr - 1, 28)
    for j, t in enumerate(heads):
        ws.write(hr - 1, 1 + j, t, hf)
    ws.write_comment(hr - 1, 2, "Escolha no menu suspenso. A lista vem da aba Config.", {"x_scale": 1.2})
    ws.write_comment(hr - 1, 5, "Digite SEMPRE valores positivos. O Tipo (Entrada/Saída) é automático "
                                "e vem da categoria.", {"x_scale": 1.4, "y_scale": 1.2})
    ws.write_comment(hr - 1, 6, "Automático: Entrada ou Saída conforme a categoria. 'Verificar' = categoria "
                                "que não existe mais na aba Config.", {"x_scale": 1.4, "y_scale": 1.2})

    # fórmulas de Tipo
    ent_rng, sai_rng = ctx.cfg_list(ent_key, n_ent), ctx.cfg_list(sai_key, n_sai)
    tf = B.fmt(align="center", bold=True, font_size=9)
    for r in range(r0, r1 + 1):
        B.f(ws, A(r, 7), f'=IF($D{r}="","",IF(COUNTIF({ent_rng},$D{r})>0,"Entrada",'
                         f'IF(COUNTIF({sai_rng},$D{r})>0,"Saída","Verificar")))', tf)

    # dados de exemplo
    if demo_rows:
        d_f = B.fmt(num_format=DATE, align="center", font_color=T["input_fg"])
        t_f = B.fmt(font_color=T["input_fg"])
        m_f = B.fmt(num_format=MONEY, font_color=T["input_fg"])
        for i, row in enumerate(demo_rows):
            r = r0 + i
            data, desc, cat, forma, valor, extra, obs = row
            ws.write_datetime(r - 1, 1, dt.datetime.combine(data, dt.time()), d_f)
            ws.write(r - 1, 2, desc, t_f)
            ws.write(r - 1, 3, cat, t_f)
            ws.write(r - 1, 4, forma, t_f)
            ws.write_number(r - 1, 5, valor, m_f)
            if extra:
                ws.write(r - 1, 7, extra, t_f)
            if obs:
                ws.write(r - 1, 8, obs, t_f)

    # validações
    ws.data_validation(A(r0, 2) + ":" + A(r1, 2), {
        "validate": "date", "criteria": "between", "minimum": dt.date(2000, 1, 1), "maximum": dt.date(2100, 12, 31),
        "input_title": "Data", "input_message": "Digite no formato dd/mm/aaaa.",
        "error_title": "Data inválida", "error_message": "Use uma data válida, ex.: 05/03/2026."})
    allc = X(N["DADOS"], RNG(L["d_all_r0"], L[all_col_key], L["d_all_r0"] + n_ent + n_sai - 1, L[all_col_key]))
    ws.data_validation(A(r0, 4) + ":" + A(r1, 4), {
        "validate": "list", "source": "=" + allc, "input_title": "Categoria",
        "input_message": "Escolha no menu suspenso (edite a lista na aba Config).",
        "error_title": "Categoria inválida", "error_message": "Escolha uma categoria da lista."})
    ws.data_validation(A(r0, 5) + ":" + A(r1, 5), {
        "validate": "list", "source": "=" + ctx.cfg_list("c_forma", NFORMA), "ignore_blank": True,
        "error_title": "Forma inválida", "error_message": "Escolha uma forma da lista."})
    ws.data_validation(A(r0, 6) + ":" + A(r1, 6), {
        "validate": "decimal", "criteria": ">", "value": 0, "input_title": "Valor",
        "input_message": "Sempre positivo. Entrada/Saída é definido pela categoria.",
        "error_title": "Valor inválido", "error_message": "Digite um número maior que zero."})
    if extra_list_ref:
        ws.data_validation(A(r0, 8) + ":" + A(r1, 8), {
            "validate": "list", "source": "=" + extra_list_ref, "ignore_blank": True,
            "error_title": "Valor inválido", "error_message": "Escolha um item da lista."})

    # formatação condicional
    full = f"{A(r0, 2)}:{A(r1, 9)}"
    ws.conditional_format(f"{A(r0, 6)}:{A(r1, 6)}", {"type": "formula", "criteria": f'=$G{r0}="Entrada"',
                                                      "format": B.fmt(font_color=T["pos"], bold=True)})
    ws.conditional_format(f"{A(r0, 6)}:{A(r1, 6)}", {"type": "formula", "criteria": f'=$G{r0}="Saída"',
                                                      "format": B.fmt(font_color=T["neg"], bold=True)})
    for txt, fc, bg in [("Entrada", T["pos"], T["pos_bg"]), ("Saída", T["neg"], T["neg_bg"]),
                        ("Verificar", T["warn"], T["warn_bg"])]:
        ws.conditional_format(f"{A(r0, 7)}:{A(r1, 7)}", {"type": "cell", "criteria": "==", "value": f'"{txt}"',
                                                          "format": B.fmt(font_color=fc, bg_color=bg)})
    ws.conditional_format(full, {"type": "formula", "criteria": f"=MOD(ROW(),2)=0",
                                 "format": B.fmt(bg_color=T["zebra"], bottom=1, bottom_color=T["line"])})
    ws.conditional_format(full, {"type": "formula", "criteria": "=MOD(ROW(),2)=1",
                                 "format": B.fmt(bottom=1, bottom_color=T["line"])})
    ws.autofilter(hr - 1, 1, r1 - 1, 8)
    ws.freeze_panes(hr, 0)
    ws.repeat_rows(hr - 1)


# ===================================================================== RESUMO ANUAL
def resumo(ctx):
    k, ws, B = "RESUMO", ctx.ws["RESUMO"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("pessoal")
    widths = [32] + [11.5] * 12 + [14, 13, 11]
    ctx.page(k, widths, "📅 Resumo anual — entradas e saídas por mês",
             "Totalizado automaticamente a partir da aba de lançamentos. Cores destacam saldos positivos e negativos.")
    ano = ctx.cfg("cfg_ano")
    lanc = N["LANC"]
    lr = lambda c: X(lanc, RNG(L["l_r0"], c, L["l_r1"], c))
    D_, CAT, VAL = lr(2), lr(4), lr(6)
    dates, hdr = L["ra_dates"], L["ra_hdr"]
    ws.set_row(dates - 1, None, None, {"hidden": True})
    for m in range(12):
        B.f(ws, A(dates, 3 + m), f"=DATE({ano},{m + 1},1)", B.fmt(num_format=DATE))
    ws.set_row(hdr - 1, 24)
    hd = ctx.f_head(th)
    ws.write(hdr - 1, 1, "Categoria", ctx.f_head(th, align="left", indent=1))
    for m in range(12):
        B.f(ws, A(hdr, 3 + m), f"=INDEX({ctx.cfg_list('c_abrev', 12)},{m + 1})", hd)
    for c, t in [(15, "Total"), (16, "Média/mês"), (17, "% das saídas")]:
        ws.write(hdr - 1, c - 1, t, hd)
    nact = ctx.dados("d_nact")

    def block(r_first, n, ckey, title, tot_row, color, light, pct=False, label_row=None):
        sec = B.fmt(bg_color=color, font_color="#FFFFFF", bold=True, indent=1)
        B.merge(ws, label_row, 2, label_row, 17, title, sec)
        for i in range(n):
            r = r_first + i
            B.f(ws, A(r, 2), f'=IF({ctx.cfg_item(ckey, i)}="","",{ctx.cfg_item(ckey, i)})',
                B.fmt(indent=1, bottom=1, bottom_color=T["line"]))
            for m in range(12):
                c = 3 + m
                B.f(ws, A(r, c), f'=IF($B{r}="",0,SUMIFS({VAL},{CAT},$B{r},{D_},">="&{A(dates, c, True)},'
                                 f'{D_},"<"&EDATE({A(dates, c, True)},1)))', ctx.f_calc(MONEY0))
            B.f(ws, A(r, 15), f"=SUM({A(r, 3)}:{A(r, 14)})", ctx.f_calc(MONEY0, bold=True))
            B.f(ws, A(r, 16), f"=IFERROR({A(r, 15)}/{nact},0)", ctx.f_calc(MONEY0, font_color=T["muted"]))
            if pct:
                B.f(ws, A(r, 17), f"=IFERROR({A(r, 15)}/{A(tot_row, 15, True, True)},0)", ctx.f_calc(PCT, align="center",
                                                                                                    font_color=T["muted"]))
            else:
                ws.write(r - 1, 16, "", ctx.f_calc())
        tf = B.fmt(bold=True, bg_color=light, top=1, bottom=1, top_color=color, bottom_color=color, num_format=MONEY0)
        ws.write(tot_row - 1, 1, "Total de " + ("entradas" if not pct else "saídas"),
                 B.fmt(bold=True, bg_color=light, indent=1, top=1, bottom=1, top_color=color, bottom_color=color))
        for c in range(3, 17):
            B.f(ws, A(tot_row, c), f"=SUM({A(r_first, c)}:{A(r_first + n - 1, c)})", tf)
        ws.write(tot_row - 1, 16, "", tf)
        # mapa de calor
        ws.conditional_format(f"{A(r_first, 3)}:{A(r_first + n - 1, 14)}", {
            "type": "2_color_scale", "min_type": "num", "min_value": 0, "max_type": "max",
            "min_color": "#FFFFFF", "max_color": "#A7F3D0" if not pct else "#FDA4AF"})

    block(L["ra_ent0"], NENT, "c_ent", "▲  ENTRADAS", L["ra_enttot"], T["pos"], T["pos_bg"], label_row=L["ra_ent0"] - 1)
    block(L["ra_sai0"], NSAI, "c_sai", "▼  SAÍDAS", L["ra_saitot"], T["neg"], T["neg_bg"], pct=True,
          label_row=L["ra_sai0"] - 1)
    # resultado
    et, st, sd, ac, tx = L["ra_enttot"], L["ra_saitot"], L["ra_saldo"], L["ra_acum"], L["ra_taxa"]
    big = lambda num=MONEY: B.fmt(bold=True, num_format=num, top=1, top_color=T["line2"], bottom=1,
                                  bottom_color=T["line2"], align="right")
    ws.write(sd - 1, 1, "💰 Saldo do mês (entradas − saídas)", B.fmt(bold=True, indent=1, top=1, bottom=1,
                                                                      top_color=T["line2"], bottom_color=T["line2"]))
    ws.write(ac - 1, 1, "📈 Saldo acumulado (inclui saldo inicial)", B.fmt(bold=True, indent=1, bottom=1,
                                                                            bottom_color=T["line2"]))
    ws.write(tx - 1, 1, "🏦 Taxa de poupança", B.fmt(bold=True, indent=1, bottom=1,
                                                                        bottom_color=T["line2"]))
    for c in range(3, 16):
        B.f(ws, A(sd, c), f"={A(et, c)}-{A(st, c)}", big())
        if c <= 14:
            prev = ctx.cfg("cfg_saldo0") if c == 3 else A(ac, c - 1)
            B.f(ws, A(ac, c), f"={prev}+{A(sd, c)}", big())
        B.f(ws, A(tx, c), f'=IF({A(et, c)}=0,"",({A(sd, c)}+{A(L["ra_sai0"] + 13, c)})/{A(et, c)})', big(PCT))
    B.f(ws, A(ac, 15), f"={A(ac, 14)}", big())
    ws.write(ac - 1, 15, "", big())
    cf_pos_neg(ws, B, f"{A(sd, 3)}:{A(sd, 15)}")
    cf_pos_neg(ws, B, f"{A(ac, 3)}:{A(ac, 15)}")
    meta = ctx.cfg("cfg_meta")
    trg = f"{A(tx, 3)}:{A(tx, 15)}"
    ws.conditional_format(trg, {"type": "formula", "criteria": f'=AND(ISNUMBER({A(tx, 3)}),{A(tx, 3)}<0)',
                                "format": B.fmt(font_color=T["neg"], bg_color=T["neg_bg"])})
    ws.conditional_format(trg, {"type": "formula", "criteria": f'=AND(ISNUMBER({A(tx, 3)}),{A(tx, 3)}>={meta})',
                                "format": B.fmt(font_color=T["pos"], bg_color=T["pos_bg"])})
    ws.conditional_format(trg, {"type": "formula", "criteria": f'=AND(ISNUMBER({A(tx, 3)}),{A(tx, 3)}>=0,{A(tx, 3)}<{meta})',
                                "format": B.fmt(font_color=T["warn"], bg_color=T["warn_bg"])})
    ws.freeze_panes(hdr, 2)
    note = B.fmt(italic=True, font_size=8, font_color=T["muted"])
    ws.write(tx + 1, 1, "Taxa de poupança: o que sobrou + o que foi para 'Reserva e Metas' (14ª categoria de saída, tratada como poupança, "
                        "não como gasto). Verde = meta atingida (Config); amarelo = abaixo da meta; vermelho = negativa.", note)


# ===================================================================== ORÇAMENTO
def orcamento(ctx):
    k, ws, B = "ORC", ctx.ws["ORC"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("pessoal")
    widths = [30, 17, 17, 17, 11, 26, 16]
    ctx.page(k, widths, "💳 Orçamento mensal — planejado × realizado",
             "Defina quanto pretende gastar em cada categoria. O 'realizado' vem dos lançamentos do mês escolhido.")
    sel_r, sel_c = L["o_sel"]
    ws.set_row(sel_r - 1, 26)
    ws.write(sel_r - 1, 1, "📅 Mês de análise:", B.fmt(bold=True, font_size=11, align="right"))
    sf = ctx.f_input(align="center", bold=True, font_size=11)
    if ctx.demo:
        ws.write(sel_r - 1, sel_c - 1, "Setembro", sf)
    else:
        B.f(ws, A(sel_r, sel_c), f"=INDEX({ctx.cfg_list('c_mes', 12)},MAX(1,{ctx.dados('d_R')}))", sf)
    month_dv(ctx, ws, A(sel_r, sel_c))
    ws.merge_range(sel_r - 1, 3, sel_r - 1, 7, "← escolha o mês no menu suspenso. Os valores planejados (amarelo) valem para todos os meses.",
                   B.fmt(italic=True, font_size=9, font_color=T["muted"], indent=1))
    hr = L["o_hdr"]
    ws.set_row(hr - 1, 28)
    hd = ctx.f_head(th)
    for j, t in enumerate(["Categoria", "Planejado (mês)", "Realizado", "Diferença", "% usado", "Progresso", "Situação"]):
        ws.write(hr - 1, 1 + j, t, ctx.f_head(th, align="left", indent=1) if j == 0 else hd)
    m = ctx.dados("d_morc")
    ra = N["RESUMO"]
    mrow = lambda r: X(ra, RNG(r, 3, r, 14))
    inp = ctx.f_input(MONEY)
    bar_f = B.fmt(font_color=T["pos"], font_size=9, bottom=1, bottom_color=T["line"])

    def line(r, label_f, planned_default, real_f, diff_f, income=False):
        B.f(ws, A(r, 4), real_f, ctx.f_calc(MONEY))
        B.f(ws, A(r, 5), diff_f, ctx.f_calc(MONEY))
        B.f(ws, A(r, 6), f'=IF({A(r, 3)}>0,{A(r, 4)}/{A(r, 3)},"")', ctx.f_calc(PCT, align="center"))
        B.f(ws, A(r, 7), f'=IF({A(r, 6)}="","",REPT("█",MIN(22,ROUND({A(r, 6)}*20,0))))', bar_f)
        if income:
            B.f(ws, A(r, 8), f'=IF({A(r, 3)}=0,"—",IF({A(r, 4)}>={A(r, 3)},"✓ Meta batida",IF({A(r, 4)}>={A(r, 3)}*0.8,"⚠ Quase lá","✖ Abaixo")))',
                ctx.f_calc(align="center", bold=True, font_size=9))
        else:
            B.f(ws, A(r, 8), f'=IF({A(r, 3)}=0,IF({A(r, 4)}>0,"Sem orçamento","—"),IF({A(r, 4)}>{A(r, 3)},"✖ Estourou",'
                             f'IF({A(r, 4)}>={A(r, 3)}*0.8,"⚠ Atenção","✓ OK")))',
                ctx.f_calc(align="center", bold=True, font_size=9))

    rr = L["o_renda"]
    ws.write(rr - 1, 1, "Renda do mês (entradas)", B.fmt(bold=True, indent=1, bottom=1, bottom_color=T["line"], bg_color=T["pos_bg"]))
    ws.write(rr - 1, 2, (4500 if ctx.aut else 9500) if ctx.demo else 0, ctx.f_input(MONEY))
    line(rr, None, None, f"=INDEX({mrow(L['ra_enttot'])},{m})", f"={A(rr, 4)}-{A(rr, 3)}", income=True)
    sec = ctx.f_section(th)
    B.merge(ws, L["o_c0"] - 1, 2, L["o_c0"] - 1, 8, "DESPESAS POR CATEGORIA", sec)
    budget = ([1100, 360, 650, 420, 250, 150, 250, 100, 90, 200, 0, 80, 0, 600, 80, 80] if ctx.aut else
              [2150, 480, 1700, 750, 600, 300, 450, 250, 100, 250, 180, 150, 450, 1250, 100, 200])
    for i in range(NSAI):
        r = L["o_c0"] + i
        B.f(ws, A(r, 2), f'=IF({ctx.cfg_item("c_sai", i)}="","",{ctx.cfg_item("c_sai", i)})',
            B.fmt(indent=1, bottom=1, bottom_color=T["line"]))
        ws.write(r - 1, 2, budget[i] if ctx.demo else 0, inp)
        saving = i == 13          # 'Reserva e Metas': guardar MAIS que o planejado é bom
        line(r, None, None, f'=IF({A(r, 2)}="",0,INDEX({mrow(L["ra_sai0"] + i)},{m}))',
             f"={A(r, 4)}-{A(r, 3)}" if saving else f"={A(r, 3)}-{A(r, 4)}", income=saving)
    sav = L["o_c0"] + 13
    ws.conditional_format(A(sav, 7), {"type": "formula", "criteria": "=TRUE", "stop_if_true": True,
                                      "format": B.fmt(font_color=T["pos"])})
    t, s = L["o_tot"], L["o_saldo"]
    tf = lambda num=MONEY0: B.fmt(bold=True, bg_color=th["light"], top=1, top_color=th["mid"], num_format=num)
    ws.write(t - 1, 1, "TOTAL DAS DESPESAS", B.fmt(bold=True, bg_color=th["light"], indent=1, top=1, top_color=th["mid"]))
    c0, c1 = L["o_c0"], L["o_c0"] + NSAI - 1
    B.f(ws, A(t, 3), f"=SUM({A(c0, 3)}:{A(c1, 3)})", tf(MONEY))
    B.f(ws, A(t, 4), f"=SUM({A(c0, 4)}:{A(c1, 4)})", tf(MONEY))
    B.f(ws, A(t, 5), f"={A(t, 3)}-{A(t, 4)}", tf(MONEY))
    B.f(ws, A(t, 6), f'=IF({A(t, 3)}>0,{A(t, 4)}/{A(t, 3)},"")', tf(PCT))
    B.f(ws, A(t, 7), f'=IF({A(t, 6)}="","",REPT("█",MIN(22,ROUND({A(t, 6)}*20,0))))', tf())
    B.f(ws, A(t, 8), f'=IF({A(t, 3)}=0,"—",IF({A(t, 4)}>{A(t, 3)},"✖ Estourou",IF({A(t, 4)}>={A(t, 3)}*0.8,"⚠ Atenção","✓ OK")))',
        B.fmt(bold=True, bg_color=th["light"], top=1, top_color=th["mid"], align="center", font_size=9))
    sf2 = lambda: B.fmt(bold=True, font_size=11, num_format=MONEY, bottom=2, bottom_color=th["mid"])
    ws.write(s - 1, 1, "SALDO (renda − despesas)", B.fmt(bold=True, font_size=11, indent=1, bottom=2, bottom_color=th["mid"]))
    B.f(ws, A(s, 3), f"={A(rr, 3)}-{A(t, 3)}", sf2())
    B.f(ws, A(s, 4), f"={A(rr, 4)}-{A(t, 4)}", sf2())
    B.f(ws, A(s, 5), f"={A(s, 4)}-{A(s, 3)}", sf2())
    for c in (6, 7, 8):
        ws.write(s - 1, c - 1, "", sf2())
    # formatação condicional
    for rng_ in (f"{A(rr, 5)}", f"{A(c0, 5)}:{A(t, 5)}", f"{A(s, 3)}:{A(s, 5)}"):
        cf_pos_neg(ws, B, rng_)
    stat = f"{A(rr, 8)}:{A(t, 8)}"
    for txt, fc, bg in [("Estourou", T["neg"], T["neg_bg"]), ("Atenção", T["warn"], T["warn_bg"]),
                        ("OK", T["pos"], T["pos_bg"]), ("Meta batida", T["pos"], T["pos_bg"]),
                        ("Quase lá", T["warn"], T["warn_bg"]), ("Abaixo", T["neg"], T["neg_bg"])]:
        ws.conditional_format(stat, {"type": "text", "criteria": "containing", "value": txt,
                                     "format": B.fmt(font_color=fc, bg_color=bg)})
    for a_, b_ in ((c0, sav - 1), (sav + 1, t)):          # poupança (Reserva e Metas) fica fora das regras de "estouro"
        bars = f"{A(a_, 7)}:{A(b_, 7)}"
        ws.conditional_format(bars, {"type": "formula", "criteria": f"=AND(ISNUMBER({A(a_, 6)}),{A(a_, 6)}>1)",
                                     "format": B.fmt(font_color=T["neg"])})
        ws.conditional_format(bars, {"type": "formula", "criteria": f"=AND(ISNUMBER({A(a_, 6)}),{A(a_, 6)}>=0.8)",
                                     "format": B.fmt(font_color="#F59E0B")})
    ws.freeze_panes(hr, 1)


# ===================================================================== METAS
GOALS_DEMO_AUT = [("Reserva de emergência", 24000, 6000, dt.date(2027, 12, 31)),
                  ("Reserva para impostos", 4000, 0, dt.date(2026, 12, 31)),
                  ("Viagem de férias", 6000, 500, dt.date(2027, 6, 30))]
GOALS_DEMO = [("Reserva de emergência", 20000, 5000, dt.date(2027, 12, 31)),
              ("Viagem de férias", 8000, 500, dt.date(2027, 7, 15)),
              ("Notebook novo", 4500, 0, dt.date(2027, 3, 31)),
              ("Curso de especialização", 3000, 300, dt.date(2026, 12, 31))]


def metas(ctx):
    k, ws, B = "METAS", ctx.ws["METAS"], ctx.book
    L, CS, N = ctx.L, ctx.CS, ctx.N
    th = ctx.theme("pessoal")
    widths = [28, 15, 15, 13, 16, 15, 10, 22, 14, 11, 17, 15]
    ctx.page(k, widths, "🎯 Metas de economia",
             "Cadastre seus objetivos. Para registrar um aporte, lance uma SAÍDA na aba de lançamentos e escolha a "
             "meta na última coluna (um resgate é uma ENTRADA com a meta escolhida).")
    hr, r0 = L["m_hdr"], L["m_r0"]
    ws.set_row(hr - 1, 32)
    heads = ["Meta", "Valor alvo", "Já guardado (antes)", "Prazo", "Aportes lançados", "Total guardado", "% concl.",
             "Progresso", "Falta", "Meses restantes", "Aporte mensal necessário", "Situação"]
    for j, t in enumerate(heads):
        ws.write(hr - 1, 1 + j, t, ctx.f_head(th, align="left", indent=1) if j == 0 else ctx.f_head(th))
    lanc = N["LANC"]
    lr = lambda c: X(lanc, RNG(L["l_r0"], c, L["l_r1"], c))
    VAL, TIPO, EXTRA = lr(6), lr(7), lr(8)
    hoje = ctx.cfg("cfg_hoje")
    inp_t, inp_m, inp_d = ctx.f_input(align="left"), ctx.f_input(MONEY), ctx.f_input(DATE, align="center")
    for i in range(NGOAL):
        r = r0 + i
        gl = GOALS_DEMO_AUT if ctx.aut else GOALS_DEMO
        g = gl[i] if ctx.demo and i < len(gl) else None
        ws.write(r - 1, 1, g[0] if g else "", inp_t)
        if g:
            ws.write_number(r - 1, 2, g[1], inp_m)
            ws.write_number(r - 1, 3, g[2], inp_m)
            ws.write_datetime(r - 1, 4, dt.datetime.combine(g[3], dt.time()), inp_d)
        else:
            for c, f in [(2, inp_m), (3, inp_m), (4, inp_d)]:
                ws.write_blank(r - 1, c, None, f)
        B.f(ws, A(r, 6), f'=IF($B{r}="","",SUMIFS({VAL},{EXTRA},$B{r},{TIPO},"Saída")-SUMIFS({VAL},{EXTRA},$B{r},{TIPO},"Entrada"))',
            ctx.f_calc(MONEY0))
        B.f(ws, A(r, 7), f'=IF($B{r}="","",N({A(r, 4)})+{A(r, 6)})', ctx.f_calc(MONEY0, bold=True))
        B.f(ws, A(r, 8), f'=IF(OR($B{r}="",N({A(r, 3)})=0),"",{A(r, 7)}/{A(r, 3)})', ctx.f_calc(PCT, align="center", bold=True))
        B.f(ws, A(r, 9), f'=IF({A(r, 8)}="","",REPT("█",MIN(24,ROUND({A(r, 8)}*20,0))))',
            B.fmt(font_color=T["teal_mid"], font_size=9, bottom=1, bottom_color=T["line"]))
        B.f(ws, A(r, 10), f'=IF({A(r, 8)}="","",MAX(0,{A(r, 3)}-{A(r, 7)}))', ctx.f_calc(MONEY0))
        B.f(ws, A(r, 11), f'=IF(OR($B{r}="",{A(r, 5)}=""),"",MAX(0,(YEAR({A(r, 5)})-YEAR({hoje}))*12+MONTH({A(r, 5)})-MONTH({hoje})))',
            ctx.f_calc("0", align="center"))
        B.f(ws, A(r, 12), f'=IF(OR({A(r, 10)}="",{A(r, 11)}=""),"",IF({A(r, 10)}=0,0,IF({A(r, 11)}=0,{A(r, 10)},{A(r, 10)}/{A(r, 11)})))',
            ctx.f_calc(MONEY0))
        B.f(ws, A(r, 13), f'=IF($B{r}="","",IF(N({A(r, 3)})=0,"—",IF({A(r, 7)}>={A(r, 3)},"✓ Concluída",'
                          f'IF({A(r, 5)}="","Em andamento",IF({hoje}>{A(r, 5)},"✖ Atrasada","● No prazo")))))',
            ctx.f_calc(align="center", bold=True, font_size=9))
    r1 = r0 + NGOAL - 1
    ws.conditional_format(f"{A(r0, 13)}:{A(r1, 13)}", {"type": "text", "criteria": "containing", "value": "Concluída",
                                                       "format": B.fmt(font_color=T["pos"], bg_color=T["pos_bg"])})
    ws.conditional_format(f"{A(r0, 13)}:{A(r1, 13)}", {"type": "text", "criteria": "containing", "value": "Atrasada",
                                                       "format": B.fmt(font_color=T["neg"], bg_color=T["neg_bg"])})
    ws.conditional_format(f"{A(r0, 13)}:{A(r1, 13)}", {"type": "text", "criteria": "containing", "value": "No prazo",
                                                       "format": B.fmt(font_color=T["saldo"], bg_color=T["navy_light"])})
    ws.conditional_format(f"{A(r0, 9)}:{A(r1, 9)}", {"type": "formula", "criteria": f"=AND(ISNUMBER({A(r0, 8)}),{A(r0, 8)}>=1)",
                                                     "format": B.fmt(font_color=T["pos"])})
    ws.conditional_format(f"{A(r0, 9)}:{A(r1, 9)}", {"type": "formula", "criteria": f"=AND(ISNUMBER({A(r0, 8)}),{A(r0, 8)}<0.34)",
                                                     "format": B.fmt(font_color="#F59E0B")})
    ws.data_validation(f"{A(r0, 3)}:{A(r1, 4)}", {"validate": "decimal", "criteria": ">=", "value": 0,
                                                  "error_message": "Digite um valor maior ou igual a zero."})
    ws.data_validation(f"{A(r0, 5)}:{A(r1, 5)}", {"validate": "date", "criteria": ">", "value": dt.date(2000, 1, 1),
                                                  "error_message": "Digite uma data válida, ex.: 31/12/2027."})
    # reserva de emergência
    rs = r0 + NGOAL + 1
    sec = ctx.f_section(th)
    B.merge(ws, rs, 2, rs, 5, "🛟 RESERVA DE EMERGÊNCIA IDEAL", sec)
    ra = N["RESUMO"]
    lines = [("Meses de cobertura desejados", 6, "0", True),
             ("Média mensal de saídas", f"=IFERROR({X(ra, AA(L['ra_saitot'], 15))}/{ctx.dados('d_nact')},0)", MONEY, False),
             ("Reserva ideal (meses × média)", f"={A(rs + 1, 4)}*{A(rs + 2, 4)}", MONEY, False),
             ("Total guardado nas suas metas", f"=SUM({A(r0, 7)}:{A(r1, 7)})", MONEY, False)]
    for i, (lbl, v, num, is_inp) in enumerate(lines):
        r = rs + 1 + i
        B.merge(ws, r, 2, r, 3, lbl, B.fmt(indent=1, bottom=1, bottom_color=T["line"]))
        if is_inp:
            ws.write(r - 1, 3, v, ctx.f_input(num))
        else:
            B.f(ws, A(r, 4), v, ctx.f_calc(num, bold=True))
    ws.write(rs + 5, 1, "A regra de bolso: entre 3 e 6 meses do seu custo de vida (6 a 12 para autônomos e renda variável).",
             B.fmt(italic=True, font_size=8, font_color=T["muted"], indent=1))

    # gráfico: guardado × alvo
    ch = ctx.book.wb.add_chart({"type": "bar"})
    nm = N["METAS"]
    cats = f"={X(nm, RNG(r0, 2, r1, 2))}"
    ch.add_series({"name": "Valor alvo", "categories": cats, "values": f"={X(nm, RNG(r0, 3, r1, 3))}",
                   "fill": {"color": "#CBD5E1"}, "gap": 60, "overlap": -10})
    ch.add_series({"name": "Total guardado", "categories": cats, "values": f"={X(nm, RNG(r0, 7, r1, 7))}",
                   "fill": {"color": T["teal_mid"]},
                   "data_labels": {"value": True, "num_format": '#,##0', "font": {"name": FONT, "size": 8}}})
    style_chart(ch, "Quanto já guardei × valor alvo", 760, 330, y_fmt=MONEY_INT, reverse_x=True, horizontal=True)
    ws.insert_chart(rs + 7, 1, ch, {"x_offset": 4, "y_offset": 4})
