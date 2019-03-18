from gatV4 import groupAssign
from tkinter import filedialog, messagebox
from tkinter import *

def get_student_file():
    root.sfilename = filedialog.askopenfilename(
        title = "Select Student Response CSV", filetypes = (("CSV files","*.csv"),
                                                            ("All files","*.*")))
    names = (root.sfilename).split("/")
    sLabel.config(text=names[-1])
def get_prof_file():
    root.pfilename = filedialog.askopenfilename(
        title = "Select Weighting CSV", filetypes = (("CSV files","*.csv"),
                                                        ("All files","*.*")))
    names = (root.pfilename).split("/")
    wLabel.config(text=names[-1])
# def change_dropdown_g(*args):
#     root.gflag = gflag.get()
#
# def change_dropdown_e(*args):
#     root.eflag = eflag.get()

def initialize():
    sfile = root.sfilename
    pfile = root.pfilename

    pg = int(per_group.get())
    nit = int(n_iter.get())
    gp = float(gpen.get())
    ep = float(epen.get())
    eq = eth.get()
    gq = gen.get()
    nq = name_q.get()

    gf = gflag.get() == "True"
    ef = eflag.get() == "True"
    mode = 'Normal'

    if sfile is not None and pfile is not None:
        assign = groupAssign(sfile, pfile, per_group = pg, mode = mode, gen_pen = gp,
            gen_flag = gf, eth_flag = ef, eth_pen = ep, n_iter = nit,
            name_q = nq, gen_q = gq, eth_q = eq)

        assign.iterate_normal()
        assign.output_state('p')
    elif sfile is None and pfile is None:
        messagebox.showerror("Files Not Provided",
                            "Please select student and weighting CSV files.")
    elif sfile is None:
        messagebox.showerror("File Not Provided", "Please select student CSV file.")
    elif pfile is None:
        messagebox.showerror("File Not Provided", "Please select weighting CSV file.")

# File selection, etc.
#per_group = 4, mode = 'Normal',
#            gen_pen = 15, gen_flag = True, eth_pen = 15, eth_flag = True,
#            scheduling_weight = 50):
if __name__ == '__main__':
    root = Tk()
    root.title("Group Assignment Tool")

    # Frame setup
    mainframe = Frame(root)
    mainframe.grid(column=0,row=0, sticky=(N,W,E,S))
    mainframe.columnconfigure(0, weight = 1)
    mainframe.rowconfigure(0, weight = 1)


    # Entry gender penalty
    Label(mainframe, text = "Gender Penalty: ").grid(row = 0, column = 1,
                                                sticky = W, padx = (10, 0), pady = (10,0))
    gpen = Entry(mainframe)
    gpen.grid(row = 0, column = 2, pady = (10,0))
    gpen.insert(0, "15")

    # Entry eth penalty
    Label(mainframe, text = "Ethnicity Penalty: ").grid(row = 1, column = 1,
                                                sticky = W, padx = (10, 0))
    epen = Entry(mainframe)
    epen.grid(row = 1, column = 2)
    epen.insert(0, "10")

    # Entry num per group
    Label(mainframe, text = "Group Size: ").grid(row = 2, column = 1,
                                    sticky = W, pady = (0,20), padx = (10, 0))
    per_group = Entry(mainframe)
    per_group.grid(row = 2, column = 2, pady = (0,20))
    per_group.insert(0, "4")

    # Entry num iterations
    Label(mainframe, text = "Iterations: ").grid(row = 0, column = 3,
                                    sticky = W, pady = (10,0), padx = (10, 0))
    n_iter = Entry(mainframe)
    n_iter.grid(row = 0, column = 4, pady = (10,0), padx = (0, 10))
    n_iter.insert(0, "15000")

    # Entry ethnicity question
    Label(mainframe, text = "Ethnicity question: ").grid(row = 1, column = 3,
                                    sticky = W, padx = (10, 0))
    eth = Entry(mainframe)
    eth.grid(row = 1, column = 4, padx = (0, 10))
    eth.insert(0, "What is your ethnicity?")

    # Entry gender question
    Label(mainframe, text = "Gender question: ").grid(row = 2, column = 3,
                                    sticky = W, padx = (10, 0))
    gen = Entry(mainframe)
    gen.grid(row = 2, column = 4, padx = (0, 10))
    gen.insert(0, "With what gender do you identify?")


    # Entry Name question
    Label(mainframe, text = "Student Identifier Question: ").grid(row = 3, column = 3,
                                    sticky = W, padx = (10, 0))
    name_q = Entry(mainframe)
    name_q.grid(row = 3, column = 4, padx = (0, 10))
    name_q.insert(0, "NETID")

    # Dropdown for flags/mode

    # Gender
    gflag = StringVar(mainframe)
    gChoices = ['True', 'False']
    gflag.set('True')
    popupGMenu = OptionMenu(mainframe, gflag, *gChoices)
    Label(mainframe, text="Gender Flag").grid(row = 3, column = 1, padx = (10, 0),
                                            sticky = W)
    popupGMenu.grid(row = 3, column = 2, sticky = W)

    #gflag.trace('w', change_dropdown_g)

    # Ethnicity
    eflag = StringVar(mainframe)
    eChoices = ['True', 'False']
    eflag.set('True')
    popupEMenu = OptionMenu(mainframe, eflag, *eChoices)
    Label(mainframe, text="Ethnicity Flag").grid(row = 4, column = 1, padx = (10, 0),
                                                pady = (0, 10), sticky = W)
    popupEMenu.grid(row = 4, column = 2, pady = (0, 10), sticky = W)

    #eflag.trace('w', change_dropdown_e)

    # Mode



    # File input
    input_s_file = Button(mainframe, text='Input Student CSV', command=get_student_file)
    input_s_file.grid(row = 5, column = 1, padx = (10, 0))
    root.sfilename = None

    sLabel = Label(mainframe, text="Select File")
    sLabel.grid(row=6, column = 1, padx = (10, 0), pady = (0, 10))

    input_p_file = Button(mainframe, text='Input Weighting CSV', command=get_prof_file)
    input_p_file.grid(row = 5, column = 2)
    root.pfilename = None

    wLabel = Label(mainframe, text="Select File")
    wLabel.grid(row=6, column = 2, padx = (10, 0), pady = (0, 10))



    run_test = Button(mainframe, text='Assign Groups', command=initialize)
    run_test.grid(row=5, column=4, padx = (0, 10), sticky = 'E')

    root.mainloop()
