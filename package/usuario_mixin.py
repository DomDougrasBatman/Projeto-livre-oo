import hashlib


class UsuarioMixin:
    def __init__(self):
        self._usuarios = {}
        self._usuario_logado = None

    def cadastrar_usuario(self, username: str, senha: str):
        if username in self._usuarios:
            raise ValueError("Usuário já existe")

        hash_senha = hashlib.sha256(senha.encode()).hexdigest()
        self._usuarios[username] = {
            'hash_senha': hash_senha,
            'transacoes': []
        }
        return True

    def login(self, username: str, senha: str) -> bool:
        if username not in self._usuarios:
            return False

        hash_senha = hashlib.sha256(senha.encode()).hexdigest()
        if self._usuarios[username]['hash_senha'] == hash_senha:
            self._usuario_logado = username
            return True
        return False

    def logout(self):
        self._usuario_logado = None

    def usuario_logado(self):
        return self._usuario_logado is not None

    def get_usuario_atual(self):
        return self._usuario_logado