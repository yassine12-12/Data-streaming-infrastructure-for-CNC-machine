from database.metadata import metadata_obj
from database.engine import engine
from sqlalchemy import Table

images_table = Table("images", metadata_obj, autoload_with=engine)
