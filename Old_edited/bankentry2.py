import csv
from datetime import datetime

def generate_tally_xml_from_bank(csv_path, company_name="Your Company Name"):
    tally_msgs = ""

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            value_date = datetime.strptime(row['Value Date'], "%d-%m-%Y").strftime("%d%m%Y")
            description = row['Description'].strip()
            debit = row['Debit'].replace(',', '').strip()
            credit = row['Credit'].replace(',', '').strip()

            # Determine voucher type
            if debit:
                amount = debit
                vch_type = "Payment"
                narration = "Temp Payment"
            elif credit:
                amount = credit
                vch_type = "Receipt"
                narration = "Temp Receipt"
            else:
                continue  # Skip rows with neither Debit nor Credit

            # Build XML
            tally_msgs += f"""
            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                <VOUCHER VCHTYPE="{vch_type}" ACTION="Create">
                    <DATE>{value_date}</DATE>
                    <VOUCHERTYPENAME>{vch_type}</VOUCHERTYPENAME>
                    <PARTYLEDGERNAME>Karur Vyshya Bank</PARTYLEDGERNAME>
                    <NARRATION>{description}</NARRATION>
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>Temp1</LEDGERNAME>
                        <AMOUNT>{amount}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
                </VOUCHER>
            </TALLYMESSAGE>
            """

    final_xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                {tally_msgs}
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

    with open("tally_bank_import.xml", "w", encoding="utf-8") as out_file:
        out_file.write(final_xml)

    print("✅ Tally XML file 'tally_bank_import.xml' created successfully!")

# Example usage:
generate_tally_xml_from_bank("a1.csv", "Suresh Traders")
