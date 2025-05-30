import os
import json
from datetime import datetime
from package.transacao import Receita, Despesa, Transacao
from package.simulador import SimuladorFinanceiro
from package.ui import InterfaceGrafica
from package.usuario_mixin import UsuarioMixin
import uuid

CAMINHO_ARQUIVO = "dados/transacoes.json"

class FinancasApp(UsuarioMixin):
    def __init__(self):
        super().__init__()
        self.transacoes: list[Transacao] = []
        self.carregar_transacoes()
        self.ui = InterfaceGrafica(self)

    def _validar_data_real(self, data_str: str) -> bool:
        try:
            datetime.strptime(data_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def adicionar_transacao(self, tipo: str, valor: float, data: str, descricao: str, **kwargs):
        if not self.usuario_logado():
            raise PermissionError("Usuário não logado")

        if not self._validar_data_real(data):
            raise ValueError("Data inválida ou inexistente. Por favor, insira uma data real (ex: 31/01/2025).")

        transacao_obj = None
        if tipo == "Receita":
            origem = kwargs.get('origem', 'Outros')
            transacao_obj = Receita(valor, data, descricao, origem)
        elif tipo == "Despesa":
            categoria = kwargs.get('categoria', 'Outros')
            transacao_obj = Despesa(valor, data, descricao, categoria)
        else:
            raise ValueError("Tipo de transação inválido")

        self.transacoes.append(transacao_obj)

        transacao_data = {
            'id': transacao_obj.get_id(),
            'tipo': tipo,
            'valor': valor,
            'data': data,
            'descricao': descricao
        }
        if tipo == "Receita":
            transacao_data['origem'] = kwargs.get('origem', 'Outros')
        elif tipo == "Despesa":
            transacao_data['categoria'] = kwargs.get('categoria', 'Outros')

        self._usuarios[self._usuario_logado]['transacoes'].append(transacao_data)
        self.salvar_transacoes()

    def calcular_saldo(self):
        if not self.usuario_logado():
            return 0.0

        saldo = 0.0
        for t_obj in self.transacoes:
            if t_obj.tipo() == "Receita":
                saldo += t_obj.get_valor()
            else:
                saldo -= t_obj.get_valor()
        return saldo

    def salvar_transacoes(self):
        os.makedirs(os.path.dirname(CAMINHO_ARQUIVO), exist_ok=True)
        with open(CAMINHO_ARQUIVO, 'w') as f:
            json.dump({
                'usuarios': self._usuarios,
                'usuario_logado': self._usuario_logado
            }, f, indent=2)

    def carregar_transacoes(self):
        if os.path.exists(CAMINHO_ARQUIVO):
            try:
                with open(CAMINHO_ARQUIVO, 'r') as f:
                    data = json.load(f)
                    self._usuarios = data.get('usuarios', {})
                    self._usuario_logado = data.get('usuario_logado')

                    self.transacoes = []
                    if self._usuario_logado and self._usuario_logado in self._usuarios:
                        for t_data in self._usuarios[self._usuario_logado]['transacoes']:
                            transacao_obj = None
                            if t_data['tipo'] == "Receita":
                                transacao_obj = Receita(t_data['valor'], t_data['data'], t_data['descricao'], t_data.get('origem', 'Outros'))
                            elif t_data['tipo'] == "Despesa":
                                transacao_obj = Despesa(t_data['valor'], t_data['data'], t_data['descricao'], t_data.get('categoria', 'Outros'))

                            if transacao_obj:
                                transacao_obj._id = t_data.get('id', str(uuid.uuid4()))
                                self.transacoes.append(transacao_obj)
            except Exception as e:
                print(f"Erro ao carregar transações: {e}")
                self._usuarios = {}
                self._usuario_logado = None
                self.transacoes = []

    def rodar(self):
        self.ui.iniciar()

    def get_transacoes_do_usuario_logado(self) -> list[Transacao]:
        if self._usuario_logado:
            return self.transacoes
        return []

    def remover_transacao(self, transacao_id: str) -> bool:
        if not self.usuario_logado():
            raise PermissionError("Usuário não logado")

        original_len_in_memory = len(self.transacoes)
        self.transacoes = [t for t in self.transacoes if t.get_id() != transacao_id]
        removed_from_memory = original_len_in_memory > len(self.transacoes)

        if self._usuario_logado in self._usuarios:
            original_len_in_dict = len(self._usuarios[self._usuario_logado]['transacoes'])
            self._usuarios[self._usuario_logado]['transacoes'] = [
                t_data for t_data in self._usuarios[self._usuario_logado]['transacoes']
                if t_data.get('id') != transacao_id
            ]
            removed_from_dict = original_len_in_dict > len(self._usuarios[self._usuario_logado]['transacoes'])

            if removed_from_memory and removed_from_dict:
                self.salvar_transacoes()
                return True
        return False

    def editar_transacao(self, transacao_id: str, novo_valor: float, nova_data: str, nova_descricao: str, **kwargs) -> bool:
        if not self.usuario_logado():
            raise PermissionError("Usuário não logado")

        if not self._validar_data_real(nova_data):
            raise ValueError("Nova data inválida ou inexistente. Por favor, insira uma data real (ex: 31/01/2025).")

        edited_in_memory = False
        for t_obj in self.transacoes:
            if t_obj.get_id() == transacao_id:
                t_obj.set_valor(novo_valor)
                t_obj.set_data(nova_data)
                t_obj.set_descricao(nova_descricao)
                if isinstance(t_obj, Receita):
                    t_obj.set_origem(kwargs.get('origem', t_obj.get_origem()))
                elif isinstance(t_obj, Despesa):
                    t_obj.set_categoria(kwargs.get('categoria', t_obj.get_categoria()))
                edited_in_memory = True
                break

        edited_in_dict = False
        if self._usuario_logado in self._usuarios:
            for t_data in self._usuarios[self._usuario_logado]['transacoes']:
                if t_data.get('id') == transacao_id:
                    t_data['valor'] = novo_valor
                    t_data['data'] = nova_data
                    t_data['descricao'] = nova_descricao
                    if t_data['tipo'] == "Receita":
                        t_data['origem'] = kwargs.get('origem', t_data.get('origem', 'Outros'))
                    elif t_data['tipo'] == "Despesa":
                        t_data['categoria'] = kwargs.get('categoria', t_data.get('categoria', 'Outros'))
                    edited_in_dict = True
                    break

        if edited_in_memory and edited_in_dict:
            self.salvar_transacoes()
            return True
        return False