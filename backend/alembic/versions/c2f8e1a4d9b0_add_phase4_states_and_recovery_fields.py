"""Add Phase 4 states and recovery fields

Revision ID: c2f8e1a4d9b0
Revises: 79f19d2b77d3
Create Date: 2026-09-04 23:13:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2f8e1a4d9b0'
down_revision: Union[str, Sequence[str], None] = '79f19d2b77d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new enum values to recovery_case_status_enum
    # In PostgreSQL, ALTER TYPE ... ADD VALUE cannot run inside an explicit transaction in older versions,
    # but in Postgres 12+ it works with commit or IF NOT EXISTS.
    new_enum_values = [
        'INVESTIGATING',
        'RECOVERY_RECOMMENDED',
        'ACTION_APPROVED',
        'ACTION_EXECUTED',
        'ESCALATED',
        'STOPPED',
    ]
    for val in new_enum_values:
        op.execute(sa.text(f"ALTER TYPE recovery_case_status_enum ADD VALUE IF NOT EXISTS '{val}'"))

    # 2. Add new columns to recovery_cases table
    op.add_column('recovery_cases', sa.Column('recovery_attempts', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('recovery_cases', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('recovery_cases', 'expires_at')
    op.drop_column('recovery_cases', 'recovery_attempts')
