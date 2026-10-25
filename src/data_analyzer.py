from __future__ import annotations
import pandas as pd


def filter_data(df: pd.DataFrame, column: str, operator: str, value: str) -> pd.DataFrame:
    if column not in df.columns: raise ValueError(f"Không tìm thấy cột: {column}")
    series = df[column]
    if operator in {"lớn hơn", "nhỏ hơn", "bằng số", "khác số"}:
        if not pd.api.types.is_numeric_dtype(series):
            raise ValueError("Toán tử so sánh số chỉ dùng cho cột số.")
        try: number = float(value)
        except ValueError as exc: raise ValueError("Hãy nhập một giá trị số hợp lệ.") from exc
        mask = {"lớn hơn": series > number, "nhỏ hơn": series < number,
                "bằng số": series == number, "khác số": series != number}[operator]
    elif operator == "chứa":
        mask = series.astype("string").str.contains(value, case=False, na=False, regex=False)
    elif operator == "bằng":
        mask = series.astype("string") == value
    elif operator == "khác":
        mask = series.astype("string") != value
    elif operator == "bị thiếu": mask = series.isna()
    elif operator == "không bị thiếu": mask = series.notna()
    else: raise ValueError("Điều kiện lọc chưa được hỗ trợ.")
    return df.loc[mask].copy()


def sort_data(df: pd.DataFrame, columns: list[str], ascending: bool = True) -> pd.DataFrame:
    if not columns: raise ValueError("Hãy chọn ít nhất một cột để sắp xếp.")
    missing = [c for c in columns if c not in df.columns]
    if missing: raise ValueError(f"Không tìm thấy cột: {', '.join(missing)}")
    return df.sort_values(columns, ascending=ascending, na_position="last", kind="stable").reset_index(drop=True)


def group_data(df: pd.DataFrame, group_columns: list[str], value_column: str | None, operation: str) -> pd.DataFrame:
    if not group_columns: raise ValueError("Hãy chọn ít nhất một cột nhóm.")
    missing = [c for c in group_columns if c not in df.columns]
    if missing: raise ValueError(f"Không tìm thấy cột: {', '.join(missing)}")
    if operation == "Đếm dòng":
        return df.groupby(group_columns, dropna=False).size().reset_index(name="số_dòng")
    if not value_column or value_column not in df.columns: raise ValueError("Hãy chọn cột cần tính.")
    if operation != "Đếm giá trị" and not pd.api.types.is_numeric_dtype(df[value_column]):
        raise ValueError("Phép tính này cần cột số. Hãy chọn cột số hoặc dùng Đếm giá trị.")
    funcs = {"Tổng": "sum", "Trung bình": "mean", "Trung vị": "median", "Nhỏ nhất": "min", "Lớn nhất": "max", "Đếm giá trị": "count"}
    if operation not in funcs: raise ValueError("Phép tính chưa được hỗ trợ.")
    return df.groupby(group_columns, dropna=False)[value_column].agg(funcs[operation]).reset_index(name=f"{operation.lower()}_{value_column}")


def add_calculated_column(df: pd.DataFrame, left: str, right: str, result_name: str) -> pd.DataFrame:
    if left not in df.columns or right not in df.columns: raise ValueError("Không tìm thấy cột đầu vào.")
    if not pd.api.types.is_numeric_dtype(df[left]) or not pd.api.types.is_numeric_dtype(df[right]):
        raise ValueError("Hai cột đầu vào phải là kiểu số.")
    name = result_name.strip()
    if not name: raise ValueError("Hãy nhập tên cột kết quả.")
    result = df.copy()
    result[name] = result[left] * result[right]
    return result
