from src.solid_lens.configuration import SolidLensConfig
from src.solid_lens.graph import app

SAMPLE_CODE = '''
class OrderService:
    def __init__(self):
        self.orders = []

    def process_order(self, order_data, order_type):
        self.orders.append(order_data)
        if order_type == "standard":
            print("Processing standard order...")
            self._send_email(order_data)
            self._generate_invoice(order_data)
            self._log("Standard order processed")
            self._save_to_db(order_data)
        elif order_type == "express":
            print("Processing express order...")
            self._send_email(order_data)
            self._generate_invoice(order_data)
            self._log("Express order processed")
            self._save_to_db(order_data)
            self._arrange_express_shipping(order_data)
        elif order_type == "international":
            print("Processing international order...")
            self._send_email(order_data)
            self._generate_invoice(order_data)
            self._log("Intl order processed")
            self._save_to_db(order_data)
            self._calculate_customs(order_data)
            self._arrange_shipping(order_data)

    def _send_email(self, data):
        print(f"Email: {data}")

    def _generate_invoice(self, data):
        print(f"Invoice: {data}")

    def _log(self, msg):
        print(f"LOG: {msg}")

    def _save_to_db(self, data):
        import sqlite3
        conn = sqlite3.connect("orders.db")
        conn.execute("INSERT INTO orders VALUES (?)", (str(data),))
        conn.commit()

    def _arrange_express_shipping(self, data):
        pass

    def _calculate_customs(self, data):
        pass

    def _arrange_shipping(self, data):
        pass
'''


def main() -> None:
    config = SolidLensConfig.from_env()
    print(f"Usando modelo: {config.model} en {config.ollama_base_url}")

    initial_state = {
        "source_code": SAMPLE_CODE,
        "language": "",
        "config": config,
        "results": {},
        "report": "",
        "errors": [],
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 50)
    print(final_state.get("report", "No report generated."))
    print("=" * 50)


if __name__ == "__main__":
    main()
