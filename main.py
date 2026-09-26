"""FastAPI Backend Service for Multi-Mode Writing Platform.

Integrates with Google Antigravity SDK (google-antigravity) to provide
dynamic persona configurations, tool execution, and token streaming.
"""

import logging
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse

from models import GenerateRequest, HealthResponse
from agent_factory import (
    create_agent_config,
    format_user_prompt,
    Agent,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("writing_platform.api")

# Initialize FastAPI Application
app = FastAPI(
    title="Multi-Mode Writing Platform API",
    description=(
        "Production backend powered by FastAPI and Google Antigravity SDK. "
        "Supports dynamic agent orchestration for Bloggers, Researchers, and Book Authors."
    ),
    version="1.0.0",
)

# Enable Cross-Origin Resource Sharing (CORS) for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


HTML_PLAYGROUND = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Multi-Mode Writing Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        code, pre { font-family: 'JetBrains Mono', monospace; }
        .mode-btn.active { border-color: #6366f1; background-color: #eef2ff; color: #4338ca; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-10">
        <!-- Header -->
        <header class="text-center mb-10">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3 tracking-wide uppercase">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Service Healthy • Powered by Google Antigravity SDK
            </div>
            <h1 class="text-4xl font-bold tracking-tight text-white sm:text-5xl">
                Multi-Mode <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Writing Platform</span>
            </h1>
            <p class="mt-3 text-slate-400 max-w-xl mx-auto text-sm sm:text-base">
                Dynamically orchestrated agent personas with customized system instructions, temperatures, and specialized toolsets.
            </p>
        </header>

        <!-- Mode Selector -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <!-- Blogger -->
            <button onclick="selectMode('blogger')" id="btn-blogger" class="mode-btn active flex flex-col p-4 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-800 transition text-left cursor-pointer">
                <div class="flex items-center justify-between w-full mb-2">
                    <span class="text-lg font-bold text-white">⚡ Blogger</span>
                    <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono">temp: 0.7</span>
                </div>
                <p class="text-xs text-slate-400">SEO-optimized, catchy hooks, viral formatting, engaging CTAs.</p>
                <span class="text-[10px] mt-2 text-slate-500">Tools: Standard</span>
            </button>

            <!-- Researcher -->
            <button onclick="selectMode('researcher')" id="btn-researcher" class="mode-btn flex flex-col p-4 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-800 transition text-left cursor-pointer">
                <div class="flex items-center justify-between w-full mb-2">
                    <span class="text-lg font-bold text-white">🔬 Researcher</span>
                    <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">temp: 0.1</span>
                </div>
                <p class="text-xs text-slate-400">Zero hallucination, academic rigor, empirical data & methodology.</p>
                <span class="text-[10px] mt-2 text-emerald-400 font-mono">Tool: query_academic_db</span>
            </button>

            <!-- Book Author -->
            <button onclick="selectMode('book_author')" id="btn-book_author" class="mode-btn flex flex-col p-4 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-800 transition text-left cursor-pointer">
                <div class="flex items-center justify-between w-full mb-2">
                    <span class="text-lg font-bold text-white">📖 Book Author</span>
                    <span class="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono">temp: 0.4</span>
                </div>
                <p class="text-xs text-slate-400">Deep continuity, sensory atmosphere, character voice & arc balance.</p>
                <span class="text-[10px] mt-2 text-purple-400 font-mono">Tool: fetch_book_bible</span>
            </button>
        </div>

        <!-- Input Form -->
        <div class="bg-slate-800/60 rounded-2xl border border-slate-700/80 p-6 backdrop-blur-sm shadow-xl mb-6">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Prompt / Topic</label>
                <textarea id="promptInput" rows="3" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition" placeholder="Enter your prompt..."></textarea>
            </div>

            <div class="mb-5">
                <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Supplementary Context / Reference Data <span class="text-slate-500 font-normal">(Optional)</span>
                </label>
                <textarea id="contextInput" rows="2" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition" placeholder="Add specific notes, background constraints, or references..."></textarea>
            </div>

            <div class="flex items-center justify-between">
                <div class="text-xs text-slate-400">
                    Endpoint: <code class="text-indigo-400">POST /generate</code> (Streamed chunk-by-chunk)
                </div>
                <button onclick="startGeneration()" id="generateBtn" class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold text-sm rounded-xl transition flex items-center gap-2 cursor-pointer shadow-lg shadow-indigo-600/25">
                    <span id="btnText">Generate Content</span>
                    <svg id="spinner" class="hidden animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                </button>
            </div>
        </div>

        <!-- Output Card -->
        <div class="bg-slate-800/60 rounded-2xl border border-slate-700/80 p-6 backdrop-blur-sm shadow-xl">
            <div class="flex items-center justify-between mb-4 border-b border-slate-700/60 pb-3">
                <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
                    <h3 class="text-sm font-semibold text-slate-200">Streaming Output</h3>
                </div>
                <button onclick="copyOutput()" class="text-xs px-3 py-1 bg-slate-700/60 hover:bg-slate-700 text-slate-300 rounded-lg transition">
                    Copy Text
                </button>
            </div>
            <div id="outputBox" class="min-h-[160px] max-h-[450px] overflow-y-auto whitespace-pre-wrap text-sm text-slate-200 leading-relaxed font-sans bg-slate-900/70 p-4 rounded-xl border border-slate-700/50">
                <span class="text-slate-500 italic">Select a mode, enter a prompt, and click Generate to view live streaming output...</span>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'blogger';
        const samplePrompts = {
            'blogger': 'Top 5 AI tools transforming developer productivity in 2026',
            'researcher': 'Evaluate the empirical scaling laws and memory constraints of sparse Mixture-of-Experts architectures.',
            'book_author': 'Write the climactic scene in Chapter 7 where Kael activates the Obsidian core.'
        };
        const sampleContexts = {
            'blogger': 'Target audience: Tech founders and early-career software engineers.',
            'researcher': 'Reference peer-reviewed literature published between 2024 and 2026 with empirical validation.',
            'book_author': 'Setting: Raining heavily over the Sector 7 clocktower. Kael’s prosthetic arm is clicking.'
        };

        function selectMode(mode) {
            currentMode = mode;
            ['blogger', 'researcher', 'book_author'].forEach(m => {
                const el = document.getElementById('btn-' + m);
                if (m === mode) {
                    el.classList.add('border-indigo-500', 'bg-indigo-950/40', 'ring-2', 'ring-indigo-500/30');
                    el.classList.remove('border-slate-700', 'bg-slate-800/80');
                } else {
                    el.classList.remove('border-indigo-500', 'bg-indigo-950/40', 'ring-2', 'ring-indigo-500/30');
                    el.classList.add('border-slate-700', 'bg-slate-800/80');
                }
            });
            document.getElementById('promptInput').value = samplePrompts[mode];
            document.getElementById('contextInput').value = sampleContexts[mode];
        }

        // Initialize default sample prompt
        selectMode('blogger');

        async function startGeneration() {
            const prompt = document.getElementById('promptInput').value.trim();
            const contextData = document.getElementById('contextInput').value.trim();
            const outputBox = document.getElementById('outputBox');
            const generateBtn = document.getElementById('generateBtn');
            const spinner = document.getElementById('spinner');
            const btnText = document.getElementById('btnText');

            if (!prompt) {
                alert('Please enter a prompt.');
                return;
            }

            outputBox.textContent = '';
            generateBtn.disabled = true;
            spinner.classList.remove('hidden');
            btnText.textContent = 'Generating...';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        mode: currentMode,
                        prompt: prompt,
                        context_data: contextData || null
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value, { stream: true });
                    outputBox.textContent += chunk;
                    outputBox.scrollTop = outputBox.scrollHeight;
                }
            } catch (err) {
                outputBox.textContent = `[Error: ${err.message}]`;
            } finally {
                generateBtn.disabled = false;
                spinner.classList.add('hidden');
                btnText.textContent = 'Generate Content';
            }
        }

        function copyOutput() {
            const text = document.getElementById('outputBox').textContent;
            navigator.clipboard.writeText(text).then(() => alert('Copied to clipboard!'));
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def serve_playground() -> HTMLResponse:
    """Serve the interactive web playground for testing agent modes and streaming."""
    return HTMLResponse(content=HTML_PLAYGROUND)


async def agent_token_streamer(request: GenerateRequest) -> AsyncGenerator[str, None]:
    """
    Asynchronously instantiates the Antigravity Agent and streams tokens chunk-by-chunk.

    Args:
        request: The validated GenerateRequest payload.

    Yields:
        Individual string tokens or text chunks as they arrive from the agent.
    """
    logger.info(f"Received generation request for mode: '{request.mode.value}'")

    try:
        # 1. Create dynamic agent configuration based on persona mode & tools
        config = create_agent_config(request.mode)

        # 2. Format final prompt including optional context data
        formatted_prompt = format_user_prompt(
            prompt=request.prompt,
            context_data=request.context_data
        )

        # 3. Execute agent within an async context manager lifecycle
        async with Agent(config) as agent:
            logger.info(f"Agent leased successfully. Sending prompt to Antigravity runtime...")
            response = await agent.chat(formatted_prompt)

            # 4. Stream response tokens in real-time
            async for token in response:
                yield token

        logger.info(f"Completed token streaming for mode: '{request.mode.value}'")

    except Exception as exc:
        logger.error(f"Error during agent streaming execution: {exc}", exc_info=True)
        yield f"\n\n[Error during generation: {str(exc)}]"


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    tags=["Monitoring"],
)
async def health_check() -> HealthResponse:
    """Return health status of the backend service."""
    return HealthResponse()


