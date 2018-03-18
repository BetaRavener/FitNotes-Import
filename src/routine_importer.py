from src.database import FitNotesDatabase, Routine


class RoutineImporter:
    def __init__(self, im_db, ex_db):
        assert isinstance(im_db, FitNotesDatabase)
        assert isinstance(ex_db, FitNotesDatabase)
        self.im_db = im_db
        self.ex_db = ex_db

    def routine_import(self, routine):
        pass

    def routine_import_dialog(self):
        print("Available routines: ")
        for i, im_r in enumerate(self.im_db.routines.values()):
            assert isinstance(im_r, Routine)
            print("{}: {}".format(i, im_r.name))
        while True:
            try:
                r_idx = int(input("Routine to import: "))
                break
            except ValueError:
                print("Invalid choice")
        self.routine_import(list(self.im_db.routines.values())[r_idx])
