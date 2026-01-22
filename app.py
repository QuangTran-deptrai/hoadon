import streamlit as st
import pandas as pd
import io
import os
from extract_invoices import extract_invoice_data, classify_content
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="Invoice Extractor", page_icon="🧾", layout="wide")

st.title("🧾 Invoice Extraction Tool")
st.markdown("""
Upload PDF invoices to automatically extract and categorize invoice data.
""")

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Invoices"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_rows = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            data, line_items = extract_invoice_data(uploaded_file, filename=uploaded_file.name)
            uploaded_file.seek(0)
            
            # Classify invoice based on line items
            if line_items:
                all_item_names = " ".join([item.get("name", "") for item in line_items])
                data["Phân loại"] = classify_content(all_item_names)
            else:
                data["Phân loại"] = "Khác"
            
            all_rows.append(data)
        
        status_text.text("Processing complete!")
        
        # Create DataFrame
        df = pd.DataFrame(all_rows)
        
        # Column order (simplified - no qty/price/amount)
        columns = [
            "Tên file", "Ngày hóa đơn", "Số hóa đơn", "Đơn vị bán", "Phân loại",
            "Số tiền trước Thuế", "Tiền thuế", "Số tiền sau", "Link lấy hóa đơn",
            "Mã tra cứu", "Mã số thuế", "Mã CQT", "Ký hiệu"
        ]
        for col in columns:
            if col not in df.columns:
                df[col] = ""
                
        df = df[columns]
        
        # Convert money columns to numbers
        money_columns = ["Số tiền trước Thuế", "Tiền thuế", "Số tiền sau"]
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
            
            worksheet = writer.sheets["Hóa đơn"]
            
            # Define Styles
            header_font = Font(bold=True, color="FFFFFF", size=11, name="Arial")
            header_fill = PatternFill("solid", fgColor="4F81BD")
            border_style = Side(style='thin', color="000000")
            border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)
            
            # Column widths for simplified layout
            widths = {
                'A': 30, 'B': 12, 'C': 15, 'D': 40, 'E': 18,
                'F': 18, 'G': 15, 'H': 18, 'I': 15,
                'J': 20, 'K': 15, 'L': 15, 'M': 12
            }
            for col_letter, width in widths.items():
                worksheet.column_dimensions[col_letter].width = width

            # Format Header Row
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = border
            
            # Freeze header row
            worksheet.freeze_panes = 'A2'
            
            # Add Filter
            worksheet.auto_filter.ref = worksheet.dimensions
            
            # Format Data Rows
            money_cols_idx = [6, 7, 8]  # F, G, H
            center_cols_idx = [2, 3, 5, 11, 13]  # B, C, E, K, M
            
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
                for cell in row:
                    if isinstance(cell, openpyxl.cell.cell.MergedCell):
                        continue
                    cell.border = border
                    cell.font = Font(name="Arial", size=10)
                    
                    if cell.col_idx in money_cols_idx:
                        cell.number_format = '#,##0'
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                    elif cell.col_idx in center_cols_idx:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    else:
                        cell.alignment = Alignment(vertical="center", wrap_text=True)

        output.seek(0)
        
        st.download_button(
            label="Download Excel",
            data=output,
            file_name="hoadon_tonghop.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
