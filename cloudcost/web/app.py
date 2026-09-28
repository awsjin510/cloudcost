"""FastAPI web application for cloud cost comparison."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import anthropic
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from cloudcost.builders import build_cloud_spec
from cloudcost.comparator import CloudCostComparator
from cloudcost.llm import (
    LLMModel,
    LLMPlatform,
    LLMWorkload,
    ModelInfo,
    QuotaPlan,
    QuotaReport,
    evaluate_workload,
    get_model,
    list_models,
    list_plans,
)
from cloudcost.models.spec import (
    ComparisonResult,
    DatabaseType,
    GroupComparisonResult,
    MachineItem,
    MachineRole,
    Region,
    StorageType,
    WorkloadGroup,
)
from cloudcost.recommender import generate_recommendation

BASE_DIR = Path(__file__).parent

# Module-level comparator — initialized at import time so it is available
# during tests (which may not trigger ASGI lifespan events).
comparator = CloudCostComparator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the shared HTTP client lifecycle for the web server."""
    yield
    await comparator.aclose()


app = FastAPI(
    title="CloudCost",
    description="Multi-cloud cost comparison engine",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------------------------------------------------------------------------
# API endpoints (JSON)
# ---------------------------------------------------------------------------


class CompareRequest(BaseModel):
    cpu_cores: int
    ram_gb: float
    storage_gb: float = 0
    storage_type: str = "ssd"
    network_transfer_gb: float = 0
    database_type: str = "none"
    region: str = "us-east-1"
    monthly_hours: float = 730
    os: str = "linux"
    description: str = ""
    include_ai: bool = True


class GroupMachineRequest(BaseModel):
    id: str
    name: str = ""
    cpu: int
    ram: float
    storage: float = 0
    quantity: int = 1
    role: str = "web"


class GroupCompareRequest(BaseModel):
    name: str = "My Workload"
    machines: list[GroupMachineRequest]
    region: str = "us-east-1"
    storage_type: str = "ssd"
    os: str = "linux"
    monthly_hours: float = 730
    description: str = ""
    include_ai: bool = False


@app.post("/api/compare-group", response_model=GroupComparisonResult)
async def api_compare_group(req: GroupCompareRequest) -> GroupComparisonResult:
    """JSON API: compare cloud costs for a workload group."""
    machines = [
        MachineItem(
            id=m.id,
            name=m.name,
            cpu=m.cpu,
            ram=m.ram,
            storage=m.storage,
            quantity=m.quantity,
            role=MachineRole(m.role),
        )
        for m in req.machines
    ]
    group = WorkloadGroup(
        name=req.name,
        machines=machines,
        region=req.region,
        storage_type=req.storage_type,
        os=req.os,
        monthly_hours=req.monthly_hours,
        description=req.description,
    )
    result = await comparator.compare_group(group)
    if req.include_ai:
        result.recommendation = await generate_recommendation(result)
    return result


@app.post("/api/compare", response_model=ComparisonResult)
async def api_compare(req: CompareRequest) -> ComparisonResult:
    """JSON API: compare cloud costs."""
    spec = build_cloud_spec(
        cpu_cores=req.cpu_cores,
        ram_gb=req.ram_gb,
        storage_gb=req.storage_gb,
        storage_type=req.storage_type,
        network_transfer_gb=req.network_transfer_gb,
        database_type=req.database_type,
        region=req.region,
        monthly_hours=req.monthly_hours,
        os=req.os,
        description=req.description,
    )
    result = await comparator.compare(spec)
    if req.include_ai:
        result.recommendation = await generate_recommendation(result)
    return result


# ---------------------------------------------------------------------------
# LLM quota planning
# ---------------------------------------------------------------------------


@app.get("/api/llm-quota/models", response_model=list[ModelInfo])
async def api_llm_models() -> list[ModelInfo]:
    """JSON API: the modelled Claude models and their list pricing."""
    return list_models()


@app.get("/api/llm-quota/plans", response_model=list[QuotaPlan])
async def api_llm_quota_plans(
    model: LLMModel | None = None, platform: LLMPlatform | None = None
) -> list[QuotaPlan]:
    """JSON API: the published default quota table."""
    return list_plans(model, platform)


class TokenCountRequest(BaseModel):
    model: LLMModel = LLMModel.FABLE_5_1
    #: The fixed, cacheable part: system prompt, rules, always-attached docs.
    system: str = Field(default="", max_length=4_000_000)
    #: One representative user turn, including per-request RAG context.
    sample: str = Field(default="", max_length=4_000_000)


class TokenCountResult(BaseModel):
    model: LLMModel
    prefix_tokens: int
    total_tokens: int


def token_counting_enabled() -> bool:
    """Whether this server holds credentials for the token counting API.

    The feature needs an API key, which is exactly why the public static
    site cannot offer it: a key shipped to the browser is a leaked key.
    """
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def _token_client() -> anthropic.AsyncAnthropic:
    # Separate factory so tests can substitute a fake without network access.
    return anthropic.AsyncAnthropic()


@app.post("/api/llm-quota/count-tokens", response_model=TokenCountResult)
async def api_llm_count_tokens(req: TokenCountRequest) -> TokenCountResult:
    """JSON API: exact prompt size via Anthropic's free token counting endpoint.

    Returns the total per-request input and how much of it is the fixed
    prefix, which is what the planner needs for both ITPM and cache rate.
    """
    if not token_counting_enabled():
        raise HTTPException(status_code=503, detail="此伺服器未設定 ANTHROPIC_API_KEY，無法精算 token")
    if not req.system.strip() and not req.sample.strip():
        raise HTTPException(status_code=422, detail="請至少提供一段提示詞")

    model_id = get_model(req.model).api_id
    # count_tokens needs at least one user turn; a single character stands in
    # when only a system prompt was pasted.
    turn = [{"role": "user", "content": req.sample if req.sample.strip() else "."}]
    client = _token_client()
    try:
        if req.system.strip():
            total = await client.messages.count_tokens(model=model_id, system=req.system, messages=turn)
            without = await client.messages.count_tokens(model=model_id, messages=turn)
            total_tokens = total.input_tokens
            prefix_tokens = max(0, total_tokens - without.input_tokens)
        else:
            total = await client.messages.count_tokens(model=model_id, messages=turn)
            total_tokens, prefix_tokens = total.input_tokens, 0
    except (anthropic.AuthenticationError, anthropic.PermissionDeniedError):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY 無效或權限不足")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="token counting 已達每分鐘上限，請稍後再試")
    except anthropic.BadRequestError as exc:
        raise HTTPException(status_code=400, detail=f"提示詞無法計算：{exc.message}")
    except anthropic.APIConnectionError:
        raise HTTPException(status_code=502, detail="無法連線到 Anthropic API")
    except anthropic.APIStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Anthropic API 錯誤（{exc.status_code}）")

    return TokenCountResult(model=req.model, prefix_tokens=prefix_tokens, total_tokens=total_tokens)


@app.post("/api/llm-quota", response_model=QuotaReport)
async def api_llm_quota(
    workload: LLMWorkload, platform: LLMPlatform | None = None
) -> QuotaReport:
    """JSON API: size a peak workload against each platform's default quota."""
    return evaluate_workload(workload, platform)


# ---------------------------------------------------------------------------
# Web UI routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with the comparison form."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "regions": [(r.value, _region_label(r)) for r in Region],
            "storage_types": [t.value for t in StorageType],
            "db_types": [d.value for d in DatabaseType],
            "token_counting": token_counting_enabled(),
            "machine_roles": [r.value for r in MachineRole],
            "result": None,
        },
    )


