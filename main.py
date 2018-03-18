import sys

from src.database import FitNotesDatabase
from src.routine_importer import RoutineImporter

in_db = FitNotesDatabase(sys.argv[1])
in_db.load()
out_db = FitNotesDatabase(sys.argv[2])
out_db.load()

importer = RoutineImporter(in_db, out_db)
importer.routine_import_dialog()
out_db.save_changes()