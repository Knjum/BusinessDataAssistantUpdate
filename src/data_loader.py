from __future__ import annotations
from io import BytesIO
from pathlib import Path
import pandas as pd

SUPPORTED_EXTENSIONS = {"csv", "xlsx", "xls"}


def load_table(file_name: str, file_bytes: bytes, sheet_name: str | int = 0) -> pd.DataFrame:
    """Load a CSV or Excel workbook into a DataFrame with helpful validation."""
    suffix = Path(file_name).suffix.lower().lstrip(".")
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Định dạng chưa hỗ trợ. Hãy tải lên CSV, XLSX hoặc XLS.")
    if not file_bytes:
        raise ValueError("File trống hoặc không đọc được.")
    try:
        if suffix == "csv":
            try:
                df = pd.read_csv(BytesIO(file_bytes), low_memory=False)
            except UnicodeDecodeError:
                df = pd.read_csv(BytesIO(file_bytes), encoding="latin-1", low_memory=False)
        else:
            df = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name)
    except Exception as exc:
        raise ValueError(f"Không thể đọc file: {exc}") from exc
    if df.empty and len(df.columns) == 0:
        raise ValueError("Không tìm thấy bảng dữ liệu trong file.")
    # Make column names usable while preserving their original meaning.
    df.columns = [str(c).strip() if str(c).strip() else f"column_{i+1}" for i, c in enumerate(df.columns)]
    if df.columns.duplicated().any():
        counts = {}
        new_cols = []
        for col in df.columns:
            counts[col] = counts.get(col, 0) + 1
            new_cols.append(col if counts[col] == 1 else f"{col}_{counts[col]}")
        df.columns = new_cols
    return df
