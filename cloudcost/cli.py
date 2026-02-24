"""CLI entry point for cloudcost.

Usage:
    python -m cloudcost.cli --cpu 4 --ram 16 --storage 100 --region ap-northeast-1
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from dotenv import load_dotenv

load_dotenv()

from cloudcost.builders import build_cloud_spec
from cloudcost.comparator import CloudCostComparator
from cloudcost.recommender import generate_recommendation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cloudcost",
        description="Compare cloud costs across AWS, GCP, Azure, and Oracle Cloud.",
    )
    parser.add_argument("--cpu", type=int, required=True, help="Number of vCPUs")
    parser.add_argument("--ram", type=float, required=True, help="RAM in GB")
    parser.add_argument("--storage", type=float, default=0, help="Storage in GB")
    parser.add_argument(
        "--storage-type",
        choices=[t.value for t in StorageType],
        default="ssd",
        help="Storage type (default: ssd)",
    )
    parser.add_argument("--network", type=float, default=0, help="Monthly outbound transfer in GB")
    parser.add_argument(
        "--db",
        choices=[d.value for d in DatabaseType],
        default="none",
        help="Managed database type (default: none)",
    )
    parser.add_argument(
        "--region",
        choices=[r.value for r in Region],
        default="us-east-1",
        help="Deployment region (default: us-east-1)",
    )
    parser.add_argument("--hours", type=float, default=730, help="Monthly usage hours (default: 730)")
    parser.add_argument("--os", default="linux", help="OS type (default: linux)")
    parser.add_argument("--description", default="", help="Usage scenario description for AI recommendations")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI recommendation (faster)")
    return parser.parse_args(argv)


async def run(args: argparse.Namespace) -> None:
    spec = build_cloud_spec(
        cpu_cores=args.cpu,
        ram_gb=args.ram,
        storage_gb=args.storage,
        storage_type=args.storage_type,
        network_transfer_gb=args.network,
        database_type=args.db,
        region=args.region,
        monthly_hours=args.hours,
        os=args.os,
        description=args.description,
    )

    async with CloudCostComparator() as comparator:
        result = await comparator.compare(spec)

    # Generate recommendation
    if not args.no_ai:
        result.recommendation = await generate_recommendation(result)

    if args.json:
        print(json.dumps(result.model_dump(), indent=2, default=str))
    else:
        _print_table(result)


def _print_table(result) -> None:
    """Pretty-print the comparison result."""
    spec = result.spec
    print(f"\n{'='*60}")
    print(f"  Cloud Cost Comparison")
    print(f"  Spec: {spec.cpu_cores} vCPU / {spec.ram_gb} GB RAM / "
          f"{spec.storage_gb} GB {spec.storage_type.value.upper()}")
    print(f"  Region: {spec.region.value} | OS: {spec.os} | Hours/mo: {spec.monthly_hours}")
    print(f"{'='*60}\n")

    header = f"{'Provider':<10} {'Instance':<28} {'On-Demand/mo':>14} {'Reserved/mo':>14}"
    print(header)
    print("-" * len(header))

    for est in sorted(result.estimates, key=lambda e: e.total_monthly_on_demand):
        ri = f"${est.total_monthly_reserved_1y:.2f}" if est.total_monthly_reserved_1y else "N/A"
        cheapest_tag = " *" if est.provider == result.cheapest_on_demand else ""
        print(
            f"{est.provider.value.upper():<10} {est.matched_instance:<28} "
            f"${est.total_monthly_on_demand:>12.2f} {ri:>14}{cheapest_tag}"
        )
        for w in est.warnings:
            print(f"  ⚠ {w}")

    print(f"\n{'─'*60}")
    if result.cheapest_on_demand:
        print(f"  Cheapest On-Demand:  {result.cheapest_on_demand.value.upper()}")
    if result.cheapest_reserved:
        print(f"  Cheapest Reserved:   {result.cheapest_reserved.value.upper()}")

    if result.recommendation:
        print(f"\n{'─'*60}")
        print("  AI Recommendation:")
        print(f"{'─'*60}")
        print(result.recommendation)
    print()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
