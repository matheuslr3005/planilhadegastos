"""Contexto compartilhado: nomes de abas, layout (endereços fixos) e helpers de página."""
from lib import *

NLANC = 1500   # linhas pré-formatadas nos lançamentos
NREC = 1000    # linhas em Recebimentos
NCLI = 30      # clientes
NGOAL = 8      # metas
NENT, NSAI, NFORMA = 8, 16, 8
NBENT, NBSAI = 3, 4      # categorias do NEGÓCIO (lista curta): entradas / saídas


class Ctx:
    def __init__(self, kind, demo, book, brand):
        self.kind, self.demo, self.book, self.brand = kind, demo, book, brand
        self.aut = kind == "aut"
        self.fmt = book.fmt
        if self.aut:
            self.N = dict(INICIO="Início", GERAL="Painel Geral", PAINEL="Painel Pessoal", PNEG="Painel Negócio",
                          LANC="Lanç. Pessoal", ORC="Orçamento Pessoal", RESUMO="Resumo Pessoal", METAS="Metas",
                          LNEG="Lanç. Negócio", REC="A Receber", IMP="Impostos",
                          FLUXO="Fluxo de Caixa", CONFIG="Config", DADOS="Dados")
            self.order = ["INICIO", "GERAL", "PAINEL", "PNEG", "LANC", "ORC", "RESUMO", "METAS", "LNEG",
                          "REC", "IMP", "FLUXO", "CONFIG", "DADOS"]
            self.nav_rows = 3
        else:
            self.N = dict(INICIO="Início", PAINEL="Painel", LANC="Lançamentos", ORC="Orçamento",
                          RESUMO="Resumo Anual", METAS="Metas", CONFIG="Config", DADOS="Dados")
            self.order = ["INICIO", "PAINEL", "LANC", "ORC", "RESUMO", "METAS", "CONFIG", "DADOS"]
            self.nav_rows = 1
        self.CS = self.nav_rows + 4          # primeira linha de conteúdo (depois de nav+banner+subtítulo)
        self.ws = {}
        tab = {"INICIO": T["ink"], "GERAL": T["navy"], "PAINEL": T["teal"], "PNEG": T["orange_mid"],
               "LANC": T["teal_mid"], "ORC": T["teal_mid"], "RESUMO": T["teal_mid"], "METAS": T["teal_mid"],
               "LNEG": "#FB923C", "REC": "#FB923C", "IMP": "#FB923C", "FLUXO": "#FB923C",
               "CONFIG": "#94A3B8", "DADOS": "#CBD5E1"}
        if not self.aut:
            tab["PAINEL"] = T["teal"]
        for k in self.order:
            w = book.wb.add_worksheet(self.N[k])
            w.set_tab_color(tab[k])
            self.ws[k] = w
        self._layout()

    # ------------------------------------------------------------ tema
    def theme(self, area):
        if area == "negocio":
            return dict(dark=T["orange"], mid=T["orange_mid"], light=T["orange_light"], banner="#9A3412")
        if area == "geral":
            return dict(dark=T["navy"], mid="#2563EB", light=T["navy_light"], banner=T["navy_dark"])
        return dict(dark=T["teal"], mid=T["teal"], light=T["teal_light"], banner=T["teal_dark"])

    # ------------------------------------------------------------ layout
    def _layout(self):
        CS = self.CS
        L = self.L = {}
        # Config
        L["cfg_ano"], L["cfg_hoje"], L["cfg_nome"] = (CS + 1, 3), (CS + 2, 3), (CS + 3, 3)
        L["cfg_meta"], L["cfg_saldo0"], L["cfg_neg"] = (CS + 4, 3), (CS + 5, 3), (CS + 6, 3)
        LS = L["ls"] = CS
        L["c_ent"], L["c_sai"], L["c_forma"], L["c_mes"], L["c_abrev"] = 5, 7, 9, 11, 12
        L["c_nent"], L["c_nsai"] = 14, 16
        # Dados (blocos pessoais)
        L["d_mpainel"], L["d_morc"], L["d_R"] = (CS + 1, 3), (CS + 2, 3), (CS + 3, 3)
        L["d_nact"], L["d_totsai"], L["d_nover"] = (CS + 4, 3), (CS + 5, 3), (CS + 6, 3)
        L["d_title_don"] = (CS + 7, 3)
        L["d_all_c"], L["d_nall_c"], L["d_all_r0"] = 17, 19, CS + 1   # listas combinadas: Q (pessoal) e S (negócio), 24 linhas
        L["d_cat_r0"] = CS + 11                                  # tabela de categorias (16)
        L["d_rank_r0"] = CS + 11                                 # ranking top 8 (H..L)
        L["d_don_r0"] = CS + 11                                  # rosca (N,O)
        # Lançamentos pessoais
        L["l_hr"] = CS + 3
        L["l_r0"] = CS + 4
        L["l_r1"] = CS + 3 + NLANC
        # Resumo anual (pessoal)
        L["ra_dates"], L["ra_hdr"] = CS, CS + 1
        L["ra_ent0"] = CS + 3
        L["ra_enttot"] = CS + 3 + NENT
        L["ra_sai0"] = CS + 3 + NENT + 2
        L["ra_saitot"] = L["ra_sai0"] + NSAI
        L["ra_saldo"] = L["ra_saitot"] + 1
        L["ra_acum"] = L["ra_saitot"] + 2
        L["ra_taxa"] = L["ra_saitot"] + 3
        # Orçamento
        L["o_sel"] = (CS, 3)
        L["o_hdr"] = CS + 2
        L["o_renda"] = CS + 3
        L["o_c0"] = CS + 5
        L["o_tot"] = CS + 5 + NSAI
        L["o_saldo"] = CS + 6 + NSAI
        # Metas
        L["m_hdr"] = CS
        L["m_r0"] = CS + 1
        # Painel pessoal
        L["p_sel"] = (CS, 4)

        if self.aut:
            self._layout_aut()

    def _layout_aut(self):
        CS, L = self.CS, self.L
        # Recebimentos
        L["r_hr"], L["r_r0"], L["r_r1"] = CS + 3, CS + 4, CS + 3 + NREC
        # Impostos
        L["i_p0"], L["i_hdr"], L["i_r0"], L["i_tot"] = CS + 1, CS + 15, CS + 16, CS + 28
        # Fluxo de caixa
        L["f_prem"] = CS + 1
        L["f_dates"], L["f_hdr"], L["f_sit"], L["f_0"] = CS + 8, CS + 9, CS + 10, CS + 11
        L["f_chart"] = CS + 27
        L["f_detsec"] = CS + 44
        L["f_dethdr"] = CS + 45
        L["f_ent0"] = CS + 47            # NBENT linhas (2 primeiras = faturamento)
        L["f_enttot"] = CS + 47 + NBENT
        L["f_sai0"] = CS + 49 + NBENT    # NBSAI linhas (última = retirada pessoal)
        L["f_saitot"] = CS + 49 + NBENT + NBSAI
        L["f_opex"] = CS + 50 + NBENT + NBSAI
        # seletores dos painéis
        L["pn_sel"], L["pg_sel"] = (CS, 4), (CS, 4)
        # Dados (blocos do negócio)
        b0 = CS + 32
        L["b0"] = b0
        L["d_mneg"], L["d_mger"], L["d_negm"] = (b0 + 1, 3), (b0 + 2, 3), (b0 + 3, 3)
        L["d_btot"], L["d_btitle"] = (b0 + 4, 3), (b0 + 5, 3)
        L["b_cat0"] = b0 + 9
        L["b_orig0"] = b0 + 28
        L["b_atr0"] = b0 + 61
        L["b_serh"] = b0 + 68
        names = ["rec", "desp", "lucro", "sreal", "sproj", "cxp", "cxn", "resp", "prol", "gasp", "neg", "op", "imp", "pro"]
        L["b_ser"] = {n: b0 + 69 + i for i, n in enumerate(names)}
        L["b_dist0"] = b0 + 86

    # ------------------------------------------------------------ referências
    def cfg(self, key):
        r, c = self.L[key]
        return X(self.N["CONFIG"], AA(r, c))

    def cfg_list(self, ckey, n):
        c = self.L[ckey]
        r0 = self.L["ls"] + 1
        return X(self.N["CONFIG"], RNG(r0, c, r0 + n - 1, c))

    def cfg_item(self, ckey, i):  # i: 0-based
        return X(self.N["CONFIG"], AA(self.L["ls"] + 1 + i, self.L[ckey]))

    def dados(self, key):
        r, c = self.L[key]
        return X(self.N["DADOS"], AA(r, c))

    # ------------------------------------------------------------ página padrão
    def nav_spec(self):
        N = self.N
        if not self.aut:
            items = [(lbl, N[k]) for lbl, k in [("🏠 Início", "INICIO"), ("📊 Painel", "PAINEL"),
                                                 ("📝 Lançamentos", "LANC"), ("💳 Orçamento", "ORC"),
                                                 ("📅 Resumo Anual", "RESUMO"), ("🎯 Metas", "METAS"),
                                                 ("⚙ Config", "CONFIG")]]
            return [dict(color=T["teal_dark"], items=items)]
        g = [("🏠 Início", "INICIO"), ("📊 Painel Geral", "GERAL"), ("👤 Painel Pessoal", "PAINEL"),
             ("💼 Painel Negócio", "PNEG"), ("⚙ Config", "CONFIG")]
        p = [("📝 Lançamentos", "LANC"), ("💳 Orçamento", "ORC"), ("📅 Resumo anual", "RESUMO"), ("🎯 Metas", "METAS")]
        b = [("📝 Lançamentos", "LNEG"), ("💰 A Receber", "REC"),
             ("🧾 Impostos", "IMP"), ("📈 Fluxo de Caixa", "FLUXO")]
        return [dict(color=T["navy"], items=[(l, N[k]) for l, k in g]),
                dict(color=T["teal"], tag="PESSOAL", items=[(l, N[k]) for l, k in p]),
                dict(color=T["orange_mid"], tag="NEGÓCIO", items=[(l, N[k]) for l, k in b])]

    def page(self, key, widths, title, subtitle, area="pessoal", bg=False, landscape=True, nav=True, one_page=False):
        """Configura colunas, nav, banner. widths = larguras das colunas B.. (A é margem de 2)."""
        ws, book = self.ws[key], self.book
        th = self.theme(area)
        ws.hide_gridlines(2)
        ws.set_default_row(16.5)
        bgf = book.fmt(bg_color=T["bg"]) if bg else None
        ncols = len(widths)
        ws.set_column(0, 0, 2, bgf)
        for i, w in enumerate(widths):
            ws.set_column(i + 1, i + 1, w, bgf)
        if bg:
            ws.set_column(ncols + 1, ncols + 25, 9, bgf)
        if nav:
            nav_bar(book, ws, widths, self.nav_spec(), self.N[key])
        r_sp = self.nav_rows + 1
        ws.set_row(r_sp - 1, 6)
        r_b = self.nav_rows + 2
        ws.set_row(r_b - 1, 38)
        fb = book.fmt(bg_color=th["banner"], font_color="#FFFFFF", bold=True, font_size=17, indent=1)
        book.merge(ws, r_b, 2, r_b, ncols + 1, title, fb)
        r_s = self.nav_rows + 3
        ws.set_row(r_s - 1, 20)
        fs = book.fmt(font_color=T["muted"], italic=True, font_size=9, indent=1,
                      bg_color=T["bg"] if bg else "#FFFFFF")
        book.merge(ws, r_s, 2, r_s, ncols + 1, subtitle, fs)
        if landscape:
            ws.set_landscape()
        ws.set_paper(9)
        ws.fit_to_pages(1, 1 if one_page else 0)
        ws.set_margins(0.4, 0.4, 0.5, 0.5)
        return self.CS

    # ------------------------------------------------------------ estilos reutilizáveis
    def f_section(self, th, **kw):
        return self.fmt(bg_color=th["mid"], font_color="#FFFFFF", bold=True, font_size=10, indent=1, **kw)

    def f_head(self, th, align="center", **kw):
        return self.fmt(bg_color=th["light"], font_color=th["dark"], bold=True, align=align, text_wrap=True,
                        bottom=2, bottom_color=th["mid"], **kw)

    def f_input(self, num=None, align=None, **kw):
        d = dict(bg_color=T["input_bg"], font_color=T["input_fg"], border=1, border_color=T["input_line"])
        if num:
            d["num_format"] = num
        if align:
            d["align"] = align
        d.update(kw)
        return self.fmt(**d)

    def f_calc(self, num=None, align=None, bold=False, **kw):
        d = dict(bottom=1, bottom_color=T["line"])
        if num:
            d["num_format"] = num
        if align:
            d["align"] = align
        if bold:
            d["bold"] = True
        d.update(kw)
        return self.fmt(**d)
