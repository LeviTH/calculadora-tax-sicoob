import streamlit as st

st.set_page_config(page_title="Calculadora de Taxas", layout="centered")

# ======= Estilo e Título =======
st.markdown("""
    <style>
        .stButton button {
            background-color: #00b894;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            height: 3em;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>💳 Calculadora de Taxas da Maquininha</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Informe quanto deseja receber e descubra quanto deve cobrar do cliente.</p>", unsafe_allow_html=True)

# ======= Tabela de taxas reais =======
taxas_recebimento = {
    "Débito à vista": 0.97,
    "Crédito à vista": 0.95361,
    "Crédito 2x": 0.94541,
    "Crédito 3x": 0.93721,
    "Crédito 4x": 0.92902,
    "Crédito 5x": 0.92082,
    "Crédito 6x": 0.91262,
    "Crédito 7x": 0.90443,
    "Crédito 8x": 0.89623,
    "Crédito 9x": 0.88804,
    "Crédito 10x": 0.87984,
    "Crédito 11x": 0.87164,
    "Crédito 12x": 0.86345,
}

# ======= Entradas do usuário =======
valor_liquido = st.number_input("💰 Valor que deseja receber (R$):", min_value=0.0, format="%.2f")
opcao_pagamento = st.selectbox("💳 Forma de pagamento:", list(taxas_recebimento.keys()))

# ======= Cálculo e resultado =======
def calcular_valor_bruto(valor_liquido, fator_recebimento):
    if fator_recebimento == 0:
        return None
    return valor_liquido / fator_recebimento

if st.button("🧮 Calcular valor a cobrar"):
    fator = taxas_recebimento[opcao_pagamento]
    valor_bruto = calcular_valor_bruto(valor_liquido, fator)

    if valor_bruto:
        st.success(f"Você deve cobrar: R$ {valor_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.markdown(f"<p style='text-align: center; color: gray;'>Com a opção '{opcao_pagamento}' você receberá exatamente R$ {valor_liquido:,.2f}</p>".replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

        # Mostrar parcelas se for crédito parcelado
        if "Crédito" in opcao_pagamento:
            parcelas = 1
            if "à vista" in opcao_pagamento:
                parcelas = 1
            else:
                parcelas = int(opcao_pagamento.split()[1].replace("x", ""))

            valor_parcela = valor_bruto / parcelas
            if parcelas > 1:
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px;">
                        📌 O cliente pagará {parcelas} parcelas de <strong>R$ {valor_parcela:,.2f}</strong> (total <strong>R$ {valor_bruto:,.2f}</strong>)
                    </div>
                """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>📌 Pagamento à vista de <strong>R$ {valor_bruto:,.2f}</strong></div>".replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
    else:
        st.error("Erro no cálculo. Verifique os valores.")
