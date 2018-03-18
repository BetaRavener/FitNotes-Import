import sys

from src.database import FitNotesDatabase
from src.routine_importer import RoutineImporter

in_db = FitNotesDatabase()
in_db.load(sys.argv[1])
out_db = FitNotesDatabase()
out_db.load(sys.argv[2])

importer = RoutineImporter(in_db, out_db)
importer.routine_import_dialog()