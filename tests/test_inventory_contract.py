from datetime import date

import pytest

from seaisi_weekly_reader.inventory import InventoryItem, validate_inventory
from seaisi_weekly_reader.retrieval import RetrievalIncomplete, completeness_gate


def test_valid_inventory():
    validate_inventory([
        InventoryItem(
            published_date=date(2026, 8, 17),
            title="Example",
            detail_url="https://www.seaisi.org/details/28280?type=news-rooms",
            read_status="READ_OK",
        )
    ])


def test_rejects_non_seaisi_url():
    with pytest.raises(ValueError):
        validate_inventory([
            InventoryItem(
                published_date=date(2026, 8, 17),
                title="Example",
                detail_url="https://example.com/article",
                read_status="READ_OK",
            )
        ])


def test_completeness_gate_blocks_non_read_ok():
    with pytest.raises(RetrievalIncomplete):
        completeness_gate(["READ_OK", "FAILED"])
