from __future__ import annotations


class RetrievalIncomplete(RuntimeError):
    pass


def completeness_gate(read_statuses: list[str]) -> None:
    """
    Formal report generation is allowed only when every frozen inventory item
    has successfully retrieved official SEAISI body content.
    """
    failed = [status for status in read_statuses if status != "READ_OK"]

    if failed:
        raise RetrievalIncomplete(
            f"{len(failed)} inventory item(s) are not READ_OK"
        )
