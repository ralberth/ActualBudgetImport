# ActualBudgetImport

Convert various broken CSV formats from systems like Venmo into something Actual Budget can import.



# Fidelity HSA

See `samples/sample_fidelity_hsa_export.csv` for an example.

The export files from Fidelity have several annoyances that we need to correct:

1. Everything is in all-uppercase (like the world still runs on COBOL...)
2. A description value of "No Description" means there shouldn't be anything in the cell
3. There's blank lines at the top for no good reason
4. There's a large block of text below the actual data that's human instructions and disclaimers
5. There are non-ASCII, unprintable characters in some rows ("Wegmans" below)
6. It puts "`(cash)`" at the end of `Action` values when there's already a `Type` column to cover that


Sample input data (with useless lines removed):

```csv
Run Date,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Cash Balance ($),Settlement Date
05/28/2026,"DEBIT CARD PURCHASE WEGMANS #007 (Cash)",,"No Description",Cash,,0.000,,,,-12,388.76,
```

What this is turned into:

| Date       | Payee                           | Notes | Amount
| ---------- | ------------------------------- | ----- | ------------------
| 05/28/2026 | Debit card purchase wegmans 007 |       | -12



# Venmo

See `samples/sample_venmo_export.csv` for an example.

Venmo files are several lines.  Breakdown:

## Lines 1 and 2

```csv
Account Statement - (@Joe-Smith) ,,,,,,,,,,,,,,,,,,,,,
Account Activity,,,,,,,,,,,,,,,,,,,,,
```

Header rows we use to confirm that the input file is a Venmo file.  These rows are ignored and not put in the output file.


## Line 3:  Column Headers

```csv
,ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,Terminal Location,Year to Date Venmo Fees,Disclaimer
```

Typical CSV header row.  This is used to decode the other rows in the file.  We use Python's `csv.DictReader` so all subsequent rows are parsed correctly, even if the column header changes over time.

Not all columns are brought into the output file.


## Data Rows

All other rows are data rows that adhere to the Column Headers row above.  However, the first and last are not important to us because they only have the beginning balance and ending balance.

To be flexible, the code doesn't single these out by their row number in the file.  It just ignores rows that don't have key fields we need to import into Actual Budget.

This makes it simpler to ignore the last row too, that has a value for the column `Disclaimer` which is a large text block, multiple lines long.

Data rows we actually care about:

```csv
,4478090889072638831,2025-12-01T14:07:13,Payment,Complete,Refund of retainer,Jane Doe,Joe Smith,+ $500.00,,0,,0,,,Venmo balance,,,,Venmo,,
,4481810063397712371,2025-12-06T17:16:33,Payment,Complete,6 magnets,Joe Smith,Tim Jones,- $25.00,,0,,0,,Venmo balance,,,,,Venmo,,
,4499369161559541579,2025-12-30T22:43:21,Payment,Complete,"Haircut, color, tip",Joe Smith,Jane Rogers,- $95.00,,0,,0,,Venmo balance,,,,,Venmo,,
```

The fields we use:

* Datetime
* Note
* From/To
* Amount (total)

Reduced, these are the rows that matter from the sample file:

| Datetime            | Note                  | From      | To          | Amount (total)
| ------------------- | --------------------- | --------- | ----------- | --------------
| 2025-12-01T14:07:13 | Refund of retainer    | Jane Doe  | Joe Smith   | + $500.00
| 2025-12-06T17:16:33 | 6 magnets             | Joe Smith | Tim Jones   | - $25.00
| 2025-12-30T22:43:21 | "Haircut, color, tip" | Joe Smith | Jane Rogers | - $95.00

The datetime field is ISO formatted, but Actual Budget can't parse that (LOSE!).  Convert it to "YYYY MM DD".

Note is left alone and included as "Note".

From/To both are processed together.  Payments use the header name as From and the Payee as the To column.  Deposits are the opposite.  This uses the column value that isn't the name from the header row as the output Payee column.

Amount is left intact with the "$" stripped-out.


## Running

Pass the input files as comment line parameters and use the "`-o`" switch to name the output file.

Exmaple:

```bash
python convert.py venmo \
    -o all_2025_fixed.csv \
    VenmoStatement_Sep_2025.csv \
    VenmoStatement_Oct_2025.csv \
    VenmoStatement_Nov_2025.csv \
    VenmoStatement_Dec_2025.csv
```
