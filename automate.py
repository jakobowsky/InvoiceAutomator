import requests
from dataclasses import dataclass
from typing import List
import os
import csv
import typer


@dataclass
class Invoice:
    from_who: str
    to_who: str
    logo: str
    number: str
    date: str
    due_date: str
    items: List[dict]
    notes: str


class CSVParser:
    def __init__(self, csv_name: str) -> None:
        self.field_names = (
            'from_who',
            'to_who',
            'logo',
            'number',
            'date',
            'due_date',
            'items',
            'notes'
        )
        self.csv_name = csv_name

    def get_array_of_invoices(self) -> List[Invoice]:
        with open(self.csv_name, 'r') as f:
            reader = csv.DictReader(f, self.field_names)
            header = 0
            current_csv = []
            for row in reader:
                if header == 0:
                    header += 1
                    continue
                invoice_obj = Invoice(**row)
                invoice_obj.items = eval(invoice_obj.items)
                current_csv.append(invoice_obj)
        return current_csv


class ApiConnector:
    def __init__(self) -> None:
        self.headers = {"Content-Type": "application/json"}
        self.url = 'https://invoice-generator.com'
        self.invoices_directory = f"{os.path.dirname(os.path.abspath(__file__))}/{'invoices'}"

    def connect_to_api_and_save_invoice_pdf(self, invoice: Invoice) -> None:
        invoice_parsed = {
            'from': invoice.from_who,
            'to': invoice.to_who,
            'logo': invoice.logo,
            'number': invoice.number,
            'date': invoice.date,
            'due_date': invoice.due_date,
            'items': invoice.items,
            'notes': invoice.notes
        }
        r = requests.post(self.url, json=invoice_parsed, headers=self.headers)
        if r.status_code == 200 or r.status_code == 201:
            pdf = r.content
            self.save_invoice_to_pdf(pdf, invoice)
            typer.echo("File Saved")
        else:
            typer.echo("Fail :", r.text)

    def save_invoice_to_pdf(self, pdf_content: str, invoice: Invoice) -> None:
        invoice_name = f"{invoice.number}_invoice.pdf"
        invoice_path = f"{self.invoices_directory}/{invoice_name}"
        with open(invoice_path, 'wb') as f:
            typer.echo(f"Generate invoice for {invoice_name}")
            f.write(pdf_content)


def main(csv_name: str = typer.Argument('invoices.csv')):
    typer.echo(f"Running script with - {csv_name}")
    csv_reader = CSVParser(csv_name)
    array_of_invoices = csv_reader.get_array_of_invoices()
    api = ApiConnector()
    for invoice in array_of_invoices:
        api.connect_to_api_and_save_invoice_pdf(invoice)


if __name__ == "__main__":
    typer.run(main)
