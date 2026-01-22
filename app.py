import streamlit as st
import pandas as pd
import io
import os
from extract_invoices import extract_invoice_data
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="Invoice Extractor", page_icon="🧾", layout="wide")

st.title("🧾 Invoice Extraction Tool")
st.markdown("""
Upload PDF invoices to automatically extract details like Date, Invoice No, Seller, and Line Items.
""")

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Invoices"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_rows = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            status_text.text(f"Processing {uploaded_file.name}...")
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Extract data
            # uploaded_file is a BytesIO-like object
            data, line_items = extract_invoice_data(uploaded_file, filename=uploaded_file.name)
            
            # Reset file pointer for potential re-read or safety (though extract closes it usually)
            uploaded_file.seek(0)
            
            # Expand to rows
            if line_items:
                for item in line_items:
                    row = data.copy()
                    row["Tên hàng hóa"] = item.get("name", "")
                    row["Số lượng"] = item.get("qty", "")
                    row["Đơn giá"] = item.get("unit_price", "")
                    row["Thành tiền"] = item.get("amount", "")
                    all_rows.append(row)
            else:
                 all_rows.append(data)
        
        status_text.text("Processing complete!")
        
        # Create DataFrame
        df = pd.DataFrame(all_rows)
        
        # Column order
        columns = [
            "Tên file", "Ngày hóa đơn", "Số hóa đơn", "Đơn vị bán", 
            "Tên hàng hóa", "Số lượng", "Đơn giá", "Thành tiền",
            "Số tiền trước Thuế", "Tiền thuế", "Số tiền sau", "Link lấy hóa đơn",
            "Mã tra cứu", "Mã số thuế", "Mã CQT", "Ký hiệu"
        ]
        # Ensure all columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = ""
                
        df = df[columns]
        
        # Convert money columns to numbers for display/excel
        money_columns = ["Số tiền trước Thuế", "Tiền thuế", "Số tiền sau", "Đơn giá", "Thành tiền"]
        for col in money_columns:
            def convert_to_number(x):
                if pd.isna(x) or x == '':
                    return None
                x_str = str(x).replace('.', '').replace(',', '')
                try:
                    return int(float(x_str))
                except (ValueError, TypeError):
                    return x
            df[col] = df[col].apply(convert_to_number)

        # Display Result
        st.subheader("Extracted Data")
        st.dataframe(df)
        
        # Excel Export Logic
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Hóa đơn")
            
            # Apply formatting
            worksheet = writer.sheets["Hóa đơn"]
            
            # Define Styles
            header_font = Font(bold=True, color="FFFFFF", size=11, name="Arial")
            header_fill = PatternFill("solid", fgColor="4F81BD")  # Professional Blue
            border_style = Side(style='thin', color="000000")
            border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)
            
            # Column widths
            widths = {
                'A': 30, 'B': 12, 'C': 15, 'D': 40,
                'E': 50, 'F': 10, 'G': 15, 'H': 18,
                'I': 18, 'J': 15, 'K': 18, 'L': 15,
                'M': 20, 'N': 15, 'O': 15, 'P': 12
            }
            for col_letter, width in widths.items():
                worksheet.column_dimensions[col_letter].width = width

            # Format Header Row (row 1)
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = border
            
            # Freeze header row
            worksheet.freeze_panes = 'A2'
            
            # Add Filter
            worksheet.auto_filter.ref = worksheet.dimensions
            
            # Columns to merge (invoice-level data - NOT line items E,F,G,H)
            merge_cols = ['A', 'B', 'C', 'D', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
            
            # Find invoice groups by "Tên file" (column A)
            current_file = None
            group_start = 2  # Data starts at row 2
            
            for row_idx in range(2, worksheet.max_row + 2):  # +2 to process last group
                if row_idx <= worksheet.max_row:
                    file_name = worksheet.cell(row=row_idx, column=1).value
                else:
                    file_name = None  # Force end of last group
                
                if file_name != current_file and current_file is not None:
                    # End of group - merge cells from group_start to row_idx-1
                    group_end = row_idx - 1
                    if group_end > group_start:  # Only merge if more than 1 row
                        for col_letter in merge_cols:
                            col_idx = ord(col_letter) - ord('A') + 1
                            
                            # Clear values in cells to be merged (except first) BEFORE merging
                            for r in range(group_start + 1, group_end + 1):
                                worksheet.cell(row=r, column=col_idx).value = None
                            
                            # Now merge cells
                            merge_range = f"{col_letter}{group_start}:{col_letter}{group_end}"
                            try:
                                worksheet.merge_cells(merge_range)
                            except:
                                pass
                            
                            # Set alignment on first cell
                            first_cell = worksheet.cell(row=group_start, column=col_idx)
                            first_cell.alignment = Alignment(vertical="center", horizontal="center" if col_letter in ['B', 'C', 'N', 'P'] else "left", wrap_text=True)
                    
                    group_start = row_idx
                
                current_file = file_name

            # Format Data Rows - borders and number formatting
            money_cols_idx = [7, 8, 9, 10, 11]  # G, H, I, J, K
            center_cols_idx = [2, 3, 6, 14, 16]  # B, C, F, N, P
            
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
                for cell in row:
                    # Skip merged cells (check if cell is MergedCell)
                    if isinstance(cell, openpyxl.cell.cell.MergedCell):
                        continue
                        
                    cell.border = border
                    cell.font = Font(name="Arial", size=10)
                    
                    # Number format for money columns
                    if cell.col_idx in money_cols_idx:
                        cell.number_format = '#,##0'
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                    elif cell.col_idx in center_cols_idx:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    else:
                        # Default alignment for text/other columns
                        # For merged cells, alignment is set during merge, but single rows need it here
                        # Check if column is in merge_cols list to check if it SHOULD have been merged (logic above handles alignment for merged blocks)
                        # But for single-row items, this ensures they are aligned too.
                        col_letter = get_column_letter(cell.col_idx)
                        if col_letter in ['B', 'C', 'N', 'P']:
                             cell.alignment = Alignment(horizontal="center", vertical="center")
                        elif col_letter in ['A', 'D', 'E', 'L', 'M', 'O']:
                             cell.alignment = Alignment(vertical="center", wrap_text=True)

        output.seek(0)
        
        st.download_button(
            label="Download Excel",
            data=output,
            file_name="hoadon_tonghop.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
