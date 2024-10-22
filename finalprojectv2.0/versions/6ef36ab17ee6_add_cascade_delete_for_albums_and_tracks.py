"""Add cascade delete for albums and tracks

Revision ID: 6ef36ab17ee6
Revises: c5f9495caa7c
Create Date: 2024-06-05 00:58:33.165186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ef36ab17ee6'
down_revision: Union[str, None] = 'c5f9495caa7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('albums',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('artist', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('musics', sa.Column('album_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'musics', 'albums', ['album_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'musics', type_='foreignkey')
    op.drop_column('musics', 'album_id')
    op.drop_table('albums')
    # ### end Alembic commands ###
