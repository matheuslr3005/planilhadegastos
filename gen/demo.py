"""Dados fictícios (determinísticos) para a versão de demonstração."""
import random
import datetime as dt
from personal import ENT_PF, ENT_AUT, SAI, NENT_L, NSAI_L

D = dt.date


def _clamp_day(y, m, d):
    import calendar
    return D(y, m, min(d, calendar.monthrange(y, m)[1]))


def personal_rows(aut=False, seed=7, months=9, year=2026):
    """Lançamentos pessoais. aut=True: renda = pró-labore do negócio e gastos de uma pessoa só."""
    rnd = random.Random(seed + (100 if aut else 0))
    ent = ENT_AUT if aut else ENT_PF
    s = SAI
    k = 0.62 if aut else 1.0                       # escala de gastos
    rows = []

    def add(m, d, desc, cat, forma, valor, meta="", obs=""):
        rows.append((_clamp_day(year, m, d), desc, cat, forma, round(valor, 2), meta, obs))

    def jit(base, pct=0.12):
        return base * (1 + rnd.uniform(-pct, pct))

    for m in range(1, months + 1):
        # ---------------- entradas
        if aut:
            add(m, 5, "Pró-labore (retirada do negócio)", ent[0], "Transferência", 3400)
            add(m, 10, "Salário / renda fixa (cônjuge)", ent[1], "Transferência", 1100)
            if m in (3, 6):
                add(m, 20, "Restituição / reembolso", ent[4], "Pix", jit(380))
            add(m, 28, "Rendimento da poupança", ent[3], "Transferência", jit(55, .3))
        else:
            add(m, 5, "Salário empresa", ent[0], "Transferência", 9500)
            if m in (2, 4, 6, 8):
                add(m, 18, "Projeto freelance", ent[1], "Pix", jit(650, .4))
            if m == 3:
                add(m, 15, "Bônus de desempenho", ent[3], "Transferência", 1400)
            add(m, 28, "Rendimento da poupança", ent[2], "Transferência", jit(80, .25))
        # ---------------- moradia e contas
        add(m, 10, "Aluguel", s[0], "Boleto", 950 if aut else 1800)
        add(m, 10, "Condomínio", s[0], "Boleto", 150 if aut else 350)
        add(m, 15, "Conta de luz", s[1], "Débito automático", jit(190 * (0.7 if aut else 1), .25))
        add(m, 12, "Conta de água", s[1], "Débito automático", jit(95 * (0.7 if aut else 1), .15))
        add(m, 8, "Internet fibra", s[1], "Débito automático", 119.90)
        if m in (2, 5, 8):
            add(m, 20, "Botijão de gás", s[1], "Pix", 112)
        # ---------------- alimentação
        for d in (3, 10, 17, 24)[: 3 if aut else 4]:
            add(m, d, "Supermercado", s[2], "Cartão de crédito", jit(165 if aut else 360, .25))
        for d in (6, 14, 22)[: 2 if aut else 3]:
            add(m, d, "Padaria / hortifruti", s[2], "Pix", jit(45 if aut else 65, .4))
        for d in (9, 19, 27)[: 2 if aut else 3]:
            add(m, d, "Delivery", s[2], "Cartão de débito", jit(55 if aut else 68, .3))
        # ---------------- transporte
        for d in (4, 14, 24)[: 1 if aut else 3]:
            add(m, d, "Combustível", s[3], "Cartão de crédito", jit(190 if aut else 205, .12))
        for d in (7, 16, 26):
            add(m, d, "App de transporte", s[3], "Cartão de crédito", jit(28, .4))
        if m == 4:
            add(m, 12, "Revisão do carro", s[3], "Cartão de crédito", 680)
        if m == 8:
            add(m, 12, "Pneus", s[3], "Cartão de crédito", 420)
        # ---------------- saúde / educação
        add(m, 10, "Plano de saúde", s[4], "Débito automático", 180 if aut else 480)
        add(m, 21, "Farmácia", s[4], "Cartão de débito", jit(55 if aut else 85, .5))
        if m in (3, 7):
            add(m, 16, "Consulta médica", s[4], "Pix", 250)
        add(m, 15, "Curso de inglês" if not aut else "Curso online", s[5], "Cartão de crédito", 290 if not aut else 149)
        # ---------------- lazer
        for d in (8, 20, 28)[: 2 if aut else 3]:
            add(m, d, "Restaurante / bar", s[6], "Cartão de crédito", jit(70 if aut else 145, .35))
        add(m, 13, "Cinema / show", s[6], "Cartão de débito", jit(55 if aut else 75, .4))
        if m == 7:
            add(m, 18, "Viagem de férias (hotel e passagens)", s[6], "Cartão de crédito", 2800 * (0.45 if aut else 1))
        if m == 5:
            add(m, 24, "Aniversário", s[6], "Cartão de crédito", 320)
        # ---------------- vestuário / assinaturas / cuidados
        if m in (2, 5, 7, 9):
            add(m, 22, "Roupas", s[7], "Cartão de crédito", jit(260 * k, .4))
        add(m, 6, "Netflix", s[8], "Cartão de crédito", 55.90)
        add(m, 6, "Spotify", s[8], "Cartão de crédito", 21.90)
        add(m, 6, "Armazenamento na nuvem", s[8], "Cartão de crédito", 9.90)
        add(m, 3, "Academia", s[9], "Débito automático", 119.90)
        add(m, 18, "Salão / barbearia", s[9], "Pix", jit(70, .3))
        if not aut:
            add(m, 20, "Ração e petshop", s[10], "Pix", jit(155, .15))
            if m == 6:
                add(m, 9, "Veterinário", s[10], "Pix", 280)
        # ---------------- presentes, dívidas, impostos, outros
        if m == 5:
            add(m, 8, "Presente Dia das Mães", s[11], "Cartão de crédito", 250 * k)
        if m == 8:
            add(m, 9, "Presente Dia dos Pais", s[11], "Cartão de crédito", 180 * k)
        add(m, 25, "Doação mensal", s[11], "Pix", 50)
        if not aut and m <= 8:
            add(m, 25, "Parcela do financiamento", s[12], "Boleto", 450)
        if m == 2:
            add(m, 12, "IPVA", s[14], "Boleto", 880 * (0.8 if aut else 1))
        add(m, 19, "Despesas diversas", s[15], "Dinheiro", jit(70, .6))
        # ---------------- reserva e metas (aportes)
        if aut:
            add(m, 6, "Aporte reserva de emergência", s[13], "Pix", 300, meta="Reserva de emergência")
            add(m, 6, "Aporte reserva para impostos", s[13], "Pix", 150, meta="Reserva para impostos")
            if m >= 4:
                add(m, 6, "Aporte viagem", s[13], "Pix", 150, meta="Viagem de férias")
        else:
            add(m, 6, "Aporte reserva de emergência", s[13], "Pix", 700, meta="Reserva de emergência")
            if m <= 6:
                add(m, 6, "Aporte viagem", s[13], "Pix", 300, meta="Viagem de férias")
            if m >= 5:
                add(m, 6, "Aporte notebook", s[13], "Pix", 400, meta="Notebook novo")
            add(m, 6, "Aporte curso", s[13], "Pix", 250, meta="Curso de especialização")
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


