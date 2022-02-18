import logging
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import pandas as pd
from random import shuffle
from util import save_pickle


class main_class:
    def __init__(self, stud_file, time_file, class_file, out_dir):
        logging.info('Instantiating main class')
        logging.info('Files:\n Student: {}\n Exams: {}\n Classrooms: {}'.format(stud_file, time_file, class_file))
        # rem_stud stores the number of remaining students of each subject
        # Reading in csv
        stud_df = pd.read_csv(stud_file)

        # Creating dictionary to relate roll number to name along with what all subjects they are in (Useful later)
        roll_mapping = {stud_df['Roll_Number'][idx]: {'name': stud_df['Name'][idx], 'sub': set()} for idx in
                        range(len(stud_df['Roll_Number']))}

        # Mapping name to Roll Numbers:
        name_roll_map = {}
        for idx in range(len(stud_df['Roll_Number'])):
            name = stud_df['Name'][idx]
            if name not in name_roll_map:
                name_roll_map[name] = []
            name_roll_map[name].append(stud_df['Roll_Number'][idx])

        subjects = stud_df.columns.tolist()[2:]  # Array containing subject names

        self.stud_arr, self.rem_stud = {}, {}
        for subject in subjects:
            # Get roll number of students who are sitting for the subject
            self.stud_arr[subject] = stud_df.loc[stud_df[subject] == 1]['Roll_Number'].tolist()
            # Shuffle the list
            shuffle(self.stud_arr[subject])
            self.rem_stud[subject] = len(self.stud_arr[subject])
            # Also add mapping of url
            for uid in self.stud_arr[subject]:
                roll_mapping[uid]['sub'].add(subject)

        # Read in the time file as csv and set Date as index
        time_df = pd.read_csv(time_file)

        # Get the exam and dates
        exam_dict = {ele[1]['Exam']: ele[1]['Date'] for ele in time_df.iterrows()}


        time_df = time_df.set_index('Date')
        self.exam_arr = []
        # Get the exams which are occuring on the same date along with the date
        for date in set(time_df.index):
            val = time_df.loc[date, 'Exam']
            if type(val) != str:
                self.exam_arr.append((date, set(val)))
            else:
                self.exam_arr.append((date, {val}))

        # Class room dictionary
        class_df = pd.read_csv(class_file)
        self.classroom_dict = {row_tuple[1]['Class_ID']: (row_tuple[1]['Row'], row_tuple[1]['Column'], row_tuple[1]['Meta'])
                               for row_tuple in class_df.iterrows()}
        class_dict = {key: val[2] for key, val in self.classroom_dict.items()}

        # Save pickle with dictionaries for production checking
        save_pickle('{}/dat.pkl'.format(out_dir),dat={'class':class_dict, 'exams': exam_dict, 'students': roll_mapping,
                                                      'name_roll_map':name_roll_map})

        self.prevcol = {}
        self.newcol_dict = {}

    def sub_choice(self, num_stud, prevcol_subj, exam_set):
        """
        Returns the subject
        :param: num_stud: number of students
        :return:
        """
        curr_max, curr_subj = 0, None
        # Find the subject which has maximum number of students remaining that was not in previous case
        for subj, rem in self.rem_stud.items():
            # tup: (remaining students, subject, corresponding index)
            if (subj in exam_set) and (subj not in prevcol_subj) and (rem > curr_max):
                curr_max, curr_subj = rem, subj
        return curr_subj

    def get_column(self, rem_seats, prevcol_subj, exam_set):
        """
        This function uses the sub_choice function to populate array representing the column.
        :param rem_seats: Remaining seats
        :param prevcol_subj: Set containing subjects in previous column
        :return:
        """
        # Store the array of seats and the pre
        seat_arr, col_subj = [], {}
        while rem_seats != 0:

            # Get subject from sub_choice
            subj = self.sub_choice(rem_seats, prevcol_subj, exam_set)
            if subj is None:
                break

            # Populate seats
            upper_idx = self.rem_stud[subj]
            lower_idx = max(0, upper_idx - rem_seats)
            seat_arr += [(val, subj) for val in self.stud_arr[subj][lower_idx:upper_idx]]

            # Updating for next iteration
            rem_seats -= (upper_idx - lower_idx)
            self.rem_stud[subj] -= (upper_idx - lower_idx)
            col_subj[subj] = None

        # If there are remaining seats add None to fill up
        if rem_seats != 0:
            seat_arr += [None] * rem_seats
        return seat_arr, col_subj

    def process_class(self, class_info, out_dir, date, class_name, exam_set):
        """
        It is used to print the matrix, providing other necessary information, and creating
        .csv files which can be printed.
        """
        fid = open(file='{}/{}_{}.csv'.format(out_dir, class_name, date.replace('/', '_')), mode='w')
        fid.writelines('JPIS\n{}\n'.format(date))
        fid.writelines('Class:{},{}\n'.format(class_name,class_info[2]))

        # Populating the classroom
        class_room, prevcol_subj = [None] * class_info[1], {}
        for x in range(class_info[1]):
            class_room[x], prevcol_subj = self.get_column(class_info[0], prevcol_subj, exam_set)

        # Printing to csv
        fid.writelines('Layout:\n')
        for r in range(len(class_room[0])):
            out_str = ""
            for c in range(len(class_room)):
                if class_room[c][r] is None:
                    out_str = '{},'.format(out_str)
                else:
                    out_str = '{}{}:{},'.format(out_str, class_room[c][r][0], class_room[c][r][1])
            fid.writelines(out_str[:-1] + '\n')

        fid.close()

    def driver(self, out_dir):
        # Loop over to get exams for each day
        for date, exams in self.exam_arr:
            for id, val in self.classroom_dict.items():
                self.process_class(out_dir=out_dir, date=date, class_name=id, class_info=val, exam_set=exams)
        logging.info('Program Complete')


def main():
    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s', level='INFO')
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            description='Makes Class Room Schedules for examinations')
    parser.add_argument('-stud_csv', type=str, default='input_students.csv',
                        help='CSV File with student info')
    parser.add_argument('-time_csv', type=str, default='timing.csv',
                        help='CSV File with examination times')
    parser.add_argument('-class_csv', type=str, default='classrooms.csv',
                        help='CSV File with classrooms info')
    parser.add_argument('-out_dir', type=str, default='output', help='Output directory')
    args = parser.parse_args()
    curr = main_class(stud_file=args.stud_csv, time_file=args.time_csv,
                      class_file=args.class_csv, out_dir=args.out_dir)
    curr.driver(args.out_dir)


if __name__ == '__main__':
    main()
