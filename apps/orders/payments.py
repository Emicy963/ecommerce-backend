import random
import string
from .models import Order, Payment


# Simulação de sistema de pagamento para AOA-Kwanza
class AOAPaymentProcessor:
    """
    Simula um processador de pagamentos para Kwanza (AOA)
    """

    @staticmethod
    def generate_reference():
        """Gera um número de referência para pagamento."""
        return f"REF-{"".join(random.choices(string.digits, k=12))}"
    
    @staticmethod
    def process_payment(order: Order, payment_method, reference_number=None):
        """
        Processa o pagamento de um pedido

        Args:
            order: Objeto Order
            payment_methdo: Método de pagamento ("reference", "mobile", "card")
            reference_number: Número de referência (para pagamentos por referência)
        
        Returns:
            tuple: (success: bool, transaction_id: str, message: str)
        """

        # Criar registro de pagamento
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
            reference_number=reference_number
        )

        # Simulação de processamento de pagamento
        # Em um ambiente real, aqui seria feita a integração com o gateway de pagamento
        success = random.choice([True, True, True, False]) # 75% de chance de sucesso

        if success:
            # Gerar ID de transação
            transaction_id = f"TXN-{"".join(random.choices(string.ascii_uppercase + string.digits, k=16))}"
            payment.transaction_id = transaction_id
            payment.payment_status = "completed"
            payment.save()

            # Atualizar stauts do pedido
            order.payment_status = "paid"
            order.status = "confirmed"
            order.save()

            return True, transaction_id, "Payment processed successfully"
        else:
            payment.payment_status = "failed"
            payment.save()

            # Atualizar status do pedido
            order.payment_status = "failed"
            order.save()

            return False, None, "Pagamento falhou. Por favor, tenta de novo ou use um outro método."
