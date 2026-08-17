"""
Founder Voice Profiling & Authentic Communication Engine

Inspired by Y Combinator QM's email-voice-profile skill:
1. Synthesizes an authentic Founder Voice Profile (sentence rhythm, hard rules, anti-patterns).
2. Constrains automated outbound drafts to sound authentically like the founder.
"""

from typing import Dict, Any, List


class VoiceProfileEngine:
    """
    Manages founder voice styling, hard communication rules, and anti-patterns.
    """

    @staticmethod
    def get_default_voice_profile(founder_comm_style: str = "Direct and brief") -> Dict[str, Any]:
        """Returns baseline voice rules grounded in the founder's communication style."""
        if "concise" in founder_comm_style.lower() or "direct" in founder_comm_style.lower():
            return {
                "register": "Direct, clear, high-signal, zero fluff",
                "sentence_rhythm": "Short, crisp paragraphs (1-3 sentences max). One idea per line.",
                "hard_rules": [
                    "Lead immediately with the core ask or bottom line.",
                    "Include explicit metrics, deadlines, or links.",
                    "Sign off simply (e.g. 'Best, [Name]' or just '- [Name]')."
                ],
                "anti_patterns": [
                    "Never use generic corporate filler ('I hope this email finds you well', 'Per my previous email', 'Circle back').",
                    "Avoid passive voice or hedging ('We might possibly want to consider...').",
                    "Do not use markdown bold/italic inside plain text emails."
                ]
            }
        else:
            return {
                "register": "Warm, collaborative, visionary, pragmatic",
                "sentence_rhythm": "Balanced sentences with clear contextual framing before asks.",
                "hard_rules": [
                    "Acknowledge customer or partner context first.",
                    "Frame outcomes around shared startup success.",
                    "Provide clear, low-friction next steps."
                ],
                "anti_patterns": [
                    "Never use overly formal legalese or bureaucratic phrasing.",
                    "Avoid unnecessary pleasantry paragraphs before getting to the point."
                ]
            }

    @staticmethod
    def apply_voice_constraints_to_prompt(prompt: str, voice_profile: Dict[str, Any]) -> str:
        """Appends strict voice profile constraints to LLM generation prompts."""
        rules = "\n".join(f"- {r}" for r in voice_profile.get("hard_rules", []))
        anti_patterns = "\n".join(f"- {a}" for a in voice_profile.get("anti_patterns", []))
        
        voice_block = f"""
        FOUNDER AUTHENTIC VOICE CONSTRAINTS:
        - Tone Register: {voice_profile.get('register')}
        - Sentence Rhythm: {voice_profile.get('sentence_rhythm')}
        
        Hard Rules:
        {rules}
        
        Strict Anti-Patterns (FORBIDDEN):
        {anti_patterns}
        """
        return f"{prompt}\n\n{voice_block}"
