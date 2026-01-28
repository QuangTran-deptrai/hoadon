import streamlit as st
import pandas as pd
import io
import os
import logging
import sys
from extract_invoices import extract_invoice_data, classify_content
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configure page - MUST be the first Streamlit command
st.set_page_config(page_title="Invoice Extractor", page_icon="🧾", layout="wide")

# Initialize Session State
if "processing_complete" not in st.session_state:
    st.session_state["processing_complete"] = False
if "processed_df" not in st.session_state:
    st.session_state["processed_df"] = None

# User Identification Logic
if "user_name" not in st.session_state:
    st.title("🔐 Xác thực người dùng")
    st.info("Vui lòng nhập tên của bạn để truy cập hệ thống.")
    
    with st.container(border=True):
        name_input = st.text_input("Tên của bạn:", placeholder="Ví dụ: Huy, Lan...")
        if st.button("Bắt đầu làm việc", type="primary"):
            if name_input.strip():
                st.session_state["user_name"] = name_input.strip()
                logger.info(f"--- USER LOGIN: {st.session_state['user_name']} ---")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên để tiếp tục!")

else:
    # --- Main Application Logic ---
    current_user = st.session_state["user_name"]
    
    # Sidebar
    with st.sidebar:
        st.write(f"👤 User: **{current_user}**")
        if st.button("Đăng xuất"):
            logger.info(f"--- USER LOGOUT: {current_user} ---")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # App Title
    st.title("🧾 Invoice Extraction Tool")
    
    # --- WIZARD FLOW ---
    
    if st.session_state["processing_complete"] and st.session_state["processed_df"] is not None:
        # === STEP 3: RESULTS & EXPORT ===
        st.markdown("### ✅ Bước 3: Kết quả xử lý")
        
        # Action Buttons
        col_res1, col_res2 = st.columns([1, 4])
        with col_res1:
            if st.button("⬅️ Làm việc với file khác"):
                # Reset state
                st.session_state["processing_complete"] = False
                st.session_state["processed_df"] = None
                st.rerun()
        
        df = st.session_state["processed_df"]
        
        # Excel Export Logic (Pre-calculated for download button)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Hóa đơn")
            worksheet = writer.sheets["Hóa đơn"]
            
            # Define Styles
            header_font = Font(bold=True, color="FFFFFF", size=11, name="Arial")
            header_fill = PatternFill("solid", fgColor="4F81BD")
            border_style = Side(style='thin', color="000000")
            border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)
            
            # Column widths
            widths = {
                'A': 30, 'B': 12, 'C': 15, 'D': 40, 'E': 18,
                'F': 18, 'G': 12, 'H': 12, 'I': 12, 'J': 12, 'K': 12,
                'L': 12, 'M': 15, 'N': 18, 'O': 15, 'P': 20, 'Q': 15, 'R': 15, 'S': 12
            }
            for col_letter, width in widths.items():
                worksheet.column_dimensions[col_letter].width = width

            # Format Header
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = border
            
            worksheet.freeze_panes = 'A2'
            worksheet.auto_filter.ref = worksheet.dimensions
            
            # Format Data
            money_cols_idx = [6, 7, 8, 9, 10, 11, 12, 13, 14] 
            center_cols_idx = [2, 3, 5, 17, 19]
            
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
                for cell in row:
                    if isinstance(cell, openpyxl.cell.cell.MergedCell): continue
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
        
        with col_res1: # Add download button next to reset
             pass       
            
        st.download_button(
            label="💾 Tải file Excel kết quả",
            data=output,
            file_name="hoadon_tonghop.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

        st.divider()
        st.dataframe(df, use_container_width=True)

    else:
        # === STEP 1 & 2: UPLOAD & PROCESS ===
        st.markdown("### 📂 Bước 1: Tải hóa đơn (PDF)")
        
        uploaded_files = st.file_uploader(
            "Kéo thả hoặc chọn nhiều file PDF vào đây", 
            type="pdf", 
            accept_multiple_files=True
        )

        if uploaded_files:
            st.divider()
            st.markdown("### ⚙️ Bước 2: Xử lý dữ liệu")
            st.write(f"Đã chọn **{len(uploaded_files)}** file.")
            
            if st.button(f"🚀 Bắt đầu trích xuất dữ liệu", type="primary"):
                logger.info(f"--- ACTION: User {current_user} started processing {len(uploaded_files)} files ---")
                
                progress_bar = st.progress(0)
                status_box = st.empty()
                
                all_rows = []
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_box.info(f"⏳ Đang xử lý: **{uploaded_file.name}** ({i+1}/{len(uploaded_files)})")
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    try:
                        data, line_items = extract_invoice_data(uploaded_file, filename=uploaded_file.name)
                        uploaded_file.seek(0)
                        
                        # Classify
                        if line_items:
                            all_item_names = " ".join([item.get("name", "") for item in line_items])
                            data["Phân loại"] = classify_content(all_item_names)
                        else:
                            data["Phân loại"] = "Khác"
                        
                        all_rows.append(data)
                    except Exception as e:
                        logger.error(f"Error processing {uploaded_file.name}: {e}")
                        status_box.error(f"Lỗi khi xử lý {uploaded_file.name}")
                
                status_box.success("✅ Đã xử lý xong tất cả!")
                logger.info(f"--- COMPLETION: User {current_user} finished processing ---")
                
                # Create DataFrame
                df = pd.DataFrame(all_rows)
                
                # Column standardization
                columns = [
                    "Tên file", "Ngày hóa đơn", "Số hóa đơn", "Đơn vị bán", "Phân loại",
                    "Số tiền trước Thuế", "Thuế 0%", "Thuế 5%", "Thuế 8%", "Thuế 10%", "Thuế khác",
                    "Phí PV", "Tiền thuế", "Số tiền sau", "Link lấy hóa đơn",
                    "Mã tra cứu", "Mã số thuế", "Mã CQT", "Ký hiệu"
                ]
                for col in columns:
                    if col not in df.columns:
                        df[col] = ""
                df = df[columns]
                
                # Convert numbers
                money_columns = ["Số tiền trước Thuế", "Thuế 0%", "Thuế 5%", "Thuế 8%", "Thuế 10%", "Thuế khác", "Tiền thuế", "Số tiền sau", "Phí PV"]
                for col in money_columns:
                    def convert_to_number(x):
                        if pd.isna(x) or x == '': return None
                        x_str = str(x).strip()
                        if ',' in x_str and x_str.endswith(',') == False:
                             # Check valid vietnamese currency format if comma is close to end
                             pass
                        
                        # Simple robust cleaning
                        # If comma is decimal separator (2 digits at end), swap. 
                        # Else remove comma/dot and just take int
                        import re
                        if re.search(r',\d{2}$', x_str):
                            x_str = x_str.replace('.', '').replace(',', '.')
                        else:
                            x_str = x_str.replace('.', '').replace(',', '')
                            
                        try:
                            return round(float(x_str))
                        except:
                            return x
                    df[col] = df[col].apply(convert_to_number)
                
                # Save to session state
                st.session_state["processed_df"] = df
                st.session_state["processing_complete"] = True
                st.rerun()
        else:
            st.info("👆 Vui lòng tải file lên để tiếp tục.")
