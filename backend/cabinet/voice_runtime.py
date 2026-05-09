import time
from typing import Any, Dict


class VoiceRuntime:
    def status(self) -> Dict[str, Any]:
        return {
            "providers": {
                "stt": ["openai_realtime", "deepgram", "whisper_local"],
                "tts": ["elevenlabs", "piper", "openai_realtime"],
            },
            "features": [
                "interruption_handling",
                "latency_monitoring",
                "turn_management",
                "emotional_routing",
                "voice_policy_rules",
                "transcripts",
                "voice_identity",
            ],
            "status": "prepared_not_enabled",
        }

    def normalize_turn(self, transcript: str, speaker_id: str = "owner") -> Dict[str, Any]:
        return {
            "input_type": "voice",
            "speaker_id": speaker_id,
            "transcript": transcript,
            "timestamp": int(time.time()),
            "interruption": False,
            "emotion_hint": "neutral",
        }
