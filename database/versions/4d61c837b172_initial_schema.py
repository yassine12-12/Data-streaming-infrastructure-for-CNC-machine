"""initial schema

Revision ID: 4d61c837b172
Revises: 
Create Date: 2023-07-29 18:13:05.579825

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '4d61c837b172'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            CREATE EXTENSION IF NOT EXISTS timescaledb; 
            """
        ),
    )

    '''
    TIMESERIES TABLE SETUP
    '''

    timeseries_timestamp_col = sa.Column(
        'timestamp', sa.TIMESTAMP, primary_key=True)

    op.create_table(
        'timeseries',
        sa.Column('sensor_name', sa.String, primary_key=True),
        timeseries_timestamp_col,
        sa.Column('humidity', sa.Integer, nullable=False),
        sa.Column('pressure', sa.Integer, nullable=False),
        sa.Column('acceleration_x', sa.Integer, nullable=False),
        sa.Column('acceleration_y', sa.Integer, nullable=False),
        sa.Column('acceleration_z', sa.Integer, nullable=False),
        sa.Column('gyro_x', sa.Integer, nullable=False),
        sa.Column('gyro_y', sa.Integer, nullable=False),
        sa.Column('gyro_z', sa.Integer, nullable=False),
        sa.Column('temperature', sa.Integer, nullable=False),
        sa.Column('noise', sa.Integer, nullable=False),
        sa.Column('light', sa.Integer, nullable=False),
    )

    conn.execute(
        text(
            """
            SELECT create_hypertable('timeseries','timestamp');; 
            """
        ),
    )

    op.create_index('idx_timeseries_timestamp', 'timeseries', [
                    'sensor_name', timeseries_timestamp_col.desc()], unique=False, postgresql_using='btree')

    '''
    IMAGES TABLE SETUP
    '''

    images_timestamp_col = sa.Column(
        'timestamp', sa.TIMESTAMP, primary_key=True)

    op.create_table(
        'images',
        sa.Column('sensor_name', sa.String, primary_key=True),
        images_timestamp_col,
        sa.Column('filename', sa.String, primary_key=True),
        sa.Column('file_data', sa.LargeBinary, nullable=False),
        sa.Column('dimension_1', sa.Integer, nullable=False),
        sa.Column('dimension_2', sa.Integer, nullable=False),
    )

    conn.execute(
        text(
            """
            SELECT create_hypertable('images','timestamp');; 
            """
        ),
    )

    op.create_index('idx_images_timestamp', 'images', [
                    'sensor_name', images_timestamp_col.desc()], unique=False, postgresql_using='btree')

    '''
    SENSORS TABLE SETUP
    '''
    op.create_table(
        'sensors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('sensor_name', sa.String, unique=True),

    )

    '''
    PROCESSED TIMESERIES TABLE SETUP
    '''

    processed_timeseries_timestamp_col = sa.Column(
        'timestamp', sa.TIMESTAMP, primary_key=True)

    op.create_table(
        'processed_timeseries',
        sa.Column('sensor_name', sa.String, primary_key=True),
        processed_timeseries_timestamp_col,
        sa.Column('humidity', sa.Integer, nullable=False),
        sa.Column('pressure', sa.Integer, nullable=False),
        sa.Column('acceleration_x', sa.Integer, nullable=False),
        sa.Column('acceleration_y', sa.Integer, nullable=False),
        sa.Column('acceleration_z', sa.Integer, nullable=False),
        sa.Column('gyro_x', sa.Integer, nullable=False),
        sa.Column('gyro_y', sa.Integer, nullable=False),
        sa.Column('gyro_z', sa.Integer, nullable=False),
        sa.Column('temperature', sa.Integer, nullable=False),
        sa.Column('noise', sa.Integer, nullable=False),
        sa.Column('light', sa.Integer, nullable=False),
    )

    conn.execute(
        text(
            """
            SELECT create_hypertable('processed_timeseries','timestamp');; 
            """
        ),
    )

    op.create_index('idx_processed_timeseries_timestamp', 'processed_timeseries', [
                    'sensor_name', processed_timeseries_timestamp_col.desc()], unique=False, postgresql_using='btree')

    '''
    PROCESSED IMAGES TABLE SETUP
    '''

    processed_images_timestamp_col = sa.Column(
        'timestamp', sa.TIMESTAMP, primary_key=True)

    op.create_table(
        'processed_images',
        sa.Column('sensor_name', sa.String, primary_key=True),
        processed_images_timestamp_col,
        sa.Column('filename', sa.String, primary_key=True),
        sa.Column('file_data', sa.LargeBinary, nullable=False),
        sa.Column('dimension_1', sa.Integer, nullable=False),
        sa.Column('dimension_2', sa.Integer, nullable=False),
    )

    conn.execute(
        text(
            """
            SELECT create_hypertable('processed_images','timestamp');; 
            """
        ),
    )

    op.create_index('idx_processed_images_timestamp', 'processed_images', [
                    'sensor_name', processed_images_timestamp_col.desc()], unique=False, postgresql_using='btree')

    '''
    IMAGES TABLE RAW SETUP
    '''
    images_timestamp_col_raw = sa.Column(
        'timestamp', sa.TIMESTAMP, primary_key=True)

    op.create_table(
        'imagesraw',
        sa.Column('sensor_name', sa.String, primary_key=True),
        images_timestamp_col_raw,
        sa.Column('file_data', sa.LargeBinary, nullable=False),
    )
    conn.execute(
        text(
            """
            SELECT create_hypertable('imagesraw','timestamp');; 
            """
        ),
    )

    op.create_index('idx_images_timestamp_raw', 'timeseries', [
                    'sensor_name', images_timestamp_col_raw.desc()], unique=False, postgresql_using='btree')                


def downgrade() -> None:
    op.drop_table('timeseries')
    op.drop_table('images')
    op.drop_table('sensors')
    op.drop_table('processed_timeseries')
    op.drop_table('processed_images')
    op.drop_table('imagesraw')
