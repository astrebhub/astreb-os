import re
import time
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class NewsCollectRequest:
    topic: str = "auto"
    channel: str = "auto"
    limit_per_source: int = 5
    max_total: int = 12


class JazekkerNewsCollector:
    TOPIC_PROFILES: Dict[str, Dict[str, Any]] = {
        "ai_coordination": {
            "label": "AI & Coordination",
            "terms": ["ai", "artificial intelligence", "agent", "model", "automation", "inference", "workflow", "coordination"],
            "who": ["organizations", "professionals", "public institutions"],
            "effect": "AI is moving from tool use toward governed coordination infrastructure.",
        },
        "europe_governance": {
            "label": "Europe & Governance",
            "terms": ["europe", "eu", "commission", "regulation", "sovereignty", "policy", "governance", "public sector"],
            "who": ["citizens", "organizations", "policy teams"],
            "effect": "European institutions are turning trust, compliance, and sovereignty into operational requirements.",
        },
        "blockchain_trust": {
            "label": "Blockchain & Trust",
            "terms": ["blockchain", "crypto", "bitcoin", "ethereum", "stablecoin", "token", "wallet", "defi", "trust"],
            "who": ["builders", "investors", "governance teams"],
            "effect": "Decentralized infrastructure keeps testing new trust, finance, and coordination models.",
        },
        "consciousness_meaning": {
            "label": "Consciousness & Meaning",
            "terms": ["consciousness", "mind", "meaning", "spiritual", "spirituality", "religion", "attention", "wellbeing", "psychology"],
            "who": ["citizens", "communities", "leaders"],
            "effect": "Human meaning, attention, and inner orientation become strategic questions in technological acceleration.",
        },
        "human_sustainability": {
            "label": "Human Sustainability",
            "terms": ["attention", "mental health", "burnout", "wellbeing", "cognitive", "workload", "resilience"],
            "who": ["citizens", "organizations", "communities"],
            "effect": "Cognitive load and attention preservation become infrastructure questions, not lifestyle extras.",
        },
        "geopolitics": {
            "label": "Geopolitics",
            "terms": ["geopolitics", "security", "china", "us", "russia", "war", "supply chain", "defense", "sanctions"],
            "who": ["citizens", "organizations", "public institutions"],
            "effect": "Technological and political systems are becoming more tightly coupled.",
        },
        "climate_energy": {
            "label": "Climate & Energy",
            "terms": ["climate", "energy", "grid", "renewable", "carbon", "battery", "electricity", "transition"],
            "who": ["citizens", "organizations", "municipalities"],
            "effect": "Energy transition and climate adaptation shape resilience, infrastructure, and public trust.",
        },
        "future_work": {
            "label": "Future of Work",
            "terms": ["work", "jobs", "skills", "labor", "productivity", "education", "workforce", "reskilling"],
            "who": ["professionals", "organizations", "educators"],
            "effect": "Work is reorganizing around human-AI teams, new skills, and governed automation.",
        },
        "future_signals": {
            "label": "Future Signals",
            "terms": ["future", "trend", "forecast", "emerging", "frontier", "breakthrough", "uncertainty"],
            "who": ["strategists", "editors", "organizations"],
            "effect": "Weak signals reveal structural trajectories before they become obvious.",
        },
    }

    def __init__(self, sources: List[Dict[str, Any]]):
        self.sources = [source for source in sources if source.get("enabled", True)]

    def topics(self) -> List[Dict[str, Any]]:
        counts: Dict[str, int] = {key: 0 for key in self.TOPIC_PROFILES}
        for source in self.sources:
            for channel in source.get("channels", [source.get("topic", "")]):
                if channel in counts:
                    counts[channel] += 1
        return [
            {"id": key, "label": profile["label"], "source_count": counts.get(key, 0)}
            for key, profile in self.TOPIC_PROFILES.items()
        ]

    async def collect(self, req: NewsCollectRequest) -> Dict[str, Any]:
        started_at = time.time()
        signals: List[Dict[str, Any]] = []
        errors: List[Dict[str, str]] = []
        sources = self._sources_for(req.channel)

        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": "AI-Cabinet-Jazekker-NewsCollector/0.1"},
        ) as client:
            for source in sources:
                try:
                    response = await client.get(source["url"])
                    response.raise_for_status()
                    items = self._parse_feed(response.text, source, req.limit_per_source)
                    signals.extend(items)
                except Exception as exc:
                    errors.append(
                        {
                            "source_id": source.get("id", ""),
                            "source": source.get("name", source.get("url", "")),
                            "error": str(exc),
                        }
                    )

        ranked = self._rank(signals, req.topic, req.channel)[: max(1, req.max_total)]
        orientation_drafts = [self._to_orientation_object(item, req.topic) for item in ranked]
        return {
            "status": "draft_only",
            "topic": req.topic,
            "channel": req.channel,
            "collected": len(signals),
            "returned": len(orientation_drafts),
            "errors": errors,
            "topics": self.topics(),
            "duration_ms": int((time.time() - started_at) * 1000),
            "governance": {
                "external_action": "rss_fetch_only",
                "publication": "none",
                "approval_required_before_publication": True,
                "memory_update": "none",
            },
            "orientation_object_drafts": orientation_drafts,
        }

    def _sources_for(self, channel: str) -> List[Dict[str, Any]]:
        if not channel or channel == "auto":
            return self.sources
        return [
            source for source in self.sources
            if channel == source.get("topic") or channel in source.get("channels", [])
        ] or self.sources

    def _parse_feed(self, xml_text: str, source: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_text)
        channel_items = root.findall(".//channel/item")
        atom_items = root.findall("{http://www.w3.org/2005/Atom}entry")
        raw_items = channel_items or atom_items
        parsed: List[Dict[str, Any]] = []

        for item in raw_items[: max(1, limit)]:
            title = self._text(item, "title")
            link = self._text(item, "link")
            if not link:
                link = self._atom_link(item)
            summary = self._text(item, "description") or self._text(item, "summary")
            published = self._text(item, "pubDate") or self._text(item, "published") or self._text(item, "updated")
            parsed.append(
                {
                    "id": f"signal-{uuid.uuid4()}",
                    "title": self._clean(title),
                    "url": link.strip(),
                    "summary": self._clean(summary),
                    "published_at": self._date(published),
                    "source": {
                        "id": source.get("id", ""),
                        "name": source.get("name", ""),
                        "url": source.get("url", ""),
                        "source_type": source.get("source_type", "media"),
                        "confidence": source.get("confidence", "medium"),
                        "topic": source.get("topic", ""),
                        "channels": source.get("channels", []),
                    },
                }
            )
        return [item for item in parsed if item["title"] and item["url"]]

    def _text(self, item: ET.Element, name: str) -> str:
        found = item.find(name)
        if found is None:
            found = item.find(f"{{http://www.w3.org/2005/Atom}}{name}")
        return found.text or "" if found is not None else ""

    def _atom_link(self, item: ET.Element) -> str:
        for link in item.findall("{http://www.w3.org/2005/Atom}link"):
            href = link.attrib.get("href")
            if href:
                return href
        return ""

    def _clean(self, value: str) -> str:
        value = re.sub(r"<[^>]+>", " ", value or "")
        value = unescape(value)
        value = self._repair_mojibake(value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    def _repair_mojibake(self, value: str) -> str:
        replacements = {
            "â": "-",
            "â": "-",
            "â": "'",
            "â": "'",
            "â": '"',
            "â": '"',
            "â¦": "...",
        }
        for broken, fixed in replacements.items():
            value = value.replace(broken, fixed)
        if "â" not in value and "Â" not in value:
            return value
        try:
            repaired = value.encode("latin1").decode("utf-8")
        except UnicodeError:
            return value
        return repaired if repaired else value

    def _date(self, value: str) -> Optional[str]:
        if not value:
            return None
        try:
            return parsedate_to_datetime(value).date().isoformat()
        except Exception:
            return value[:10]

    def _rank(self, signals: List[Dict[str, Any]], topic: str, channel: str) -> List[Dict[str, Any]]:
        topic_terms = [term for term in re.split(r"[^a-z0-9]+", topic.lower()) if len(term) > 2 and term != "auto"]
        profile_terms = self.TOPIC_PROFILES.get(channel, {}).get("terms", [])
        governance_terms = ["governance", "policy", "safety", "regulation", "agent", "model", "security", "trust", "sovereignty", "attention"]
        terms = topic_terms + profile_terms

        def score(item: Dict[str, Any]) -> int:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            value = sum(3 for term in terms if term.lower() in text)
            value += sum(1 for term in governance_terms if term in text)
            if item.get("source", {}).get("source_type") == "official":
                value += 2
            if channel and channel in item.get("source", {}).get("channels", []):
                value += 4
            return value

        return sorted(signals, key=score, reverse=True)

    def _to_orientation_object(self, item: Dict[str, Any], topic: str) -> Dict[str, Any]:
        source = item["source"]
        category = self._classify(item, topic)
        profile = self.TOPIC_PROFILES.get(category, self.TOPIC_PROFILES["future_signals"])
        title_slug = re.sub(r"[^a-z0-9]+", "-", item["title"].lower()).strip("-")[:80] or "news-signal"
        object_id = f"oo-{time.strftime('%Y-%m-%d')}-{title_slug}"
        return {
            "id": object_id,
            "title": item["title"],
            "slug": title_slug,
            "status": "draft",
            "language": "en",
            "category": category,
            "category_label": profile["label"],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "signal": {
                "summary": item["summary"] or item["title"],
                "signal_type": category,
                "why_now": f"Collected from an approved source for the topic: {topic}.",
            },
            "context": f"This is an automatically collected draft signal. Orientation lens: {profile['effect']} It needs source review, interpretation, and human approval before publication.",
            "noise_level": "medium",
            "impact_horizon": "weeks",
            "who_should_care": ["Jazekker editors", *profile["who"]],
            "systemic_effects": [
                profile["effect"],
                "Requires editorial review to separate confirmed facts from interpretation.",
            ],
            "next_orientation_step": "Review the source, verify the claim, then decide whether this signal deserves a full Orientation Object.",
            "sources": [
                {
                    "title": item["title"],
                    "url": item["url"],
                    "source_type": source.get("source_type", "media"),
                    "publisher": source.get("name", ""),
                    "published_at": item.get("published_at"),
                    "last_checked": time.strftime("%Y-%m-%d"),
                    "confidence": source.get("confidence", "medium"),
                    "topic": source.get("topic", ""),
                    "channels": source.get("channels", []),
                    "notes": "Automatically collected via approved RSS source. Not publication-ready.",
                }
            ],
            "confidence": {
                "level": source.get("confidence", "medium"),
                "rationale": "Confidence is inherited from the configured source and must be reviewed by a human editor.",
                "last_checked": time.strftime("%Y-%m-%d"),
            },
            "governance": {
                "risk_level": "medium",
                "sensitive_domains": ["reputational"],
                "approval_required": True,
                "approval_status": "not_requested",
                "ai_assisted": False,
                "human_reviewer": None,
                "audit_ids": [],
            },
            "distribution": {
                "website": {"status": "not_started", "draft_path": None},
                "newsletter": {"status": "not_started", "draft_path": None},
                "linkedin": {"status": "not_started", "draft_path": None},
                "telegram": {"status": "not_started", "draft_path": None},
                "rss": {"status": "not_started", "draft_path": None},
            },
            "strategic_memory_note": None,
        }

    def _classify(self, item: Dict[str, Any], topic: str) -> str:
        source = item.get("source", {})
        for channel in source.get("channels", []):
            if channel in self.TOPIC_PROFILES:
                return channel
        if source.get("topic") in self.TOPIC_PROFILES:
            return source["topic"]
        text = f"{topic} {item.get('title', '')} {item.get('summary', '')}".lower()
        scores = {}
        for key, profile in self.TOPIC_PROFILES.items():
            scores[key] = sum(1 for term in profile["terms"] if term.lower() in text)
        return max(scores, key=scores.get) if scores else "future_signals"
