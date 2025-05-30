class SimuladorFinanceiro:
    @staticmethod
    def juros_simples(capital: float, taxa: float, tempo: float) -> float:
        taxa_decimal = taxa / 100
        juros = capital * taxa_decimal * tempo
        montante = capital + juros
        return montante

    @staticmethod
    def juros_compostos(capital: float, taxa: float, tempo: float) -> float:
        taxa_decimal = taxa / 100
        montante = capital * ((1 + taxa_decimal) ** tempo)
        return montante