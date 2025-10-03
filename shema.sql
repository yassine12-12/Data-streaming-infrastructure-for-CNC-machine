CREATE SCHEMA IF NOT EXISTS timeseriesschema;

CREATE TABLE IF NOT EXISTS timeseries
(
    timestamp TIMESTAMPTZ NOT NULL,
    sensor_name TEXT  NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    acceleration_x INTEGER NOT NULL,
    acceleration_y INTEGER NOT NULL,
    acceleration_z INTEGER NOT NULL,
    gyro_x INTEGER NOT NULL,
    gyro_y INTEGER NOT NULL,
    gyro_z INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    noise INTEGER NOT NULL,
    light INTEGER NOT NULL,
    PRIMARY KEY (timestamp, sensor_name)
);

-- Create a hypertable using the 'timestamp' column for timeseries
SELECT create_hypertable('timeseries', 'timestamp');

-- Create an index on the 'timeseries' table
CREATE INDEX idx_timeseries_timestamp ON timeseries (sensor_name, timestamp DESC);


CREATE TABLE IF NOT EXISTS timeseriesraw
(
    timestamp TIMESTAMPTZ NOT NULL,
    sensor_name TEXT NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    acceleration_x INTEGER NOT NULL,
    acceleration_y INTEGER NOT NULL,
    acceleration_z INTEGER NOT NULL,
    gyro_x INTEGER NOT NULL,
    gyro_y INTEGER NOT NULL,
    gyro_z INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    noise INTEGER NOT NULL,
    light INTEGER NOT NULL,
    PRIMARY KEY (timestamp, sensor_name)
);

-- Create a hypertable using the 'timestamp' column for timeseries
SELECT create_hypertable('timeseriesraw', 'timestamp');

-- Create an index on the 'timeseries' table
CREATE INDEX idx_timeseriesraw_timestamp ON timeseriesraw (sensor_name, timestamp DESC);







