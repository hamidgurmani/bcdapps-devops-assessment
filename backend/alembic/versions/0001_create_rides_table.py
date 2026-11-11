"""Create the rides table."""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_rides"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("passenger_name", sa.String(length=120), nullable=False),
        sa.Column("pickup_location", sa.String(length=255), nullable=False),
        sa.Column("dropoff_location", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="requested",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('requested', 'accepted', 'in_progress', 'completed', 'cancelled')",
            name="ck_ride_status",
        ),
    )


def downgrade() -> None:
    op.drop_table("rides")
