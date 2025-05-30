import uuid
from abc import ABC, abstractmethod

class Transacao(ABC):
    def __init__(self, valor: float, data: str, descricao: str):
        self._id = str(uuid.uuid4())
        self._valor = valor
        self._data = data
        self._descricao = descricao

    def get_id(self):
        return self._id

    def get_valor(self):
        return self._valor

    def get_data(self):
        return self._data

    def get_descricao(self):
        return self._descricao

    def set_descricao(self, nova_descricao: str):
        self._descricao = nova_descricao

    def set_valor(self, novo_valor: float):
        self._valor = novo_valor

    def set_data(self, nova_data: str):
        self._data = nova_data

    @abstractmethod
    def tipo(self):
        pass

    @abstractmethod
    def get_info(self):
        pass


class Receita(Transacao):
    def __init__(self, valor: float, data: str, descricao: str, origem: str = "Outros"):
        super().__init__(valor, data, descricao)
        self._origem = origem

    def tipo(self):
        return "Receita"

    def get_origem(self):
        return self._origem

    def set_origem(self, nova_origem: str):
        self._origem = nova_origem

    def get_info(self):
        return f"ID: {self._id[:8]}... | Tipo: {self.tipo()} | Valor: R${self._valor:,.2f} | Data: {self._data} | Descrição: {self._descricao} | Origem: {self._origem}"


class Despesa(Transacao):
    def __init__(self, valor: float, data: str, descricao: str, categoria: str = "Outros"):
        super().__init__(valor, data, descricao)
        self._categoria = categoria

    def tipo(self):
        return "Despesa"

    def get_categoria(self):
        return self._categoria

    def set_categoria(self, nova_categoria: str):
        self._categoria = nova_categoria

    def get_info(self):
        return f"ID: {self._id[:8]}... | Tipo: {self.tipo()} | Valor: R${self._valor:,.2f} | Data: {self._data} | Descrição: {self._descricao} | Categoria: {self._categoria}"