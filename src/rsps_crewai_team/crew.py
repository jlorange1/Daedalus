from __future__ import annotations

import os
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from rsps_crewai_team.tools.repo_tools import (
    run_rsps_build,
    run_rsps_tests,
    summarize_rsps_repo,
)


BASE_DIR = Path(__file__).resolve().parent


AGENT_MODEL_DEFAULTS = {
    "producer": {
        "model": "openrouter/openai/gpt-oss-120b:free",
        "fallbacks": "openai/gpt-oss-120b:free,nex-agi/nex-n2-pro:free,meta-llama/llama-3.3-70b-instruct:free",
        "temperature": 0.15,
    },
    "lead_designer": {
        "model": "openrouter/qwen/qwen3-next-80b-a3b-instruct:free",
        "fallbacks": "qwen/qwen3-next-80b-a3b-instruct:free,nousresearch/hermes-3-llama-3.1-405b:free,google/gemma-4-31b-it:free",
        "temperature": 0.35,
    },
    "server_planner": {
        "model": "openrouter/openai/gpt-oss-120b:free",
        "fallbacks": "openai/gpt-oss-120b:free,qwen/qwen3-next-80b-a3b-instruct:free,nex-agi/nex-n2-pro:free",
        "temperature": 0.16,
    },
    "backend_developer": {
        "model": "openrouter/qwen/qwen3-coder:free",
        "fallbacks": "qwen/qwen3-coder:free,openai/gpt-oss-120b:free,poolside/laguna-m.1:free",
        "temperature": 0.12,
    },
    "content_developer": {
        "model": "openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
        "fallbacks": "nousresearch/hermes-3-llama-3.1-405b:free,google/gemma-4-31b-it:free,meta-llama/llama-3.3-70b-instruct:free",
        "temperature": 0.4,
    },
    "client_developer": {
        "model": "openrouter/poolside/laguna-m.1:free",
        "fallbacks": "poolside/laguna-m.1:free,qwen/qwen3-coder:free,openai/gpt-oss-20b:free",
        "temperature": 0.18,
    },
    "qa_tester": {
        "model": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "fallbacks": "nvidia/nemotron-3-super-120b-a12b:free,openai/gpt-oss-120b:free,meta-llama/llama-3.3-70b-instruct:free",
        "temperature": 0.1,
    },
    "security_reviewer": {
        "model": "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
        "fallbacks": "nvidia/nemotron-3-ultra-550b-a55b:free,nvidia/nemotron-3.5-content-safety:free,openai/gpt-oss-120b:free",
        "temperature": 0.08,
    },
    "documentation_writer": {
        "model": "openrouter/google/gemma-4-31b-it:free",
        "fallbacks": "google/gemma-4-31b-it:free,openai/gpt-oss-20b:free,meta-llama/llama-3.3-70b-instruct:free",
        "temperature": 0.2,
    },
    "world_designer": {
        "model": "openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
        "fallbacks": "nousresearch/hermes-3-llama-3.1-405b:free,google/gemma-4-31b-it:free,meta-llama/llama-3.3-70b-instruct:free",
        "temperature": 0.34,
    },
    "economy_designer": {
        "model": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "fallbacks": "nvidia/nemotron-3-super-120b-a12b:free,openai/gpt-oss-120b:free,qwen/qwen3-next-80b-a3b-instruct:free",
        "temperature": 0.12,
    },
    "build_release_engineer": {
        "model": "openrouter/openai/gpt-oss-20b:free",
        "fallbacks": "openai/gpt-oss-20b:free,qwen/qwen3-coder:free,poolside/laguna-xs.2:free",
        "temperature": 0.08,
    },
    "devops_engineer": {
        "model": "openrouter/qwen/qwen3-coder:free",
        "fallbacks": "qwen/qwen3-coder:free,openai/gpt-oss-20b:free,poolside/laguna-m.1:free",
        "temperature": 0.08,
    },
    "art_audio_director": {
        "model": "openrouter/google/gemma-4-31b-it:free",
        "fallbacks": "google/gemma-4-31b-it:free,meta-llama/llama-3.3-70b-instruct:free,openai/gpt-oss-20b:free",
        "temperature": 0.28,
    },
}


def _env_name(agent_name: str, suffix: str) -> str:
    return f"OPENROUTER_{agent_name.upper()}_{suffix}"


