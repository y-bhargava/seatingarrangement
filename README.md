#README
## Requirements:
The requirements of the project are present in the file ``requirements.txt``. Python version 3 is required. To install the requirements use the command: ``pip3 install -r requirements.txt``. To run the gui use ``python3 main_gui.py``.
## Instructions:
### Getting Seat Arrangement
Three input files are required which should be of the csv format.
* For Students: the first two columns should be ``Roll_Number,Name`` and there should be no duplication of Roll Number along with being an integer. Each student should have a 0/1 indicated for each subject (0 meaning not taking it) and (1 meaning taking it)
* For Timings: There should be only two columns ``Exam, Date`` where all exams should be declared and date for each exam should be stated
* For Classroom: Columns should be ``Class_ID,Meta,Row,Column`` where ``Class_ID`` is unique identifier for each classroom, and ``Meta`` contains additional information about the classroom which would be printed in the csv.

The input files should be loaded and then the output folder should be selected where the seating plan for each classroom will be produced. The file names are of the format ``Class_ID_Date`` where the ``Date`` is seperated by **_** rather than **/**. 
### Looking up schedule for student and sending emails
The output files from the previous step can be altered but should have the similar form. Input checks in this step will ensure that each student is enrolled in the same subjects, and that exam for subject takes place at the correct time. The output folder needs to be selected (temperory file created by the first step ``dat.pkl`` should still be present in it). After loading the roll number or name of student can be entered in the Roll Number/Name entry area. To get info about the student represented by Roll Number/Name click on ``Get Info``.  CSV file with emails has to be loaded with columns: ``Roll_Number,Email`` and each roll number in the data should be present, and no duplication should be present. The server settings along with login and password should be provided. The mails which will be sent will have the following format:

**Subject:**
 
Exam schedule and seating

**Body:**

Dear Student

Your examination details are: 

Roll Number: {}

Subject: {} Date: {} Class ID:{} Row:{} Column: {} ``This is done for each exam``


The mails will be sent when the button ``Send Email`` is pressed and the progress will be shown in the progress bar.