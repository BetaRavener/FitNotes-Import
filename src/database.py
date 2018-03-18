import sqlite3
from abc import ABC, abstractmethod


class DbObject(ABC):
    """
    Base type for all DB objects.
    Making it abstract just to be cool.
    """

    def __init__(self):
        self.id = 0

    @abstractmethod
    def load(self, row):
        pass

    @abstractmethod
    def clone(self):
        pass

    @abstractmethod
    def pack(self):
        pass

# Following classes make up routines

# Routine, a workout template class
class Routine(DbObject):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.notes = ""

    def load(self, row):
        self.id, self.name, self.notes = row

    def clone(self):
        tmp = Routine()
        tmp.id = self.id
        tmp.name = self.name
        tmp.notes = self.notes
        return tmp

    def pack(self):
        return self.name, self.notes


# Each routine has parts or "sections" which could be
# various days or alternations in one routine.
class RoutineSection(DbObject):
    def __init__(self):
        super().__init__()
        self.routine_id = 0
        self.name = ""
        self.sort_number = 0

    def load(self, row):
        self.id, self.routine_id, self.name, self.sort_number = row

    def clone(self):
        tmp = RoutineSection()
        tmp.id = self.id
        tmp.routine_id = self.routine_id
        tmp.name = self.name
        tmp.sort_number = self.sort_number
        return tmp

    def pack(self):
        return self.routine_id, self.name, self.sort_number


# Now these are individual exercises that make up each
# routine section and therefore whole routines.
class RoutineSectionExercise(DbObject):
    def __init__(self):
        super().__init__()
        self.routine_section_id = 0
        self.exercise_id = 0
        self.sort_order = 0

    def load(self, row):
        self.id, self.routine_section_id, self.exercise_id, self.sort_order = row

    def clone(self):
        tmp = RoutineSectionExercise()
        tmp.id = self.id
        tmp.routine_section_id = self.routine_section_id
        tmp.exercise_id = self.exercise_id
        tmp.sort_order = self.sort_order
        return tmp

    def pack(self):
        return self.routine_section_id, self.exercise_id, self.sort_order


# These are sets for each exercise in routine.
class RoutineSectionExerciseSet(DbObject):
    def __init__(self):
        super().__init__()
        self.routine_section_exercise_id = 0
        self.metric_weight = 0
        self.reps = 0
        self.sort_order = 0
        self.distance = 0
        self.duration_seconds = 0
        self.unit = 0

    def load(self, row):
        self.id, self.routine_section_exercise_id, self.metric_weight, \
            self.reps, self.sort_order, self.distance, \
            self.duration_seconds, self.unit = row

    def clone(self):
        tmp = RoutineSectionExerciseSet()
        tmp.id = self.id
        tmp.routine_section_exercise_id = self.routine_section_exercise_id
        tmp.metric_weight = self.metric_weight
        tmp.reps = self.reps
        tmp.sort_order = self.sort_order
        tmp.distance = self.distance
        tmp.duration_seconds = self.duration_seconds
        tmp.unit = self.unit
        return tmp

    def pack(self):
        return self.routine_section_exercise_id, self.metric_weight, self.reps, \
                self.sort_order, self.distance, self.duration_seconds, self.unit


# Following classes are used by workouts

class Category(DbObject):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.colour = 0
        self.sort_order = 0

    def load(self, row):
        self.id, self.name, self.colour, self.sort_order = row

    def clone(self):
        tmp = Category()
        tmp.id = self.id
        tmp.name = self.name
        tmp.colour = self.colour
        tmp.sort_order = self.sort_order
        return tmp

    def pack(self):
        return self.name, self.colour, self.sort_order


class Exercise(DbObject):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.category_id = 0
        self.exercise_type_id = 0  # References `MeasurementUnit` table `type` column
        self.notes = None
        self.weight_increment = None
        self.default_graph_id = None
        self.default_rest_time = None

    def load(self, row):
        self.id, self.name, self.category_id, \
            self.exercise_type_id, self.notes, self.weight_increment, \
            self.default_graph_id, self.default_rest_time = row

    def clone(self):
        tmp = Exercise()
        tmp.id = self.id
        tmp.name = self.name
        tmp.category_id = self.category_id
        tmp.exercise_type_id = self.exercise_type_id
        tmp.notes = self.notes
        tmp.weight_increment = self.weight_increment
        tmp.default_graph_id = self.default_graph_id
        tmp.default_rest_time = self.default_rest_time
        return tmp

    def pack(self):
        return self.name, self.category_id, self.exercise_type_id, self.notes, self.weight_increment, \
                self.default_graph_id, self.default_rest_time


