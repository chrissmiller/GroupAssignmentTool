# Group Assignment Tool
## Updater README

The groupUpdater, stored in `groupUpdater.py`, is designed to update previously formed groups by removing students who have dropped the course and adding new students who have joined the course. 

Importantly, the groupUpdater keeps students who remain in the class in the same groups (as long as there are at least two students remaining from the original group). This allows professors to easily adjust to add/drop course changes without worrying that groups will change unexpectedly. It also allows professors to easily assign some new students to groups before running the algorithm simply by adding them to the original groups CSV. If this group permanency behavior is not desired, please use the original Group Assignment Tool.

To use the updater, first import using `from groupUpdater.py import groupUpdater`. Then instantiate a `groupUpdater()` object, and use the `add()` method followed by the `output_state()` method to update groups and report the formed groups.

### Parameters

`old_groups_csv` stores the original groups formed before the student population changed

`new_responses_csv` stores the updated student responses

`weighting_csv` stores question types and weights.

`no_new` is a boolean value which should be set to true if new groups are not allowed. If this is set to true, and there is not enough space for all new students, group size will be increased by one.

`prefer_new` is a boolean value which should be set to true if new groups are preferred over expanding group sizes by one.

All other parameters are identical to the parameters listed in the Group Assignment Tool README.


### CSV Formatting

`old_groups_csv` must be a comma separated document in which each line contains one group, defined by a list of student names separated by commas. For example:
	
	Lauren, Amy, Josh, Alexei
	Darryl, Michael, Elizabeth, May
	
In this case, Lauren, Amy, Josh, and Alexei are in group 1, while Darryl, Michael, Elizabeth, and May are in group 2. 

`new_responses_csv` must be a comma separated document of student responses to the survey.

 **Important**: For the algorithm to update correctly, `new_responses_csv` must have all new student responses added and the responses of all students who have dropped deleted. Without this, the program cannot detect new students or students who have left.
 
`weighting_csv` is a weighting/question type document, and can be the same as the weighting CSV provided when initially forming groups. 
