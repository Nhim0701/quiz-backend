"""update responses table schema

Revision ID: b6b6f926d575
Revises: cfd5ca7cd517
Create Date: 2025-11-20 21:24:53.856821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6b6f926d575'
down_revision: Union[str, Sequence[str], None] = 'cfd5ca7cd517'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing columns to responses table
    op.add_column('responses', sa.Column('selected_option_id', sa.Integer(), nullable=True))
    op.add_column('responses', sa.Column('answered_at', sa.DateTime(), nullable=True))

    # Create foreign key constraint
    op.create_foreign_key('fk_responses_selected_option', 'responses', 'answers', ['selected_option_id'], ['id'])

    # Set default values for existing rows (if any)
    op.execute("UPDATE responses SET answered_at = created_at WHERE answered_at IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign key and columns
    op.drop_constraint('fk_responses_selected_option', 'responses', type_='foreignkey')
    op.drop_column('responses', 'answered_at')
    op.drop_column('responses', 'selected_option_id')
