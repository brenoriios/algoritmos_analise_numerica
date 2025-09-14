from decimal import Decimal, getcontext

def formatar_decimal(numero: Decimal) -> str:
    """
    Formata um número Decimal de acordo com as seguintes regras:
    - Parte inteira ocupa 5 espaços para números positivos.
    - Parte inteira ocupa 6 espaços para números negativos (incluindo o sinal).
    - Sempre exibe 10 casas decimais.
    """
    if numero >= 0:
        # Formata o número positivo com 5 espaços para a parte inteira e 10 decimais.
        # O ">" alinha à direita dentro de um campo de 5 caracteres.
        return f'{numero: >5.10f}'
    else:
        # Formata o número negativo com 6 espaços para a parte inteira e 10 decimais.
        # O alinhamento é feito considerando o sinal de menos.
        return f'{numero: >6.10f}'

# Exemplo de uso
getcontext().prec = 50

numero_positivo = Decimal('123.456789')
numero_negativo = Decimal('-9876.54321')
numero_pequeno_pos = Decimal('1.2')
numero_pequeno_neg = Decimal('-0.0001')

print(f"Número positivo (123.456789): {formatar_decimal(numero_positivo)}")
print(f"Número negativo (-9876.54321): {formatar_decimal(numero_negativo)}")
print(f"Número pequeno positivo (1.2): {formatar_decimal(numero_pequeno_pos)}")
print(f"Número pequeno negativo (-0.0001): {formatar_decimal(numero_pequeno_neg)}")