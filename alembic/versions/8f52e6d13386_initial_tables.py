"""initial tables

Revision ID: 8f52e6d13386
Revises: 
Create Date: 2026-07-18 19:02:37.903696

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8f52e6d13386'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    legacy = [
        'authors_same_as', 'posts_faqs', 'posts_rels',
        'payload_locked_documents_rels', 'site_settings_same_as',
        'users_sessions', 'payload_preferences_rels',
        'posts', 'categories', 'site_settings',
        'media', 'image_blobs', 'authors',
        'payload_preferences', 'payload_locked_documents',
        'payload_migrations', 'payload_kv',
    ]
    for t in legacy:
        conn.execute(sa.text(f"DROP TABLE IF EXISTS {t} CASCADE"))
    conn.execute(sa.text("DROP SCHEMA IF EXISTS payload CASCADE"))

    for col in ['lock_until', 'hash', 'reset_password_token', 'reset_password_expiration', 'updated_at', 'login_attempts', 'created_at', 'salt']:
        conn.execute(sa.text(f"ALTER TABLE users DROP COLUMN IF EXISTS {col}"))

    for idx in ['users_created_at_idx', 'users_email_idx', 'users_updated_at_idx']:
        conn.execute(sa.text(f"DROP INDEX IF EXISTS {idx}"))

    conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR NOT NULL DEFAULT ''"))
    conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR NOT NULL DEFAULT ''"))
    conn.execute(sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'USER'"))

    conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)"))

    with op.batch_alter_table('cart') as batch_op:
        batch_op.alter_column('user_id', nullable=False)
        batch_op.alter_column('product_id', nullable=False)
        batch_op.alter_column('quantity', nullable=False)
        batch_op.create_index('ix_cart_user_id', ['user_id'])
        batch_op.create_unique_constraint('uq_cart_user_product', ['user_id', 'product_id'])

    with op.batch_alter_table('order_items') as batch_op:
        batch_op.alter_column('order_id', nullable=False)
        batch_op.alter_column('product_id', nullable=False)
        batch_op.alter_column('quantity', nullable=False)
        batch_op.alter_column('price', nullable=False)
        batch_op.create_index('idx_order_items_order_id', ['order_id'])
        batch_op.create_index('idx_order_items_product_id', ['product_id'])

    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column('user_id', nullable=False)
        batch_op.alter_column('total_price', nullable=False)
        batch_op.create_index('idx_orders_created_at', ['created_at'])
        batch_op.create_index('idx_orders_status', ['status'])
        batch_op.create_index('idx_orders_user_id', ['user_id'])

    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('price', nullable=False)
        batch_op.alter_column('stock', nullable=False)
        batch_op.create_index('ix_products_category', ['category'])
        batch_op.create_index('ix_products_name', ['name'])
        batch_op.create_index('ix_products_price', ['price'])

    with op.batch_alter_table('reviews') as batch_op:
        batch_op.alter_column('user_id', nullable=False)
        batch_op.alter_column('product_id', nullable=False)
        batch_op.alter_column('rating', nullable=False)
        batch_op.create_index('idx_reviews_product_id', ['product_id'])
        batch_op.create_index('idx_reviews_rating', ['rating'])
        batch_op.create_index('idx_reviews_user_id', ['user_id'])
        batch_op.create_unique_constraint('uq_review_user_product', ['user_id', 'product_id'])

    with op.batch_alter_table('wishlist') as batch_op:
        batch_op.alter_column('user_id', nullable=False)
        batch_op.alter_column('product_id', nullable=False)
        batch_op.create_index('ix_wishlist_user_id', ['user_id'])
        batch_op.create_unique_constraint('uq_wishlist_user_product', ['user_id', 'product_id'])


def downgrade() -> None:
    with op.batch_alter_table('wishlist') as batch_op:
        batch_op.drop_constraint('uq_wishlist_user_product', type_='unique')
        batch_op.drop_index('ix_wishlist_user_id')

    with op.batch_alter_table('reviews') as batch_op:
        batch_op.drop_constraint('uq_review_user_product', type_='unique')
        batch_op.drop_index('idx_reviews_user_id')
        batch_op.drop_index('idx_reviews_rating')
        batch_op.drop_index('idx_reviews_product_id')

    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_index('ix_products_price')
        batch_op.drop_index('ix_products_name')
        batch_op.drop_index('ix_products_category')

    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_index('idx_orders_user_id')
        batch_op.drop_index('idx_orders_status')
        batch_op.drop_index('idx_orders_created_at')

    with op.batch_alter_table('order_items') as batch_op:
        batch_op.drop_index('idx_order_items_product_id')
        batch_op.drop_index('idx_order_items_order_id')

    with op.batch_alter_table('cart') as batch_op:
        batch_op.drop_constraint('uq_cart_user_product', type_='unique')
        batch_op.drop_index('ix_cart_user_id')

    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
