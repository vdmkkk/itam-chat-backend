"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2025-11-04 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('avatar', sa.String(length=2048), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.create_index('ix_user_username', 'user', ['username'], unique=True)
    op.create_index('ix_user_username_lower', 'user', [sa.text('lower(username)')], unique=True)
    op.create_index('ix_user_first_name_lower', 'user', [sa.text('lower(first_name)')])
    op.create_index('ix_user_last_name_lower', 'user', [sa.text('lower(last_name)')])

    # chats
    op.create_table(
        'chat',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('is_group', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('avatar', sa.String(length=2048), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # chat users
    op.create_table(
        'chatuser',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('chat_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_chatuser_chat_id', 'chatuser', ['chat_id'])
    op.create_index('ix_chatuser_user_id', 'chatuser', ['user_id'])

    # messages
    op.create_table(
        'message',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('chat_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('text_content', sa.String(length=4000), nullable=True),
        sa.Column('image_content', sa.String(length=2048), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_message_created_at', 'message', ['created_at'])
    op.create_index('ix_message_chat_id', 'message', ['chat_id'])

    # message seen
    op.create_table(
        'messageseen',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('message.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('message_id', 'user_id', name='uq_message_seen_message_user'),
    )
    op.create_index('ix_messageseen_message_id', 'messageseen', ['message_id'])
    op.create_index('ix_messageseen_user_id', 'messageseen', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_messageseen_user_id', table_name='messageseen')
    op.drop_index('ix_messageseen_message_id', table_name='messageseen')
    op.drop_table('messageseen')

    op.drop_index('ix_message_chat_id', table_name='message')
    op.drop_index('ix_message_created_at', table_name='message')
    op.drop_table('message')

    op.drop_index('ix_chatuser_user_id', table_name='chatuser')
    op.drop_index('ix_chatuser_chat_id', table_name='chatuser')
    op.drop_table('chatuser')

    op.drop_table('chat')

    op.drop_index('ix_user_last_name_lower', table_name='user')
    op.drop_index('ix_user_first_name_lower', table_name='user')
    op.drop_index('ix_user_username_lower', table_name='user')
    op.drop_index('ix_user_username', table_name='user')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')


