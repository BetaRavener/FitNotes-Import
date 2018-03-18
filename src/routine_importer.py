from src.database import FitNotesDatabase, Routine, RoutineSectionExercise, Exercise, Category


class RoutineImporter:
    def __init__(self, im_db, ex_db):
        assert isinstance(im_db, FitNotesDatabase)
        assert isinstance(ex_db, FitNotesDatabase)
        self.im_db = im_db
        self.ex_db = ex_db

    def exercise_comp(self, ex1, ex2):
        assert isinstance(ex1, Exercise)
        assert isinstance(ex2, Exercise)
        return ex1.name == ex2.name

    def category_cmp(self, c1, c2):
        assert isinstance(c1, Category)
        assert isinstance(c2, Category)
        return c1.name == c2.name

    def routine_section_exercise_import(self, section_exercise, new_section, matched_exercises):
        tmp_ex = section_exercise.clone()
        tmp_ex.routine_section_id = new_section.id
        tmp_ex.exercise_id = matched_exercises[section_exercise.exercise_id].id
        new_ex = self.ex_db.add_routine_section_exercise(tmp_ex)

        for ex_set in self.im_db.list_sets(section_exercise):
            tmp_set = ex_set.clone()
            tmp_set.routine_section_exercise_id = new_ex.id
            self.ex_db.add_routine_section_exercise_set(tmp_set)

    def routine_section_import(self, routine_section, new_routine, matched_exercises):
        tmp_sec = routine_section.clone()
        tmp_sec.routine_id = new_routine.id
        new_section = self.ex_db.add_routine_section(tmp_sec)

        for ex in self.im_db.list_exercises(routine_section):
            self.routine_section_exercise_import(ex, new_section, matched_exercises)

    def routine_import(self, routine):
        # Clone exercise and category dictionaries from `im_db` because we will change entries
        matched_categories = {}
        matched_exercises = {}

        # First we need to pull all categories used by routine, check if they are
        # present in target database and if not, add them
        categories = self.im_db.categories_in_routine(routine)
        for im_cat in categories:
            matched_cat = None
            for ex_cat in self.ex_db.categories.values():
                if self.category_cmp(im_cat, ex_cat):
                    matched_cat = ex_cat
                    break
            if matched_cat is None:
                matched_cat = self.category_import_dialog(im_cat)

            matched_categories[im_cat.id] = matched_cat

        # Then do the same process for exercises
        exercises = self.im_db.exercises_in_routine(routine)
        for im_ex in exercises:
            # Change the category id using mapping created above
            trans_ex = im_ex.clone()
            trans_ex.category_id = matched_categories[im_ex.category_id].id

            matched_ex = None
            for ex_ex in self.ex_db.exercises.values():
                if self.exercise_comp(trans_ex, ex_ex):
                    matched_ex = ex_ex
                    break
            if matched_ex is None:
                matched_ex = self.exercise_import_dialog(trans_ex)

            # Change the Id in cloned exercise to that of matched one
            matched_exercises[im_ex.id] = matched_ex

        # Now it's easy to transfer routines, sections and exercises
        new_routine = self.ex_db.add_routine(routine)
        for sec in self.im_db.list_sections(routine):
            self.routine_section_import(sec, new_routine, matched_exercises)

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

    def category_import_dialog(self, required_category):
        print("Category '{}' from imported routine"
              "not found in your database.\n"
              "Select from your categories or use -1 to import\n"
              "the category as defined in other database.".format(required_category.name))
        for i, ex_cat in enumerate(self.ex_db.categories.values()):
            assert isinstance(ex_cat, Category)
            print("{}: {}".format(i, ex_cat.name))
        while True:
            try:
                choice = int(input("Your choice: "))
                break
            except ValueError:
                print("Invalid choice")

        if choice >= 0:
            return list(self.im_db.categories.values())[choice]

        return self.ex_db.add_category(required_category)

    def exercise_import_dialog(self, required_exercise):
        print("Exercise '{}' from imported routine"
              "not found in your database.\n"
              "Select from your categories or use -1 to import\n"
              "the category as defined in other database.".format(required_exercise.name))
        for i, ex_ex in enumerate(self.ex_db.exercises.values()):
            assert isinstance(ex_ex, Exercise)
            print("{}: {}".format(i, ex_ex.name))
        while True:
            try:
                choice = int(input("Your choice: "))
                break
            except ValueError:
                print("Invalid choice")

        if choice >= 0:
            return list(self.im_db.exercises.values())[choice]

        return self.ex_db.add_exercise(required_exercise)