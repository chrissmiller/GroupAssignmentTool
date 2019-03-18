## GROUP ASSIGNMENT TOOL: README

Easily run the basic version of the Group Assignment Tool by calling `python3 GAT_demo.py`. For more control, access the groupAssign object by calling `from gatV4.py import groupAssign` in your program and instantiating your own groupAssign object. After doing so, simply call the object's `iterate_normal()` method to begin swapping.


### Parameters
The tool takes a few parameters to get started. The student response and weighting CSVs are discussed below,  and it is mandatory to provide filenames for these.

`per_group`: Set the number of students per group

`mode`: Set to 'Normal' - this needs to be updated, but typically allows random assignment and also performed group updating before that was moved to groupUpdater.py

`gen_pen`/`eth_pen`: The size of the score pentalties for groups with a student isolated by gender or ethnicity

`gen_flag`/`eth_flag`: Whether or not those penalties are implemented

`gen_q`/`eth_q`: The gender and ethnicity questions in the survey - only relevant if penalties are turned on.

`name_q`: This question determines which student response will be output when displaying formed groups - ensure that it is unique to each student.

`n_iter`: Number of iterations. This is a bit trial-and-error based and depends heavily on your dataset. In general it is safe to set this as a high number (25000+), since the program will stop once it reaches convergence. However, the default discount rate (`self.discount`) for the epsilon greedy swap strategy is based on reaching a 1% random swap rate after n_iter iterations, so you may have unexpectedly unstable behavior if the algorithm converges much faster.

Inside, a few parameters are unlikely to change often and are hardcoded.

`self.delimiter`: Stores the delimiter (';' by default) for checkbox style question outputs.

`self.epsilon`: Initial rate of making random swaps over greedy ones.

`self.discount`: Determines how fast epsilon decays towards 0. By default, set to reach an epsilon of .01 after n_iter iterations.

`self.conv_thresh`: Convergence threshold, set to .05 by default. If the algorithm goes 1000 iterations without score improvements of more than 5%, it cuts out. 

`self.blocks`: Stores all possible scheduling blocks. By default, the Dartmouth College class schedule when not in demo mode.


### CSV Formatting

#### Student CSV Formatting: 
Row 1 contains the questions/question names, each in their own column. These must be the same as those indicated in the weighting csv. Each subsequent row contains a single student's responses to each question (with the responses to the question in column 3, for example, listed in column 3).

#### Weighting CSV Formatting:
Row 1 contains the questions or question names. This content MUST be the same as the questions/question names used in the student dataset or the program will not be able to match professor weights and question types with student responses.

Row 2 contains the weights of each question. Negative weights indicate selection for homogeneity, while positive weights indicate selection for heterogeneity.

Row 3 contains question types, which indicates how the program will process them. Please input M for a multiple choice question, C for a checkbox style question other than scheduling, S for a string entry question (ie name, ID number, etc.), and Sc for a scheduling question.

Feel free to use the test datasets, `demo_student.csv` and `demo_prof.csv`, as a guiding example. 


### More?

Feel free to email me at `Chris.20@Dartmouth.edu` with any questions or issues. As of March 16th, 2019, I have just completed a major renovation of the code. Everything should run more efficiently and effectively now, but it is possible that my testing didn't find everything.
