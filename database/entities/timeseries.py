from database.metadata import metadata_obj
from database.engine import engine
from sqlalchemy import Table

timeseries_table = Table("timeseries", metadata_obj, autoload_with=engine)