# Now class that will represent whole database.
# Each table is stored as dictionary where key is `id` field.
# This helps to cross-reference entries.
class FitNotesDatabase:
    def __init__(self, filepath):
        # Open connection to SQLite database
        self.connection = sqlite3.connect(filepath)
        self.routines = {}
        self.routine_sections = {}
        self.routine_section_exercises = {}
        self.routine_sets = {}
        self.categories = {}
        self.exercises = {}

    def load(self):
        """
        Loads database from FitNotes backup file
        :param filepath: Path to backup file
        """
        c = self.connection.cursor()

        # Now we need to simply load all data from each table
        # we are interested in. To prevent serious code duplication, we
        # create some objects that group everything needed for extraction.
        class Extractor:
            def __init__(self, db_name, associated_dict, db_type):
                self.db_name = db_name
                self.associtaed_dict = associated_dict
                self.db_type = db_type

        extractors = [
            Extractor("Category", self.categories, Category),
            Extractor("exercise", self.exercises, Exercise),
            Extractor("Routine", self.routines, Routine),
            Extractor("RoutineSection", self.routine_sections, RoutineSection),
            Extractor("RoutineSectionExercise", self.routine_section_exercises, RoutineSectionExercise),
            Extractor("RoutineSectionExerciseSet", self.routine_sets, RoutineSectionExerciseSet)
        ]
        # Iterate all tables
        for extr in extractors:
            # Iterate all entries
            for row in c.execute('SELECT * FROM {}'.format(extr.db_name)):
                # Create new object of correct type and assert that it is base type DbObject
                o = extr.db_type()
                assert isinstance(o, DbObject)
                # Load data from row
                o.load(row)
                # Add to dict
                extr.associtaed_dict[o.id] = o

    def categories_in_routine(self, routine):
        """
        Finds all categories (from `Categories` table) that are used in the routine
        :param routine: Routine that is queried
        :return: List of categories
        """
        # Get all exercises for routine
        exercises = self.exercises_in_routine(routine)

        # Gather `category_id` across exercises
        category_ids = [e.category_id for e in exercises]

        # Remove duplicates
        category_ids = set(category_ids)

        # Transform ids into exercises
        return [self.categories[i] for i in category_ids]

    def exercises_in_routine(self, routine):
        """
        Finds all exercises (from `exercises` table) that are used in the routine
        :param routine: Routine that is queried
        :return: List of exercises
        """
        # First, get all section ids that are in routine
        section_ids = []
        for sec in self.routine_sections.values():
            assert isinstance(sec, RoutineSection)
            if sec.routine_id == routine.id:
                section_ids.append(sec.id)

        # Now go trough routine exercises and check, if they belong
        # to section in the list above. If yes, save exercise id.
        exercise_ids = []
        for ex in self.routine_section_exercises.values():
            assert isinstance(ex, RoutineSectionExercise)
            if ex.routine_section_id in section_ids:
                exercise_ids.append(ex.exercise_id)

        # Remove duplicates
        exercise_ids = set(exercise_ids)

        # Transform ids into exercises
        return [self.exercises[i] for i in exercise_ids]

    def list_sections(self, routine):
        l = []
        for sec in self.routine_sections.values():
            if sec.routine_id == routine.id:
                l.append(sec)
        return l

    def list_exercises(self, routine_section):
        l = []
        for ex in self.routine_section_exercises.values():
            if ex.routine_section_id == routine_section.id:
                l.append(ex)
        return l

    def list_sets(self, routine_section_exercise):
        l = []
        for ex_set in self.routine_sets.values():
            if ex_set.routine_section_exercise_id == routine_section_exercise.id:
                l.append(ex_set)
        return l

    def insert(self, table_name, columns, db_object):
        assert isinstance(db_object, DbObject)
        c = self.connection.cursor()

        new_obj = db_object.clone()

        # Prepare insert command
        ins_str = "INSERT INTO {} ({}) VALUES ({})".format(table_name,
                                                           ",".join(columns),
                                                           ",".join(["?" for x in columns]))
        # Execute the command
        c.execute(ins_str, new_obj.pack())
        # Update id
        new_obj.id = c.lastrowid

        return new_obj

    def add_category(self, category):
        new_cat = self.insert("Category", ["name", "colour", "sort_order"], category)
        self.categories[new_cat.id] = new_cat
        return new_cat

    def add_exercise(self, exercise):
        new_ex = self.insert("exercise", ["name", "category_id", "exercise_type_id", "notes",
                                          "weight_increment", "default_graph_id", "default_rest_time"],
                             exercise)
        self.exercises[new_ex.id] = new_ex
        return new_ex

    def add_routine(self, routine):
        new_rt = self.insert("Routine", ["name", "notes"], routine)
        self.routines[new_rt.id] = new_rt
        return new_rt

    def add_routine_section(self, routine_section):
        new_rts = self.insert("RoutineSection", ["routine_id", "name", "sort_order"], routine_section)
        self.routine_sections[new_rts.id] = new_rts
        return new_rts

    def add_routine_section_exercise(self, routine_section_exercise):
        new_rtse = self.insert("RoutineSectionExercise", ["routine_section_id", "exercise_id", "sort_order"],
                               routine_section_exercise)
        self.routine_section_exercises[new_rtse.id] = new_rtse
        return new_rtse

    def add_routine_section_exercise_set(self, routine_section_exercise_set):
        new_rtses = self.insert("RoutineSectionExerciseSet", ["routine_section_exercise_id", "metric_weight", "reps",
                                                             "sort_order", "distance", "duration_seconds", "unit"],
                               routine_section_exercise_set)
        self.routine_sets[new_rtses.id] = new_rtses
        return new_rtses

    def save_changes(self):
        self.connection.commit()