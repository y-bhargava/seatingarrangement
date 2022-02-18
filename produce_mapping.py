from glob import glob
from util import load_pickle

student_dict = {}


def read_csv(fname, out_dir, dat):
    global student_dict
    class_id, d, m, y = fname[:-4].split('_')
    date = '{}/{}/{}'.format(d, m, y)
    fid = open('{}/{}'.format(out_dir, fname), 'r')
    curr_line = ""
    while curr_line != 'Layout:\n':
        curr_line = fid.readline()
    row_idx = 0
    # Input data into data structure
    while len(curr_line) > 1:
        row_idx += 1
        curr_line = fid.readline()
        curr_row = curr_line.split(',')
        for col_idx, val in enumerate(curr_row):
            if len(val) < 2:
                continue
            roll_num, subject = val.split(':')
            roll_num, subject = roll_num.strip(), subject.strip()
            roll_num = int(roll_num)
            if roll_num not in student_dict:
                student_dict[roll_num] = {}
            # Duplicate entry checker
            if subject in student_dict[roll_num]:
                return 'Check file: {} Roll Num: {} Duplicate Entry\n '.format(fname[:-4], roll_num)
            # Checking that exam date is correct
            if dat['exams'][subject] != date:
                return 'Check file: {} Roll Num: {} \n Exam For Subject: {} does not take place on: {}'.format(
                    fname[:-4], roll_num, subject, date)
            student_dict[roll_num][subject] = (class_id, date, row_idx, col_idx + 1)
    return ""


def driver(out_dir):
    global student_dict
    student_dict = {}
    # Load data
    dat, errors = load_pickle('{}/dat.pkl'.format(out_dir))
    if errors:
        return errors
    # If there is error then return
    error_str = ""
    f_arr = glob('{}/*.csv'.format(out_dir))
    if len(f_arr) == 0:
        return None, "Zero .csv files present"
    for f_name in f_arr:
        error_str += read_csv(f_name[len(out_dir) + 1:], out_dir, dat)

    if len(error_str) != 0:
        return None, error_str

    # Ensure that the mapping is not destroyed
    error_str = ""
    for roll_num, value in dat['students'].items():
        if roll_num not in student_dict:
            error_str = "{}\nRoll Number: {} is not in updated csv".format(error_str, roll_num)
            continue
        # Make set of all subjects
        curr_subj = {key for key in student_dict[roll_num].keys()}
        if curr_subj != value['sub']:
            error_str = "{}\nRoll Number: {}\n has different subjects".format(error_str, roll_num)

    if len(error_str) != 0:
        return None, error_str
    return (student_dict, dat['name_roll_map']), None
