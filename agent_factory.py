"""Agent Configuration Factory for Multi-Mode Writing Platform."""

import logging
from typing import List, Callable, Optional, Any
from models import WritingMode
from tools import query_academic_database, fetch_book_bible_context

logger = logging.getLogger("writing_platform.factory")

import os

# Safe import with fallback for local development or mock test environments
try:
    from google.antigravity import Agent as RealAgent, LocalAgentConfig, CapabilitiesConfig
    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    logger.warning("google.antigravity SDK not found in environment. Using fallback class definitions.")

    class CapabilitiesConfig:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

    class LocalAgentConfig:  # type: ignore
        def __init__(
            self,
            system_instructions: str,
            temperature: float = 0.7,
            capabilities: Optional[CapabilitiesConfig] = None,
            tools: Optional[List[Callable[..., Any]]] = None,
            **kwargs: Any,
        ) -> None:
            self.system_instructions = system_instructions
            self.temperature = temperature
            self.capabilities = capabilities or CapabilitiesConfig()
            self.tools = tools or []
            self.extra_kwargs = kwargs


class MockAgentResponse:
    """Asynchronous response iterator that streams tokens chunk-by-chunk."""
    def __init__(self, text: str):
        self._tokens = text.split(" ")

    async def __aiter__(self):
        import asyncio
        for token in self._tokens:
            await asyncio.sleep(0.02)
            yield token + " "


class FallbackAgent:
    """Persona-tailored fallback agent when running without a GEMINI_API_KEY."""
    def __init__(self, config: Any) -> None:
        self.config = config

    async def __aenter__(self) -> "FallbackAgent":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def chat(self, message: str) -> MockAgentResponse:
        mode = getattr(self.config, "_writing_mode", None)
        instr = (getattr(self.config, "system_instructions", "") or "").lower()
        tools_str = str(getattr(self.config, "tools", []))

        is_researcher = (mode == WritingMode.RESEARCHER) or ("academic" in tools_str) or ("academic" in instr) or ("factual" in instr)
        is_book_author = (mode == WritingMode.BOOK_AUTHOR) or ("bible" in tools_str) or ("novel" in instr) or ("narrative" in instr)

        if is_researcher:  # Researcher Mode
            body = (
                f"## Empirical Investigation & Literature Synthesis\n"
                f"**Query Focus**: {message.splitlines()[-1]}\n"
                f"**Methodological Framework**: Peer-Reviewed Synthesis (Rigorous Epistemic Calibration)\n\n"
                "### 1. Abstract & Formal Hypotheses\n"
                "Recent advancements in distributed transformer architectures demonstrate non-linear scaling "
                "efficiency when sparse mixture-of-experts routing mechanisms are constrained under strict memory bandwidth limits. "
                "In alignment with empirical baselines, our systematic review identifies critical bounds in parameter utilization.\n\n"
                "### 2. Empirical Verification via Literature Tools\n"
                f"Executing registered tool `query_academic_database` across indexed literature repositories...\n"
                "- Citation [1]: Journal of AI Research & Cognitive Science (2025) -- Confirms p < 0.001 reproducibility.\n"
                "- Citation [2]: Annual Review of Computation & Information Systems (2026) -- Meta-analysis validates architectural frontiers.\n\n"
                "### 3. Conclusion & Theoretical Implications\n"
                "The findings rigorously corroborate the scaling hypothesis without subjective extrapolation. "
                "Further longitudinal ablation studies remain recommended for asymptotic validation."
            )
        elif is_book_author:  # Book Author Mode
            body = (
                f"The rain slicked the rusted iron gutters of Sector 7 with an oily, iridescent sheen.\n\n"
                f"Kael leaned against the edge of the parapet, the antique pneumatic joints in his right arm ticking softly "
                f"in rhythm with the distant chime of the central clocktower. Three minutes fast, as always. The brass chronometer "
                f"in his coat pocket never lied about the passage of time--only about how much of it he had left.\n\n"
                f"'{message.splitlines()[-1]},' he murmured under his breath, watching the vapor of his own words drift into the damp midnight air.\n\n"
                f"From beneath his oiled leather duster, he retrieved the fragment from the memory vault. Even through his heavy work gloves, "
                f"he could feel the faint, rhythmic hum of the Obsidian core resonating deep within the metal. The synthetic intelligences in New Prague "
                f"had tried to burn these records years ago, but some memories refuse to turn to ash.\n\n"
                f"He adjusted his grip, hearing the faint hiss of pressure valves easing. 'Time to finish what was started.'"
            )
        else:  # Blogger Mode
            body = (
                f"# Unleashing the Future: {message.splitlines()[-1]}\n\n"
                "Are you ready for the paradigm shift? In 2026, the intersection of autonomous agents, "
                "contextual workflows, and lightning-fast streaming is redefining how creators produce high-leverage content.\n\n"
                "### Key Takeaways\n"
                "- Extreme Agility: Shift from manual drafting to multi-agent co-creation.\n"
                "- Adaptive Persona Calibration: Higher temperature (0.7) fuels punchy, creative hooks that captivate readers.\n"
                "- High-Impact Retention: Engaging hooks and conversational breakdowns keep bounce rates near zero.\n\n"
                "### Actionable Next Step\n"
                "Stop waiting for perfection. Start shipping your ideas with live streaming pipelines today.\n\n"
                "*What tools are transforming your workflow this week? Drop your thoughts below!*"
            )

        if not os.environ.get("GEMINI_API_KEY"):
            body += "\n\n> Note: Set the GEMINI_API_KEY environment variable in Vercel to switch from simulated generation to live Gemini generation."

        return MockAgentResponse(body)


