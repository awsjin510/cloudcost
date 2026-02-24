"""FastAPI web application for cloud cost comparison."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from cloudcost.comparator import CloudCostComparator
from cloudcost.models.spec import (
    CloudSpec,
    ComparisonResult,
    DatabaseType,
    Region,
    StorageType,
)
from cloudcost.recommender import generate_recommendation

BASE_DIR = Path(__file__).parent
app = FastAPI(title="CloudCost", description="Multi-cloud cost comparison engine")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

comparator = CloudCostComparator()


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


@app.post("/api/compare", response_model=ComparisonResult)
async def api_compare(req: CompareRequest) -> ComparisonResult:
    """JSON API: compare cloud costs."""
    spec = CloudSpec(
        cpu_cores=req.cpu_cores,
        ram_gb=req.ram_gb,
        storage_gb=req.storage_gb,
        storage_type=StorageType(req.storage_type),
        network_transfer_gb=req.network_transfer_gb,
        database_type=DatabaseType(req.database_type),
        region=Region(req.region),
        monthly_hours=req.monthly_hours,
        os=req.os,
        description=req.description,
    )
    result = await comparator.compare(spec)
    if req.include_ai:
        result.recommendation = await generate_recommendation(result)
    return result


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
    spec = CloudSpec(
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        storage_type=StorageType(storage_type),
        network_transfer_gb=network_transfer_gb,
        database_type=DatabaseType(database_type),
        region=Region(region),
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
        Region.EU_WEST_1: "Europe (Ireland)",
    }
    return labels.get(r, r.value)


def start():
    """Entry point for `cloudcost-web` command."""
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("cloudcost.web.app:app", host="0.0.0.0", port=port, reload=True)
