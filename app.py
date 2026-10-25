from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.data_loader import load_table
from src.data_quality import quality_report, issues_table
from src.data_cleaner import drop_duplicate_rows, trim_text, fill_missing, clean_column_names
from src.data_analyzer import filter_data, sort_data, group_data, add_calculated_column
from src.exporter import export_csv, export_excel
from src.ai_assistant import ask_data_question
from src.db import get_engine, initialize_database

load_dotenv()
st.set_page_config(page_title="BDA · Trợ lý dữ liệu", page_icon="📊", layout="wide")
st.title("📊 Business Data Assistant")
st.caption("Trợ lý dữ liệu dễ dùng cho học tập và công việc — tải lên, hiểu dữ liệu, phân tích và xuất kết quả.")

with st.sidebar:
    st.header("Bắt đầu")
    st.write("1. Tải CSV hoặc Excel lên.\n2. Xem báo cáo chất lượng.\n3. Chọn công cụ hoặc hỏi AI.\n4. Tải kết quả về máy.")
    st.divider()
    st.caption("Dữ liệu tải lên được xử lý trong phiên ứng dụng. Không tải dữ liệu nhạy cảm lên máy chủ chưa được bạn tin cậy.")

uploaded = st.file_uploader("Chọn file dữ liệu", type=["csv", "xlsx", "xls"], help="Có thể cấu hình giới hạn upload trong .streamlit/config.toml. File lớn vẫn cần đủ RAM và dung lượng xử lý.")
if uploaded is None:
    st.info("Tải lên một file CSV hoặc Excel để bắt đầu.")
    sample_path = Path("data/sample/sales_demo.csv")
    if sample_path.exists() and st.button("Dùng dữ liệu mẫu để thử"):
        st.session_state["bda_df"] = pd.read_csv(sample_path)
        st.session_state["bda_name"] = sample_path.name
    else:
        st.markdown("**BDA hỗ trợ:** kiểm tra dữ liệu, làm sạch, lọc, sắp xếp, nhóm, công thức, biểu đồ, xuất CSV/Excel và trợ lý AI tùy cấu hình.")
if uploaded is not None:
    try:
        df = load_table(uploaded.name, uploaded.getvalue())
        st.session_state["bda_df"] = df
        st.session_state["bda_name"] = uploaded.name
    except Exception as exc:
        st.error(str(exc))

