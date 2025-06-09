import csv
from datetime import datetime
import uuid

def generate_tally_xml_from_bank(csv_path, company_name="Your Company Name"):
    tally_msgs = ""

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            value_date = datetime.strptime(row['Value Date'], "%d-%m-%Y").strftime("%Y%m%d")
            description = row['Description'].strip()
            debit = row['Debit'].replace(',', '').strip()
            credit = row['Credit'].replace(',', '').strip()

            if debit:
                amount = float(debit)
                vch_type = "Payment"
                is_deemed_positive_main = "Yes"
                is_deemed_positive_party = "No"
                main_amount = -amount
                party_amount = amount
            elif credit:
                amount = float(credit)
                vch_type = "Receipt"
                is_deemed_positive_main = "Yes"
                is_deemed_positive_party = "No"
                main_amount = -amount
                party_amount = amount
            else:
                continue  # Skip rows with neither debit nor credit

            bank_uuid = str(uuid.uuid4())

            tally_msgs += f"""
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="{vch_type}" ACTION="Create">
                        <DATE>{value_date}</DATE>
                        <VOUCHERTYPENAME>{vch_type}</VOUCHERTYPENAME>
                        <PARTYLEDGERNAME>Temp1</PARTYLEDGERNAME>
                        <VOUCHERNUMBERSERIES>Default</VOUCHERNUMBERSERIES>
                        <NARRATION>{description}</NARRATION>

                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Temp1</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>{is_deemed_positive_party}</ISDEEMEDPOSITIVE>
                            <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
                            <AMOUNT>{party_amount:.2f}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>

                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Karur Vyshya Bank</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>{is_deemed_positive_main}</ISDEEMEDPOSITIVE>
                            <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
                            <AMOUNT>{main_amount:.2f}</AMOUNT>
                            <BANKALLOCATIONS.LIST>
                                <DATE>{value_date}</DATE>
                                <INSTRUMENTDATE>{value_date}</INSTRUMENTDATE>
                                <NAME>{bank_uuid}</NAME>
                                <TRANSACTIONTYPE>Others</TRANSACTIONTYPE>
                                <PAYMENTFAVOURING>Temp1</PAYMENTFAVOURING>
                                <BANKPARTYNAME>Temp1</BANKPARTYNAME>
                                <AMOUNT>{main_amount:.2f}</AMOUNT>
                            </BANKALLOCATIONS.LIST>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            """

    # Company message
    company_msg = f"""
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
            <COMPANY>
                <REMOTECMPINFO.LIST MERGE="Yes">
                    <NAME>5c2b5700-a8ed-11d9-8626-e5767e127270</NAME>
                    <REMOTECMPNAME>{company_name}</REMOTECMPNAME>
                    <REMOTECMPSTATE>Tamil Nadu</REMOTECMPSTATE>
                </REMOTECMPINFO.LIST>
            </COMPANY>
        </TALLYMESSAGE>
    """

    # Final XML
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
                {tally_msgs.strip()}
                {company_msg.strip()}
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

    with open("tally_bank_import.xml", "w", encoding="utf-8") as out_file:
        out_file.write(final_xml)

    print("✅ Tally XML file 'tally_bank_import.xml' created successfully!")

# Example usage:
generate_tally_xml_from_bank("a1.csv", "Suresh Traders - (from 1-Apr-25)")
