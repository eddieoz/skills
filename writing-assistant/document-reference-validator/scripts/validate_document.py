#!/usr/bin/env python3
"""
Main validation orchestrator for document reference validation.
Validates all references in a Markdown document and generates reports.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

from extract_references import extract_references
from fetch_content import fetch_content
from verify_claim import verify_claim
from check_authority import check_authority


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate references in a Markdown document"
    )
    parser.add_argument("document", help="Path to Markdown document")
    parser.add_argument(
        "--output", "-o", default="./validation-output",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--timeout", type=int, default=30,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        "--use-browser", action="store_true",
        help="Force browser automation for all links"
    )
    parser.add_argument(
        "--check-authority", action="store_true", default=True,
        help="Validate source authority"
    )
    parser.add_argument(
        "--semantic-threshold", type=float, default=0.35,
        help="Semantic match threshold 0-1 (default: 0.35 for citations, 0.6 for claims)"
    )
    parser.add_argument(
        "--parallel", "-p", action="store_true",
        help="Use parallel processing (delegates to validate_parallel.py)"
    )
    parser.add_argument(
        "--max-workers", "-w", type=int, default=5,
        help="Number of parallel workers (only with --parallel)"
    )
    return parser.parse_args()


def validate_document(
    doc_path: str,
    output_dir: str,
    timeout: int = 30,
    use_browser: bool = False,
    check_authority: bool = True,
    semantic_threshold: float = 0.6
) -> Dict[str, Any]:
    """Validate all references in a document."""
    
    doc_path = Path(doc_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Validating references in: {doc_path}")
    
    # Step 1: Extract references
    print("\n📖 Extracting references...")
    references = extract_references(str(doc_path))
    print(f"   Found {len(references)} reference(s)")
    
    if not references:
        print("   No references found to validate.")
        return {"document": str(doc_path), "references": [], "summary": {}}
    
    # Step 2: Validate each reference
    results = []
    failed_fetches = []
    
    for i, ref in enumerate(references, 1):
        print(f"\n[{i}/{len(references)}] Checking: {ref['url'][:60]}...")
        
        result = {
            "claim": ref.get("claim", ""),
            "context": ref.get("context", ""),
            "url": ref["url"],
            "reference_type": ref.get("type", "unknown"),
            "status": "pending",
            "confidence": 0.0,
            "requires_review": False,
            "authority_check": None,
            "fetch_error": None,
            "alternatives": []
        }
        
        # Check authority first
        if check_authority:
            authority = check_authority(ref["url"])
            result["authority_check"] = authority
            if not authority["is_authoritative"]:
                print(f"   ⚠️  Unreliable source: {authority.get('reason', 'Unknown')}")
                result["status"] = "unreliable"
                result["requires_review"] = True
        
        # Fetch content
        fetch_result = fetch_content(
            ref["url"],
            timeout=timeout,
            use_browser=use_browser
        )
        
        if not fetch_result["success"]:
            print(f"   ❌ Failed to fetch: {fetch_result.get('error', 'Unknown error')}")
            result["status"] = "failed"
            result["fetch_error"] = fetch_result.get("error", "Unknown")
            result["requires_review"] = True
            failed_fetches.append({
                "url": ref["url"],
                "error": fetch_result.get("error", "Unknown")
            })
            results.append(result)
            continue
        
        print(f"   ✅ Content fetched ({len(fetch_result['content'])} chars)")
        
        # Verify claim against content
        if ref.get("claim"):
            verification = verify_claim(
                ref["claim"],
                fetch_result["content"],
                threshold=semantic_threshold
            )
            result["confidence"] = verification["confidence"]
            result["status"] = verification["status"]
            result["excerpt"] = verification.get("excerpt", "")
            
            if verification["status"] == "verified":
                print(f"   ✅ Claim verified (confidence: {verification['confidence']:.2f})")
            elif verification["status"] == "partial":
                print(f"   ⚠️  Partial match (confidence: {verification['confidence']:.2f})")
                result["requires_review"] = True
            else:
                print(f"   ❌ Mismatch (confidence: {verification['confidence']:.2f})")
                result["requires_review"] = True
                # TODO: Suggest alternatives
        else:
            result["status"] = "no_claim"
            print("   ℹ️  No claim found to verify")
        
        results.append(result)
    
    # Generate summary
    summary = {
        "total": len(references),
        "verified": sum(1 for r in results if r["status"] == "verified"),
        "partial": sum(1 for r in results if r["status"] == "partial"),
        "mismatch": sum(1 for r in results if r["status"] == "mismatch"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "unreliable": sum(1 for r in results if r["status"] == "unreliable"),
        "needs_review": sum(1 for r in results if r["requires_review"])
    }
    
    # Build report
    report = {
        "document": str(doc_path),
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "summary": summary,
        "results": results
    }
    
    # Save reports
    save_reports(report, failed_fetches, output_path)
    
    return report


def save_reports(report: Dict, failed_fetches: List[Dict], output_path: Path):
    """Save validation reports."""
    
    # JSON log
    json_path = output_path / "validation-log.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📝 JSON log saved: {json_path}")
    
    # Failed fetches log
    if failed_fetches:
        failed_path = output_path / "failed-fetches.log"
        with open(failed_path, "w", encoding="utf-8") as f:
            for item in failed_fetches:
                f.write(f"{item['url']} | {item['error']}\n")
        print(f"📝 Failed fetches log: {failed_path}")
    
    # Human-readable Markdown report
    md_path = output_path / "validation-report.md"
    generate_markdown_report(report, md_path)
    print(f"📝 Markdown report: {md_path}")


def generate_markdown_report(report: Dict, output_path: Path):
    """Generate human-readable Markdown report."""
    
    s = report["summary"]
    lines = [
        "# Document Reference Validation Report",
        "",
        f"**Document:** `{report['document']}`",
        f"**Timestamp:** {report['timestamp']}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
        f"| ✅ Verified | {s['verified']} |",
        f"| ⚠️ Partial | {s['partial']} |",
        f"| ❌ Mismatch | {s['mismatch']} |",
        f"| 🔍 Failed | {s['failed']} |",
        f"| 🚫 Unreliable | {s['unreliable']} |",
        f"| **Needs Review** | **{s['needs_review']}** |",
        "",
        "---",
        "",
        "## Detailed Results",
        ""
    ]
    
    for i, result in enumerate(report["results"], 1):
        status_emoji = {
            "verified": "✅",
            "partial": "⚠️",
            "mismatch": "❌",
            "failed": "🔍",
            "unreliable": "🚫",
            "no_claim": "ℹ️",
            "pending": "⏳"
        }.get(result["status"], "❓")
        
        lines.extend([
            f"### [{i}] {status_emoji} {result['status'].upper()}",
            "",
            f"**URL:** [{result['url']}]({result['url']})",
            f"**Type:** {result['reference_type']}",
        ])
        
        if result.get("claim"):
            lines.extend([
                "",
                "**Claim:**",
                f"> {result['claim']}",
            ])
        
        if result.get("confidence", 0) > 0:
            lines.append(f"**Confidence:** {result['confidence']:.2f}")
        
        if result.get("authority_check"):
            auth = result["authority_check"]
            if auth.get("is_authoritative"):
                lines.append(f"**Authority:** ✅ {auth.get('category', 'Known source')}")
            else:
                lines.append(f"**Authority:** ⚠️ {auth.get('reason', 'Unknown source')}")
        
        if result.get("excerpt"):
            excerpt = result["excerpt"][:500] + "..." if len(result["excerpt"]) > 500 else result["excerpt"]
            lines.extend([
                "",
                "**Source Excerpt:**",
                f"> {excerpt}",
            ])
        
        if result.get("fetch_error"):
            lines.extend([
                "",
                f"**Error:** `{result['fetch_error']}`",
            ])
        
        if result.get("requires_review"):
            lines.extend([
                "",
                "🚩 **FLAGGED FOR HUMAN REVIEW**",
            ])
            if result.get("alternatives"):
                lines.extend([
                    "",
                    "**Suggested Alternatives:**",
                ])
                for alt in result["alternatives"]:
                    lines.append(f"- [{alt['title']}]({alt['url']})")
        
        lines.extend(["", "---", ""])
    
    lines.extend([
        "",
        "## Next Steps",
        "",
        "1. Review all items flagged with 🚩",
        "2. Check `failed-fetches.log` for URLs that couldn't be accessed",
        "3. Replace unreliable sources with authoritative alternatives",
        "4. Update claims that don't match their sources",
        "",
        f"*See `validation-log.json` for machine-readable data.*",
        ""
    ])
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    args = parse_args()
    
    if not Path(args.document).exists():
        print(f"❌ Error: Document not found: {args.document}")
        sys.exit(1)
    
    # Delegate to parallel version if requested
    if args.parallel:
        from validate_parallel import validate_document_parallel
        report = validate_document_parallel(
            args.document,
            args.output,
            max_workers=args.max_workers,
            timeout=args.timeout,
            use_browser=args.use_browser,
            check_authority=args.check_authority,
            semantic_threshold=args.semantic_threshold
        )
    else:
        report = validate_document(
            args.document,
            args.output,
            timeout=args.timeout,
            use_browser=args.use_browser,
            check_authority=args.check_authority,
            semantic_threshold=args.semantic_threshold
        )
    
    s = report["summary"]
    print("\n" + "=" * 50)
    print("VALIDATION COMPLETE")
    print("=" * 50)
    print(f"Total references: {s['total']}")
    print(f"✅ Verified: {s['verified']}")
    print(f"⚠️ Partial: {s['partial']}")
    print(f"❌ Mismatch: {s['mismatch']}")
    print(f"🔍 Failed: {s['failed']}")
    print(f"🚫 Unreliable: {s['unreliable']}")
    print(f"🚩 Needs Review: {s['needs_review']}")
    
    if s['needs_review'] > 0:
        print(f"\n⚠️  {s['needs_review']} item(s) require human review.")
        sys.exit(2)  # Exit code 2 indicates issues found


if __name__ == "__main__":
    main()
