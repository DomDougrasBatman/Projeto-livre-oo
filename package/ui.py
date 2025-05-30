import tkinter as tk
from tkinter import ttk, messagebox
from package.simulador import SimuladorFinanceiro
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import uuid
import re

class InterfaceGrafica:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.title("App de Finanças Pessoais")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)

        self._criar_aba_login()
        self._criar_aba_transacoes()
        self._criar_aba_simulador()
        self._criar_aba_graficos()

        self.notebook.tab(1, state='disabled')
        self.notebook.tab(2, state='disabled')
        self.notebook.tab(3, state='disabled')

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def iniciar(self):
        self.root.mainloop()

    def _on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Transações":
            self._atualizar_lista_transacoes()
        elif selected_tab == "Gráficos":
            self._plotar_barras()

    def _criar_aba_login(self):
        self.frame_login = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_login, text="Login")

        ttk.Label(self.frame_login, text="Cadastro", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2,
                                                                                      pady=5)

        ttk.Label(self.frame_login, text="Usuário:").grid(row=1, column=0, sticky='e')
        self.cadastro_user_entry = ttk.Entry(self.frame_login)
        self.cadastro_user_entry.grid(row=1, column=1)

        ttk.Label(self.frame_login, text="Senha:").grid(row=2, column=0, sticky='e')
        self.cadastro_senha_entry = ttk.Entry(self.frame_login, show="*")
        self.cadastro_senha_entry.grid(row=2, column=1)

        ttk.Button(self.frame_login, text="Cadastrar", command=self._cadastrar).grid(row=3, column=0, columnspan=2,
                                                                                     pady=5)

        ttk.Label(self.frame_login, text="Login", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=2,
                                                                                   pady=5)

        ttk.Label(self.frame_login, text="Usuário:").grid(row=5, column=0, sticky='e')
        self.login_user_entry = ttk.Entry(self.frame_login)
        self.login_user_entry.grid(row=5, column=1)

        ttk.Label(self.frame_login, text="Senha:").grid(row=6, column=0, sticky='e')
        self.login_senha_entry = ttk.Entry(self.frame_login, show="*")
        self.login_senha_entry.grid(row=6, column=1)

        ttk.Button(self.frame_login, text="Entrar", command=self._login).grid(row=7, column=0, columnspan=2, pady=5)

    def _cadastrar(self):
        user = self.cadastro_user_entry.get()
        senha = self.cadastro_senha_entry.get()

        if not user or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            self.app.cadastrar_usuario(user, senha)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.cadastro_user_entry.delete(0, tk.END)
            self.cadastro_senha_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def _login(self):
        user = self.login_user_entry.get()
        senha = self.login_senha_entry.get()

        if not user or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        if self.app.login(user, senha):
            messagebox.showinfo("Sucesso", f"Bem-vindo, {user}!")
            self.login_user_entry.delete(0, tk.END)
            self.login_senha_entry.delete(0, tk.END)

            self.notebook.tab(1, state='normal')
            self.notebook.tab(2, state='normal')
            self.notebook.tab(3, state='normal')
            self.notebook.select(1)
            self._atualizar_lista_transacoes()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    def _criar_aba_transacoes(self):
        self.frame_transacoes = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_transacoes, text="Transações")

        form_frame = ttk.LabelFrame(self.frame_transacoes, text="Adicionar/Editar Transação")
        form_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.tipo_var = ttk.Combobox(form_frame, values=["Receita", "Despesa"])
        self.tipo_var.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.tipo_var.set("Receita")
        self.tipo_var.bind("<<ComboboxSelected>>", self._on_tipo_transacao_change)


        ttk.Label(form_frame, text="Valor:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.valor_entry = ttk.Entry(form_frame)
        self.valor_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Data (dd/mm/aaaa):").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.data_entry = ttk.Entry(form_frame)
        self.data_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(form_frame, text="Descrição:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.descricao_entry = ttk.Entry(form_frame)
        self.descricao_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        self.label_origem_categoria = ttk.Label(form_frame, text="Origem:")
        self.label_origem_categoria.grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.entry_origem_categoria = ttk.Entry(form_frame)
        self.entry_origem_categoria.grid(row=4, column=1, sticky='ew', padx=5, pady=2)

        self.btn_adicionar = ttk.Button(form_frame, text="Adicionar", command=self._adicionar_transacao)
        self.btn_adicionar.grid(row=5, column=0, columnspan=2, pady=5)
        self.current_edit_transacao_id = None

        list_frame = ttk.LabelFrame(self.frame_transacoes, text="Minhas Transações")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.transacoes_tree = ttk.Treeview(list_frame, columns=("ID", "Tipo", "Valor", "Data", "Descrição", "Detalhe"), show="headings")
        self.transacoes_tree.heading("ID", text="ID")
        self.transacoes_tree.heading("Tipo", text="Tipo")
        self.transacoes_tree.heading("Valor", text="Valor")
        self.transacoes_tree.heading("Data", text="Data")
        self.transacoes_tree.heading("Descrição", text="Descrição")
        self.transacoes_tree.heading("Detalhe", text="Origem/Categoria")

        self.transacoes_tree.column("ID", width=70, stretch=tk.NO)
        self.transacoes_tree.column("Tipo", width=70, stretch=tk.NO)
        self.transacoes_tree.column("Valor", width=80, stretch=tk.NO, anchor='e')
        self.transacoes_tree.column("Data", width=90, stretch=tk.NO)
        self.transacoes_tree.column("Descrição", width=150)
        self.transacoes_tree.column("Detalhe", width=100)

        self.transacoes_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.transacoes_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.transacoes_tree.configure(yscrollcommand=scrollbar.set)

        action_buttons_frame = ttk.Frame(self.frame_transacoes)
        action_buttons_frame.pack(pady=5)
        ttk.Button(action_buttons_frame, text="Editar Selecionada", command=self._editar_transacao).pack(side="left", padx=5)
        ttk.Button(action_buttons_frame, text="Remover Selecionada", command=self._remover_transacao).pack(side="left", padx=5)

        self.saldo_var = tk.StringVar()
        self._atualizar_saldo()
        ttk.Label(self.frame_transacoes, textvariable=self.saldo_var, font=("Arial", 12, "bold")) \
            .pack(pady=10)

    def _on_tipo_transacao_change(self, event=None):
        if self.tipo_var.get() == "Receita":
            self.label_origem_categoria.config(text="Origem:")
        else:
            self.label_origem_categoria.config(text="Categoria:")

    def _criar_aba_simulador(self):
        self.frame_simulador = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_simulador, text="Simulador de Juros")

        ttk.Label(self.frame_simulador, text="Capital (R$):").grid(row=0, column=0, sticky='e')
        self.capital_entry = ttk.Entry(self.frame_simulador)
        self.capital_entry.grid(row=0, column=1)

        ttk.Label(self.frame_simulador, text="Taxa (% ao mês):").grid(row=1, column=0, sticky='e')
        self.taxa_entry = ttk.Entry(self.frame_simulador)
        self.taxa_entry.grid(row=1, column=1)

        ttk.Label(self.frame_simulador, text="Tempo (meses):").grid(row=2, column=0, sticky='e')
        self.tempo_entry = ttk.Entry(self.frame_simulador)
        self.tempo_entry.grid(row=2, column=1)

        ttk.Button(self.frame_simulador, text="Calcular Juros Simples", command=self._calcular_simples) \
            .grid(row=3, column=0, pady=10)

        ttk.Button(self.frame_simulador, text="Calcular Juros Compostos", command=self._calcular_compostos) \
            .grid(row=3, column=1, pady=10)

        self.resultado_var = tk.StringVar()
        ttk.Label(self.frame_simulador, textvariable=self.resultado_var, font=("Arial", 11)) \
            .grid(row=4, column=0, columnspan=2)

    def _criar_aba_graficos(self):
        self.frame_graficos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_graficos, text="Gráficos")

        botoes_frame = ttk.Frame(self.frame_graficos)
        botoes_frame.pack(pady=10)

        ttk.Button(botoes_frame,
                   text="Barras (Receitas x Despesas)",
                   command=self._plotar_barras).grid(row=0, column=0, padx=5)

        ttk.Button(botoes_frame,
                   text="Pizza (Distribuição)",
                   command=self._plotar_pizza).grid(row=0, column=1, padx=5)

        ttk.Button(botoes_frame,
                   text="Linhas (Histórico)",
                   command=self._plotar_linhas).grid(row=0, column=2, padx=5)

        self.grafico_frame = ttk.Frame(self.frame_graficos)
        self.grafico_frame.pack(fill='both', expand=True)

    def _plotar_barras(self):
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if not self.app.usuario_logado():
            tk.Label(self.grafico_frame, text="Faça login para visualizar os gráficos").pack()
            return

        receitas = sum(t.get_valor() for t in self.app.get_transacoes_do_usuario_logado() if t.tipo() == "Receita")
        despesas = sum(t.get_valor() for t in self.app.get_transacoes_do_usuario_logado() if t.tipo() == "Despesa")

        if receitas == 0 and despesas == 0:
            tk.Label(self.grafico_frame, text="Nenhuma transação registrada").pack()
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        categorias = ['Receitas', 'Despesas']
        valores = [receitas, despesas]
        cores = ['green', 'red']

        ax.bar(categorias, valores, color=cores)
        ax.set_title('Receitas vs Despesas')
        ax.set_ylabel('Valor (R$)')

        for i, v in enumerate(valores):
            ax.text(i, v + 0.1, f"R${v:,.2f}", ha='center')

        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plotar_pizza(self):
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if not self.app.usuario_logado():
            tk.Label(self.grafico_frame, text="Faça login para visualizar os gráficos").pack()
            return

        despesas_por_categoria = {}
        for t in self.app.get_transacoes_do_usuario_logado():
            if t.tipo() == "Despesa":
                categoria = t.get_categoria() if hasattr(t, 'get_categoria') else t.get_descricao()
                despesas_por_categoria[categoria] = despesas_por_categoria.get(categoria, 0) + t.get_valor()

        if not despesas_por_categoria:
            tk.Label(self.grafico_frame, text="Nenhuma despesa registrada").pack()
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(despesas_por_categoria.values(),
               labels=despesas_por_categoria.keys(),
               autopct='%1.1f%%',
               startangle=90)
        ax.set_title('Distribuição de Despesas por Categoria')
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plotar_linhas(self):
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if not self.app.usuario_logado():
            tk.Label(self.grafico_frame, text="Faça login para visualizar os gráficos").pack()
            return

        transacoes_por_data = {}
        for t in self.app.get_transacoes_do_usuario_logado():
            data = t.get_data()
            if data not in transacoes_por_data:
                transacoes_por_data[data] = {'Receita': 0, 'Despesa': 0}
            transacoes_por_data[data][t.tipo()] += t.get_valor()

        if not transacoes_por_data:
            tk.Label(self.grafico_frame, text="Nenhuma transação registrada").pack()
            return

        datas_ordenadas = sorted(transacoes_por_data.keys())
        receitas = [transacoes_por_data[d]['Receita'] for d in datas_ordenadas]
        despesas = [transacoes_por_data[d]['Despesa'] for d in datas_ordenadas]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(datas_ordenadas, receitas, label='Receitas', marker='o', color='green')
        ax.plot(datas_ordenadas, despesas, label='Despesas', marker='o', color='red')
        ax.set_title('Histórico de Receitas e Despesas')
        ax.set_ylabel('Valor (R$)')
        ax.legend()
        plt.xticks(rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _validar_formato_data(self, data_str: str) -> bool:
        return re.match(r'^(\d{2})\/(\d{2})\/(\d{4})$', data_str) is not None

    def _adicionar_transacao(self):
        try:
            tipo = self.tipo_var.get()
            valor_str = self.valor_entry.get().replace(',', '.')
            data = self.data_entry.get()
            descricao = self.descricao_entry.get()
            detalhe = self.entry_origem_categoria.get()

            if not self._validar_formato_data(data):
                messagebox.showerror("Erro de Validação", "Formato de data inválido. Use dd/mm/aaaa.")
                return

            valor = float(valor_str)

            kwargs = {}
            if tipo == "Receita":
                kwargs['origem'] = detalhe
            elif tipo == "Despesa":
                kwargs['categoria'] = detalhe

            if self.current_edit_transacao_id:
                if self.app.editar_transacao(self.current_edit_transacao_id, valor, data, descricao, **kwargs):
                    messagebox.showinfo("Sucesso", "Transação editada com sucesso!")
                else:
                    messagebox.showerror("Erro", "Falha ao editar transação.")
                self._resetar_modo_edicao()
            else:
                self.app.adicionar_transacao(tipo, valor, data, descricao, **kwargs)
                messagebox.showinfo("Sucesso", f"{tipo} adicionada com sucesso!")

            self._limpar_campos()
            self._atualizar_saldo()
            self._atualizar_lista_transacoes()

            if self.notebook.index(self.notebook.select()) == 3:
                self._plotar_barras()

        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Valor inválido. Certifique-se de que o valor é numérico. Detalhes: {e}")
        except PermissionError as e:
            messagebox.showerror("Erro de Permissão", str(e))
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")


    def _editar_transacao(self):
        selected_item = self.transacoes_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma transação para editar.")
            return

        item_values = self.transacoes_tree.item(selected_item, 'values')
        displayed_id_prefix = item_values[0].replace("...", "")

        transacao_id_completo = None
        for t_obj in self.app.get_transacoes_do_usuario_logado():
            if t_obj.get_id().startswith(displayed_id_prefix):
                transacao_id_completo = t_obj.get_id()
                break

        if not transacao_id_completo:
            messagebox.showerror("Erro", "Não foi possível encontrar a transação para edição.")
            return

        self.current_edit_transacao_id = transacao_id_completo

        self.tipo_var.set(item_values[1])
        self.valor_entry.delete(0, tk.END)
        self.valor_entry.insert(0, item_values[2].replace('R$', '').replace(',', ''))
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, item_values[3])
        self.descricao_entry.delete(0, tk.END)
        self.descricao_entry.insert(0, item_values[4])
        self.entry_origem_categoria.delete(0, tk.END)
        self.entry_origem_categoria.insert(0, item_values[5])

        self._on_tipo_transacao_change()

        self.btn_adicionar.config(text="Salvar Edição", command=self._adicionar_transacao)

    def _resetar_modo_edicao(self):
        self.current_edit_transacao_id = None
        self.btn_adicionar.config(text="Adicionar", command=self._adicionar_transacao)
        self._limpar_campos()


    def _remover_transacao(self):
        selected_item = self.transacoes_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma transação para remover.")
            return

        item_values = self.transacoes_tree.item(selected_item, 'values')
        displayed_id_prefix = item_values[0].replace("...", "")

        transacao_id_completo = None
        for t_obj in self.app.get_transacoes_do_usuario_logado():
            if t_obj.get_id().startswith(displayed_id_prefix):
                transacao_id_completo = t_obj.get_id()
                break

        if not transacao_id_completo:
            messagebox.showerror("Erro", "Não foi possível encontrar a transação para remoção.")
            return


        if messagebox.askyesno("Confirmar Remoção", "Tem certeza que deseja remover esta transação?"):
            try:
                if self.app.remover_transacao(transacao_id_completo):
                    messagebox.showinfo("Sucesso", "Transação removida com sucesso!")
                    self._atualizar_saldo()
                    self._atualizar_lista_transacoes()
                else:
                    messagebox.showerror("Erro", "Falha ao remover transação.")
            except PermissionError as e:
                messagebox.showerror("Erro", str(e))
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao remover: {e}")

    def _limpar_campos(self):
        self.valor_entry.delete(0, tk.END)
        self.data_entry.delete(0, tk.END)
        self.descricao_entry.delete(0, tk.END)
        self.entry_origem_categoria.delete(0, tk.END)
        self.tipo_var.set("Receita")
        self._on_tipo_transacao_change()


    def _atualizar_saldo(self):
        saldo = self.app.calcular_saldo()
        self.saldo_var.set(f"Saldo atual: R$ {saldo:,.2f}")

    def _atualizar_lista_transacoes(self):
        for item in self.transacoes_tree.get_children():
            self.transacoes_tree.delete(item)

        if self.app.usuario_logado():
            for transacao in self.app.get_transacoes_do_usuario_logado():
                detalhe = ""
                if transacao.tipo() == "Receita":
                    detalhe = transacao.get_origem() if hasattr(transacao, 'get_origem') else "N/A"
                elif transacao.tipo() == "Despesa":
                    detalhe = transacao.get_categoria() if hasattr(transacao, 'get_categoria') else "N/A"

                self.transacoes_tree.insert("", "end", values=(
                    transacao.get_id()[:8] + "...",
                    transacao.tipo(),
                    f"R${transacao.get_valor():,.2f}",
                    transacao.get_data(),
                    transacao.get_descricao(),
                    detalhe
                ))
        self._atualizar_saldo()


    def _calcular_simples(self):
        try:
            capital_str = self.capital_entry.get().replace(',', '.')
            taxa_str = self.taxa_entry.get().replace(',', '.')
            tempo_str = self.tempo_entry.get().replace(',', '.')

            c = float(capital_str)
            i = float(taxa_str)
            t = float(tempo_str)
            m = SimuladorFinanceiro.juros_simples(c, i, t)
            self.resultado_var.set(f"Montante com juros simples: R$ {m:,.2f}")
        except ValueError:
            messagebox.showerror("Erro", "Preencha todos os campos com valores numéricos válidos.")

    def _calcular_compostos(self):
        try:
            capital_str = self.capital_entry.get().replace(',', '.')
            taxa_str = self.taxa_entry.get().replace(',', '.')
            tempo_str = self.tempo_entry.get().replace(',', '.')

            c = float(capital_str)
            i = float(taxa_str)
            t = float(tempo_str)
            m = SimuladorFinanceiro.juros_compostos(c, i, t)
            self.resultado_var.set(f"Montante com juros compostos: R$ {m:,.2f}")
        except ValueError:
            messagebox.showerror("Erro", "Preencha todos os campos com valores numéricos válidos.")