@app.post(
    "/generate",
    summary="Generate Persona-Tailored Content (Streaming)",
    description=(
        "Dispatches prompt to Google Antigravity Agent with dynamic persona configurations "
        "(Blogger, Researcher, Book Author) and streams output chunk-by-chunk."
    ),
    response_class=StreamingResponse,
    tags=["Generation"],
    responses={
        200: {
            "description": "Chunked text stream containing generated response tokens.",
            "content": {"text/plain": {}},
        },
        422: {"description": "Validation Error (e.g. invalid mode or empty prompt)."},
        500: {"description": "Internal Server Error."},
    },
)
async def generate_content(request: GenerateRequest) -> StreamingResponse:
    """
    Main generation endpoint that initiates agent streaming.

    - **mode**: 'blogger' (temp: 0.7, SEO/hook-focused),
                'researcher' (temp: 0.1, academic rigor, `query_academic_database` tool),
                'book_author' (temp: 0.4, narrative continuity, `fetch_book_bible_context` tool).
    - **prompt**: Core topic or generation instruction.
    - **context_data**: Optional supplementary reference data or background notes.
    """
    try:
        return StreamingResponse(
            agent_token_streamer(request),
            media_type="text/plain; charset=utf-8",
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        logger.error(f"Failed to initiate streaming response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start generation stream: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
