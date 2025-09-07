class SuccessfulPayment:
    def __init__(self, successful_payment_data: dict):
        self.currency = successful_payment_data.get("currency")
        self.total_amount = successful_payment_data.get("total_amount")
        self.invoice_payload = successful_payment_data.get("invoice_payload")
        self.telegram_payment_charge_id = successful_payment_data.get("telegram_payment_charge_id")

    def __str__(self):
        fields = []
        if self.currency is not None:
            fields.append(f"currency={self.currency}")
        if self.total_amount is not None:
            fields.append(f"total_amount={self.total_amount}")
        if self.invoice_payload is not None:
            fields.append(f"invoice_payload={self.invoice_payload}")
        if self.telegram_payment_charge_id is not None:
            fields.append(f"telegram_payment_charge_id={self.telegram_payment_charge_id}")
        
        return "SuccessfulPayment(\n    " + ",\n    ".join(fields) + "\n)"