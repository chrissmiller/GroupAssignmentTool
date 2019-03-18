import csv
import sys
import copy
from random import randint
import random
import os.path
import timeit
import math

from courseElements import *

class groupAssign:
    def __init__(self, student_csv, weighting_csv, per_group = 4, mode = 'Normal',
                gen_pen = 15, gen_flag = True, eth_pen = 15, eth_flag = True,
                name_q = 'Name', gen_q = "With what gender do you identify?",
                eth_q = "What is your ethnicity?", n_iter = 15000):


        self.student_csv = student_csv
        self.weighting_csv = weighting_csv
        self.check_delimiter = ";" # delimeter for checkbox questions
        self.per_group = per_group

        self.n_iter = n_iter
        self.epsilon = .35
        self.conv_thresh = .05
        self.discount = math.pow(.01/self.epsilon, 1/(self.n_iter))

        self.question_weights = []
        self.question_types = []

        self.students = []
        self.questions = []

        self.mode = mode

        #self.blocks = ["9L", "9S", "10", "11", "12", "2", "10A", "2A", "3A", "3B", "6A", "6B"]
        self.blocks = ["block1;block2;block3"]
        self.name_question = name_q

        self.class_state = full_state()

        #defines the strings which indicate the respondent's gender/ethnicity. Can be left null.
        self.gen_question = gen_q
        self.eth_question = eth_q
        #penalties for groups with either only one girl or one minority student
        self.gender_penalty = gen_pen
        self.ethnicity_penalty = eth_pen

        #indicates whether or not gender/ethnicity is being tested for
        self.gen_flag = gen_flag
        self.eth_flag = eth_flag

        self.process_prof()
        self.process_students()

        self.assign_initial_groups()


#===============================================================================
#=========================== DATA PROCESSING / SETUP ===========================
#===============================================================================
    # Processes professor data CSV
    def process_prof(self):
        prof_data = self.read_csv_data(self.weighting_csv)
        self.question_weights = (prof_data[0]).copy()
        self.question_types = (prof_data[1]).copy()

    # Processes student response CSV
    def process_students(self):
        response_data = self.read_csv_data(self.student_csv)
        #use as list so that it's indexable (but no longer tied to dictionary's values)
        self.questions = list(response_data[0].keys())

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
        self.students = [Student() for i in range(len(response_data))]
        counter = 0

        #Populates list of students
        for student in self.students:
            student.name = (response_data[counter])[self.name_question]
            student.answers = response_data[counter]
            counter += 1

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


#===============================================================================
#========================== Assignment Initialization ==========================
#===============================================================================

    # Assigns each student to a random group to begin
    def assign_initial_groups(self):
        per_group = self.per_group
        num_students = len(self.students)
        num_groups = int(num_students/self.per_group) # number of full groups we can make
        remainder = num_students%self.per_group

        self.class_state.groups = [Group() for i in range(num_groups)]

        i = 0

        # Gets a randomly shuffled copy of the student list for random group assignment
        rand_students = random.sample(self.students, len(self.students))
        n = 0
        for group in self.class_state.groups:

            group.number = int(i/self.per_group)
            group.size = per_group
            group.students = rand_students[i:(i+self.per_group)]
            i += self.per_group
            n+=1


        # if remainder is within one person of the desired group size,
        # makes the remainders into a group otherwise, adds remainder to other
        # groups
        if remainder:
            if remainder + 1 == per_group and remainder != 1 and per_group>=3:
                new_group = Group()
                new_group.size = remainder
                new_group.students = rand_students[i:]
                new_group.number = num_groups
                self.class_state.groups.append(new_group)


            #distributes remainder across other groups
            else:
                j = 0
                while remainder:
                    self.class_state.groups[j].students.append(rand_students[i])
                    self.class_state.groups[j].size += 1
                    i+=1
                    j+=1
                    remainder -= 1

        for group in self.class_state.groups:
            group.score = self.score_group(group)


        #testing purposes - verifies groups and sizes
        if __debug__:
            print(str(len(self.class_state.groups)) + " groups in class")
            for group in self.class_state.groups:
                print("Group " + str(group.number) + " contains " + str(group.size) + " students and a score of " + str(group.score) +".")
            self.output_state('p')
        #end testing

        print("Initial class score = " + str(self.score_class_state()))


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

        #max_scheduling = len(self.blocks) - 4
        # For demo purposes -
        max_scheduling = len(self.blocks)

        #Lists all scheduling blocks. 9L block excluded since this class meets during that block.
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
        return -options_over_count

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


