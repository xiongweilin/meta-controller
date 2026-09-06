from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class MetaPolicyEvent:
    id: str
    event_type: str
    controller_ref: str
    kernel_state_version: int
    policy_version: str
    payload: dict[str, object]
    basis_refs: tuple[str, ...]
    created_at: datetime


class MetaPolicyJournal:
    """Append-only durable policy journal that never owns runtime truth or authority."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS meta_policy_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    controller_ref TEXT NOT NULL,
                    kernel_state_version INTEGER NOT NULL,
                    policy_version TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    basis_refs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_meta_policy_events_controller
                ON meta_policy_events(controller_ref, sequence)
                """
            )

    def record(
        self,
        *,
        event_type: str,
        controller_ref: str,
        kernel_state_version: int,
        policy_version: str,
        payload: dict[str, object] | None = None,
        basis_refs: tuple[str, ...] = (),
    ) -> MetaPolicyEvent:
        if not event_type.strip() or not controller_ref.strip() or not policy_version.strip():
            raise ValueError("event_type, controller_ref and policy_version must be non-empty")
        if kernel_state_version < 0:
            raise ValueError("kernel_state_version cannot be negative")
        event = MetaPolicyEvent(
            id=f"meta_event_{uuid4().hex}",
            event_type=event_type,
            controller_ref=controller_ref,
            kernel_state_version=kernel_state_version,
            policy_version=policy_version,
            payload=dict(payload or {}),
            basis_refs=tuple(basis_refs),
            created_at=datetime.now(UTC),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO meta_policy_events (
                    id, event_type, controller_ref, kernel_state_version,
                    policy_version, payload_json, basis_refs_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.event_type,
                    event.controller_ref,
                    event.kernel_state_version,
                    event.policy_version,
                    json.dumps(event.payload, ensure_ascii=False, sort_keys=True),
                    json.dumps(event.basis_refs, ensure_ascii=False),
                    event.created_at.isoformat(),
                ),
            )
        return event

    def list_events(
        self,
        *,
        controller_ref: str | None = None,
        event_type: str | None = None,
    ) -> tuple[MetaPolicyEvent, ...]:
        clauses: list[str] = []
        values: list[object] = []
        if controller_ref is not None:
            clauses.append("controller_ref = ?")
            values.append(controller_ref)
        if event_type is not None:
            clauses.append("event_type = ?")
            values.append(event_type)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM meta_policy_events{where} ORDER BY sequence ASC"
        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def _from_row(self, row: sqlite3.Row) -> MetaPolicyEvent:
        payload = json.loads(str(row["payload_json"]))
        basis_refs = json.loads(str(row["basis_refs_json"]))
        if not isinstance(payload, dict) or not isinstance(basis_refs, list):
            raise ValueError("invalid persisted meta-policy event")
        return MetaPolicyEvent(
            id=str(row["id"]),
            event_type=str(row["event_type"]),
            controller_ref=str(row["controller_ref"]),
            kernel_state_version=int(row["kernel_state_version"]),
            policy_version=str(row["policy_version"]),
            payload={str(key): value for key, value in payload.items()},
            basis_refs=tuple(str(value) for value in basis_refs),
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )
