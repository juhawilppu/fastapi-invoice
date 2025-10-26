from confluent_kafka import Consumer, KafkaException
import json
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, ValidationError

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer-group-1',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['invoice-events'])
print("Subscribing to:", consumer.list_topics().topics.keys())


def calculate_invoice_totals(invoice):
    VAT_RATE = Decimal("0.14")  # 14% VAT per row
    CENT = Decimal("0.01")

    total_excl = Decimal("0")
    total_vat = Decimal("0")
    total_incl = Decimal("0")

    rows_out = []

    for r in invoice.rows:
        qty = Decimal(r.quantity)
        unit = r.unit_price if isinstance(r.unit_price, Decimal) else Decimal(str(r.unit_price))
        unit = unit.quantize(CENT, rounding=ROUND_HALF_UP)

        line_excl = (qty * unit).quantize(CENT, rounding=ROUND_HALF_UP)
        vat = (line_excl * VAT_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
        line_incl = (line_excl + vat).quantize(CENT, rounding=ROUND_HALF_UP)

        total_excl += line_excl
        total_vat += vat
        total_incl += line_incl

        row_data = {
        "id": r.id,
        "name": r.name,
        "quantity": int(qty),
        "unit_price_excl_vat": str(unit),
        "line_total_excl_vat": str(line_excl),
        "vat_14%": str(vat),
        "line_total_incl_vat": str(line_incl),
        }
        rows_out.append(row_data)

        print(row_data)

    # Final totals (rounded to cents)
    total_excl = total_excl.quantize(CENT, rounding=ROUND_HALF_UP)
    total_vat = total_vat.quantize(CENT, rounding=ROUND_HALF_UP)
    total_incl = total_incl.quantize(CENT, rounding=ROUND_HALF_UP)

    invoice_data = {
        "order_id": invoice.order_id,
        "customer_id": invoice.customer_id,
        "vat_rate": str(VAT_RATE),
        "rows": rows_out,
        "totals": {
        "total_excl_vat": str(total_excl),
        "total_vat": str(total_vat),
        "total_incl_vat": str(total_incl),
        },
    }

    return invoice_data


try:
    while True:
        class InvoiceRow(BaseModel):
            id: str
            name: str
            quantity: int
            unit_price: Decimal

        class InvoiceCreate(BaseModel):
            order_id: str
            customer_id: str
            rows: list[InvoiceRow]

        print("Waiting for messages...")
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            print("No message received")
            continue
        if msg.error():
            raise KafkaException(msg.error())

        print("-----------------")

        payload = msg.value().decode('utf-8')

        try:
            data = json.loads(payload)
            # Parse into Pydantic models (unit_price -> Decimal)
            invoice = InvoiceCreate.parse_obj(data)
        except (json.JSONDecodeError, ValidationError) as e:
            print("Failed to parse invoice:", e)
            continue

        print(f"Handling invoice: {invoice.order_id}")
        invoice_data = calculate_invoice_totals(invoice)
        print("Processed Invoice:", invoice_data)
finally:
    consumer.close()
