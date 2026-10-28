#!/usr/bin/env python3
"""
Parallel document reference validation using sub-agents.
Dispatches multiple validation tasks in parallel for faster processing.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Import extraction logic directly (no parallel needed for this)
from extract_references import extract_references


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate references in parallel using sub-agents"
    )
    parser.add_argument("document", help="Path to Markdown document")
    parser.add_argument(
        "--output", "-o", default="./validation-output",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--max-workers", "-w", type=int, default=5,
        help="Maximum parallel workers (default: 5)"
    )
    parser.add_argument(
        "--timeout", type=int, default=30,
        help="Request timeout per reference in seconds"
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
        help="Semantic match threshold 0-1 (default: 0.35 for citation-style docs, use 0.6 for claim verification)"
    )
    parser.add_argument(
        "--dispatch-method", choices=["subagent", "thread", "auto"], default="auto",
        help="Dispatch method: subagent (MCP), thread (local), auto (choose based on env)"
    )
    return parser.parse_args()


def validate_single_reference(
    ref: Dict[str, Any],
    timeout: int = 30,
    use_browser: bool = False,
    check_authority: bool = True,
    semantic_threshold: float = 0.6
) -> Dict[str, Any]:
    """
    Validate a single reference.
    This function runs in parallel for each reference.
    """
    import fetch_content
    import verify_claim
    import check_authority
    
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
        "alternatives": [],
        "processing_time": 0
    }
    
    start_time = time.time()
    
    try:
        # Check authority
        if check_authority:
            authority = check_authority.check_authority(ref["url"])
            result["authority_check"] = authority
            if not authority["is_authoritative"]:
                result["status"] = "unreliable"
                result["requires_review"] = True
        
        # Fetch content
        fetch_result = fetch_content.fetch_content(
            ref["url"],
            timeout=timeout,
            use_browser=use_browser
        )
        
        if not fetch_result["success"]:
            result["status"] = "failed"
            result["fetch_error"] = fetch_result.get("error", "Unknown")
            result["requires_review"] = True
            result["processing_time"] = time.time() - start_time
            return result
        
        # Verify claim
        content = fetch_result.get("content", "")
        if not content or len(content) < 200:
            # Content too short - likely anti-scraping or fetch failure
            result["status"] = "failed"
            result["fetch_error"] = f"Content too short ({len(content)} chars) - possible anti-scraping"
            result["requires_review"] = True
        elif ref.get("claim"):
            verification = verify_claim.verify_claim(
                ref["claim"],
                content,
                threshold=semantic_threshold
            )
            result["confidence"] = verification["confidence"]
            result["status"] = verification["status"]
            result["excerpt"] = verification.get("excerpt", "")
            result["verification_reason"] = verification.get("reason", "")
            
            if verification["status"] in ["partial", "mismatch"]:
                result["requires_review"] = True
        else:
            result["status"] = "no_claim"
        
    except Exception as e:
        result["status"] = "error"
        result["fetch_error"] = str(e)
        result["requires_review"] = True
    
    result["processing_time"] = time.time() - start_time
    return result


def validate_document_parallel(
    doc_path: str,
    output_dir: str,
    max_workers: int = 5,
    timeout: int = 30,
    use_browser: bool = False,
    check_authority: bool = True,
    semantic_threshold: float = 0.6,
    dispatch_method: str = "auto"
) -> Dict[str, Any]:
    """Validate all references in a document using parallel processing."""
    
    doc_path = Path(doc_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Validating references in: {doc_path}")
    print(f"⚡ Using {max_workers} parallel workers\n")
    
    # Step 1: Extract references (sequential, fast)
    print("📖 Extracting references...")
    references = extract_references(str(doc_path))
    print(f"   Found {len(references)} reference(s)\n")
    
    if not references:
        print("   No references found to validate.")
        return {"document": str(doc_path), "references": [], "summary": {}}
    
    # Step 2: Validate in parallel
    results = []
    failed_fetches = []
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for local parallel processing
    # (Sub-agent dispatch would be handled by the MCP caller)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_ref = {}
        for i, ref in enumerate(references):
            future = executor.submit(
                validate_single_reference,
                ref,
                timeout,
                use_browser,
                check_authority,
                semantic_threshold
            )
            future_to_ref[future] = (i, ref)
        
        # Process results as they complete
        completed = 0
        for future in as_completed(future_to_ref):
            idx, ref = future_to_ref[future]
            completed += 1
            
            try:
                result = future.result()
                results.append((idx, result))
                
                # Print progress
                status_emoji = {
                    "verified": "✅",
                    "partial": "⚠️",
                    "mismatch": "❌",
                    "failed": "🔍",
                    "unreliable": "🚫",
                    "no_claim": "ℹ️",
                    "error": "💥"
                }.get(result["status"], "❓")
                
                print(f"[{completed}/{len(references)}] {status_emoji} {ref['url'][:50]}... "
                      f"({result.get('processing_time', 0):.1f}s)")
                
                if result["status"] == "failed":
                    failed_fetches.append({
                        "url": ref["url"],
                        "error": result.get("fetch_error", "Unknown")
                    })
                    
            except Exception as e:
                print(f"[{completed}/{len(references)}] 💥 {ref['url'][:50]}... ERROR: {e}")
                failed_fetches.append({
                    "url": ref["url"],
                    "error": str(e)
                })
                results.append((idx, {
                    "claim": ref.get("claim", ""),
                    "url": ref["url"],
                    "reference_type": ref.get("type", "unknown"),
                    "status": "error",
                    "fetch_error": str(e),
                    "requires_review": True
                }))
    
    total_time = time.time() - start_time
    
    # Sort results by original order
    results.sort(key=lambda x: x[0])
    results = [r[1] for r in results]
    
    # Generate summary
    summary = {
        "total": len(references),
        "verified": sum(1 for r in results if r["status"] == "verified"),
        "partial": sum(1 for r in results if r["status"] == "partial"),
        "mismatch": sum(1 for r in results if r["status"] == "mismatch"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "unreliable": sum(1 for r in results if r["status"] == "unreliable"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "needs_review": sum(1 for r in results if r["requires_review"]),
        "total_time_seconds": round(total_time, 2),
        "avg_time_per_reference": round(total_time / len(references), 2) if references else 0
    }
    
    # Build report
    report = {
        "document": str(doc_path),
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "parallel_config": {
            "max_workers": max_workers,
            "timeout": timeout,
            "use_browser": use_browser,
            "check_authority": check_authority,
            "semantic_threshold": semantic_threshold
        },
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
    pc = report["parallel_config"]
    
    lines = [
        "# Document Reference Validation Report",
        "",
        f"**Document:** `{report['document']}`",
        f"**Timestamp:** {report['timestamp']}",
        f"**Processing Mode:** Parallel ({pc['max_workers']} workers)",
        f"**Total Time:** {s['total_time_seconds']}s",
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
        f"| 💥 Error | {s['error']} |",
        f"| **Needs Review** | **{s['needs_review']}** |",
        "",
        f"**Performance:** {s['avg_time_per_reference']}s avg per reference",
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
            "error": "💥",
            "pending": "⏳"
        }.get(result["status"], "❓")
        
        lines.extend([
            f"### [{i}] {status_emoji} {result['status'].upper()}",
            "",
            f"**URL:** [{result['url']}]({result['url']})",
            f"**Type:** {result['reference_type']}",
            f"**Processing Time:** {result.get('processing_time', 0):.2f}s",
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
    
    report = validate_document_parallel(
        args.document,
        args.output,
        max_workers=args.max_workers,
        timeout=args.timeout,
        use_browser=args.use_browser,
        check_authority=args.check_authority,
        semantic_threshold=args.semantic_threshold,
        dispatch_method=args.dispatch_method
    )
    
    s = report["summary"]
    print("\n" + "=" * 50)
    print("PARALLEL VALIDATION COMPLETE")
    print("=" * 50)
    print(f"Total references: {s['total']}")
    print(f"✅ Verified: {s['verified']}")
    print(f"⚠️ Partial: {s['partial']}")
    print(f"❌ Mismatch: {s['mismatch']}")
    print(f"🔍 Failed: {s['failed']}")
    print(f"🚫 Unreliable: {s['unreliable']}")
    print(f"💥 Errors: {s['error']}")
    print(f"🚩 Needs Review: {s['needs_review']}")
    print(f"\n⏱️  Total time: {s['total_time_seconds']}s")
    print(f"⏱️  Avg per reference: {s['avg_time_per_reference']}s")
    
    if s['needs_review'] > 0:
        print(f"\n⚠️  {s['needs_review']} item(s) require human review.")
        sys.exit(2)


if __name__ == "__main__":
    main()
