import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# --- Lógica de Cálculo das Taxas ---
# Mapeamento das porcentagens que o vendedor RECEBE do valor COBRADO
# Key: modalidade ou número de parcelas
# Value: porcentagem que o vendedor recebe (em decimal)
TAXAS = {
    'debito_vista': 0.97,
    'credito_vista': 0.95361,
    'credito_2x': 0.94541,
    'credito_3x': 0.93721,
    'credito_4x': 0.92902,
    'credito_5x': 0.92082,
    'credito_6x': 0.91262,
    'credito_7x': 0.90443,
    'credito_8x': 0.89623,
    'credito_9x': 0.88804,
    'credito_10x': 0.87984,
    'credito_11x': 0.87164,
    'credito_12x': 0.86345,
}

def calcular_valor(valor_desejado, modalidade, num_parcelas=None):
    """
    Calcula o valor que deve ser cobrado do cliente.
    Retorna o valor a cobrar e a porcentagem que você recebe.
    """
    porcentagem_recebida = 0.0
    modalidade_texto = ""

    if modalidade == 'debito_vista':
        porcentagem_recebida = TAXAS['debito_vista']
        modalidade_texto = "Débito à vista"
    elif modalidade == 'credito_vista':
        porcentagem_recebida = TAXAS['credito_vista']
        modalidade_texto = "Crédito à vista"
    elif modalidade == 'credito_parcelado':
        if num_parcelas is not None and 2 <= num_parcelas <= 12:
            chave_parcela = f'credito_{num_parcelas}x'
            if chave_parcela in TAXAS:
                porcentagem_recebida = TAXAS[chave_parcela]
                modalidade_texto = f"Crédito parcelado em {num_parcelas}x"
            else:
                return None, None, "Número de parcelas inválido ou não configurado."
        else:
            return None, None, "Número de parcelas inválido. Deve ser entre 2 e 12."
    else:
        return None, None, "Modalidade de pagamento inválida."

    if porcentagem_recebida > 0:
        valor_a_cobrar = valor_desejado / porcentagem_recebida
        return valor_a_cobrar, porcentagem_recebida, modalidade_texto
    else:
        return None, None, "Não foi possível calcular. Porcentagem de recebimento inválida."

# --- Lógica de Histórico ---
HISTORICO_FILE = 'historico_calculos.json'

def carregar_historico():
    """Carrega o histórico de cálculos de um arquivo JSON."""
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] # Retorna lista vazia se o arquivo estiver corrompido
    return []

def salvar_historico(historico_data):
    """Salva o histórico de cálculos em um arquivo JSON."""
    with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
        json.dump(historico_data, f, indent=4, ensure_ascii=False)

