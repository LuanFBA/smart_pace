"""add_average_power_watts_to_workout_logs

Revision ID: b1f3e7d9a452
Revises: a2caaccfb60e
Create Date: 2026-04-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b1f3e7d9a452'
down_revision: Union[str, Sequence[str], None] = 'a2caaccfb60e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Coluna nullable — registros existentes de corrida ficam com NULL
    op.add_column(
        'workout_logs',
        sa.Column('average_power_watts', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('workout_logs', 'average_power_watts')
