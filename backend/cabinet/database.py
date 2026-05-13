import json
import sqlite3
import time
from typing import Any, Dict, Iterable, Optional

from .config import DB_PATH


class Database:
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                role TEXT,
                content TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                request_id TEXT,
                user_id TEXT,
                risk_level TEXT,
                data_class TEXT,
                policy TEXT,
                tokens_estimated INTEGER,
                tokens_used INTEGER,
                cost_estimated REAL,
                cost_real REAL,
                provider TEXT,
                model TEXT,
                status TEXT,
                error TEXT,
                pii_summary TEXT,
                action_id TEXT
            )
            """)
            self._ensure_columns(
                conn,
                "audit_log",
                {
                    "request_id": "TEXT",
                    "data_class": "TEXT",
                    "policy": "TEXT",
                    "tokens_estimated": "INTEGER",
                    "tokens_used": "INTEGER",
                    "cost_estimated": "REAL",
                    "cost_real": "REAL",
                    "model": "TEXT",
                    "error": "TEXT",
                    "pii_summary": "TEXT",
                    "action_id": "TEXT",
                },
            )
            conn.execute("""
            CREATE TABLE IF NOT EXISTS action_queue (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                request_id TEXT,
                user_id TEXT,
                plugin TEXT,
                action TEXT,
                access_level INTEGER,
                risk_level TEXT,
                status TEXT,
                payload TEXT,
                policy_decision TEXT,
                approval_note TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS governed_memory (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                layer TEXT,
                status TEXT,
                content TEXT,
                metadata TEXT,
                immutable INTEGER DEFAULT 0
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_proposals (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                request_id TEXT,
                layer TEXT,
                observation TEXT,
                hypothesis TEXT,
                proposal TEXT,
                status TEXT,
                approval_note TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS budget_events (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                user_id TEXT,
                agent_id TEXT,
                session_id TEXT,
                tokens_estimated INTEGER,
                tokens_used INTEGER,
                cost_estimated REAL,
                cost_real REAL,
                provider TEXT,
                model TEXT,
                status TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS local_runtime_models (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                provider TEXT,
                model_name TEXT,
                family TEXT,
                quantization TEXT,
                device TEXT,
                loaded INTEGER,
                available INTEGER,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS vector_memory (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                namespace TEXT,
                content TEXT,
                embedding TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS runtime_state (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                request_id TEXT,
                state TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                role TEXT,
                status TEXT,
                permissions TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                user_id TEXT,
                status TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                user_id TEXT,
                name TEXT,
                key_hash TEXT,
                scopes TEXT,
                status TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS secrets_vault (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                name TEXT UNIQUE,
                provider TEXT,
                encrypted_value TEXT,
                status TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_registry (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                role TEXT,
                instructions TEXT,
                permissions TEXT,
                budget TEXT,
                tools TEXT,
                memory_scope TEXT,
                risk_level TEXT,
                status TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_sources (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                request_id TEXT,
                source TEXT,
                url TEXT,
                confidence REAL,
                verification_status TEXT,
                citation TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS observability_events (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                event_type TEXT,
                request_id TEXT,
                latency_ms INTEGER,
                severity TEXT,
                payload TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                target_type TEXT,
                target_id TEXT,
                requested_by TEXT,
                status TEXT,
                reason TEXT,
                metadata TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS forecast_records (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                created_by TEXT,
                domain TEXT,
                event_statement TEXT,
                deadline TEXT,
                final_probability REAL,
                confidence_level TEXT,
                status TEXT,
                outcome INTEGER,
                brier_score REAL,
                record TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS jazekker_news_signals (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                topic TEXT,
                title TEXT,
                url TEXT,
                source TEXT,
                status TEXT,
                record TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS orientation_objects (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                updated_at INTEGER,
                status TEXT,
                rubric TEXT,
                title TEXT,
                publication_target TEXT,
                risk_level TEXT,
                confidence_score REAL,
                orientation_score REAL,
                record TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS editorial_audit (
                id TEXT PRIMARY KEY,
                created_at INTEGER,
                object_id TEXT,
                stage TEXT,
                actor TEXT,
                action TEXT,
                from_status TEXT,
                to_status TEXT,
                metadata TEXT
            )
            """)
            conn.commit()

    def _ensure_columns(self, conn: sqlite3.Connection, table: str, columns: Dict[str, str]) -> None:
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for name, column_type in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {column_type}")

    def insert_memory(self, role: str, content: str, metadata: Dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO memory VALUES (?, ?, ?, ?, ?)",
                (metadata["id"], int(time.time()), role, content, json.dumps(metadata, ensure_ascii=False)),
            )
            conn.commit()

    def insert_audit(self, record: Dict[str, Any]) -> None:
        columns = [
            "id",
            "created_at",
            "request_id",
            "user_id",
            "risk_level",
            "data_class",
            "policy",
            "tokens_estimated",
            "tokens_used",
            "cost_estimated",
            "cost_real",
            "provider",
            "model",
            "status",
            "error",
            "pii_summary",
            "action_id",
        ]
        values = [record.get(column) for column in columns]
        placeholders = ", ".join("?" for _ in columns)
        with self.connect() as conn:
            conn.execute(
                f"INSERT INTO audit_log ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
            conn.commit()

    def create_action(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO action_queue VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record["created_at"],
                    record["request_id"],
                    record["user_id"],
                    record["plugin"],
                    record["action"],
                    record["access_level"],
                    record["risk_level"],
                    record["status"],
                    json.dumps(record["payload"], ensure_ascii=False),
                    record["policy_decision"],
                    record.get("approval_note", ""),
                ),
            )
            conn.commit()
        return record["id"]

    def update_action_status(self, action_id: str, status: str, note: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM action_queue WHERE id = ?", (action_id,)).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE action_queue SET status = ?, approval_note = ? WHERE id = ?",
                (status, note, action_id),
            )
            conn.commit()
            return dict(row)

    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM action_queue WHERE id = ?", (action_id,)).fetchone()
        if not row:
            return None
        record = dict(row)
        try:
            record["payload"] = json.loads(record.get("payload") or "{}")
        except json.JSONDecodeError:
            record["payload"] = {}
        return record

    def list_rows(self, table: str, limit: int) -> Iterable[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    def daily_usage(self, user_id: str, created_after: int) -> Dict[str, float]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(tokens_estimated), 0) AS tokens,
                       COALESCE(SUM(cost_estimated), 0) AS cost
                FROM audit_log
                WHERE user_id = ? AND created_at >= ?
                """,
                (user_id, created_after),
            ).fetchone()
        return {"tokens": float(row["tokens"]), "cost": float(row["cost"])}

    def insert_budget_event(self, record: Dict[str, Any]) -> None:
        columns = [
            "id",
            "created_at",
            "user_id",
            "agent_id",
            "session_id",
            "tokens_estimated",
            "tokens_used",
            "cost_estimated",
            "cost_real",
            "provider",
            "model",
            "status",
        ]
        values = [record.get(column) for column in columns]
        placeholders = ", ".join("?" for _ in columns)
        with self.connect() as conn:
            conn.execute(f"INSERT INTO budget_events ({', '.join(columns)}) VALUES ({placeholders})", values)
            conn.commit()

    def insert_memory_proposal(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO memory_proposals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record["created_at"],
                    record["request_id"],
                    record["layer"],
                    record["observation"],
                    record["hypothesis"],
                    record["proposal"],
                    record["status"],
                    record.get("approval_note", ""),
                ),
            )
            conn.commit()
        return record["id"]

    def update_memory_proposal_status(self, proposal_id: str, status: str, note: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM memory_proposals WHERE id = ?", (proposal_id,)).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE memory_proposals SET status = ?, approval_note = ? WHERE id = ?",
                (status, note, proposal_id),
            )
            if status == "approved":
                conn.execute(
                    "INSERT INTO governed_memory VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        row["id"],
                        int(time.time()),
                        row["layer"],
                        "active",
                        row["proposal"],
                        json.dumps({"source": "approved_learning_proposal", "request_id": row["request_id"]}),
                        0,
                    ),
                )
            conn.commit()
            return dict(row)

    def insert_vector_memory(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO vector_memory VALUES (?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record["created_at"],
                    record["namespace"],
                    record["content"],
                    json.dumps(record["embedding"]),
                    json.dumps(record.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def all_vector_memory(self, namespace: str) -> Iterable[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM vector_memory WHERE namespace = ? ORDER BY created_at DESC",
                (namespace,),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["embedding"] = json.loads(item["embedding"])
            item["metadata"] = json.loads(item["metadata"])
            result.append(item)
        return result

    def insert_runtime_state(self, request_id: str, state: str, metadata: Dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO runtime_state VALUES (?, ?, ?, ?, ?)",
                (
                    metadata.get("id") or f"{request_id}:{state}:{int(time.time() * 1000)}",
                    int(time.time()),
                    request_id,
                    state,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            conn.commit()

    def upsert_user(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET role=excluded.role, status=excluded.status,
                    permissions=excluded.permissions, metadata=excluded.metadata
                """,
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record.get("role", "guest"),
                    record.get("status", "active"),
                    json.dumps(record.get("permissions", [])),
                    json.dumps(record.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    def insert_secret(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO secrets_vault VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET encrypted_value=excluded.encrypted_value,
                    status=excluded.status, metadata=excluded.metadata
                """,
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record["name"],
                    record.get("provider", ""),
                    record["encrypted_value"],
                    record.get("status", "active"),
                    json.dumps(record.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def get_secret(self, name: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM secrets_vault WHERE name = ?", (name,)).fetchone()
        return dict(row) if row else None

    def upsert_agent(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_registry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET role=excluded.role, instructions=excluded.instructions,
                    permissions=excluded.permissions, budget=excluded.budget, tools=excluded.tools,
                    memory_scope=excluded.memory_scope, risk_level=excluded.risk_level, status=excluded.status
                """,
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record.get("role", "agent"),
                    record.get("instructions", ""),
                    json.dumps(record.get("permissions", []), ensure_ascii=False),
                    json.dumps(record.get("budget", {}), ensure_ascii=False),
                    json.dumps(record.get("tools", []), ensure_ascii=False),
                    record.get("memory_scope", "operational"),
                    record.get("risk_level", "low"),
                    record.get("status", "active"),
                ),
            )
            conn.commit()
        return record["id"]

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM agent_registry WHERE id = ?", (agent_id,)).fetchone()
        if not row:
            return None
        record = dict(row)
        for key in ["permissions", "budget", "tools"]:
            try:
                record[key] = json.loads(record.get(key) or "[]" if key != "budget" else record.get(key) or "{}")
            except json.JSONDecodeError:
                record[key] = {} if key == "budget" else []
        return record

    def insert_evidence(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO evidence_sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record["request_id"],
                    record.get("source", ""),
                    record.get("url", ""),
                    record.get("confidence", 0.0),
                    record.get("verification_status", "unverified"),
                    record.get("citation", ""),
                    json.dumps(record.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def insert_observability_event(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO observability_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record["event_type"],
                    record.get("request_id", ""),
                    record.get("latency_ms", 0),
                    record.get("severity", "info"),
                    json.dumps(record.get("payload", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def insert_approval(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO approvals VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record["target_type"],
                    record["target_id"],
                    record.get("requested_by", ""),
                    record.get("status", "pending"),
                    record.get("reason", ""),
                    json.dumps(record.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def insert_forecast(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO forecast_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["forecast_id"],
                    record.get("created_at", int(time.time())),
                    record.get("created_by", ""),
                    record.get("domain", ""),
                    record.get("event_statement", ""),
                    record.get("deadline", ""),
                    record.get("final_probability", 0),
                    record.get("confidence_level", ""),
                    record.get("status", "open"),
                    record.get("outcome"),
                    record.get("brier_score"),
                    json.dumps(record, ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["forecast_id"]

    def get_forecast(self, forecast_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM forecast_records WHERE id = ?", (forecast_id,)).fetchone()
        return dict(row) if row else None

    def update_forecast_record(self, forecast_id: str, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM forecast_records WHERE id = ?", (forecast_id,)).fetchone()
            if not row:
                return None
            conn.execute(
                """
                UPDATE forecast_records
                SET status = ?, outcome = ?, brier_score = ?, record = ?
                WHERE id = ?
                """,
                (
                    record.get("status", "open"),
                    record.get("outcome"),
                    record.get("brier_score"),
                    json.dumps(record, ensure_ascii=False),
                    forecast_id,
                ),
            )
            conn.commit()
        return record

    def insert_news_signal(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jazekker_news_signals
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record.get("topic", ""),
                    record.get("title", ""),
                    record.get("url", ""),
                    record.get("source", ""),
                    record.get("status", "draft"),
                    json.dumps(record, ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def upsert_orientation_object(self, record: Dict[str, Any]) -> str:
        now = int(time.time())
        with self.connect() as conn:
            existing = conn.execute("SELECT created_at FROM orientation_objects WHERE id = ?", (record["id"],)).fetchone()
            conn.execute(
                """
                INSERT OR REPLACE INTO orientation_objects
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    existing["created_at"] if existing else record.get("created_at_epoch", now),
                    record.get("updated_at_epoch", now),
                    record.get("status", "collected"),
                    record.get("rubric", ""),
                    record.get("title", ""),
                    record.get("publication_target", "local"),
                    record.get("risk_level", "medium"),
                    float(record.get("confidence_score", 0)),
                    float(record.get("orientation_score", 0)),
                    json.dumps(record, ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def list_orientation_objects(self, limit: int = 100, status: str = "", rubric: str = "") -> Iterable[Dict[str, Any]]:
        query = "SELECT * FROM orientation_objects"
        params: list[Any] = []
        filters = []
        if status:
            filters.append("status = ?")
            params.append(status)
        if rubric:
            filters.append("rubric = ?")
            params.append(rubric)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["record"] = json.loads(item["record"]) if item.get("record") else {}
            result.append(item)
        return result

    def get_orientation_object(self, object_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM orientation_objects WHERE id = ?", (object_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["record"] = json.loads(item["record"]) if item.get("record") else {}
        return item

    def find_orientation_object(self, title: str, source_url: str = "") -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM orientation_objects").fetchall()
        title_norm = " ".join((title or "").lower().split())
        for row in rows:
            item = dict(row)
            record = json.loads(item["record"]) if item.get("record") else {}
            if source_url:
                for source in record.get("sources", []):
                    if source.get("url") == source_url:
                        item["record"] = record
                        return item
            if title_norm and " ".join(record.get("title", "").lower().split()) == title_norm:
                item["record"] = record
                return item
        return None

    def insert_editorial_audit(self, record: Dict[str, Any]) -> str:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO editorial_audit
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record.get("created_at", int(time.time())),
                    record["object_id"],
                    record.get("stage", ""),
                    record.get("actor", ""),
                    record.get("action", ""),
                    record.get("from_status", ""),
                    record.get("to_status", ""),
                    json.dumps(record.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return record["id"]

    def list_editorial_audit(self, object_id: str = "", limit: int = 100) -> Iterable[Dict[str, Any]]:
        if object_id:
            query = "SELECT * FROM editorial_audit WHERE object_id = ? ORDER BY created_at DESC LIMIT ?"
            params: tuple[Any, ...] = (object_id, limit)
        else:
            query = "SELECT * FROM editorial_audit ORDER BY created_at DESC LIMIT ?"
            params = (limit,)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata"]) if item.get("metadata") else {}
            result.append(item)
        return result
