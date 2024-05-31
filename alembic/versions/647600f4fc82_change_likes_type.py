"""change likes type

Revision ID: 647600f4fc82
Revises: dc07554b1b00
Create Date: 2024-05-28 02:06:06.570622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '647600f4fc82'
down_revision: Union[str, None] = 'dc07554b1b00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lz_posts', 'likes',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=False,
               postgresql_using='likes::integer')
    op.alter_column('lz_posts', 'dislikes',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=False,
               postgresql_using='likes::integer')
               
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lz_posts', 'dislikes',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('lz_posts', 'likes',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    # ### end Alembic commands ###
