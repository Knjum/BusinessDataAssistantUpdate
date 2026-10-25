import pandas as pd
import pytest
from src.data_analyzer import filter_data, sort_data, group_data, add_calculated_column
from src.data_cleaner import drop_duplicate_rows, trim_text
from src.data_quality import quality_report

@pytest.fixture
def sample():
    return pd.DataFrame({"country": ["VN", "JP", "VN", None], "qty": [2, 3, 4, 1], "price": [5.0, 2.0, 5.0, 3.0]})

def test_filter_numeric(sample):
    result = filter_data(sample, "qty", "lớn hơn", "2")
    assert result["qty"].tolist() == [3, 4]

def test_sort_descending(sample):
    result = sort_data(sample, ["qty"], ascending=False)
    assert result["qty"].tolist() == [4, 3, 2, 1]

def test_group_sum(sample):
    result = group_data(sample, ["country"], "qty", "Tổng")
    assert result["tổng_qty"].sum() == 10

def test_calculated_column(sample):
    result = add_calculated_column(sample, "qty", "price", "revenue")
    assert result["revenue"].tolist() == [10.0, 6.0, 20.0, 3.0]

def test_drop_duplicates():
    df = pd.DataFrame({"x": [1, 1, 2]})
    assert len(drop_duplicate_rows(df)) == 2

def test_trim_text():
    result = trim_text(pd.DataFrame({"x": [" a ", None]}))
    assert result.loc[0, "x"] == "a"

def test_quality_counts_missing(sample):
    assert quality_report(sample)["missing_cells"] == 1

def test_invalid_column(sample):
    with pytest.raises(ValueError):
        filter_data(sample, "missing", "bằng", "x")
