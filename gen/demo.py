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
            add(m, 5, "Pró-labore do mês", ent[0], "Transferência", 4500)
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


# ---------------------------------------------------------------- negócio (autônomo)
CLIENTES = [
    ("Studio Aurora", "Camila Prado", "camila@studioaurora.com.br", "Indicação"),
    ("Clínica Vida Plena", "Dr. Rafael Nunes", "(11) 98877-1020", "Instagram"),
    ("Padaria Dois Irmãos", "Seu Antônio", "(11) 3344-2211", "Indicação"),
    ("Tech Nova Ltda", "Bianca Torres", "bianca@technova.com", "LinkedIn"),
    ("Escola Horizonte", "Coord. Marta", "marta@escolahorizonte.edu.br", "Site"),
    ("Loja Bella Moda", "Juliana Reis", "(21) 99120-4455", "Instagram"),
    ("Café do Centro", "Paulo Menezes", "(11) 97766-3300", "Indicação"),
    ("Maria Oliveira (PF)", "Maria Oliveira", "maria.oliveira@email.com", "Indicação"),
]


def business_rows(year=2026, months=9, seed=11):
    """Retorna (recebimentos, lançamentos do negócio, impostos_pagos) fictícios."""
    rnd = random.Random(seed)
    rec, lan = [], []
    ref = D(year, 9, 30)

    def receb(emissao, cliente, desc, valor, venc_dias=15, atraso=None, pago=True, forma="Pix"):
        venc = emissao + dt.timedelta(days=venc_dias)
        if pago:
            pg = venc + dt.timedelta(days=atraso if atraso is not None else rnd.choice([-3, -1, 0, 0, 2, 5]))
            pg = min(pg, ref)
        else:
            pg = None
        rec.append((emissao, cliente, desc, round(valor, 2), venc, pg, forma))

    for m in range(1, months + 1):
        # contratos mensais
        receb(D(year, m, 3), "Studio Aurora", f"Gestão de redes sociais – {m:02d}/{year}", 1800, 10)
        receb(D(year, m, 5), "Clínica Vida Plena", f"Pacote de conteúdo mensal – {m:02d}/{year}", 1500, 10)
        if m >= 3:
            receb(D(year, m, 8), "Padaria Dois Irmãos", f"Materiais e cardápio – {m:02d}/{year}", 650, 10)
    # projetos avulsos
    projs = [(1, 14, "Tech Nova Ltda", "Identidade visual completa", 3200),
             (2, 20, "Loja Bella Moda", "Catálogo digital", 1850),
             (3, 12, "Maria Oliveira (PF)", "Logotipo e cartão de visita", 780),
             (4, 9, "Escola Horizonte", "Redesenho do material de matrícula", 2400),
             (4, 28, "Café do Centro", "Cardápio e placas", 950),
             (5, 15, "Tech Nova Ltda", "Landing page", 2600),
             (6, 6, "Loja Bella Moda", "Campanha Dia dos Namorados", 1900),
             (6, 25, "Escola Horizonte", "Posts de volta às aulas", 1200),
             (7, 10, "Café do Centro", "Fotos e arte para delivery", 1100),
             (7, 22, "Tech Nova Ltda", "Apresentação institucional", 1700),
             (8, 4, "Loja Bella Moda", "Campanha Dia dos Pais", 1650),
             (8, 18, "Escola Horizonte", "Site institucional – 1ª parcela", 2200),
             (9, 2, "Escola Horizonte", "Site institucional – 2ª parcela", 2200),
             (9, 9, "Maria Oliveira (PF)", "Identidade para consultório", 1500)]
    for m, d, cli, desc, val in projs:
        receb(D(year, m, d), cli, desc, val, 15)
    # pendências / atrasos (referência: 30/09)
    receb(D(year, 9, 3), "Studio Aurora", "Gestão de redes sociais – 09/2026", 1800, 10, pago=False)   # vencida
    rec[:] = [r for r in rec if not (r[1] == "Studio Aurora" and "09/2026" in r[2] and r[5] is not None)]
    receb(D(year, 9, 5), "Clínica Vida Plena", "Pacote de conteúdo mensal – 09/2026", 1500, 10, pago=False)  # vencida
    rec[:] = [r for r in rec if not (r[1] == "Clínica Vida Plena" and "09/2026" in r[2] and r[5] is not None)]
    receb(D(year, 9, 8), "Padaria Dois Irmãos", "Materiais e cardápio – 09/2026", 650, 10, pago=False)  # vencida
    rec[:] = [r for r in rec if not (r[1] == "Padaria Dois Irmãos" and "09/2026" in r[2] and r[5] is not None)]
    receb(D(year, 9, 24), "Tech Nova Ltda", "Manutenção da landing page", 900, 20, pago=False)         # a vencer
    receb(D(year, 9, 28), "Loja Bella Moda", "Campanha Black Friday (sinal)", 1400, 25, pago=False)    # a vencer
    # atraso mais antigo
    receb(D(year, 8, 12), "Café do Centro", "Reimpressão de materiais", 480, 15, pago=False)
    rec.sort(key=lambda r: r[0])

    # lançamentos do negócio
    N_ = NSAI_L
    for m in range(1, months + 1):
        lan.append((D(year, m, 5), "Retirada de pró-labore", N_[0], "Transferência", 4500, "", "Vai para Pessoal"))
        lan.append((D(year, m, 2), "Adobe Creative Cloud", N_[2], "Cartão de crédito", 124.0, "", ""))
        lan.append((D(year, m, 2), "Canva Pro", N_[2], "Cartão de crédito", 34.9, "", ""))
        lan.append((D(year, m, 12), "Hospedagem e domínio", N_[2], "Cartão de crédito", 59.9, "", ""))
        lan.append((D(year, m, 10), "Coworking", N_[7], "Boleto", 450.0, "", ""))
        lan.append((D(year, m, 15), "Internet e celular (parte profissional)", N_[8], "Débito automático", 140.0, "", ""))
        lan.append((D(year, m, 28), "Tarifas bancárias e maquininha", N_[10], "Débito automático", round(rnd.uniform(25, 48), 2), "", ""))
        lan.append((D(year, m, 16), "Anúncios (Meta Ads)", N_[3], "Cartão de crédito", round(rnd.uniform(150, 360), 2), "", ""))
        lan.append((D(year, m, 21), "Transporte a clientes", N_[5], "Cartão de crédito", round(rnd.uniform(60, 190), 2), "", ""))
        if m in (2, 5, 8):
            lan.append((D(year, m, 18), "Almoço com cliente", N_[6], "Cartão de crédito", round(rnd.uniform(70, 140), 2), "", ""))
        if m in (4, 9):
            lan.append((D(year, m, 9), "Curso de especialização", N_[11], "Cartão de crédito", 320.0, "", ""))
        if m == 6:
            lan.append((D(year, m, 14), "Monitor 27\" 4K", N_[4], "Cartão de crédito", 1480.0, "", "Equipamento"))
        if m in (3, 7):
            lan.append((D(year, m, 22), "Freelancer de motion design", N_[13], "Pix", 600.0, "", ""))
        if m == 1:
            lan.append((D(year, m, 20), "Seguro de equipamentos", N_[14], "Cartão de crédito", 380.0, "", ""))
        if m in (2, 6, 9):
            lan.append((D(year, m, 27), "Receita avulsa – venda de templates", NENT_L[0], "Pix", round(rnd.uniform(180, 420), 2), "", ""))
    lan.sort(key=lambda r: (r[0], r[1]))
    return rec, lan
