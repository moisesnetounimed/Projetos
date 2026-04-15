from __future__ import annotations

# =========================================================
# MENUS (nível 1 - sidebar principal)
# =========================================================
MENU_CONTABILIDADE = "contabilidade"
MENU_FINANCEIRO = "financeiro"
MENU_OPERACOES = "operacoes"


# =========================================================
# MÓDULOS (nível 2 - agrupadores)
# =========================================================
MOD_CONTABIL_REINF = "reinf"
MOD_CONTABIL_CP = "cp_contabil"

MOD_FINANCEIRO_CP = "cp_financeiro"
MOD_FINANCEIRO_CR = "cr_financeiro"

MOD_OPER_CONTAS_MEDICAS = "contasmedicas"
MOD_OPER_CADASTRO = "cadastro"
MOD_OPER_COOPERADO = "casadocooperado"


# =========================================================
# SUBMÓDULOS (nível 3 - ações reais)
# =========================================================

# ---- CONTABILIDADE / REINF
SUBMOD_CONTABIL_EXECUTAR_REINF = "executarreinf"
SUBMOD_CONTABIL_EXCLUIR_REINF = "excluirduplicadosreinf"

# ---- CONTABILIDADE / CONTAS A PAGAR
SUBMOD_CONTABIL_VENCIMENTO_IMPOSTO = "alterardatavencimentoimposto"

# ---- FINANCEIRO / CONTAS A PAGAR
SUBMOD_FINANCEIRO_CP_RATEIO = "ajustarrateio"

# ---- FINANCEIRO / CONTAS A RECEBER
SUBMOD_FINANCEIRO_CR_SUSPENDER = "suspenderdescontousuario"

# ---- OPERAÇÕES / CONTAS MÉDICAS
SUBMOD_OPER_CONTA_MEDICA = "alterarcontamedica"

# ---- OPERAÇÕES / CADASTRO
SUBMOD_OPER_IMPORT_LAYOUT = "importalayoutempresa"
SUBMOD_OPER_ALTERAR_FLAG = "alterarflagcadbenef"

# ---- OPERAÇÕES / CASA DO COOPERADO
SUBMOD_OPER_EVENTOS = "importaeventoprestador"
SUBMOD_OPER_HORAS = "importarhorasmedicas"

