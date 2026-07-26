import argparse
import asyncio

from src.solid_lens.configuration import SolidLensConfig
from src.solid_lens.graph import app
from src.solid_lens.mcp_client import close_mcp_client, create_mcp_client

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


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="SolidLens — Auditor de principios SOLID")
    parser.add_argument("--dir", type=str, default=None, help="Ruta al proyecto a analizar")
    parser.add_argument("--check-deps", action="store_true", help="Verificar dependencias vía Context7 MCP")
    args = parser.parse_args()

    config = SolidLensConfig.from_env()
    print(f"Usando modelo: {config.model} en {config.ollama_base_url}")

    initial_state = {
        "source_code": SAMPLE_CODE,
        "source_path": args.dir,
        "language": "",
        "config": config,
        "results": {},
        "report": "",
        "errors": [],
        "dep_warnings": [],
    }

    if args.check_deps:
        client = await create_mcp_client(config.mcp_config_path)
        if client is not None:
            print("Cliente MCP inicializado")
        else:
            print("No se encontró configuración MCP (mcp_config.json)")

    try:
        final_state = await app.ainvoke(initial_state)
    finally:
        if args.check_deps:
            await close_mcp_client()

    print("\n" + "=" * 50)
    print(final_state.get("report", "No report generated."))
    print("=" * 50)

    dep_warnings = final_state.get("dep_warnings", [])
    if dep_warnings:
        print("\n--- Advertencias de dependencias ---")
        for w in dep_warnings:
            print(f"  {w}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
