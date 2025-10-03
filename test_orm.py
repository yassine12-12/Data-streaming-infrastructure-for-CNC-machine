from datetime import datetime
from sqlalchemy import exc, insert
from database.entities.timeseries import timeseries_table
from database.engine import engine

insert_query = insert(timeseries_table).values(
    sensor_name='test_1',
    timestamp=datetime.now(),
    humidity=1,
    pressure=2,
    acceleration_x=3,
    acceleration_y=4,
    acceleration_z=5,
    gyro_x=6,
    gyro_y=7,
    gyro_z=8,
    temperature=9,
    noise=11,
    light=12
)

print(insert_query)

try:
    with engine.connect() as conn:
        result = conn.execute(insert_query)
        conn.commit()
# except exc.SQLAlchemyError as e:  # parent of IOError, OSError *and* WindowsError where available
#     print(e)
except exc.DBAPIError as e:
    print(e)
