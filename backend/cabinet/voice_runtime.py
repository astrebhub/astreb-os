import time
from typing import Any, Dict


class VoiceRuntime:
    def status(self) -> Dict[str, Any]:
        return {
            "providers": {
                "browser_stt": ["web_speech_api"],
                "browser_tts": ["speech_synthesis"],
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
            "status": "browser_voice_enabled_cloud_voice_prepared",
            "safety": {
                "audio_storage": "disabled",
                "pipeline_input": "transcript_only",
                "external_voice_providers": "not_enabled",
                "governance": "voice transcript enters the same policy pipeline",
            },
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
