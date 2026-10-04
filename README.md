# Finanças em Dia — planilhas financeiras (Excel + Google Sheets)

Produto digital em **duas versões**, cada uma em **2 arquivos** (em branco e com dados de exemplo):

| Arquivo (`dist/`) | Para quem | Abas |
|---|---|---|
| `Financas-em-Dia_Pessoal_EM-BRANCO.xlsx` / `_COM-EXEMPLO.xlsx` | Pessoa física (finanças domésticas) | Início · Painel · Lançamentos · Orçamento · Resumo Anual · Metas · Config · Dados |
| `Financas-em-Dia_Autonomo-MEI_EM-BRANCO.xlsx` / `_COM-EXEMPLO.xlsx` | Autônomos e MEI (pessoal **e** negócio separados) | Início · Painel Geral · Painel Pessoal · Painel Negócio · Lanç. Pessoal · Orçamento Pessoal · Resumo Pessoal · Metas · Lanç. Negócio · Clientes · Recebimentos · Impostos · Fluxo de Caixa · Config · Dados |

> **Nome "Finanças em Dia" é provisório** — troque em `gen/build.py` (`BRAND`) e regenere.
> O arquivo **COM-EXEMPLO** é ótimo para a página de venda e para o comprador entender; o **EM-BRANCO** é o que ele usa de verdade.
> Prévias dos painéis (renderizadas no LibreOffice, ficam um pouco diferentes no Excel/Sheets): `previews/`.

## O que cada versão entrega

**Pessoal** — registro de entradas e saídas (categoria em menu suspenso; o *tipo* Entrada/Saída é automático), 16 categorias de saída
(Moradia, Alimentação, Transporte, Lazer…) e 8 de entrada, **todas renomeáveis** em `Config`; resumo anual mês × categoria com mapa de calor;
orçamento planejado × realizado com barras de progresso e alertas; **metas de economia** (aporte mensal necessário, situação, reserva de
emergência ideal); **painel** com seletor de mês, 6 cartões (com variação vs mês anterior), 4 gráficos dinâmicos, metas e alertas.

**Autônomo** — tudo do Pessoal **+** separação Pessoal × Negócio (abas e categorias próprias), **Clientes** (faturado, recebido,
a receber, em atraso, concentração), **Recebimentos** (vencimento, pagamento, status automático Pago/Pendente/Atrasado, dias de atraso),
**Impostos** (DAS do MEI calculado por atividade, ou % para Simples/outro; vencimento dia 20; status; **limite anual do MEI** com
projeção e alerta de 80%/100%) e **Fluxo de Caixa** do negócio mês a mês — **realizado** até o mês de hoje e **projetado** depois (a receber em aberto,
DAS em aberto, média de despesas, pró-labore e receita nova previstos). Três painéis: Geral (consolidado), Pessoal e Negócio.

Recursos de UX: botões de navegação (hiperlinks internos) no topo de todas as abas · listas suspensas · formatação condicional
(verde/vermelho/amarelo para saldos, status e alertas) · faixa de **verificação automática** nos lançamentos · células amarelas = você preenche.

## Compatibilidade — decisões de projeto

Só funções clássicas (`SUMIFS`, `INDEX/MATCH`, `LARGE`, `COUNTIFS`, `SUMPRODUCT`, `EDATE`, `IFERROR`, `REPT`…): nada de
`XLOOKUP`, `FILTER`, `SORT`, macros/VBA, tabelas dinâmicas ou segmentações (não funcionam no Google Sheets). Gráficos são nativos
(colunas, linhas, áreas, barras, rosca, combinados), alimentados por fórmulas → atualizam sozinhos. Arquivo `.xlsx` abre no Excel (Windows/Mac/web) e
no Google Sheets (envie para o Drive → *Abrir com Planilhas Google*).

## Como foi validado

* **Fórmulas**: `python gen/build.py` recalcula cada arquivo no LibreOffice → **0 erros** nas ~2.350 (Pessoal) e ~10.300 (Autônomo) fórmulas.
* **Números**: `python gen/tools/verify.py` recalcula tudo de forma independente em Python a partir dos dados de exemplo e compara
  (totais mensais, saldo acumulado, taxa de poupança, metas, status dos recebimentos, DAS, limite MEI, saldo do fluxo realizado **e projetado**) → **tudo confere**.
* **Interatividade**: `python gen/tools/scenarios.py` altera entradas (mês do painel, regime tributário, ano, novo lançamento, pagamento de cobrança,
  renomear categoria), recalcula e confere o resultado.
* **Não testado aqui**: abertura em Excel e Google Sheets reais (o ambiente de desenvolvimento só tem LibreOffice). **Antes de vender, abra cada arquivo no Excel e
  no Google Sheets e confira** principalmente: aparência dos gráficos (o Sheets recria os gráficos ao importar — títulos ligados a células e eixo invertido das barras podem variar),
  e os botões de navegação.

## Premissas que você deve manter atualizadas

* **DAS-MEI 2026**: salário mínimo R$ 1.621 → INSS 5% = R$ 81,05 + ICMS R$ 1,00 e/ou ISS R$ 5,00 fixos. **Limite anual R$ 81.000** (proporcional ao mês de início).
  Tudo é editável na aba *Impostos*; confirme a cada ano no Portal do Simples Nacional. A planilha organiza, **não substitui um contador** (aviso presente na aba).
* Renomear categoria **depois** de lançar deixa lançamentos antigos como "Verificar" (a faixa de verificação avisa; use Localizar e Substituir). Aviso presente em *Config*.
* "Reserva e Metas" (14ª categoria de saída) é tratada como **poupança** no cálculo da taxa de poupança; a 1ª categoria de saída do negócio é o **pró-labore** (lance a
  retirada nas duas pontas) e a 1ª de entrada do negócio conta como **faturamento**.

## Regenerar os arquivos

```bash
pip install xlsxwriter openpyxl           # + LibreOffice Calc (apt: libreoffice-calc) para recalcular e gravar valores em cache
python gen/build.py                        # gera os 4 arquivos em dist/ (ou: pf-blank | pf-demo | aut-blank | aut-demo)
python gen/tools/verify.py                 # confere números dos exemplos
python gen/tools/scenarios.py              # testes de interatividade
python gen/tools/preview.py dist/ARQUIVO.xlsx "texto do título da aba"   # PNG da aba (LibreOffice)
```

Estrutura: `gen/lib.py` (tema, navegação, gráficos) · `gen/ctx.py` (layout/endereços) · `gen/personal.py` (Config, Dados, Lançamentos, Resumo, Orçamento, Metas) ·
`gen/painel.py` · `gen/business.py` (Recebimentos, Clientes, Impostos, Fluxo, painéis do negócio) · `gen/intro.py` (Início) · `gen/demo.py` (dados fictícios).
