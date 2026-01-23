"""add_verification_and_privacy_models

Revision ID: 5930599a8caa
Revises: f248f041b3f4
Create Date: 2026-01-23 10:37:28.635629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5930599a8caa'
down_revision: Union[str, None] = 'f248f041b3f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
