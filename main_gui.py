from seat_arrangement_gui import *
from produce_mapping_gui import *


class main_app(tk.Tk):
    def __init__(self):
        super(main_app, self).__init__()
        # Master frame
        master_fr = tk.Frame(self)
        master_fr.pack(side="top", fill="both", expand=True)
        master_fr.grid_rowconfigure(0), master_fr.grid_columnconfigure(0)
        self.frames_val = {}
        self.frames_val['home'] = home_page(master=self, parent=master_fr)
        self.frames_val['main'] = first_step(master=self, parent=master_fr)
        self.frames_val['mapping'] = mapping_gui(master=self, parent=master_fr)
        for val in self.frames_val.values():
            val.grid(row=0, column=0, sticky="nsew")
        self.put_on_top('home')
        self.winfo_toplevel().title("Seating Arrangement")


    def put_on_top(self, name):
        self.frames_val[name].tkraise()


class home_page(tk.Frame):
    def __init__(self, parent, master):
        super(home_page, self).__init__(parent)
        self.controller = master
        label = tk.Label(self, text="Please Choose Options:")
        label.pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Order Seats", command=lambda: master.put_on_top('main'), height=4, width=25).place(
            relx=0.5, rely=0.35, anchor=tk.CENTER)
        tk.Button(self, text="Lookup\n Send Emails", command=lambda: master.put_on_top('mapping'), height=4,
                  width=25).place(relx=0.5, rely=0.75, anchor=tk.CENTER)


if __name__ == '__main__':
    app = main_app()
    app.mainloop()
