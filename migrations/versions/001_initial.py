"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-03-13
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create flights table
    op.create_table(
        'flights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('callsign', sa.String(), nullable=True),
        sa.Column('icao24', sa.String(), nullable=True),
        sa.Column('departure_time', sa.DateTime(), nullable=True),
        sa.Column('arrival_time', sa.DateTime(), nullable=True),
        sa.Column('departure_airport', sa.String(), nullable=True),
        sa.Column('arrival_airport', sa.String(), nullable=True),
        sa.Column('aircraft_type', sa.String(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flights_callsign'), 'flights', ['callsign'], unique=False)
    op.create_index(op.f('ix_flights_departure_time'), 'flights', ['departure_time'], unique=False)
    op.create_index(op.f('ix_flights_arrival_time'), 'flights', ['arrival_time'], unique=False)
    op.create_index(op.f('ix_flights_departure_airport'), 'flights', ['departure_airport'], unique=False)
    op.create_index(op.f('ix_flights_arrival_airport'), 'flights', ['arrival_airport'], unique=False)

    # Create flight_states table
    op.create_table(
        'flight_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_id', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('altitude', sa.Float(), nullable=True),
        sa.Column('velocity', sa.Float(), nullable=True),
        sa.Column('on_ground', sa.Boolean(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flight_states_timestamp'), 'flight_states', ['timestamp'], unique=False)

    # Create beverage_inventory table
    op.create_table(
        'beverage_inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_id', sa.Integer(), nullable=True),
        sa.Column('coffee_initial', sa.Integer(), nullable=True),
        sa.Column('coffee_final', sa.Integer(), nullable=True),
        sa.Column('water_initial', sa.Integer(), nullable=True),
        sa.Column('water_final', sa.Integer(), nullable=True),
        sa.Column('soda_initial', sa.Integer(), nullable=True),
        sa.Column('soda_final', sa.Integer(), nullable=True),
        sa.Column('juice_initial', sa.Integer(), nullable=True),
        sa.Column('juice_final', sa.Integer(), nullable=True),
        sa.Column('alcohol_initial', sa.Integer(), nullable=True),
        sa.Column('alcohol_final', sa.Integer(), nullable=True),
        sa.Column('total_weight_initial', sa.Float(), nullable=True),
        sa.Column('total_weight_final', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.Column('is_actual', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create weather_data table
    op.create_table(
        'weather_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('airport_code', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('precipitation', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('wind_direction', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weather_data_airport_code'), 'weather_data', ['airport_code'], unique=False)
    op.create_index(op.f('ix_weather_data_timestamp'), 'weather_data', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_table('weather_data')
    op.drop_table('beverage_inventory')
    op.drop_table('flight_states')
    op.drop_table('flights') 