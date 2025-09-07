class Invoice:
    def __init__(self, invoice_data: dict):
        self.title = invoice_data.get("title")
        self.description = invoice_data.get("description")
        self.start_parameter = invoice_data.get("start_parameter")
        self.currency = invoice_data.get("currency")
        self.total_amount = invoice_data.get("total_amount")

    def __str__(self):
        fields = []
        if self.title is not None:
            fields.append(f"title={self.title}")
        if self.description is not None:
            fields.append(f"description={self.description}")
        if self.start_parameter is not None:
            fields.append(f"start_parameter={self.start_parameter}")
        if self.currency is not None:
            fields.append(f"currency={self.currency}")
        if self.total_amount is not None:
            fields.append(f"total_amount={self.total_amount}")
        
        return "Invoice(\n    " + ",\n    ".join(fields) + "\n)"