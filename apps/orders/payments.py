import random
import string


# Simulação de sistema de pagamento para AOA-Kwanza
class AOAPaymentProcessor:
    """
    Simula um processador de pagamentos para Kwanza (AOA)
    """

    @staticmethod
    def generate_reference():
        """Gera um número de referência para pagamento."""
        return f"REF-{"".join(random.choices(string.digits, k=12))}"
