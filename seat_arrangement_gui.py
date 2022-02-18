import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
import seat_arrangement
from tkinter import messagebox
import pandas as pd

fields_dict = {'Students': {}, 'Classrooms': {}, 'Timings': {}}
folder_fields_dict = {'Output Folder': {}}
required_headings = {'Students': ['Roll_Number', 'Name'], 'Classrooms': ['Class_ID', 'Meta', 'Row', 'Column'],
                     'Timings': ['Exam', 'Date']}

def get_file(field_name):
    fname = askopenfilename(filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")),
                            title="Choose a file")
    if len(fname) == 0:
        return

    # Check whether the file is in the correct format
    error_str = file_format_checking(field_name, fname)
    if len(error_str) != 0:
        messagebox.showwarning("Warning", error_str)
        return

    fields_dict[field_name]['btn'].config(text='  Added  ')
    fields_dict[field_name]['btn'].config(foreground='green')
    fields_dict[field_name]['file'] = fname


def get_folder(field_name):
    fname = askdirectory(title="Choose output directory")
    if len(fname) == 0:
        return
    folder_fields_dict[field_name]['btn'].config(text=' Added ', foreground='green')
    folder_fields_dict[field_name]['folder'] = fname


# **** THIS SECTION CONTAINS VALIDATION TESTS FOR THE INPUT **
def check_required_columns(fields, df):
    idx = -1
    for field in fields:
        idx += 1
        if field != df.columns[idx]:
            return 'Required Columns (Same order):\n{}'.format("\n".join(fields))
    return ""


def check_pos_integer(arr, col_name):
    error_str = ""
    for idx, val in enumerate(arr):
        try:
            int(val)
        except ValueError:
            error_str = "{}\n Row Number: {} Column Name: {} should be integer".format(error_str, idx + 1, col_name)
    return error_str


def check_no_duplication(df, col_name):
    error_str = ""
    present_set = set()
    for val in df[col_name]:
        if val in present_set:
            error_str = '{}\n Duplicate {} found: {}'.format(error_str, col_name, val)
        present_set.add(val)
    return error_str


def file_format_checking(field_name, fname):
    df = pd.read_csv(fname)

    # Check for the headings
    error_str = check_required_columns(required_headings[field_name], df)
    if len(error_str) != 0: return error_str

    # Check for NaN and report empty cells
    for row_num, row in df.isnull().iterrows():
        for col_idx, val in enumerate(row):
            if val:
                error_str = "{}\n No value in Row Number: {} Column Name: {}".format(error_str, row_num + 1,
                                                                                     df.columns[col_idx])
    if len(error_str) != 0: return error_str

    # Individual checks
    if field_name == "Students":

        # Check that all roll numbers are integers
        error_str = check_pos_integer(df['Roll_Number'], 'Roll_Number')
        if len(error_str) != 0: return error_str

        # Check for all columns after name that they are integers
        for col_name in df.columns[2:]:
            arr = df[col_name]
            error_str = error_str + check_pos_integer(arr, col_name)
        if len(error_str) != 0: return error_str

        error_str = check_no_duplication(df, 'Roll_Number')

        # Check that the integers are 0/1 only for all subjects
        for col_name in df.columns[2:]:
            for idx, val in enumerate(df[col_name]):
                val = int(val)
                if val != 0 and val != 1:
                    error_str = "{}\n Value should be 0/1 encountered:{} for row number: {} column name: {}".format(
                        error_str, val, idx + 1, col_name)
        if error_str != 0: return error_str
    elif field_name == "Timings":
        error_str = check_no_duplication(df, 'Exam')
    else:
        # Check that no classroom is duplicated
        error_str = check_no_duplication(df, 'Class_ID')
        # Check positive integers in row and column
        error_str = "{}{}".format(error_str, check_pos_integer(df['Row'], 'Row'))
        error_str = "{}{}".format(error_str, check_pos_integer(df['Column'], 'Column'))
        if len(error_str) != 0: return error_str
        for col_name in ['Row', 'Column']:
            for idx, val in enumerate(df[col_name]):
                if int(val) < 1:
                    error_str = "{}\n Value should be >1 encountered:{} for row number: {} column name: {}".format(
                        error_str, val, idx + 1, col_name)
    return error_str


# *** VALIDATION TESTING ENDS HERE ***

def driver():
    file_not_added = [field for field, value in fields_dict.items() if 'file' not in value]

    if len(file_not_added) != 0:
        messagebox.showwarning("Warning",
                               "Files Not Selected For: \n{}".format('\n'.join(file_not_added)))
        return
    if 'folder' not in folder_fields_dict['Output Folder']:
        messagebox.showwarning("Warning", "Output folder not selected")
        return
    curr = seat_arrangement.main_class(stud_file=fields_dict['Students']['file'],
                                       time_file=fields_dict['Timings']['file'],
                                       class_file=fields_dict['Classrooms']['file'],
                                       out_dir=folder_fields_dict['Output Folder']['folder'])
    curr.driver(out_dir=folder_fields_dict['Output Folder']['folder'])


class first_step(tk.Frame):
    def __init__(self, master, parent):
        super(first_step, self).__init__(parent)
        # Make the browse CSV file buttons
        for field in fields_dict.keys():
            self.make_row(field)
        for folder in folder_fields_dict.keys():
            self.make_row(folder,file=False)

        # Adding execute button
        tk.Button(self, text='Execute', command=driver,padx=5,pady=5).place(relx=0.1, rely=0.8, anchor=tk.CENTER)
        # Adding button for second page
        tk.Button(self, text='Home', command=lambda: master.put_on_top('home'),padx=5,pady=5).place(relx=0.5, rely=0.8, anchor=tk.CENTER)
        # Adding quit button
        tk.Button(self, text='Quit', command=master.quit, foreground='red',padx=5, pady=5).place(relx=0.9, rely=0.8, anchor=tk.CENTER)

    def make_row(self, field, file=True):
        row = tk.Frame(self)
        curr_label = tk.Label(row, width=25, text=field, anchor='w')
        if file:
            new_button = tk.Button(row, text='Browse CSV', command=lambda: get_file(field),padx=5, pady=5)
            fields_dict[field] = {'label': curr_label, 'btn': new_button}
        else:
            new_button = tk.Button(row, text='Choose Folder', command=lambda: get_folder(field),padx=5, pady=5)
            folder_fields_dict[field] = {'label': curr_label, 'btn': new_button}

        row.pack(side=tk.TOP, fill=tk.X, padx=10, pady=20)
        new_button.pack(side=tk.RIGHT)
        curr_label.pack(side=tk.LEFT)
