from __future__ import annotations
import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = ["_".join(str(c).strip().lower().split()) for c in result.columns]
    return result


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def trim_text(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for col in result.select_dtypes(include=["object", "string"]).columns:
        result[col] = result[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    return result


def fill_missing(df: pd.DataFrame, columns: list[str], method: str, custom_value: str = "") -> pd.DataFrame:
    result = df.copy()
    for col in columns:
        if col not in result.columns:
            raise ValueError(f"Không tìm thấy cột: {col}")
        if method == "Giá trị tùy chỉnh":
            value = custom_value
            if pd.api.types.is_numeric_dtype(result[col]):
                try:
                    value = float(custom_value)
                except ValueError as exc:
                    raise ValueError(f"Cột {col} là kiểu số; hãy nhập giá trị số.") from exc
            result[col] = result[col].fillna(value)
        elif method == "Trung bình" and pd.api.types.is_numeric_dtype(result[col]):
            if result[col].notna().any(): result[col] = result[col].fillna(result[col].mean())
        elif method == "Trung vị" and pd.api.types.is_numeric_dtype(result[col]):
            if result[col].notna().any(): result[col] = result[col].fillna(result[col].median())
        elif method == "Giá trị phổ biến" and result[col].notna().any():
            result[col] = result[col].fillna(result[col].mode(dropna=True).iloc[0])
        elif method == "Giữ nguyên":
            pass
        else:
            if method in {"Trung bình", "Trung vị"}:
                raise ValueError(f"Phương pháp {method} chỉ áp dụng cho cột số: {col}")
    return result