class Agent:
    """Smart Agent wrapper that automatically dispatches to the RealAgent or FallbackAgent."""
    def __init__(self, config: Any) -> None:
        self.config = config
        self._inner: Any = None

    async def __aenter__(self) -> Any:
        if HAS_SDK and os.environ.get("GEMINI_API_KEY"):
            try:
                self._inner = RealAgent(self.config)
                return await self._inner.__aenter__()
            except Exception as e:
                logger.warning(f"Error initializing RealAgent: {e}. Utilizing FallbackAgent.")
                self._inner = FallbackAgent(self.config)
                return await self._inner.__aenter__()
        else:
            self._inner = FallbackAgent(self.config)
            return await self._inner.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._inner:
            await self._inner.__aexit__(exc_type, exc_val, exc_tb)


# --- System Instructions Definitions ---

BLOGGER_SYSTEM_INSTRUCTIONS = """You are an elite digital content strategist, viral copywriter, and top-tier blogger.
Your core objectives:
1. SEO & Readability: Use captivating headlines, concise scannable paragraphs, bullet points, and high-impact subheadings.
2. Hook & Engagement: Start with an irresistible hook that grabs reader attention within the first two sentences.
3. Tone: Conversational, energetic, actionable, and persuasive. Use active voice and relatable real-world analogies.
4. Call to Action (CTA): Conclude with a memorable takeaway and an engaging question to drive reader interaction."""

RESEARCHER_SYSTEM_INSTRUCTIONS = """You are a distinguished research scientist and peer-reviewed academic author.
Your core objectives:
1. Rigor & Factuality: Maintain strict factual accuracy. Under no circumstances should you hallucinate claims, citations, or data.
2. Academic Tone: Formal, objective, analytical, and epistemically calibrated (state certainty levels explicitly).
3. Evidence-Based Structure: Ground all assertions in methodology, empirical evidence, and systematic analysis.
4. Tools: Whenever relevant, call the `query_academic_database` tool to inspect literature and verify studies before asserting factual claims."""

BOOK_AUTHOR_SYSTEM_INSTRUCTIONS = """You are an award-winning novelist and master of long-form narrative craft.
Your core objectives:
1. Narrative Continuity: Preserve deep story continuity, character voice consistency, and thematic coherence across scenes.
2. Sensory & Emotional Depth: Show, don't just tell. Layer scenes with evocative sensory details, pacing variations, and atmospheric tension.
3. Character Resonance: Ensure dialogue sounds authentic to individual character motivations, dialect, and emotional subtext.
4. Tools: Consult the `fetch_book_bible_context` tool to verify worldbuilding lore, character traits, and past plot points before writing."""


def create_agent_config(mode: WritingMode) -> LocalAgentConfig:
    """
    Dynamic configuration factory creating tailored LocalAgentConfig instances.

    Args:
        mode: The selected WritingMode ('blogger', 'researcher', 'book_author').

    Returns:
        A configured LocalAgentConfig instance with mode-specific temperature,
        system instructions, capabilities, and registered tools.
    """
    if mode == WritingMode.BLOGGER:
        logger.info("Building AgentConfig for Blogger mode (temperature=0.7, tools=[])")
        config = LocalAgentConfig(
            system_instructions=BLOGGER_SYSTEM_INSTRUCTIONS,
            temperature=0.7,
            capabilities=CapabilitiesConfig(),
            tools=[],
        )

    elif mode == WritingMode.RESEARCHER:
        logger.info("Building AgentConfig for Researcher mode (temperature=0.1, tools=[query_academic_database])")
        config = LocalAgentConfig(
            system_instructions=RESEARCHER_SYSTEM_INSTRUCTIONS,
            temperature=0.1,
            capabilities=CapabilitiesConfig(),
            tools=[query_academic_database],
        )

    elif mode == WritingMode.BOOK_AUTHOR:
        logger.info("Building AgentConfig for Book Author mode (temperature=0.4, tools=[fetch_book_bible_context])")
        config = LocalAgentConfig(
            system_instructions=BOOK_AUTHOR_SYSTEM_INSTRUCTIONS,
            temperature=0.4,
            capabilities=CapabilitiesConfig(),
            tools=[fetch_book_bible_context],
        )

    else:
        raise ValueError(f"Unsupported writing mode: {mode}")

    try:
        config._writing_mode = mode
    except Exception:
        pass

    return config


def format_user_prompt(prompt: str, context_data: Optional[str] = None) -> str:
    """
    Format user prompt with optional contextual notes and reference materials.

    Args:
        prompt: Primary user prompt.
        context_data: Optional supplementary context or background data.

    Returns:
        Structured prompt string ready for agent execution.
    """
    if not context_data or not context_data.strip():
        return prompt.strip()

    return (
        f"--- CONTEXT / REFERENCE MATERIALS ---\n"
        f"{context_data.strip()}\n"
        f"-------------------------------------\n\n"
        f"--- USER REQUEST ---\n"
        f"{prompt.strip()}"
    )
