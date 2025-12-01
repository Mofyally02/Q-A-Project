"""
Compliance and audit CRUD operations
"""

from typing import Optional, List, Dict, Any
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def get_flagged_content(
    db: asyncpg.Connection,
    reason: Optional[str] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get flagged content with filters"""
    offset = (page - 1) * page_size
    conditions = []
    params = []
    param_count = 0
    
    if reason:
        param_count += 1
        conditions.append(f"reason = ${param_count}")
        params.append(reason)
    
    if severity:
        param_count += 1
        conditions.append(f"severity = ${param_count}")
        params.append(severity)
    
    if resolved is not None:
        param_count += 1
        conditions.append(f"resolved = ${param_count}")
        params.append(resolved)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM compliance_flags WHERE {where_clause}"
    total = await db.fetchval(count_query, *params)
    
    # Get flagged items
    param_count += 1
    params.append(page_size)
    param_count += 1
    params.append(offset)
    
    query = f"""
        SELECT * FROM compliance_flags
        WHERE {where_clause}
        ORDER BY flagged_at DESC
        LIMIT ${param_count - 1} OFFSET ${param_count}
    """
    
    rows = await db.fetch(query, *params)
    items = [dict(row) for row in rows]
    
    # Get statistics
    stats_query = """
        SELECT 
            reason,
            COUNT(*) as count
        FROM compliance_flags
        GROUP BY reason
    """
    by_reason_rows = await db.fetch(stats_query)
    by_reason = {row["reason"]: row["count"] for row in by_reason_rows}
    
    severity_query = """
        SELECT 
            severity,
            COUNT(*) as count
        FROM compliance_flags
        GROUP BY severity
    """
    by_severity_rows = await db.fetch(severity_query)
    by_severity = {row["severity"]: row["count"] for row in by_severity_rows}
    
    return {
        "items": items,
        "total": total,
        "by_reason": by_reason,
        "by_severity": by_severity
    }


async def get_user_compliance_history(
    db: asyncpg.Connection,
    user_id: UUID
) -> Dict[str, Any]:
    """Get user compliance history"""
    # Get all violations for user
    violations = await db.fetch("""
        SELECT 
            cf.*,
            q.question_text,
            a.answer_text
        FROM compliance_flags cf
        LEFT JOIN questions q ON cf.content_id = q.id AND cf.content_type = 'question'
        LEFT JOIN answers a ON cf.content_id = a.id AND cf.content_type = 'answer'
        WHERE (q.client_id = $1 OR a.expert_id = $1 OR cf.user_id = $1)
        ORDER BY cf.flagged_at DESC
    """, user_id)
    
    # Calculate statistics
    total_violations = len(violations)
    violations_by_type = {}
    for v in violations:
        reason = v["reason"]
        violations_by_type[reason] = violations_by_type.get(reason, 0) + 1
    
    last_violation = violations[0]["flagged_at"] if violations else None
    
    # Calculate compliance score (100 - (violations * 5), min 0)
    compliance_score = max(0, 100 - (total_violations * 5))
    
    # Determine status
    if total_violations == 0:
        status = "clean"
    elif total_violations < 3:
        status = "warning"
    elif total_violations < 10:
        status = "flagged"
    else:
        status = "banned"
    
    return {
        "user_id": user_id,
        "total_violations": total_violations,
        "violations_by_type": violations_by_type,
        "last_violation": last_violation,
        "compliance_score": compliance_score,
        "status": status,
        "violations": [dict(v) for v in violations]
    }


async def create_compliance_flag(
    db: asyncpg.Connection,
    content_id: UUID,
    content_type: str,
    reason: str,
    severity: str,
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[UUID] = None
) -> UUID:
    """Create compliance flag"""
    row = await db.fetchrow("""
        INSERT INTO compliance_flags 
        (content_id, content_type, reason, severity, details, user_id)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
    """, content_id, content_type, reason, severity,
        json.dumps(details) if details else None, user_id)
    return row['id']


async def resolve_compliance_flag(
    db: asyncpg.Connection,
    flag_id: UUID,
    resolved_by: UUID,
    resolution_notes: Optional[str] = None
) -> bool:
    """Resolve compliance flag"""
    result = await db.execute("""
        UPDATE compliance_flags 
        SET resolved = TRUE, resolved_at = NOW(), resolved_by = $1, resolution_notes = $2
        WHERE id = $3
    """, resolved_by, resolution_notes, flag_id)
    return result == "UPDATE 1"


async def get_compliance_stats(db: asyncpg.Connection) -> Dict[str, Any]:
    """Get compliance statistics"""
    stats = await db.fetchrow("""
        SELECT 
            COUNT(*) as total_flagged,
            COUNT(*) FILTER (WHERE resolved = TRUE) as resolved,
            COUNT(*) FILTER (WHERE resolved = FALSE) as pending,
            COUNT(*) FILTER (WHERE reason = 'ai_content') as ai_content_detections,
            COUNT(*) FILTER (WHERE reason = 'plagiarism') as plagiarism_detections,
            COUNT(*) FILTER (WHERE reason = 'vpn') as vpn_detections,
            COUNT(*) FILTER (WHERE reason = 'suspicious_activity') as suspicious_activity
        FROM compliance_flags
    """)
    
    # Get by reason
    by_reason = await db.fetch("""
        SELECT reason, COUNT(*) as count
        FROM compliance_flags
        GROUP BY reason
    """)
    
    # Get by severity
    by_severity = await db.fetch("""
        SELECT severity, COUNT(*) as count
        FROM compliance_flags
        GROUP BY severity
    """)
    
    result = dict(stats) if stats else {}
    result["by_reason"] = {row["reason"]: row["count"] for row in by_reason}
    result["by_severity"] = {row["severity"]: row["count"] for row in by_severity}
    
    return result


async def export_audit_logs(
    db: asyncpg.Connection,
    format: str = "json",
    admin_id: Optional[UUID] = None,
    action_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Export audit logs in specified format"""
    conditions = []
    params = []
    param_count = 0
    
    if admin_id:
        param_count += 1
        conditions.append(f"aa.admin_id = ${param_count}")
        params.append(admin_id)
    
    if action_type:
        param_count += 1
        conditions.append(f"aa.action_type = ${param_count}")
        params.append(action_type)
    
    if date_from:
        param_count += 1
        conditions.append(f"aa.created_at >= ${param_count}")
        params.append(date_from)
    
    if date_to:
        param_count += 1
        conditions.append(f"aa.created_at <= ${param_count}")
        params.append(date_to)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT 
            aa.*,
            u.email as admin_email
        FROM admin_actions aa
        LEFT JOIN users u ON aa.admin_id = u.id
        WHERE {where_clause}
        ORDER BY aa.created_at DESC
    """
    
    rows = await db.fetch(query, *params)
    return [dict(row) for row in rows]

