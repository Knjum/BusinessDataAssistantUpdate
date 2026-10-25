from __future__ import annotations
import pandas as pd


def quality_report(df: pd.DataFrame) -> dict:
    rows, cols = df.shape
    missing_by_col = df.isna().sum().sort_values(ascending=False)
    duplicate_rows = int(df.duplicated().sum()) if rows else 0
    memory_mb = float(df.memory_usage(index=True, deep=True).sum() / (1024 * 1024))
    return {
        "rows": rows,
        "columns": cols,
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": duplicate_rows,
        "memory_mb": round(memory_mb, 2),
        "missing_by_column": missing_by_col[missing_by_col > 0],
        "dtypes": df.dtypes.astype(str),
    }


def issues_table(df: pd.DataFrame) -> pd.DataFrame:
    report = quality_report(df)
    records = []
    for col, count in report["missing_by_column"].items():
        records.append({"Cột": col, "Vấn đề": "Thiếu dữ liệu", "Số lượng": int(count)})
    if report["duplicate_rows"]:
        records.append({"Cột": "Toàn bộ bảng", "Vấn đề": "Dòng trùng lặp", "Số lượng": report["duplicate_rows"]})
    for col in df.select_dtypes(include="number").columns:
        negatives = int((df[col] < 0).sum())
        if negatives:
            records.append({"Cột": col, "Vấn đề": "Giá trị âm (cần kiểm tra theo ngữ cảnh)", "Số lượng": negatives})
    return pd.DataFrame(records, columns=["Cột", "Vấn đề", "Số lượng"])
