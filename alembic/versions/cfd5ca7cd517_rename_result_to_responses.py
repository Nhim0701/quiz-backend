"""rename result to responses

Revision ID: cfd5ca7cd517
Revises: a2be5cefc538
Create Date: 2025-11-02 12:18:42.154305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfd5ca7cd517'
down_revision: Union[str, Sequence[str], None] = 'a2be5cefc538'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("results", "responses")


def downgrade() -> None:
    op.rename_table("responses", "result")
