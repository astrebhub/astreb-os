import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

from .database import Database


ORIENTATION_STATUSES = [
    "collected",
    "classified",
    "drafted",
    "review_required",
    "approved",
    "scheduled",
    "published_local",
    "published_external",
    "blocked",
    "archived",
]

ALLOWED_TRANSITIONS = {
    "collected": {"classified", "drafted", "review_required", "blocked", "archived"},
    "classified": {"drafted", "review_required", "blocked", "archived"},
    "drafted": {"review_required", "approved", "blocked", "archived"},
    "review_required": {"approved", "blocked", "archived"},
    "approved": {"scheduled", "published_local", "published_external", "archived"},
    "scheduled": {"published_local", "published_external", "archived"},
    "published_local": {"published_external", "archived"},
    "published_external": {"archived"},
    "blocked": {"review_required", "archived"},
    "archived": set(),
}


class OrientationWorkflow:
    def __init__(self, database: Database):
        self.database = database

    def from_rss_draft(self, draft: Dict[str, Any], actor: str = "news_collector") -> Dict[str, Any]:
        source = (draft.get("sources") or [{}])[0]
        existing = self.database.find_orientation_object(draft.get("title", ""), source.get("url", ""))
        record = self._canonicalize(draft, source=source, default_status="collected")
        if existing:
            existing_record = existing["record"]
            existing_record["updated_at"] = self._now_iso()
            existing_record["updated_at_epoch"] = int(time.time())
            existing_record["extraction_metadata"] = record["extraction_metadata"]
            existing_record["governance_notes"] = "Duplicate intake detected. Provenance refreshed; editorial state preserved."
            self.database.upsert_orientation_object(existing_record)
            self.audit(existing_record["id"], "Deduplication", actor, "deduplicate", existing_record["status"], existing_record["status"], {"source_url": source.get("url", "")})
            return existing_record
        self.database.upsert_orientation_object(record)
        self.audit(record["id"], "Source Intake", actor, "create", "", record["status"], {"source_url": source.get("url", ""), "publisher": source.get("publisher", "")})
        self.transition(record["id"], "classified", actor, "Automatic rubric and source classification.")
        self.transition(record["id"], "drafted", actor, "Editorial draft generated from Orientation Object metadata.")
        if record["review_required"]:
            self.transition(record["id"], "review_required", actor, "Human review required before publication.")
        return self.database.get_orientation_object(record["id"])["record"]

    def from_local_article(self, article: Dict[str, Any], actor: str = "local_editor") -> Dict[str, Any]:
        source = {
            "title": article.get("title", ""),
            "url": article.get("url") or f"local://content/articles/{article.get('slug', article.get('id', 'article'))}",
            "publisher": "JAZEKKER",
            "source_type": "internal",
            "confidence": "medium",
            "published_at": article.get("published_at"),
            "last_checked": article.get("published_at") or self._today(),
        }
        existing = self.database.find_orientation_object(article.get("title", ""), source["url"])
        record = self._canonicalize(article, source=source, default_status=article.get("status", "published_local"))
        record["human_approved"] = article.get("status") == "published_local"
        record["human_reviewer"] = "local_editor" if record["human_approved"] else None
        record["governance_status"] = "local_publication_allowed" if record["human_approved"] else record["governance_status"]
        if existing:
            existing_record = existing["record"]
            record["status"] = existing_record.get("status", record["status"])
        self.database.upsert_orientation_object(record)
        self.audit(record["id"], "Local Publication", actor, "upsert_local_article", existing["record"].get("status", "") if existing else "", record["status"], {"slug": article.get("slug", "")})
        return record

    def transition(
        self,
        object_id: str,
        to_status: str,
        actor: str = "editor",
        notes: str = "",
        patch: Optional[Dict[str, Any]] = None,
        publication_target: Optional[str] = None,
    ) -> Dict[str, Any]:
        if to_status not in ORIENTATION_STATUSES:
            raise ValueError(f"unsupported_status:{to_status}")
        row = self.database.get_orientation_object(object_id)
        if not row:
            raise KeyError("orientation_object_not_found")
        record = row["record"]
        from_status = record.get("status", "collected")
        if to_status not in ALLOWED_TRANSITIONS.get(from_status, set()) and to_status != from_status:
            raise ValueError(f"invalid_transition:{from_status}->{to_status}")
        if patch:
            self._deep_update(record, patch)
        if publication_target:
            record["publication_target"] = publication_target
        self._apply_governance(record, to_status, actor, notes)
        record["status"] = to_status
        record["updated_at"] = self._now_iso()
        record["updated_at_epoch"] = int(time.time())
        self.database.upsert_orientation_object(record)
        self.audit(object_id, self._stage_for(to_status), actor, "transition", from_status, to_status, {"notes": notes, "publication_target": record.get("publication_target")})
        return record

    def audit(
        self,
        object_id: str,
        stage: str,
        actor: str,
        action: str,
        from_status: str,
        to_status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.database.insert_editorial_audit(
            {
                "id": f"ea-{uuid.uuid4()}",
                "created_at": int(time.time()),
                "object_id": object_id,
                "stage": stage,
                "actor": actor,
                "action": action,
                "from_status": from_status,
                "to_status": to_status,
                "metadata": metadata or {},
            }
        )

    def seed_from_articles(self, articles: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        records = [self.from_local_article(article) for article in articles]
        return {"status": "seeded", "count": len(records), "records": records}

    def _canonicalize(self, item: Dict[str, Any], source: Dict[str, Any], default_status: str) -> Dict[str, Any]:
        title = item.get("title", "Untitled signal")
        rubric = item.get("category") or item.get("rubric") or source.get("topic") or "future_signals"
        sources = self._sources(item, source)
        risk_level, risk_reason = self._risk(item, rubric)
        confidence_score = self._confidence_score(sources)
        orientation_score = self._orientation_score(item, confidence_score, risk_level)
        source_url = sources[0].get("url", "")
        object_id = item.get("id") if str(item.get("id", "")).startswith("oo-") else f"oo-{self._today()}-{self._slug(title)}"
        review_required = risk_level in {"medium", "high", "critical"} or default_status not in {"published_local"}
        governance_status = "review_required" if review_required else "local_publication_allowed"
        summary = item.get("summary") or item.get("dek") or item.get("signal", {}).get("summary") or title
        context = item.get("context") or item.get("orientation_lens") or "This object needs editorial context before external publication."
        recommended_action = item.get("recommended_action") or item.get("next_orientation_step") or "Review sources, verify claims, and decide publication status."
        return {
            "id": object_id,
            "title": title,
            "summary": summary,
            "signal": item.get("signal", {}).get("summary") if isinstance(item.get("signal"), dict) else item.get("signal", summary),
            "context": context,
            "impact": item.get("impact") or item.get("impact_horizon", "weeks"),
            "confidence_score": confidence_score,
            "risk_level": risk_level,
            "orientation_score": orientation_score,
            "recommended_action": recommended_action,
            "rubric": rubric,
            "category": rubric,
            "category_label": item.get("category_label") or item.get("rubric_label") or rubric.replace("_", " ").title(),
            "sources": sources,
            "source_count": len(sources),
            "status": default_status if default_status in ORIENTATION_STATUSES else "collected",
            "created_at": item.get("created_at") or self._now_iso(),
            "updated_at": self._now_iso(),
            "created_at_epoch": int(time.time()),
            "updated_at_epoch": int(time.time()),
            "review_required": review_required,
            "governance_notes": item.get("governance_notes", "Draft-only until reviewed. External publication requires approval."),
            "human_approved": bool(item.get("human_approved", False)),
            "human_reviewer": item.get("human_reviewer"),
            "publication_target": item.get("publication_target", "local"),
            "governance_status": governance_status,
            "policy_applied": "jazekker_editorial_governance_v1",
            "risk_reason": risk_reason,
            "approval_required": review_required,
            "approval_timestamp": item.get("approval_timestamp"),
            "review_notes": item.get("review_notes", ""),
            "generated_draft": self._draft_text(title, summary, context, recommended_action),
            "rollback": {"previous_status": None, "reversible": True},
            "extraction_metadata": {
                "dedupe_key": self._dedupe_key(title, source_url),
                "source_url": source_url,
                "publisher": source.get("publisher") or source.get("name", ""),
                "timestamp": self._now_iso(),
                "method": "rss_or_local_normalization",
            },
        }

    def _sources(self, item: Dict[str, Any], source: Dict[str, Any]) -> list[Dict[str, Any]]:
        raw_sources = item.get("sources") if isinstance(item.get("sources"), list) else [source]
        normalized = []
        for raw in raw_sources:
            if not isinstance(raw, dict):
                continue
            normalized.append(
                {
                    "url": raw.get("url", ""),
                    "publisher": raw.get("publisher") or raw.get("name", ""),
                    "title": raw.get("title") or item.get("title", ""),
                    "timestamp": raw.get("published_at") or raw.get("last_checked") or self._today(),
                    "confidence": raw.get("confidence", "medium"),
                    "source_type": raw.get("source_type", "media"),
                    "extraction_metadata": {
                        "last_checked": raw.get("last_checked") or self._today(),
                        "topic": raw.get("topic", ""),
                        "channels": raw.get("channels", []),
                    },
                }
            )
        return normalized or [{"url": "", "publisher": "", "title": item.get("title", ""), "timestamp": self._today(), "confidence": "low", "source_type": "unknown", "extraction_metadata": {}}]

    def _confidence_score(self, sources: list[Dict[str, Any]]) -> float:
        values = {"low": 35, "medium": 62, "high": 85}
        if not sources:
            return 25
        score = sum(values.get(source.get("confidence", "medium"), 62) for source in sources) / len(sources)
        if len(sources) > 1:
            score += min(10, len(sources) * 2)
        return min(100, round(score, 1))

    def _risk(self, item: Dict[str, Any], rubric: str) -> tuple[str, str]:
        text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('dek', '')}".lower()
        high_terms = ["war", "legal", "lawsuit", "medical", "health", "election", "sanction", "security", "crime"]
        if any(term in text for term in high_terms) or rubric in {"geopolitics", "blockchain_trust"}:
            return "high" if rubric == "geopolitics" else "medium", "Sensitive domain or high-impact topic requires human review."
        if rubric in {"consciousness_meaning", "human_sustainability", "climate_energy"}:
            return "medium", "Interpretive or public-interest topic requires careful framing."
        return "low", "Low-risk local orientation material."

    def _orientation_score(self, item: Dict[str, Any], confidence_score: float, risk_level: str) -> float:
        score = confidence_score * 0.55
        text = " ".join(str(item.get(key, "")) for key in ["context", "orientation_lens", "next_orientation_step", "recommended_action"])
        if len(text) > 120:
            score += 25
        if risk_level == "low":
            score += 10
        elif risk_level == "high":
            score -= 8
        return max(0, min(100, round(score, 1)))

    def _apply_governance(self, record: Dict[str, Any], to_status: str, actor: str, notes: str) -> None:
        record["approval_required"] = record.get("risk_level") in {"medium", "high", "critical"} or record.get("publication_target") == "external"
        if to_status in {"approved", "published_local", "published_external"}:
            if record.get("risk_level") in {"high", "critical"} and not notes:
                raise ValueError("review_notes_required_for_high_risk")
            if to_status == "published_external" and not record.get("human_approved"):
                raise ValueError("external_publication_requires_prior_approval")
            record["human_approved"] = True
            record["human_reviewer"] = actor
            record["approval_timestamp"] = self._now_iso()
            record["governance_status"] = "approved"
        if to_status == "blocked":
            record["governance_status"] = "blocked"
        if to_status == "published_external":
            record["publication_target"] = "external"
        if to_status == "published_local":
            record["publication_target"] = "local"
        if notes:
            record["review_notes"] = notes

    def _stage_for(self, status: str) -> str:
        return {
            "classified": "Classification",
            "drafted": "Editorial Draft Generation",
            "review_required": "Governance Review",
            "approved": "Human Approval",
            "scheduled": "Publication Queue",
            "published_local": "Publishing",
            "published_external": "Publishing",
            "blocked": "Governance Review",
            "archived": "Rollback",
        }.get(status, "Editorial Workflow")

    def _draft_text(self, title: str, summary: str, context: str, recommended_action: str) -> str:
        return f"{title}\n\nSignal: {summary}\n\nContext: {context}\n\nNext orientation step: {recommended_action}"

    def _deep_update(self, target: Dict[str, Any], patch: Dict[str, Any]) -> None:
        for key, value in patch.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def _dedupe_key(self, title: str, url: str) -> str:
        return f"{self._slug(title)}::{url.strip().lower()}"

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug[:80] or f"object-{uuid.uuid4().hex[:8]}"

    def _today(self) -> str:
        return time.strftime("%Y-%m-%d")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