# ---------------------------------------------------------------- negócio (MEI que vende produtos e serviços)
def business_rows(year=2026, months=9, seed=11):
    """Retorna (A Receber, lançamentos do negócio) fictícios — uma lojinha de acessórios e presentes."""
    rnd = random.Random(seed)
    rec, lan = [], []
    ref = D(year, 9, 30)

    def receb(emissao, cliente, desc, valor, venc_dias=15, pago=True, atraso=None, forma="Pix"):
        venc = emissao + dt.timedelta(days=venc_dias)
        pg = None
        if pago:
            pg = min(venc + dt.timedelta(days=atraso if atraso is not None else rnd.choice([-3, -1, 0, 0, 2, 5])), ref)
        rec.append((emissao, cliente, desc, round(valor, 2), venc, pg, forma))

    pedidos = [(1, 14, "Tech Nova Ltda", "Kits de brindes corporativos", 1900),
               (2, 9, "Escola Aurora", "Material de volta às aulas", 1650),
               (3, 12, "Maria Oliveira (PF)", "Encomenda de presentes", 780),
               (3, 28, "Café do Centro", "Lembrancinhas de evento", 950),
               (4, 15, "Tech Nova Ltda", "Brindes — reposição", 1400),
               (5, 6, "Clínica Vida Plena", "Kits de boas-vindas", 1200),
               (5, 22, "Loja Bella Moda", "Revenda de acessórios", 1500),
               (6, 10, "Escola Aurora", "Lembranças de formatura", 2100),
               (7, 8, "Café do Centro", "Cestas para clientes", 1100),
               (7, 24, "Tech Nova Ltda", "Brindes semestrais", 1700),
               (8, 4, "Loja Bella Moda", "Revenda — Dia dos Pais", 1650),
               (8, 19, "Escola Aurora", "Kits Dia do Professor", 1200),
               (9, 2, "Escola Aurora", "Pedido de setembro", 1300),
               (9, 9, "Maria Oliveira (PF)", "Presentes corporativos", 1500)]
    for m, dd, cli, desc, val in pedidos:
        receb(D(year, m, dd), cli, desc, val, 15)
    receb(D(year, 8, 12), "Café do Centro", "Cestas (reposição)", 480, 15, pago=False)            # atrasada há 34 dias
    receb(D(year, 9, 3), "Tech Nova Ltda", "Brindes de setembro", 1800, 10, pago=False)             # atrasada
    receb(D(year, 9, 6), "Loja Bella Moda", "Pedido de setembro", 1500, 10, pago=False)             # atrasada
    receb(D(year, 9, 24), "Clínica Vida Plena", "Kits de outubro", 900, 20, pago=False)             # a vencer
    receb(D(year, 9, 28), "Loja Bella Moda", "Pedido Black Friday (sinal)", 1400, 25, pago=False)   # a vencer
    rec.sort(key=lambda r: r[0])

    V, MEN, OUT = NENT_L
    COMP, DESP, IMPT, RET = NSAI_L
    for m in range(1, months + 1):
        for d_ in (7, 14, 21, 28):
            lan.append((D(year, m, d_), "Vendas da semana (balcão, Pix e cartão)", V, "Pix", round(rnd.uniform(600, 950), 2), "", ""))
        lan.append((D(year, m, 5), "Mensalidade — Escola Aurora (kits)", MEN, "Pix", 650.0, "Escola Aurora", ""))
        lan.append((D(year, m, 8), "Mensalidade — Clínica Vida Plena (brindes)", MEN, "Pix", 450.0, "Clínica Vida Plena", ""))
        lan.append((D(year, m, 3), "Reposição de mercadoria — Fornecedor Alfa", COMP, "Boleto", round(rnd.uniform(650, 800), 2), "", ""))
        lan.append((D(year, m, 17), "Reposição de mercadoria — Fornecedor Beta", COMP, "Boleto", round(rnd.uniform(600, 780), 2), "", ""))
        lan.append((D(year, m, 10), "Aluguel do ponto", DESP, "Boleto", 450.0, "", ""))
        lan.append((D(year, m, 12), "Internet e celular", DESP, "Débito automático", 140.0, "", ""))
        lan.append((D(year, m, 16), "Anúncios no Instagram", DESP, "Cartão de crédito", round(rnd.uniform(150, 260), 2), "", ""))
        lan.append((D(year, m, 20), "Frete e entregas", DESP, "Pix", round(rnd.uniform(90, 180), 2), "", ""))
        lan.append((D(year, m, 22), "Embalagens", DESP, "Pix", round(rnd.uniform(80, 140), 2), "", ""))
        lan.append((D(year, m, 27), "Tarifas e maquininha", DESP, "Débito automático", round(rnd.uniform(45, 80), 2), "", ""))
        lan.append((D(year, m, 5), "Retirada pessoal", RET, "Transferência", 3400.0, "", "Vai para Pessoal"))
        if m == 3:
            lan.append((D(year, m, 18), "Taxa de alvará", IMPT, "Boleto", 180.0, "", ""))
        if m == 4:
            lan.append((D(year, m, 9), "Reembolso de fornecedor", OUT, "Pix", 120.0, "", ""))
        if m == 6:
            lan.append((D(year, m, 14), "Expositor novo para a loja", DESP, "Cartão de crédito", 650.0, "", "Equipamento"))
    lan.sort(key=lambda r: (r[0], r[1]))
    return rec, lan
