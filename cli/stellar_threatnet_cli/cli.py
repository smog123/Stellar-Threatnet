"""Stellar ThreatNet CLI.

Talk to a ThreatNet API instance (default http://localhost:8000/api/v1).
Set THREATNET_API_URL and THREATNET_API_TOKEN in your environment or pass
--api-url / --token.
"""
import json
import os
import sys
from typing import Optional

import click
import httpx

API_URL = os.environ.get("THREATNET_API_URL", "http://localhost:8000/api/v1")
API_TOKEN = os.environ.get("THREATNET_API_TOKEN", "")


def _client(api_url: str, token: str) -> httpx.Client:
    headers = {"Authorization": f"Bearer {token or API_TOKEN}"} if (token or API_TOKEN) else {}
    return httpx.Client(base_url=api_url, headers=headers, timeout=30)


def _die(resp: httpx.Response) -> None:
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text
    click.echo(click.style(f"error [{resp.status_code}]: {detail}", fg="red"), err=True)
    sys.exit(1)


def _print_json(data) -> None:
    click.echo(json.dumps(data, indent=2, default=str))


@click.group(help="Stellar ThreatNet — the open threat intelligence platform for Stellar.")
@click.option("--api-url", envvar="THREATNET_API_URL", default=API_URL, help="API base URL.")
@click.option("--token", envvar="THREATNET_API_TOKEN", default="", help="JWT or API key token.")
@click.pass_context
def main(ctx: click.Context, api_url: str, token: str) -> None:
    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url
    ctx.obj["token"] = token


@main.group(help="Reputation lookups.")
def lookup() -> None:
    pass


@lookup.command("wallet", help="Look up a Stellar wallet (G...) reputation.")
@click.argument("address")
@click.pass_context
def lookup_wallet(ctx, address: str) -> None:
    resp = httpx.get(f"{ctx.obj['api_url']}/lookup/wallet/{address}", timeout=30)
    if resp.status_code == 404:
        click.echo(click.style(f"no threat data for {address} (treat as unknown/neutral)", fg="yellow"))
        return
    if resp.status_code != 200:
        _die(resp)
    data = resp.json()
    color = {"confirmed_malicious": "red", "suspicious": "yellow", "under_investigation": "cyan", "trusted": "green"}.get(data["status"], "white")
    click.echo(f"address : {data['address']}")
    click.echo(f"score   : {data['reputation_score']}/100")
    click.echo(f"status  : {click.style(data['status'], fg=color)}")
    click.echo(f"category: {data.get('category') or '-'}")
    click.echo(f"reason  : {data['reason']}")
    click.echo(f"reports : {data['report_count']}")


@lookup.command("domain", help="Look up a domain reputation.")
@click.argument("domain")
@click.pass_context
def lookup_domain(ctx, domain: str) -> None:
    resp = httpx.get(f"{ctx.obj['api_url']}/lookup/domain/{domain}", timeout=30)
    if resp.status_code == 404:
        click.echo(click.style(f"no threat data for {domain}", fg="yellow"))
        return
    if resp.status_code != 200:
        _die(resp)
    data = resp.json()
    click.echo(json.dumps(data, indent=2))


@lookup.command("token", help="Look up a token reputation (CODE and issuer).")
@click.argument("asset_code")
@click.argument("issuer")
@click.pass_context
def lookup_token(ctx, asset_code: str, issuer: str) -> None:
    resp = httpx.get(f"{ctx.obj['api_url']}/lookup/token/{asset_code}/{issuer}", timeout=30)
    if resp.status_code == 404:
        click.echo(click.style(f"no threat data for {asset_code}:{issuer}", fg="yellow"))
        return
    if resp.status_code != 200:
        _die(resp)
    click.echo(json.dumps(resp.json(), indent=2))


@main.command("incidents", help="List incidents (optionally filtered by status).")
@click.option("--status", default=None, help="open|investigating|resolved|dismissed")
@click.option("--limit", default=20, type=int)
@click.pass_context
def incidents(ctx, status: Optional[str], limit: int) -> None:
    params = {"limit": limit}
    if status:
        params["status"] = status
    resp = httpx.get(f"{ctx.obj['api_url']}/incidents", params=params, timeout=30)
    if resp.status_code != 200:
        _die(resp)
    data = resp.json()
    click.echo(f"total: {data['total']}\n")
    for item in data["items"]:
        click.echo(f"[{item['severity']}] {click.style(item['id'], bold=True)} — {item['title']} ({item['status']})")


@main.command("stats", help="Show global threat statistics.")
@click.pass_context
def stats(ctx) -> None:
    resp = httpx.get(f"{ctx.obj['api_url']}/stats", timeout=30)
    if resp.status_code != 200:
        _die(resp)
    click.echo(json.dumps(resp.json(), indent=2))


@main.command("submit", help="Submit a community threat report (requires a token).")
@click.argument("target_type", type=click.Choice(["wallet", "domain", "token"]))
@click.argument("target_value")
@click.option("--category", default=None, help="Suggested category, e.g. Fake Airdrop")
@click.option("--description", required=True, help="Why is this a threat?")
@click.option("--evidence-url", default=None)
@click.option("--token", default="", help="Auth token (overrides env).")
@click.pass_context
def submit(ctx, target_type: str, target_value: str, category: Optional[str], description: str, evidence_url: Optional[str], token: str) -> None:
    payload = {
        "target_type": target_type,
        "target_value": target_value,
        "category": category,
        "description": description,
        "evidence_url": evidence_url,
    }
    resp = _client(ctx.obj["api_url"], token).post("/reports", json=payload)
    if resp.status_code not in (200, 201):
        _die(resp)
    data = resp.json()
    click.echo(click.style(f"queued report {data['id']} for moderation (status: {data['status']})", fg="green"))


@main.command("feed", help="Download the full threat feed as CSV.")
@click.option("--output", default="threatnet-feed.csv", help="Output file path.")
@click.pass_context
def feed(ctx, output: str) -> None:
    resp = httpx.get(f"{ctx.obj['api_url']}/feed", timeout=60)
    if resp.status_code != 200:
        _die(resp)
    with open(output, "w", encoding="utf-8") as fh:
        fh.write(resp.text)
    click.echo(click.style(f"saved {len(resp.text)} bytes -> {output}", fg="green"))


@main.command("ai", help="Ask the AI threat assistant.")
@click.argument("query")
@click.pass_context
def ai(ctx, query: str) -> None:
    resp = httpx.post(f"{ctx.obj['api_url']}/ai/query", json={"query": query}, timeout=60)
    if resp.status_code != 200:
        _die(resp)
    data = resp.json()
    click.echo(data["analysis"])
    click.echo(click.style(f"\nsources: {', '.join(data['sources_referenced'])}", fg="blue"))
    click.echo(click.style(f"disclaimer: {data['confidence_disclaimer']}", fg="yellow"))


if __name__ == "__main__":
    main()