# --- Interface Gráfica (Tkinter) ---
class AppCalculadoraTaxas:
    def __init__(self, root):
        self.root = root
        root.title("Calculadora de Preço com Taxas")
        root.geometry("600x600") # Tamanho inicial da janela
        root.resizable(False, False) # Impede redimensionamento

        self.historico = carregar_historico()

        # Configurar estilos
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#e0e0e0')
        self.style.configure('TLabel', background='#e0e0e0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('TCombobox', font=('Arial', 10))
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 9))

        # --- Frame Principal ---
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção de Cálculo ---
        calculo_frame = ttk.LabelFrame(main_frame, text="Calcular Valor a Cobrar", padding="10")
        calculo_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(calculo_frame, text="Valor Desejado (R$):").grid(row=0, column=0, sticky="w", pady=5)
        self.valor_desejado_entry = ttk.Entry(calculo_frame)
        self.valor_desejado_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(calculo_frame, text="Modalidade:").grid(row=1, column=0, sticky="w", pady=5)
        self.modalidade_var = tk.StringVar()
        self.modalidade_combobox = ttk.Combobox(
            calculo_frame,
            textvariable=self.modalidade_var,
            values=["Débito à vista", "Crédito à vista", "Crédito parcelado"],
            state="readonly"
        )
        self.modalidade_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.modalidade_combobox.set("Débito à vista") # Valor padrão
        self.modalidade_combobox.bind("<<ComboboxSelected>>", self.on_modalidade_selected)

        ttk.Label(calculo_frame, text="Parcelas (apenas Crédito Parcelado):").grid(row=2, column=0, sticky="w", pady=5)
        self.parcelas_var = tk.StringVar()
        self.parcelas_combobox = ttk.Combobox(
            calculo_frame,
            textvariable=self.parcelas_var,
            values=[str(i) for i in range(2, 13)], # De 2 a 12 parcelas
            state="disabled" # Desabilitado por padrão
        )
        self.parcelas_combobox.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        calcular_button = ttk.Button(calculo_frame, text="Calcular", command=self.realizar_calculo)
        calcular_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Resultado
        self.resultado_label = ttk.Label(calculo_frame, text="Valor a Cobrar: R$ 0.00", font=('Arial', 11, 'bold'), foreground="blue")
        self.resultado_label.grid(row=4, column=0, columnspan=2, pady=5)
        self.recebera_label = ttk.Label(calculo_frame, text="Você Receberá: R$ 0.00", font=('Arial', 9), foreground="green")
        self.recebera_label.grid(row=5, column=0, columnspan=2, pady=2)


        # Configura as colunas para expandir
        calculo_frame.grid_columnconfigure(1, weight=1)

        # --- Seção de Histórico ---
        historico_frame = ttk.LabelFrame(main_frame, text="Histórico de Cálculos", padding="10")
        historico_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.historico_tree = ttk.Treeview(historico_frame, columns=("Data", "Desejado", "Modalidade", "Cobrar", "Recebido"), show="headings")
        self.historico_tree.heading("Data", text="Data")
        self.historico_tree.heading("Desejado", text="Desejado (R$)")
        self.historico_tree.heading("Modalidade", text="Modalidade")
        self.historico_tree.heading("Cobrar", text="Cobrar (R$)")
        self.historico_tree.heading("Recebido", text="Recebido (R$)")

        # Ajuste de largura das colunas
        self.historico_tree.column("Data", width=120, anchor=tk.CENTER)
        self.historico_tree.column("Desejado", width=80, anchor=tk.E)
        self.historico_tree.column("Modalidade", width=150, anchor=tk.W)
        self.historico_tree.column("Cobrar", width=80, anchor=tk.E)
        self.historico_tree.column("Recebido", width=80, anchor=tk.E)


        self.historico_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar para o Treeview
        scrollbar = ttk.Scrollbar(historico_frame, orient="vertical", command=self.historico_tree.yview)
        self.historico_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.carregar_historico_na_arvore()

        # Configura o frame do histórico para expandir
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)


    def on_modalidade_selected(self, event=None):
        """Habilita/desabilita o combobox de parcelas com base na modalidade selecionada."""
        if self.modalidade_var.get() == "Crédito parcelado":
            self.parcelas_combobox.config(state="readonly")
            self.parcelas_combobox.set("2") # Define um valor padrão para parcelas
        else:
            self.parcelas_combobox.config(state="disabled")
            self.parcelas_combobox.set("") # Limpa o valor

    def realizar_calculo(self):
        """Coleta os dados da GUI, realiza o cálculo e atualiza a interface e o histórico."""
        try:
            valor_desejado = float(self.valor_desejado_entry.get().replace(',', '.')) # Permite vírgula ou ponto
            if valor_desejado <= 0:
                messagebox.showerror("Erro", "O valor desejado deve ser maior que zero.")
                return

            modalidade_selecionada = self.modalidade_var.get()
            num_parcelas = None
            modalidade_para_calculo = ""

            if modalidade_selecionada == "Débito à vista":
                modalidade_para_calculo = "debito_vista"
            elif modalidade_selecionada == "Crédito à vista":
                modalidade_para_calculo = "credito_vista"
            elif modalidade_selecionada == "Crédito parcelado":
                modalidade_para_calculo = "credito_parcelado"
                try:
                    num_parcelas = int(self.parcelas_var.get())
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, selecione o número de parcelas.")
                    return
            else:
                messagebox.showerror("Erro", "Selecione uma modalidade de pagamento válida.")
                return

            valor_a_cobrar, porcentagem_recebida, modalidade_texto = calcular_valor(
                valor_desejado, modalidade_para_calculo, num_parcelas
            )

            if valor_a_cobrar is not None:
                self.resultado_label.config(text=f"Valor a Cobrar: R$ {valor_a_cobrar:.2f}")
                valor_real_recebido = valor_a_cobrar * porcentagem_recebida
                self.recebera_label.config(text=f"Você Receberá: R$ {valor_real_recebido:.2f} (Aprox.)")

                # Adiciona ao histórico
                self.adicionar_ao_historico(
                    valor_desejado, modalidade_texto, valor_a_cobrar, valor_real_recebido
                )
            else:
                messagebox.showerror("Erro de Cálculo", modalidade_texto) # modalidade_texto aqui contém a mensagem de erro

        except ValueError:
            messagebox.showerror("Erro", "Por favor, digite um número válido para o valor desejado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

    def adicionar_ao_historico(self, desejado, modalidade, cobrar, recebido):
        """Adiciona um novo cálculo ao histórico e atualiza a Treeview."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        novo_registro = {
            "data": timestamp,
            "valor_desejado": desejado,
            "modalidade": modalidade,
            "valor_cobrar": cobrar,
            "valor_recebido": recebido
        }
        self.historico.append(novo_registro)
        salvar_historico(self.historico)
        self.carregar_historico_na_arvore() # Recarrega a Treeview para mostrar o novo item

    def carregar_historico_na_arvore(self):
        """Limpa e preenche a Treeview com os dados do histórico."""
        # Limpa itens existentes
        for item in self.historico_tree.get_children():
            self.historico_tree.delete(item)

        # Adiciona itens do histórico (ordem inversa para os mais recentes no topo)
        for registro in reversed(self.historico):
            self.historico_tree.insert("", tk.END, values=(
                registro['data'],
                f"{registro['valor_desejado']:.2f}",
                registro['modalidade'],
                f"{registro['valor_cobrar']:.2f}",
                f"{registro['valor_recebido']:.2f}"
            ))

# --- Execução do Aplicativo ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AppCalculadoraTaxas(root)
    root.mainloop()