#===============================================================================
#=============================== Group Assignment ==============================
#===============================================================================

    # Swaps two random groups
    # Accepts a number of iterations to perform
    # returns 1 and new state if score improves, 0 and old state else.
    def iterate_normal(self, iterations=0):

        if(iterations == 0):
            iterations = self.n_iter

        failure = 0
        prev_score = 0
        conv_1 = False
        for i in range(iterations):
            if i%500 == 0:
                print("At iteration " + str(i))
                scoresum = 0
                for group in self.class_state.groups:
                    scoresum += group.score
                print(str(scoresum/len(self.class_state.groups)))

                if prev_score != 0 and \
                        (scoresum - prev_score)/prev_score < self.conv_thresh:
                    if conv_1: # Ensures that convergence is stable for at least two 500 rounds
                        print("Score converged.")
                        break
                    else:
                        conv_1 = True
                elif conv_1: # if it escaped convergence, reset flag
                    conv_1 = False
                # This means that for the next run (last chance to improve)
                # we give it a chance and compare 1000 iterations back for improvement
                # instead of the typical 500
                if not conv_1:
                    prev_score = scoresum

            self.swap_students_limited(self.class_state.groups)


        # Scores and prints the final class state
        end_score = self.score_class_state()
        print("Final class score is: " + str(end_score))

    def random_swap(self):
        n_groups = len(self.class_state.groups)

    def get_rand_index(self, max_num):
        rand_index_one = randint(0, max_num)
        rand_index_two = rand_index_one
        while rand_index_two == rand_index_one:
            rand_index_two = randint(0, max_num)

        return (rand_index_one, rand_index_two)

    # swaps students between limited groups. Takes class state and list of groups which are ok to swap.
    def swap_students_limited(self, swappable_groups):
        swap_size = len(swappable_groups)
        (rand_group_one, rand_group_two) = self.get_rand_index(swap_size - 1)
        g1 = swappable_groups[rand_group_one]
        g2 = swappable_groups[rand_group_two]
        self.epsilon *= self.discount

        if random.random() > self.epsilon: # Greedy search

            group_one = copy.deepcopy(swappable_groups[rand_group_one])
            group_two = copy.deepcopy(swappable_groups[rand_group_two])

            total_score = group_one.score + group_two.score

            best_from_one = None
            best_from_two = None
            best_g1 = group_one.score
            best_g2 = group_two.score
            best_score = total_score

            # For each student pairing, swap, test, and swap back
            for i in group_one.students:
                for j in group_two.students:
                    self.swap(group_one, i, group_two, j)
                    g1_score = self.score_group(group_one)
                    g2_score = self.score_group(group_two)
                    candidate_score = (g1_score + g2_score)
                    self.swap(group_one, j, group_two, i)

                    if candidate_score > best_score: # Improvement
                        best_from_one = i
                        best_from_two = j
                        best_g1 = g1_score
                        best_g2 = g2_score
                        best_score = candidate_score

            if best_from_one is not None: # Do the permanent swap, this is the best
                self.swap(group_one, best_from_one, group_two, best_from_two)
                group_one.score = best_g1
                group_two.score = best_g2

                self.class_state.groups.remove(g1)
                self.class_state.groups.remove(g2)
                self.class_state.groups.append(group_one)
                self.class_state.groups.append(group_two)

                return 1

            else:
                return 0

        else: # Random swap
            s1 = random.choice(swappable_groups[rand_group_one].students)
            s2 = random.choice(swappable_groups[rand_group_two].students)
            self.swap(swappable_groups[rand_group_one], s1,
                        swappable_groups[rand_group_two], s2)
            swappable_groups[rand_group_one].score = self.score_group(swappable_groups[rand_group_one])
            swappable_groups[rand_group_two].score = self.score_group(swappable_groups[rand_group_two])

            return 1

    # Swaps student i from group one with student j from group two
    def swap(self, group_one, i, group_two, j):
        i.group = group_two.number
        j.group = group_one.number

        group_one.students.append(j)
        group_two.students.append(i)

        group_one.students.remove(i)
        group_two.students.remove(j)
