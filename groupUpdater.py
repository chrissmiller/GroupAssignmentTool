import csv
import sys
import copy
from random import randint
import random
import os.path
import timeit
import math
import itertools
from courseElements import *

class groupUpdater:
    def __init__(self, old_groups_csv = 'demo_group_setting.csv',
                new_responses_csv = 'demo_update_new_response_ngroups.csv',
                weighting_csv = 'demo_prof.csv', gen_pen = 100, gen_flag = True,
                eth_pen = 15, eth_flag = False, name_q = 'Name',
                gen_q = "With what gender do you identify?",
                eth_q = "What is your ethnicity?", no_new = False, prefer_new = False,
                n_iter = 10000):
        self.class_state = None
        self.per_group = 4
        self.loose_students = []
        self.check_delimiter = ';'
        self.csv_delimiter = ','
        self.demoMode = True
        if self.demoMode:
            self.blocks = ["block1;block2;block3"]
            name_q = 'Please select your name'
            gen_q = 'Gender'
        else:
            self.blocks = ["9L", "9S", "10", "11", "12", "2", "10A", "2A", "3A", "3B", "6A", "6B"]

        self.name_question = name_q

        #defines the strings which indicate the respondent's gender/ethnicity. Can be left null.
        self.gen_question = gen_q
        self.eth_question = eth_q
        #penalties for groups with either only one girl or one minority student
        self.gender_penalty = gen_pen
        self.ethnicity_penalty = eth_pen

        #indicates whether or not gender/ethnicity is being tested for
        self.gen_flag = gen_flag
        self.eth_flag = eth_flag


        self.weighting_csv = weighting_csv
        self.process_prof()
        self.rebuild_original_state(old_groups_csv)
        self.update_new_responses(new_responses_csv)
        self.no_new = no_new
        self.prefer_new = prefer_new
        self.n_to_add = len(self.loose_students)
        self.existing_space = self.get_space()
        self.adding = self.existing_space >= self.n_to_add # we can just add to groups

        # we can just add to existing groups (exceeding per_group a bit)
        self.adding_plus = ((self.existing_space + (self.per_group - 1) >=
                            self.n_to_add) or self.no_new) and not self.prefer_new

        self.new_groups = not self.adding_plus
        #self.new_groups = True
        if prefer_new:
            self.n_new = int((self.n_to_add - self.existing_space)/self.per_group)
        else:
            self.n_new = int((self.n_to_add - (self.existing_space +
                        len(self.class_state.groups)))/self.per_group)
        self.n_iter = n_iter



    # Processes professor data CSV
    def process_prof(self):
        prof_data = self.read_csv_data(self.weighting_csv)
        self.question_weights = (prof_data[0]).copy()
        self.question_types = (prof_data[1]).copy()

    # Rebuild the original class state
    def rebuild_original_state(self, old_groups_csv):

        original_class = full_state()

        with open(old_groups_csv, 'r') as old_group_file:
            old_groups = old_group_file.readlines()

        group_number = 0
        original_class.groups = [Group() for i in range(len(old_groups))]
        for row in old_groups:

            #Generates a group and numbers it
            current_group = original_class.groups[group_number]
            current_group.students = []
            current_group.number = group_number

            stud_split = row.split(self.csv_delimiter)

            for item in stud_split:
                #Generates a student, sets the name, appends it to the group
                new_student = Student()
                new_student.name = item.replace("\n", "")
                new_student.group = group_number
                new_student.mutable = False
                current_group.students.append(new_student)
                current_group.size += 1

            group_number += 1



        self.class_state = original_class


    def update_new_responses(self, new_responses_csv):
        new_data = self.read_csv_data(new_responses_csv)

        self.questions = list(new_data[0].keys())

        if self.name_question not in self.questions:
            raise ValueError("Provided name question {} not \
                            found in student CSV.".format(self.name_question))
        if self.gen_flag and self.gen_question not in self.questions:
            raise ValueError("Provided gender question {} not \
                            found in student CSV.".format(self.gen_question))
        if self.eth_flag and self.eth_question not in self.questions:
            raise ValueError("Provided ethnicity question {} not \
                            found in student CSV.".format(self.eth_question))


        #Creates an empty student object for each student
        self.students = [Student() for i in range(len(new_data))]
        counter = 0

        #Populates list of students
        for student in self.students:
            student.name = (new_data[counter])[self.name_question]
            student.name = student.name.replace("\n", "")
            student.answers = new_data[counter]
            counter += 1

        loose_students = []



        # Stores students in self.students who have a match in the
        # original class
        matched = set()


        # Remove students who have dropped

        group_to_remove = set()
        for group in self.class_state.groups:
            to_remove = set()
            for student_old in group.students:
                found = False
                for student_new in self.students:
                    if student_old.name == student_new.name:
                        found = True
                        student_old.answers = student_new.answers # transfer response data
                        matched.add(student_new)
                        break

                if not found:
                    to_remove.add(student_old)
            for removal in to_remove:
                group.students.remove(removal)

            if len(group.students) <= 1:
                for student in group.students:
                    print(student.name)
                if len(group.students) == 1: # Lone student - should be regrouped
                    loose_students.append(group.students[0])

                group_to_remove.add(group) # Remove group regardless of whether 1 or 0 students

        for group in group_to_remove:
            self.class_state.groups.remove(group)

        for m_student in matched:
            self.students.remove(m_student)

        for unmatched_student in self.students:
            loose_students.append(unmatched_student)

        self.loose_students = loose_students

    #read_csv_data function was originally written by Mark Franklin (Thayer IT), 9/29/17
    # input: file name
    # return: list containing a dictionary for each row indexed by column headers
    def read_csv_data(self, input_csv_file):

        headers = ""
        csv_data = []

        with open(input_csv_file, 'rU') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in csv_reader:    # headers row is a special case
                if headers == "":
                    headers = row
                else:
                    row_data = {}
                    i = 0  # used to iterate through the columns
                    for item in row:  # stash each row element
                        #print(str(headers[i]) + "i = " + str(i))
                        row_data[headers[i]] = item  # keyed by column header
                        i = i + 1

                    csv_data.append(row_data)  # save this row in the list
        return(csv_data)


    def add(self):
        loose_students = self.loose_students.copy()
        # Do an exhaustive search of combos because for combinations this is
        # tractable even for high n_to_add so why not
        if self.new_groups:
            for i in range(self.n_new):
                max_score = float("-inf")
                max_group = None

                potentials = itertools.combinations(loose_students, self.per_group)
                for potential in potentials:
                    g = Group()
                    g.number = len(self.class_state.groups)
                    g.students = list(potential)
                    g.size = len(potential)
                    g.score = self.score_group(g)
                    if g.score > max_score:
                        max_score = g.score
                        max_group = g

                for s in max_group.students:
                    loose_students.remove(s)
                self.class_state.groups.append(max_group)

        with_space = self.get_groups_with_space()

        max_assign = None
        max_gain = float("-inf")

        if with_space:

            for i in range(self.n_iter):
                #if i % 500 == 0:
                print("Gain max: " +  str(max_gain))
                repl = set()
                assignment = []
                for stud in loose_students:
                    random.shuffle(with_space)
                    g = with_space.pop()
                    g.students.append(stud)
                    assignment.append((g, stud))
                    repl.add(g)
                osum = 0
                for g in repl:
                    osum += g.score

                nsum = 0
                for g in repl:
                    nsum += self.score_group(g)

                # Track gain to avoid having to rescore the entire class state
                # Even if different groups are used,
                gain = nsum - osum

                if gain > max_gain:
                    max_gain= gain
                    max_assign = assignment

                self.reverse_assign(assignment,  with_space)

            for item in max_assign:
                item[0].students.append(item[1])
                item[0].size += 1
                item[0].score = self.score_group(item[0])
                item[1].group = item[0].number
        self.score_class_state()

    def reverse_assign(self, assignment, with_space):
        for item in assignment:
            item[0].students.remove(item[1])
            with_space.append(item[0])


    # Calculates available space in existing groups
    def get_space(self):
        space = 0
        for group in self.class_state.groups:
            space += max((self.per_group - group.size), 0)
        return space

    # Returns a list of groups with available sapce
    def get_groups_with_space(self, plus_one = False):
        spaces = []
        per_group = self.per_group
        if plus_one: # allows overflow of one extra student per group
            per_group += 1

        for group in self.class_state.groups:
            for i in range(per_group - len(group.students)):
                spaces.append(group)
        return spaces