@app.post("/compare", response_class=HTMLResponse)
async def compare_form(
    request: Request,
    cpu_cores: int = Form(...),
    ram_gb: float = Form(...),
    storage_gb: float = Form(0),
    storage_type: str = Form("ssd"),
    network_transfer_gb: float = Form(0),
    database_type: str = Form("none"),
    region: str = Form("us-east-1"),
    monthly_hours: float = Form(730),
    os_type: str = Form("linux"),
    description: str = Form(""),
    include_ai: bool = Form(False),
):
    """Handle form submission and show results."""
    spec = build_cloud_spec(
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        storage_type=storage_type,
        network_transfer_gb=network_transfer_gb,
        database_type=database_type,
        region=region,
        monthly_hours=monthly_hours,
        os=os_type,
        description=description,
    )
    result = await comparator.compare(spec)
    if include_ai:
        result.recommendation = await generate_recommendation(result)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "regions": [(r.value, _region_label(r)) for r in Region],
            "storage_types": [t.value for t in StorageType],
            "db_types": [d.value for d in DatabaseType],
            "token_counting": token_counting_enabled(),
            "machine_roles": [r.value for r in MachineRole],
            "result": result,
            # Preserve form values
            "form": {
                "cpu_cores": cpu_cores,
                "ram_gb": ram_gb,
                "storage_gb": storage_gb,
                "storage_type": storage_type,
                "network_transfer_gb": network_transfer_gb,
                "database_type": database_type,
                "region": region,
                "monthly_hours": monthly_hours,
                "os_type": os_type,
                "description": description,
                "include_ai": include_ai,
            },
        },
    )


def _region_label(r: Region) -> str:
    labels = {
        Region.US_EAST_1: "US East (N. Virginia)",
        Region.US_WEST_2: "US West (Oregon)",
        Region.AP_NORTHEAST_1: "Asia Pacific (Tokyo)",
        Region.AP_NORTHEAST_2: "Asia Pacific (Seoul)",
        Region.AP_SOUTHEAST_1: "Asia Pacific (Singapore)",
        Region.AP_EAST_1: "Asia Pacific (Hong Kong)",
        Region.AP_EAST_2: "Asia Pacific (Taipei)",
        Region.EU_WEST_1: "Europe (Ireland)",
    }
    return labels.get(r, r.value)


def start():
    """Entry point for `cloudcost-web` command."""
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    dev = os.environ.get("CLOUDCOST_DEV", "").lower() in ("1", "true")
    uvicorn.run("cloudcost.web.app:app", host="0.0.0.0", port=port, reload=dev)
