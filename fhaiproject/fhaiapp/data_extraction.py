import pdfplumber
import csv
import os

# File paths
pdf_path = "fhaiproject/IFCT2017.pdf"
output_folder = "ifct_tables"
os.makedirs(output_folder, exist_ok=True)

# Define page range (1-based indexing)
start_page = 41
end_page = 475

with pdfplumber.open(pdf_path) as pdf:
    table_counter = 1
    for page_number in range(start_page, end_page + 1):
        page = pdf.pages[page_number - 1]  # zero-based index in pdfplumber
        tables = page.extract_tables()

        for table in tables:
            if not table or len(table) < 2:
                continue  # Skip empty/malformed tables

            output_file = os.path.join(
                output_folder, f"table_{table_counter}_page_{page_number}.csv"
            )
            
            with open("food_data.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in table:
                    writer.writerow([cell.strip() if cell else "" for cell in row])

            print(f"✅ Saved Table {table_counter} from Page {page_number} to: {output_file}")
            table_counter += 1

print(f"\n✅ Extracted {table_counter - 1} tables from pages {start_page} to {end_page}.")
