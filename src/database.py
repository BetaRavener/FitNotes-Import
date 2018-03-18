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


# Following classes make up routines

# Routine, a workout template class
class Routine(DbObject):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.notes = ""

    def load(self, row):
        self.id, self.name, self.notes = row


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


# Following classes are used by workouts

class Category(DbObject):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.colour = 0
        self.sort_order = 0

    def load(self, row):
        self.id, self.name, self.colour, self.sort_order = row


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


# Now class that will represent whole database.
# Each table is stored as dictionary where key is `id` field.
# This helps to cross-reference entries.
class FitNotesDatabase:
    def __init__(self):
        self.routines = {}
        self.routine_sections = {}
        self.routine_exercises = {}
        self.routine_sets = {}
        self.categories = {}
        self.exercises = {}

    def load(self, filepath):
        """
        Loads database from FitNotes backup file
        :param filepath: Path to backup file
        """
        # Open connection to SQLite database
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

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
            Extractor("RoutineSectionExercise", self.routine_exercises, RoutineSectionExercise),
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

        # Finish by closing connestion
        conn.close()