if "bda_df" in st.session_state:
    original = st.session_state["bda_df"]
    if not isinstance(original, pd.DataFrame):
        original = pd.DataFrame(original)
    st.subheader(f"Dữ liệu: {st.session_state.get('bda_name', 'dataset')}")
    report = quality_report(original)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Số dòng", f"{report['rows']:,}")
    c2.metric("Số cột", f"{report['columns']:,}")
    c3.metric("Ô trống", f"{report['missing_cells']:,}")
    c4.metric("Dòng trùng", f"{report['duplicate_rows']:,}")
    with st.expander("Xem trước dữ liệu", expanded=True):
        st.dataframe(original.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Bộ nhớ ước tính trong RAM: {report['memory_mb']:.2f} MB. Đây không phải kích thước file trên ổ đĩa.")
    tab_quality, tab_clean, tab_filter, tab_analysis, tab_ai, tab_db, tab_export = st.tabs(["Chất lượng", "Làm sạch", "Lọc & sắp xếp", "Phân tích", "Hỏi AI", "Database", "Xuất file"])
    with tab_quality:
        st.write("### Các vấn đề cần xem xét")
        issues = issues_table(original)
        if issues.empty: st.success("Chưa phát hiện vấn đề cơ bản từ các kiểm tra hiện có. Điều này không bảo đảm dữ liệu hoàn toàn chính xác.")
        else: st.dataframe(issues, use_container_width=True, hide_index=True)
        st.write("### Kiểu dữ liệu")
        st.dataframe(pd.DataFrame({"Cột": original.columns, "Kiểu dữ liệu": [str(original[c].dtype) for c in original.columns], "Giá trị khác nhau": [int(original[c].nunique(dropna=True)) for c in original.columns]}), use_container_width=True, hide_index=True)
    with tab_clean:
        st.write("Thao tác tạo ra bản kết quả mới; dữ liệu gốc đang tải lên không bị sửa tại chỗ.")
        action = st.selectbox("Bạn muốn làm gì?", ["Xóa dòng trùng lặp", "Xóa khoảng trắng văn bản", "Chuẩn hóa tên cột", "Xử lý ô trống"])
        if action == "Xóa dòng trùng lặp":
            result = drop_duplicate_rows(original)
            st.write(f"Dòng sẽ bị loại: {len(original)-len(result):,}")
        elif action == "Xóa khoảng trắng văn bản": result = trim_text(original)
        elif action == "Chuẩn hóa tên cột": result = clean_column_names(original)
        else:
            cols = st.multiselect("Chọn cột", list(original.columns))
            method = st.selectbox("Cách xử lý", ["Giữ nguyên", "Giá trị phổ biến", "Trung bình", "Trung vị", "Giá trị tùy chỉnh"])
            custom = st.text_input("Giá trị tùy chỉnh", "Chưa rõ") if method == "Giá trị tùy chỉnh" else ""
            result = fill_missing(original, cols, method, custom) if cols else original.copy()
        st.dataframe(result.head(100), use_container_width=True, hide_index=True)
        if st.button("Dùng kết quả làm dữ liệu hiện tại", key="apply_clean"):
            st.session_state["bda_df"] = result
            st.success("Đã cập nhật dữ liệu trong phiên hiện tại. File gốc trên máy bạn không bị thay đổi.")
            st.rerun()
    with tab_filter:
        col = st.selectbox("Cột lọc", list(original.columns), key="filter_col")
        op = st.selectbox("Điều kiện", ["chứa", "bằng", "khác", "lớn hơn", "nhỏ hơn", "bằng số", "khác số", "bị thiếu", "không bị thiếu"])
        val = st.text_input("Giá trị so sánh", disabled=op in {"bị thiếu", "không bị thiếu"})
        if st.button("Lọc dữ liệu"):
            try:
                filtered = filter_data(original, col, op, val)
                st.session_state["bda_result"] = filtered
                st.success(f"Còn {len(filtered):,} / {len(original):,} dòng.")
                st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)
            except Exception as exc: st.error(str(exc))
        st.divider()
        sort_cols = st.multiselect("Sắp xếp theo cột", list(original.columns), key="sort_cols")
        ascending = st.radio("Thứ tự", ["Tăng dần", "Giảm dần"], horizontal=True) == "Tăng dần"
        if st.button("Sắp xếp dữ liệu"):
            try:
                sorted_df = sort_data(original, sort_cols, ascending)
                st.session_state["bda_result"] = sorted_df
                st.dataframe(sorted_df.head(500), use_container_width=True, hide_index=True)
            except Exception as exc: st.error(str(exc))
    with tab_analysis:
        st.write("### Nhóm và tổng hợp")
        groups = st.multiselect("Nhóm theo cột", list(original.columns), key="group_cols")
        numeric_cols = list(original.select_dtypes(include="number").columns)
        value_col = st.selectbox("Cột cần tính", ["(không cần — đếm dòng)"] + list(original.columns), key="group_value")
        operation = st.selectbox("Phép tính", ["Đếm dòng", "Tổng", "Trung bình", "Trung vị", "Nhỏ nhất", "Lớn nhất", "Đếm giá trị"])
        if st.button("Chạy phân tích"):
            try:
                val_col = None if operation == "Đếm dòng" else value_col
                if val_col == "(không cần — đếm dòng)": val_col = None
                result = group_data(original, groups, val_col, operation)
                st.session_state["bda_result"] = result
                st.dataframe(result, use_container_width=True, hide_index=True)
                if len(result.columns) >= 2:
                    possible = [c for c in result.columns if pd.api.types.is_numeric_dtype(result[c])]
                    if possible:
                        y = st.selectbox("Cột biểu đồ", possible, key="chart_y")
                        x_candidates = [c for c in result.columns if c != y]
                        if x_candidates:
                            x = st.selectbox("Nhóm trên trục ngang", x_candidates, key="chart_x")
                            st.plotly_chart(px.bar(result.head(50), x=x, y=y), use_container_width=True)
            except Exception as exc: st.error(str(exc))
        st.divider()
        st.write("### Tạo cột doanh thu / công thức nhân")
        c_left, c_right = st.columns(2)
        left = c_left.selectbox("Cột số thứ nhất", numeric_cols, key="calc_left") if numeric_cols else None
        right = c_right.selectbox("Cột số thứ hai", numeric_cols, key="calc_right") if numeric_cols else None
        new_name = st.text_input("Tên cột kết quả", "doanh_thu")
        if st.button("Tạo cột bằng phép nhân"):
            if left and right:
                try:
                    result = add_calculated_column(original, left, right, new_name)
                    st.session_state["bda_result"] = result
                    st.dataframe(result.head(100), use_container_width=True, hide_index=True)
                except Exception as exc: st.error(str(exc))
            else: st.warning("File chưa có cột số phù hợp.")
    with tab_ai:
        st.write("Hãy hỏi về cấu trúc dữ liệu hoặc yêu cầu gợi ý phân tích. AI chưa tự thực thi các thao tác thay đổi dữ liệu.")
        question = st.text_area("Câu hỏi", placeholder="Ví dụ: Tôi nên phân tích doanh thu theo quốc gia như thế nào?")
        if st.button("Hỏi trợ lý AI"):
            if not question.strip(): st.warning("Hãy nhập câu hỏi trước.")
            else:
                with st.spinner("Đang phân tích..."):
                    st.markdown(ask_data_question(question, original))
    with tab_db:
        st.write("Kết nối PostgreSQL tùy chọn. BDA không tự tải toàn bộ nội dung file lên database.")
        engine = None
        try: engine = get_engine()
        except Exception as exc: st.error(f"Cấu hình database chưa hợp lệ: {exc}")
        if engine is None:
            st.info("Chưa cấu hình DATABASE_URL. Sao chép .env.example thành .env và điền chuỗi kết nối PostgreSQL để bật.")
        else:
            if st.button("Kiểm tra kết nối và tạo bảng BDA"):
                try:
                    initialize_database(engine)
                    st.success("Kết nối thành công và các bảng metadata đã được khởi tạo.")
                except Exception as exc: st.error(f"Không thể khởi tạo database: {exc}")
    with tab_export:
        result = st.session_state.get("bda_result", original)
        st.write(f"Bảng sẽ xuất: {len(result):,} dòng, {len(result.columns):,} cột.")
        st.download_button("Tải CSV", data=export_csv(result), file_name="bda_result.csv", mime="text/csv", use_container_width=True)
        st.download_button("Tải Excel", data=export_excel(result), file_name="bda_result.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        if st.button("Xóa kết quả tạm, quay về dữ liệu hiện tại"):
            st.session_state.pop("bda_result", None)
            st.rerun()
