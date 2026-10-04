"""Aba Início: boas-vindas, passo a passo, mapa de navegação, legenda e dicas."""
from lib import *
from ctx import *


def inicio(ctx):
    k, ws, B = "INICIO", ctx.ws["INICIO"], ctx.book
    CS, N = ctx.CS, ctx.N
    aut = ctx.aut
    th = ctx.theme("geral" if aut else "pessoal")
    sub = ("Controle financeiro pessoal + negócio • Excel e Google Sheets" if aut
           else "Controle financeiro pessoal e doméstico • Excel e Google Sheets")
    ctx.page(k, [11] * 12, f"{ctx.brand}", sub, area="geral" if aut else "pessoal", bg=True)
    ws.set_default_row(18)
    wrap = lambda **kw: B.fmt(text_wrap=True, valign="top", bg_color="#FFFFFF", indent=1, **kw)
    r = CS
    ws.set_row(r - 1, 64)
    welcome = ("Bem-vindo(a)! Esta planilha organiza suas finanças do jeito mais simples: você só LANÇA os valores e "
               "todo o resto — resumos, gráficos, alertas e metas — é calculado automaticamente. "
               + ("Aqui, vida pessoal e negócio ficam separados, com controle de clientes, recebimentos, impostos (DAS do MEI) "
                  "e fluxo de caixa." if aut else
                  "Use o Painel para enxergar para onde o dinheiro vai e a aba Metas para transformar sonhos em planos."))
    B.merge(ws, r, 2, r, 13, welcome, wrap(font_size=11, font_color=T["ink"]))
    r += 2
    sec = lambda text: (B.merge(ws, r, 2, r, 13, text, B.fmt(bg_color=th["mid"], font_color="#FFFFFF", bold=True,
                                                             indent=1, font_size=11)), ws.set_row(r - 1, 24))
    sec("🚀  COMECE EM 5 MINUTOS")
    r += 1
    steps = (["Em ⚙ Config: confira o ANO, escreva seu nome/negócio e renomeie as categorias, se quiser.",
              "Em 💳 Orçamento Pessoal e 🎯 Metas: informe quanto pretende gastar e quais objetivos quer alcançar.",
              "Em 🧾 Impostos: escolha seu regime (MEI, Simples ou outro) e confira o valor do DAS.",
              "Cadastre seus 🤝 Clientes e registre cada cobrança em 💰 Recebimentos (com vencimento e data de pagamento).",
              "No dia a dia: lance gastos em 📝 Lançamentos (pessoal e negócio). Depois é só abrir os 📊 Painéis!"] if aut else
             ["Em ⚙ Config: confira o ANO, escreva seu nome e renomeie as categorias, se quiser.",
              "Em 💳 Orçamento: informe a renda prevista e quanto pretende gastar em cada categoria.",
              "Em 🎯 Metas: cadastre seus objetivos (reserva de emergência, viagem, carro...).",
              "No dia a dia: registre cada entrada e saída em 📝 Lançamentos — escolha a categoria no menu suspenso.",
              "Abra o 📊 Painel, escolha o mês e veja gráficos, alertas e a evolução das suas metas."])
    for i, t in enumerate(steps):
        ws.set_row(r - 1, 28)
        B.merge(ws, r, 2, r, 2, i + 1, B.fmt(bg_color=th["light"], font_color=th["dark"], bold=True, font_size=14, align="center"))
        B.merge(ws, r, 3, r, 13, t, B.fmt(bg_color="#FFFFFF", indent=1, text_wrap=True, bottom=1, bottom_color=T["line"]))
        r += 1
    r += 1
    sec("🗺  MAPA DA PLANILHA — clique no botão para navegar")
    r += 1
    if aut:
        items = [("📊 Painel Geral", "GERAL", "navy", "Visão consolidada: caixa pessoal + negócio, resultado mensal e cobertura do custo de vida."),
                 ("👤 Painel Pessoal", "PAINEL", "teal", "Entradas, saídas, saldo, taxa de poupança, categorias, metas e alertas da vida pessoal."),
                 ("💼 Painel Negócio", "PNEG", "orange", "Receita, despesas, lucro, top clientes, cobranças em atraso e limite do MEI."),
                 ("📝 Lanç. Pessoal", "LANC", "teal", "Registro de entradas e saídas pessoais (tipo automático pela categoria)."),
                 ("💳 Orçamento Pessoal", "ORC", "teal", "Planejado × realizado por categoria, com barras de progresso e alertas."),
                 ("📅 Resumo Pessoal", "RESUMO", "teal", "Quadro anual mês a mês por categoria, com mapa de calor."),
                 ("🎯 Metas", "METAS", "teal", "Objetivos de economia, aporte mensal necessário e reserva de emergência."),
                 ("📝 Lanç. Negócio", "LNEG", "orange", "Despesas e receitas avulsas do negócio (separadas das pessoais)."),
                 ("🤝 Clientes", "CLI", "orange", "Cadastro de clientes com faturamento, recebido, a receber e inadimplência."),
                 ("💰 Recebimentos", "REC", "orange", "Cobranças emitidas: vencimento, data de pagamento e status automático."),
                 ("🧾 Impostos", "IMP", "orange", "DAS do MEI (ou % do Simples), vencimentos, pagamentos e limite anual."),
                 ("📈 Fluxo de Caixa", "FLUXO", "orange", "Caixa do negócio mês a mês: realizado e projetado, com saldo acumulado."),
                 ("⚙ Config", "CONFIG", "navy", "Ano, nome, categorias, formas de pagamento e metas gerais.")]
    else:
        items = [("📊 Painel", "PAINEL", "teal", "Cartões, gráficos e alertas do mês escolhido: entradas, saídas, saldo e poupança."),
                 ("📝 Lançamentos", "LANC", "teal", "Registro de todas as entradas e saídas (tipo automático pela categoria)."),
                 ("💳 Orçamento", "ORC", "teal", "Planejado × realizado por categoria, com barras de progresso e alertas."),
                 ("📅 Resumo Anual", "RESUMO", "teal", "Quadro mês a mês por categoria (entradas e saídas), com mapa de calor."),
                 ("🎯 Metas", "METAS", "teal", "Objetivos de economia, aporte mensal necessário e reserva de emergência."),
                 ("⚙ Config", "CONFIG", "navy", "Ano, nome, categorias, formas de pagamento e meta de poupança.")]
    colors = {"teal": T["teal"], "navy": T["navy"], "orange": T["orange_mid"]}
    for lbl, key, colr, desc in items:
        ws.set_row(r - 1, 26)
        f = B.fmt(bg_color=colors[colr], font_color="#FFFFFF", bold=True, align="center", font_size=10,
                  border=1, border_color="#FFFFFF")
        ws.merge_range(r - 1, 1, r - 1, 3, "", f)
        ws.write_url(r - 1, 1, f"internal:{S(N[key])}!A1", f, lbl)
        B.merge(ws, r, 5, r, 13, desc, B.fmt(bg_color="#FFFFFF", indent=1, text_wrap=True, bottom=1, bottom_color=T["line"], font_size=9))
        r += 1
    r += 1
    sec("🎨  LEGENDA DE CORES")
    r += 1
    ws.set_row(r - 1, 26)
    B.merge(ws, r, 2, r, 3, "Você preenche", B.fmt(bg_color=T["input_bg"], font_color=T["input_fg"], border=1, border_color=T["input_line"], align="center", bold=True))
    B.merge(ws, r, 4, r, 5, "Fórmula (automático)", B.fmt(bg_color="#FFFFFF", border=1, border_color=T["line2"], align="center"))
    B.merge(ws, r, 6, r, 7, "Positivo / bom", B.fmt(bg_color=T["pos_bg"], font_color=T["pos"], align="center", bold=True))
    B.merge(ws, r, 8, r, 9, "Atenção", B.fmt(bg_color=T["warn_bg"], font_color=T["warn"], align="center", bold=True))
    B.merge(ws, r, 10, r, 11, "Negativo / alerta", B.fmt(bg_color=T["neg_bg"], font_color=T["neg"], align="center", bold=True))
    B.merge(ws, r, 12, r, 13, "Informação", B.fmt(bg_color=T["navy_light"], font_color=T["saldo"], align="center", bold=True))
    r += 2
    sec("💡  DICAS IMPORTANTES")
    r += 1
    tips = ["Google Sheets: envie o arquivo .xlsx para o Google Drive e abra com o Google Planilhas (ou Arquivo ▸ Importar). Os menus, gráficos, listas suspensas e cores funcionam igualmente.",
            "Digite sempre valores POSITIVOS. Se a categoria for de entrada, o valor soma; se for de saída, subtrai — o tipo é automático.",
            "Para começar um novo ano: salve uma cópia do arquivo, apague os lançamentos (colunas amarelas) e mude o ano em Config.",
            "Não insira/apague linhas dentro das tabelas de fórmulas. Para ver mais lançamentos, use os filtros do cabeçalho; há espaço para " + str(NLANC) + " linhas.",
            "Cada aba tem botões de navegação no topo. Se algo parecer estranho, confira a faixa de VERIFICAÇÃO no topo de Lançamentos."]
    if aut:
        tips.insert(2, "Retirada do negócio: lance a saída 'Pró-labore / Retirada' em Lanç. Negócio e a entrada 'Pró-labore' em Lanç. Pessoal. Receitas de clientes: lance só em Recebimentos (não duplique).")
        tips.append("Os valores do DAS/MEI e o limite anual são parâmetros editáveis na aba Impostos — confira sempre a legislação vigente no Portal do Simples Nacional. Esta planilha organiza, mas não substitui um contador.")
    for t in tips:
        ws.set_row(r - 1, 36 if len(t) > 150 else 28)
        B.merge(ws, r, 2, r, 13, "•  " + t, B.fmt(bg_color="#FFFFFF", indent=1, text_wrap=True, bottom=1, bottom_color=T["line"], font_size=9))
        r += 1
    r += 1
    B.merge(ws, r, 2, r, 13, "Planilha educativa de organização financeira. Valores e exemplos são fictícios.",
            B.fmt(italic=True, font_size=8, font_color=T["muted"], bg_color=T["bg"], align="center"))
