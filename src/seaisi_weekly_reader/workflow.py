from __future__ import annotations

from .boundary import previous_complete_cycle
from .inventory import InventoryItem, validate_inventory
from .retrieval import completeness_gate


def validate_run(items: list[InventoryItem]):
    boundary = previous_complete_cycle()
    validate_inventory(items)
    completeness_gate([item.read_status for item in items])
    return boundary
