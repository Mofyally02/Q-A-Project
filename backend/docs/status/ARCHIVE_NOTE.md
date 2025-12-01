# Archive Note

## Old Application Code

The old application code that was in the `app/` directory has been removed as part of the backbone cleanup.

The old structure included:
- Old routes (admin, client, expert)
- Old services
- Old models
- Old utilities

**All functionality has been replaced by the new backbone structure in `src/app/`**

If you need to reference the old code, it should be available in git history.

## Current Structure

The new clean backbone is located in:
- `src/app/` - Main application code
- `src/app/core/` - Configuration and security
- `src/app/db/` - Database management
- `src/app/models/` - SQLAlchemy models
- `src/app/api/v1/` - API routes
- `src/app/utils/` - Utilities

See `BACKBONE_README.md` for complete documentation.

