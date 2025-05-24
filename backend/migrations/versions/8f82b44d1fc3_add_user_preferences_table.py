"""add_user_preferences_table

Revision ID: 8f82b44d1fc3
Revises: e8fe544ecdc2
Create Date: 2025-05-24 12:10:51.552992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '8f82b44d1fc3'
down_revision: Union[str, None] = 'e8fe544ecdc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - production safe."""
    conn = op.get_bind()
    
    # Check if user_preferences table exists
    table_exists = conn.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='user_preferences'"
    )).fetchone()
    
    if table_exists:
        # Check current schema
        columns = conn.execute(text("PRAGMA table_info(user_preferences)")).fetchall()
        column_names = [col[1] for col in columns]  # col[1] is column name
        
        if 'preferences' in column_names and 'preferences_text' not in column_names:
            # Old schema exists - need to migrate data
            print("🔄 Migrating existing user_preferences data...")
            
            # Create temporary table with new schema
            op.create_table('user_preferences_new',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('user_id', sa.Integer(), nullable=False),
                sa.Column('preferences_text', sa.Text(), nullable=False),
                sa.Column('last_updated', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
                sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                sa.PrimaryKeyConstraint('id')
            )
            
            # Copy data from old table to new table (preferences -> preferences_text)
            conn.execute(text("""
                INSERT INTO user_preferences_new (id, user_id, preferences_text, last_updated)
                SELECT id, user_id, preferences, 
                       COALESCE(last_updated, CURRENT_TIMESTAMP)
                FROM user_preferences
            """))
            
            # Drop old table and rename new one
            op.drop_table('user_preferences')
            op.rename_table('user_preferences_new', 'user_preferences')
            
            print("✅ Data migration completed successfully!")
            
        elif 'preferences_text' in column_names:
            # New schema already exists - do nothing
            print("✅ Table already has correct schema")
            
        else:
            # Unknown schema - safer to recreate
            print("⚠️  Unknown schema detected, recreating table...")
            op.drop_table('user_preferences')
            op.create_table('user_preferences',
                sa.Column('id', sa.Integer(), nullable=False),
                sa.Column('user_id', sa.Integer(), nullable=False),
                sa.Column('preferences_text', sa.Text(), nullable=False),
                sa.Column('last_updated', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
                sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                sa.PrimaryKeyConstraint('id')
            )
    else:
        # Table doesn't exist - create fresh
        print("🆕 Creating new user_preferences table...")
        op.create_table('user_preferences',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('preferences_text', sa.Text(), nullable=False),
            sa.Column('last_updated', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop user_preferences table
    op.drop_table('user_preferences')
