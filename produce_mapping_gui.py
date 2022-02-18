import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import messagebox
import produce_mapping
import pandas as pd
import socket
from tkinter import ttk
fields_dict = {''}


class mapping_gui(tk.Frame):
    def __init__(self, master, parent):
        super(mapping_gui, self).__init__(parent)

        self.student_dict, self.roll_num = {}, {}

        # Making the add folder path, and loading of data
        self.add_folder = self.make_row('Input Folder', file=False)

        # Mapping of roll numbers to email id
        self.roll_email = {}

        # Get Info regarding roll number or name
        row = tk.Frame(self)
        tk.Label(row, text="Roll Number/Name").pack(side="left")
        self.rollnum_name = tk.Entry(row, text="", width=10)
        tk.Button(row, text='Get Info', command=self.get_info_roll_number, padx=5, pady=5).pack(side="right")
        self.rollnum_name.pack(anchor=tk.CENTER)
        row.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Text widget area
        row_2 = tk.Frame(self)
        self.disp_area = tk.Text(row_2, height=4, width=50)
        self.disp_area.pack(anchor=tk.CENTER)
        row_2.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self, text="", height=1,width=50,bg="grey").pack(side="top")

        # ***EMAIL SECTION***
        tk.Label(self, text="Email Settings", height=4).pack(side="top")

        # Adding email csv load
        self.add_email = self.make_row('Roll Number Email Address', file=True)

        # Adding Hosts settings
        row_3 = tk.Frame(self)
        tk.Label(row_3, text="Host Address", height=4).pack(side="left")
        self.host_address = tk.Entry(row_3, text="", width=10)
        self.host_address.pack(side="left")
        self.host_port = tk.Entry(row_3, text="", width=10)
        self.host_port.pack(side="right")
        tk.Label(row_3, text="Host Port", height=4).pack(side="right")
        row_3.pack(side="top", fill=tk.X, padx=40)

        # Adding loging requirements
        row_4 = tk.Frame(self)
        tk.Label(row_4, text="Login Details", height=1).pack(side="left")
        self.login_detail = tk.Entry(row_4, text="", width=10)
        self.login_detail.pack(side="left")
        self.password = tk.Entry(row_4, text="", width=10, show="*")
        self.password.pack(side="right")
        tk.Label(row_4, text="Password", height=1).pack(side="right")
        row_4.pack(side="top", fill=tk.X, padx=40)

        # Adding send email and progress bar
        row_5 = tk.Frame(self)
        self.progress_bar = ttk.Progressbar(row_5, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(side="top",fill=tk.X)
        row_5.pack(side="top")


        row_6 = tk.Frame(self)
        # Adding button for second page
        tk.Button(row_6, text='Home', command=lambda: master.put_on_top('home'),padx=5,pady=5).pack(side=tk.LEFT)
        # Adding quit button

        tk.Button(row_6, text='Quit', command=master.quit, foreground='red',padx=5, pady=5).pack(side=tk.RIGHT)
        row_6.pack(side=tk.TOP, fill=tk.X, padx=40, pady=5)


        tk.Button(self, text='Send Email', command=self.send_email,padx=5,pady=5).place(rely=0.925,relx=0.45)

    def make_row(self, field, file):
        row = tk.Frame(self)
        curr_label = tk.Label(row, width=25, text=field, anchor='w')
        if file:
            new_button = tk.Button(row, text='Browse CSV',padx=5,pady=5, command=lambda: self.email_csv())
            out_var = {'label': curr_label, 'btn': new_button, 'file': None}
        else:
            new_button = tk.Button(row, text='Choose Folder',padx=5,pady=5, command=lambda: self.input_folder())
            out_var = {'label': curr_label, 'btn': new_button, 'folder': None}

        row.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        new_button.pack(side=tk.RIGHT)
        curr_label.pack(side=tk.LEFT)
        return out_var

    def input_folder(self):
        fname = askdirectory(title="Choose output directory")
        if len(fname) == 0:
            return
        self.add_folder['folder'] = fname
        if self.load_data():
            self.add_folder['btn'].config(text=' Added ', foreground='green')


    def email_csv(self):
        if self.add_folder['folder'] is None:
            messagebox.showerror(title='Input order error', message='Please add folder with files before')
            return
        if len(self.student_dict) == 0:
            messagebox.showerror(title='Load data', message='Please load data from the folder')
            return

        fname = askopenfilename(filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")),
                                title="Choose a file")
        if len(fname) == 0:
            return

        # Check whether the file is in the correct format
        df = pd.read_csv(fname)
        if df.columns.tolist() != ['Roll_Number', 'Email']:
            messagebox.showerror(title='Load data error', message='Columns: \n Roll_Number and Email needed (Only)')
            return

        # Put in the dictionary
        for roll_num, email in zip(df['Roll_Number'].tolist(), df['Email'].tolist()):
            if roll_num in self.roll_email:
                messagebox.showerror(title='Duplication error', message='Roll Num: {} has two record'.format(roll_num))
                self.roll_email = {}
                return
            self.roll_email[roll_num] = email

        # Ensure all students in system have emails
        error_str = ""
        for key in self.student_dict.keys():
            if key not in self.roll_email:
                error_str += "Roll Number: {} has no email\n".format(key)
        if len(error_str) > 0:
            messagebox.showerror(title='Missing emails', message=error_str)

        self.add_email['btn'].config(text='  Added  ', foreground='green')
        self.add_email['file'] = fname

    def load_data(self):
        if self.add_folder['folder'] is None:
            messagebox.showerror(title='No folder selected', message='Please add folder')
            return None
        dict_tuple, error_str = produce_mapping.driver(self.add_folder['folder'])
        if error_str:
            messagebox.showerror(title='Error', message=error_str)
            return None
        self.student_dict, self.roll_num = dict_tuple
        return 1

    def add_text(self, text):
        self.disp_area.config(state=tk.NORMAL)
        self.disp_area.delete(1.0, tk.END)
        self.disp_area.insert(tk.END, text)
        self.disp_area.config(state=tk.DISABLED)

    def get_info_roll_number(self):
        if self.add_folder['folder'] is None:
            messagebox.showerror(title='No folder selected', message='Please add folder and load data')
            return
        roll_num_name = self.rollnum_name.get()
        try:
            roll_num = int(roll_num_name)
            # If name
        except ValueError:
            if roll_num_name not in self.roll_num:
                self.add_text('Name: {} not present in database'.format(roll_num_name))
                return
            if len(self.roll_num[roll_num_name]) > 1:
                self.add_text('Multiple roll numbers for names {} '.format(self.roll_num[roll_num_name]))
                return
            roll_num = int(self.roll_num[roll_num_name][0])

        # If roll number not in the student dictionary error out
        if roll_num not in self.student_dict:
            self.add_text('Roll Number: {} not in database'.format(roll_num))
            return
        out_str = "Roll Number: {}".format(roll_num)
        for subj, info_tuple in self.student_dict[roll_num].items():
            out_str += "\nSubject {}:\nClass: {} Date: {} Row: {} Column:{}".format(
                subj, info_tuple[0], info_tuple[1], info_tuple[2], info_tuple[3])
        self.add_text(out_str)

    def generate_email(self, key):
        out_str = "Dear Student\n Your examination details are: \n Roll Number: {}\n".format(key)
        for subject, info in self.student_dict[key].items():
            out_str += "Subject: {} Date: {} Class ID:{} Row:{} Column: {}\n".format(subject, info[1], info[0], info[2],
                                                                                     info[3])
        return out_str

    def send_email(self):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        if len(self.roll_email) < 1:
            messagebox.showerror(title='Load error', message='Roll Number email file not loaded')
            return
        if len(self.host_address.get()) == 0:
            messagebox.showerror(title='Wrong settings', message='Host address not present')
            return
        if len(self.host_port.get()) == 0:
            messagebox.showerror(title='Wrong settings', message='Host port not present')
            return
        if len(self.login_detail.get()) == 0:
            messagebox.showerror(title='Wrong settings', message='Login detail not present')
            return
        if len(self.password.get()) == 0:
            messagebox.showerror(title='Wrong settings', message='Password not present')
            return
        try:
            host_port = int(self.host_port.get())
        except ValueError:
            messagebox.showerror(title='Wrong settings', message='Host port should be integer')
            return
        try:
            msg_connection = smtplib.SMTP(host=self.host_address.get(), port=host_port,timeout=30)
        except (TimeoutError, socket.gaierror):
            messagebox.showerror(title='Wrong host settings', message='Unable to reach host')
            return
        msg_connection.starttls()

        # Authneticating with server
        try:
            msg_connection.login(self.login_detail.get(), self.password.get())
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror(title='Wrong login', message='Wrong login information')
            return
        subject = "Exam schedule and seating"
        from_adress = self.login_detail.get()
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.student_dict.keys())
        for key in self.student_dict.keys():
            body = self.generate_email(key)
            msg = MIMEMultipart()
            msg['From'] = from_adress
            msg['To'] = self.roll_email[key]
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            msg_connection.send_message(msg)
            self.progress_bar["value"] += 1
        del msg
        msg_connection.quit()
