class Student:
    name = ""
    answers = {}
    group = 0
    mutable = True

    #has_dropped and new_student value used only for add students mode
    has_dropped = True
    new_student = False

class Group:
    number = 0
    students = []
    size = 0
    score = 0

    #used for adding students, tracks if the group has a mutable student or has room
    mutable = False


class full_state:
    groups = []
    score = 0
