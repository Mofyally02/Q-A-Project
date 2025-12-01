"""
Override triggers CRUD operations
"""

from typing import Dict, Any, Optional
import asyncpg
from uuid import UUID
from datetime import datetime
import json


async def bypass_ai_check(
    db: asyncpg.Connection,
    question_id: UUID,
    overridden_by: UUID,
    reason: str
) -> Dict[str, Any]:
    """Bypass AI content check"""
    # Update question to bypass AI check
    await db.execute("""
        UPDATE questions
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'::jsonb),
            '{ai_bypassed}',
            to_jsonb(TRUE)
        ),
        metadata = jsonb_set(
            metadata,
            '{ai_bypass_reason}',
            to_jsonb($1)
        ),
        metadata = jsonb_set(
            metadata,
            '{ai_bypassed_by}',
            to_jsonb($2::text)
        ),
        metadata = jsonb_set(
            metadata,
            '{ai_bypassed_at}',
            to_jsonb(NOW()::text)
        )
        WHERE id = $3
    """, reason, overridden_by, question_id)
    
    return {
        "success": True,
        "override_id": question_id,
        "action": "ai_bypass",
        "target_id": question_id
    }


async def pass_originality_check(
    db: asyncpg.Connection,
    answer_id: UUID,
    overridden_by: UUID,
    reason: str
) -> Dict[str, Any]:
    """Pass originality check override"""
    await db.execute("""
        UPDATE answers
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'::jsonb),
            '{originality_bypassed}',
            to_jsonb(TRUE)
        ),
        metadata = jsonb_set(
            metadata,
            '{originality_bypass_reason}',
            to_jsonb($1)
        ),
        metadata = jsonb_set(
            metadata,
            '{originality_bypassed_by}',
            to_jsonb($2::text)
        ),
        metadata = jsonb_set(
            metadata,
            '{originality_bypassed_at}',
            to_jsonb(NOW()::text)
        )
        WHERE id = $3
    """, reason, overridden_by, answer_id)
    
    return {
        "success": True,
        "override_id": answer_id,
        "action": "originality_pass",
        "target_id": answer_id
    }


async def override_confidence_threshold(
    db: asyncpg.Connection,
    question_id: UUID,
    min_confidence: Optional[float],
    overridden_by: UUID,
    reason: str
) -> Dict[str, Any]:
    """Override confidence threshold"""
    await db.execute("""
        UPDATE questions
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'::jsonb),
            '{confidence_overridden}',
            to_jsonb(TRUE)
        ),
        metadata = jsonb_set(
            metadata,
            '{min_confidence_override}',
            to_jsonb($1)
        ),
        metadata = jsonb_set(
            metadata,
            '{confidence_override_reason}',
            to_jsonb($2)
        ),
        metadata = jsonb_set(
            metadata,
            '{confidence_overridden_by}',
            to_jsonb($3::text)
        ),
        metadata = jsonb_set(
            metadata,
            '{confidence_overridden_at}',
            to_jsonb(NOW()::text)
        )
        WHERE id = $4
    """, min_confidence, reason, overridden_by, question_id)
    
    return {
        "success": True,
        "override_id": question_id,
        "action": "confidence_override",
        "target_id": question_id
    }


async def skip_humanization(
    db: asyncpg.Connection,
    answer_id: UUID,
    overridden_by: UUID,
    reason: str
) -> Dict[str, Any]:
    """Skip humanization step"""
    await db.execute("""
        UPDATE answers
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'::jsonb),
            '{humanization_skipped}',
            to_jsonb(TRUE)
        ),
        metadata = jsonb_set(
            metadata,
            '{humanization_skip_reason}',
            to_jsonb($1)
        ),
        metadata = jsonb_set(
            metadata,
            '{humanization_skipped_by}',
            to_jsonb($2::text)
        ),
        metadata = jsonb_set(
            metadata,
            '{humanization_skipped_at}',
            to_jsonb(NOW()::text)
        )
        WHERE id = $3
    """, reason, overridden_by, answer_id)
    
    return {
        "success": True,
        "override_id": answer_id,
        "action": "humanization_skip",
        "target_id": answer_id
    }


async def bypass_expert_review(
    db: asyncpg.Connection,
    answer_id: UUID,
    overridden_by: UUID,
    reason: str
) -> Dict[str, Any]:
    """Bypass expert review"""
    await db.execute("""
        UPDATE answers
        SET status = 'approved',
            metadata = jsonb_set(
                COALESCE(metadata, '{}'::jsonb),
                '{expert_review_bypassed}',
                to_jsonb(TRUE)
            ),
            metadata = jsonb_set(
                metadata,
                '{expert_review_bypass_reason}',
                to_jsonb($1)
            ),
            metadata = jsonb_set(
                metadata,
                '{expert_review_bypassed_by}',
                to_jsonb($2::text)
            ),
            metadata = jsonb_set(
                metadata,
                '{expert_review_bypassed_at}',
                to_jsonb(NOW()::text)
            )
        WHERE id = $3
    """, reason, overridden_by, answer_id)
    
    return {
        "success": True,
        "override_id": answer_id,
        "action": "expert_bypass",
        "target_id": answer_id
    }

