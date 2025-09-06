from alembic import op
import sqlalchemy as sa


revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('prices',
    sa.Column('symbol', sa.String(), nullable=False),
    sa.Column('ts', sa.DateTime(), nullable=False),
    sa.Column('o', sa.Float()), sa.Column('h', sa.Float()), sa.Column('l', sa.Float()), sa.Column('c', sa.Float()), sa.Column('v', sa.Float()),
    sa.PrimaryKeyConstraint('symbol','ts'))
    op.create_table('news',
    sa.Column('symbol', sa.String(), nullable=False),
    sa.Column('ts', sa.DateTime(), nullable=False),
    sa.Column('source', sa.String()), sa.Column('headline', sa.String()), sa.Column('url', sa.String()),
    sa.Column('sentiment', sa.Float()), sa.Column('p_pos', sa.Float()), sa.Column('p_neg', sa.Float()),
    sa.PrimaryKeyConstraint('symbol','ts','headline'))
    op.create_table('features',
    sa.Column('symbol', sa.String(), nullable=False), sa.Column('ts', sa.DateTime(), nullable=False),
    sa.Column('rsi', sa.Float()), sa.Column('macd', sa.Float()), sa.Column('atr', sa.Float()), sa.Column('vol', sa.Float()), sa.Column('sent_agg', sa.Float()),
    sa.PrimaryKeyConstraint('symbol','ts'))
    op.create_table('runs',
    sa.Column('id', sa.String(), primary_key=True), sa.Column('status', sa.String()), sa.Column('algo', sa.String()),
    sa.Column('params_json', sa.JSON()), sa.Column('started_at', sa.DateTime()), sa.Column('finished_at', sa.DateTime()), sa.Column('metrics_json', sa.JSON()))
    op.create_table('signals',
    sa.Column('run_id', sa.String(), nullable=False), sa.Column('symbol', sa.String(), nullable=False), sa.Column('ts', sa.DateTime(), nullable=False),
    sa.Column('action', sa.Integer()), sa.Column('confidence', sa.Float()), sa.Column('price', sa.Float()), sa.Column('pnl_1d', sa.Float()), sa.Column('pnl_5d', sa.Float()),
    sa.PrimaryKeyConstraint('run_id','symbol','ts'))


def downgrade():
    for t in ('signals','runs','features','news','prices'):
        op.drop_table(t)