#===============================================================================
#=================================== Scoring ===================================
#===============================================================================

    # Returns a score for the provided group
    def score_group(self, group):
        scheduling_score = 0
        num_students = len(group.students)

        #eventually we want to pull number of choices here
        #num_divisor = min(num_students, num_choices)
        #but for now just use num_students like catme
        self.num_divisor = num_students

        scores = {}


        for question in self.questions:

            if self.question_types[question] == "M":
                scores[question] = self.score_m(group, question)

            #Scheduling question scoring mode
            elif self.question_types[question] == "Sc":
                    scores[question] = self.score_scheduling(group, question)

                #Scoring for checkbox style questions
            elif self.question_types[question] == "C":
                    scores[question] = self.score_c(group, question)

            elif self.question_types[question] == "S":
                scores[question] = 0

            else:
                scores[question] = 0
                print("Unrecognized type " + self.question_types[question] + " for question " + question)

        score_sum = 0
        for key in scores.keys():
            score_sum += scores[key]

        # Implements penalties for isolation. This improves diversity of
        # groups, avoiding leaving one non-male student or one minority isolated in a group.
        if self.gen_flag:
            score_sum -= self.get_gender_penalty(group)
        if self.eth_flag:
            score_sum -= self.get_homogeneity_penalty(group)

        return score_sum

    # Scores scheduling element of groups for use in calculating final group score
    def score_scheduling(self, group, question):

        # out of 12 blocks, maximum free (assuming all students take 3 classes)
        # is 8 since 9L and 9S overlap
        # For demo purposes -
        if self.demoMode:
            max_scheduling = len(self.blocks)
        else:
            max_scheduling = len(self.blocks) - 4

        #Lists all scheduling blocks
        scheduling_blocks = self.blocks.copy()

        for student in group.students:
            student_classes = student.answers[question].split(self.check_delimiter)

            #Goes though every student's classes and removes them from the list
            #since those blocks are unavailable now
            for block in student_classes:
                if block in scheduling_blocks:
                    scheduling_blocks.remove(block)

        #scheduling is now the remaining number of blocks that all members have free
        scheduling = len(scheduling_blocks)
        #Allows us to limit how much open time is needed (ie, 40 hours/week or 2)
        #temporary - update so that it stops processing after max is reached
        if scheduling>max_scheduling:
            scheduling = max_scheduling

        return int(self.question_weights[question])*(scheduling/max_scheduling)

    # Multiple choice question style
    # Scores heterogeneity via number of unique answers
    def score_m(self, group, question):
        sum_values = 0
        selected_choices = {}

        # Sets all selected answers in the group to 1
        for student in group.students:
            selected_choices[student.answers[question]] = 1

        #
        for value in selected_choices.values():
            if value == 1:
                sum_values += 1

        return (sum_values/group.size) * int(self.question_weights[question])

    # Scores checkbox style questions
    def score_c(self, group, question):
        # A list of lists - each list within group_selections represents
        # one student's selected choices in the checkbox question.
        group_selections = []

        for student in group.students:
            #Since google forms represents checkbox responses as "A;B;C" this splits it into a list
            student_selections = student.answers[question].split(self.check_delimiter)
            group_selections.append(student_selections)


        # tracks how many selected option matches occur
        option_counter = 0

        # tracks total number of unique selections
        total_selection_count = 0

        # For each student's selected options
        for student_options_list in group_selections:

            # For each selected option in the list of selected options
            for student_options in student_options_list:
                # how many matches for THIS option (so we can square this)
                temp_option_counter = 0

                for student_options_list_2 in group_selections:
                    for student_options_2 in student_options_list_2:

                        if student_options_list != student_options_list_2 and student_options == student_options_2:
                            temp_option_counter += 1

                # square this to appropriately weight three members selecting an option as much better
                option_counter += temp_option_counter*temp_option_counter

            # tracks the total number of options the students have picked
            total_selection_count += len(student_options_list)

        # accounts for the fact that options will be counted twice (1 matches with 2, then later 2 matches with 1)
        option_counter /= 2

        if total_selection_count > option_counter:
            total_selection_count -= option_counter
            options_over_count = option_counter/total_selection_count
        else:
            options_over_count = 1
        # negative because if homogenous (negative weight) we need it to end up positive to add to score
        # and if heterogenous (positive weight) we want it negative to reduce score as homogeneity increases
        return -options_over_count * int(self.question_weights[question])

    # implements penalties for one non-male student alone in a group
    def get_gender_penalty(self, group):
        gender_counter = 0

        for student in group.students:
            if student.answers[self.gen_question] != "Male":
                gender_counter += 1

        if gender_counter == 1:
            return self.gender_penalty
        else:
            return 0

    # Implements penalties for one non-white student alone in a group
    def get_homogeneity_penalty(self, group):
        eth_counter = 0

        for student in group.students:
            if student.answers[self.eth_question] != "White":
                eth_counter += 1


        if eth_counter == 1:
            return self.eth_penalty
        else:
            return 0

    # Scores a class state by averaging the scores of each group in the state
    def score_class_state(self):
        sum_scores = 0
        num_groups = len(self.class_state.groups)
        for group in self.class_state.groups:
            gscore = self.score_group(group)
            group.score = gscore
            print("Group " + str(group.number) + " score: " + str(gscore))
            sum_scores += gscore
        return (sum_scores/num_groups)

    # Displays groups, scores, and students in each group
    # Input is a full class state and an output type - p, c, b, or u (Print/CSV/Both/User-defined)
    def output_state(self, output_type):
        if output_type == 'u':
            output_type = input("Please indicate the type of output you would like (C for CSV, P for Print, B for both)")
        output_type = output_type.lower()


        if output_type == 'c' or output_type == 'b':
            output_filename = input("Please enter a filename for the output: ")

            #Verifies that the file doesn't exist - if it does, verifies that the user would like to overwrite
            if os.path.isfile(output_filename):
                overwrite = input("This file already exists. Would you like to overwrite? (y/n) ")
                if not(overwrite == 'y' or overwrite == 'Y'):
                    while os.path.isfile(output_filename):
                        output_filename = input("Please enter a filename for the output: ")
            output_file = open(output_filename, 'w')

            #Writes each group on a line in the new file
            for group in self.class_state.groups:
                output_file.write(group.students[0].name)
                for student in group.students[1:]:
                    output_file.write(", " + student.name)
                output_file.write("\n")
            output_file.close()

        if output_type == 'p' or output_type == 'b':
            for group in self.class_state.groups:
                print("-----------------------------")
                print("Group number: " + str(group.number))
                print("Group score: " + str(group.score))
                print("Group members:")
                for student in group.students:
                    print(student.name)
        if output_type not in ['c', 'p', 'b']:
            print("Invalid output type.")
            self.output_state('u')



if  __name__ == '__main__':
    updater = groupUpdater()
    updater.add()
    updater.output_state('p')



# Want: List of mutable groups (groups with space)
# List of mutable students

# In the case of adding or adding plus:
# Assign everyone to a group
# select random from list of added students
# iterate over them if in random groups? idk that


#for new_groups:
#    make best group possible (by  taking every subset of per_group from n students)
#   and testing
#   possible bc combinations are tractable in number we need (~20 max)