def openrouter_llm(agent_name: str = "default") -> LLM:
    api_key = os.getenv("OPENROUTER_API_KEY")
    defaults = AGENT_MODEL_DEFAULTS.get(agent_name, {})
    model = os.getenv(
        _env_name(agent_name, "MODEL"),
        defaults.get("model", os.getenv("OPENROUTER_MODEL", "openrouter/deepseek/deepseek-r1")),
    )
    timeout = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "75"))
    max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "1400"))
    temperature = float(
        os.getenv(
            _env_name(agent_name, "TEMPERATURE"),
            str(defaults.get("temperature", os.getenv("OPENROUTER_TEMPERATURE", "0.2"))),
        )
    )
    fallback_models = [
        item.strip()
        for item in os.getenv(
            _env_name(agent_name, "FALLBACK_MODELS"),
            defaults.get("fallbacks", os.getenv("OPENROUTER_FALLBACK_MODELS", "")),
        ).split(",")
        if item.strip()
    ][:3]
    additional_params = {}
    if fallback_models:
        additional_params = {
            "extra_body": {
                "models": fallback_models,
                "route": "fallback",
            }
        }
    return LLM(
        model=model,
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=temperature,
        additional_params=additional_params,
        timeout=timeout,
        max_tokens=max_tokens,
    )


def tool_calling_enabled() -> bool:
    value = os.getenv("RSPS_ENABLE_CREW_TOOLS", "").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    model = os.getenv("OPENROUTER_MODEL", "")
    if "fusion" in model.lower() or model.lower().endswith("/free") or ":free" in model.lower():
        return False
    return False


def repo_tools() -> list:
    if not tool_calling_enabled():
        return []
    return [summarize_rsps_repo]


@CrewBase
class RspsCrew:
    """CrewAI workforce for RSPS development planning and review."""

    agents_config = str(BASE_DIR / "config" / "agents.yaml")
    tasks_config = str(BASE_DIR / "config" / "tasks.yaml")

    @agent
    def producer(self) -> Agent:
        return Agent(config=self.agents_config["producer"], llm=openrouter_llm("producer"), tools=repo_tools())

    @agent
    def lead_designer(self) -> Agent:
        return Agent(config=self.agents_config["lead_designer"], llm=openrouter_llm("lead_designer"), tools=repo_tools())

    @agent
    def server_planner(self) -> Agent:
        return Agent(config=self.agents_config["server_planner"], llm=openrouter_llm("server_planner"), tools=repo_tools())

    @agent
    def backend_developer(self) -> Agent:
        return Agent(config=self.agents_config["backend_developer"], llm=openrouter_llm("backend_developer"), tools=repo_tools())

    @agent
    def content_developer(self) -> Agent:
        return Agent(config=self.agents_config["content_developer"], llm=openrouter_llm("content_developer"), tools=repo_tools())

    @agent
    def client_developer(self) -> Agent:
        return Agent(config=self.agents_config["client_developer"], llm=openrouter_llm("client_developer"), tools=repo_tools())

    @agent
    def qa_tester(self) -> Agent:
        tools = [summarize_rsps_repo, run_rsps_build, run_rsps_tests] if tool_calling_enabled() else []
        return Agent(config=self.agents_config["qa_tester"], llm=openrouter_llm("qa_tester"), tools=tools)

    @agent
    def security_reviewer(self) -> Agent:
        return Agent(config=self.agents_config["security_reviewer"], llm=openrouter_llm("security_reviewer"), tools=repo_tools())

    @agent
    def documentation_writer(self) -> Agent:
        return Agent(config=self.agents_config["documentation_writer"], llm=openrouter_llm("documentation_writer"))

    @agent
    def world_designer(self) -> Agent:
        return Agent(config=self.agents_config["world_designer"], llm=openrouter_llm("world_designer"), tools=repo_tools())

    @agent
    def economy_designer(self) -> Agent:
        return Agent(config=self.agents_config["economy_designer"], llm=openrouter_llm("economy_designer"), tools=repo_tools())

    @agent
    def build_release_engineer(self) -> Agent:
        return Agent(config=self.agents_config["build_release_engineer"], llm=openrouter_llm("build_release_engineer"))

    @agent
    def devops_engineer(self) -> Agent:
        return Agent(config=self.agents_config["devops_engineer"], llm=openrouter_llm("devops_engineer"))

    @agent
    def art_audio_director(self) -> Agent:
        return Agent(config=self.agents_config["art_audio_director"], llm=openrouter_llm("art_audio_director"))

    @task
    def scope_task(self) -> Task:
        return Task(config=self.tasks_config["scope_task"])

    @task
    def design_task(self) -> Task:
        return Task(config=self.tasks_config["design_task"])

    @task
    def server_planning_task(self) -> Task:
        return Task(config=self.tasks_config["server_planning_task"])

    @task
    def implementation_task(self) -> Task:
        return Task(config=self.tasks_config["implementation_task"])

    @task
    def qa_task(self) -> Task:
        return Task(config=self.tasks_config["qa_task"])

    @task
    def security_task(self) -> Task:
        return Task(config=self.tasks_config["security_task"])

    @task
    def documentation_task(self) -> Task:
        return Task(config=self.tasks_config["documentation_task"], output_file="rsps_development_packet.md")

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
