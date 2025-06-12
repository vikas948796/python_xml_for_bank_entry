import csv
from datetime import datetime
import uuid

def generate_tally_xml_from_bank(csv_path, company_name="Your Company Name"):
    tally_msgs = ""

    with open(csv_path, newline='', encoding='utf-8') as f:
        # Detect header row dynamically
        headers_found = False
        while not headers_found:
            pos = f.tell()
            line = f.readline()
            if all(h in line for h in ['Transaction Date', 'Value Date', 'Branch', 'Cheque No.', 'Description', 'Debit', 'Credit', 'Balance']):
                f.seek(pos)  # Go back to start of the header line
                headers_found = True

        # Initialize DictReader after header row is found
        reader = csv.DictReader(f)

        for row in reader:
            try:
                value_date_raw = row['Value Date'].strip()
                if not value_date_raw:
                    continue  # Skip rows with empty date
                value_date = datetime.strptime(value_date_raw, "%d-%m-%Y").strftime("%Y%m%d")
                description = row['Description'].strip()
                debit = row['Debit'].replace(',', '').strip()
                credit = row['Credit'].replace(',', '').strip()
                amount = 0.0
                bank_uuid = str(uuid.uuid4())

                if debit:
                    amount = float(debit)
                    tally_msgs += f"""
<TALLYMESSAGE xmlns:UDF="TallyUDF">
 <VOUCHER VCHTYPE="Payment" ACTION="Create">
  <DATE>{value_date}</DATE>
  <GUID>{bank_uuid}</GUID>
  <NARRATION>{description}</NARRATION>
  <VOUCHERTYPENAME>Payment</VOUCHERTYPENAME>
  <PARTYLEDGERNAME>Temp1</PARTYLEDGERNAME>
  <VOUCHERTYPEORIGNAME>Payment</VOUCHERTYPEORIGNAME>
  <ALLLEDGERENTRIES.LIST>
   <LEDGERNAME>Temp1</LEDGERNAME>
   <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
   <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
   <AMOUNT>-{amount:.2f}</AMOUNT>
  </ALLLEDGERENTRIES.LIST>
  <ALLLEDGERENTRIES.LIST>
   <LEDGERNAME>Karur Vyshya Bank</LEDGERNAME>
   <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
   <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
   <AMOUNT>{amount:.2f}</AMOUNT>
   <BANKALLOCATIONS.LIST>
    <DATE>{value_date}</DATE>
    <INSTRUMENTDATE>{value_date}</INSTRUMENTDATE>
    <TRANSACTIONTYPE>Inter Bank Transfer</TRANSACTIONTYPE>
    <PAYMENTFAVOURING>Temp1</PAYMENTFAVOURING>
    <TRANSFERMODE>NEFT</TRANSFERMODE>
    <AMOUNT>{amount:.2f}</AMOUNT>
   </BANKALLOCATIONS.LIST>
  </ALLLEDGERENTRIES.LIST>
 </VOUCHER>
</TALLYMESSAGE>
"""
                elif credit:
                    amount = float(credit)
                    tally_msgs += f"""
<TALLYMESSAGE xmlns:UDF="TallyUDF">
    <VOUCHER VCHTYPE="Receipt" ACTION="Create">
        <DATE>{value_date}</DATE>
        <VOUCHERTYPENAME>Receipt</VOUCHERTYPENAME>
        <PARTYLEDGERNAME>Temp1</PARTYLEDGERNAME>
        <VOUCHERNUMBERSERIES>Default</VOUCHERNUMBERSERIES>
        <NARRATION>{description}</NARRATION>
        <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>Temp1</LEDGERNAME>
            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
            <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
            <AMOUNT>{amount:.2f}</AMOUNT>
        </ALLLEDGERENTRIES.LIST>
        <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>Karur Vyshya Bank</LEDGERNAME>
            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
            <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
            <AMOUNT>-{amount:.2f}</AMOUNT>
            <BANKALLOCATIONS.LIST>
                <DATE>{value_date}</DATE>
                <INSTRUMENTDATE>{value_date}</INSTRUMENTDATE>
                <NAME>{bank_uuid}</NAME>
                <TRANSACTIONTYPE>Others</TRANSACTIONTYPE>
                <PAYMENTFAVOURING>Temp1</PAYMENTFAVOURING>
                <BANKPARTYNAME>Temp1</BANKPARTYNAME>
                <AMOUNT>-{amount:.2f}</AMOUNT>
            </BANKALLOCATIONS.LIST>
        </ALLLEDGERENTRIES.LIST>
    </VOUCHER>
</TALLYMESSAGE>
"""
                else:
                    continue  # Skip rows with neither debit nor credit
            except Exception as e:
                print(f"⚠️ Skipping row due to error: {e}")

    # Company message block
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

    # Final XML output
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
