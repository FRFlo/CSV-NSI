from function import *
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
from functools import partial


class App(Tk):
    file = ""
    columns = ()

    def __init__(self):
        Tk.__init__(self)
        self.menubar()
        self.maketable()

        # Propriétés de la fenêtre

        self.title("CSV-NSI")
        self.geometry("1280x720")
        self["bg"] = "#121212"

    def menubar(self):
        menu_bar = Menu(self)

        filemenu = Menu(menu_bar, tearoff=0)
        filemenu.add_command(label="Ouvrir", command=self.choosefile)
        filemenu.add_command(label="Fermer", command=self.updatetable)
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.quit)
        menu_bar.add_cascade(label="Fichier", menu=filemenu)

        filtermenu = Menu(menu_bar, tearoff=0)
        filtermenu.add_command(label="Supprimer le filtre", command=self.filter)
        filtermenu.add_separator()
        for key in self.columns:
            filtermenu.add_command(label=key, command=partial(self.filter, key))
        menu_bar.add_cascade(label="Filtrer", menu=filtermenu)

        self.config(menu=menu_bar)

    def maketable(self):
        frame = Frame(self)
        frame.config(background="#121212")
        frame.pack(fill=BOTH, expand=True)

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.table = ttk.Treeview(
            frame, yscrollcommand=scrollbar.set, xscrollcommand=scrollbar.set
        )
        self.table.pack(fill=BOTH, expand=True)

        scrollbar.config(command=self.table.yview)
        scrollbar.config(command=self.table.xview)

    def updatetable(self, columns=(), data=[]):
        for i in self.table.get_children():
            self.table.delete(i)

        self.table.column("#0", width=0, stretch=NO)
        self.table.heading("#0", text="", anchor=CENTER)
        self.table["columns"] = columns
        for key in columns:
            self.table.column(key, anchor=CENTER, width=80)
            self.table.heading(key, text=key, anchor=CENTER)

        for index, key in enumerate(data):
            self.table.insert(parent="", index="end", iid=index, text="", values=key)
        self.table.pack(fill=BOTH, expand=True)

    def choosefile(self):
        file = askopenfilename(
            title="Ouvrir un fichier CSV",
            filetypes=[
                ("Fichier CSV", "*.csv"),
                ("Fichiers TXT", "*.txt"),
                ("Tous les fichiers", "*.*"),
            ],
        )

        self.columns, self.cache = cache(file)
        self.icolumns = {k: v for v, k in enumerate(self.columns)}
        self.updatetable(self.columns, self.cache)

    def filter(self, key=None):
        if key:
            value = askstring("Filtrer", "Valeur à filtrer")
            self.updatetable(listfilter(self.cache, self.icolumns, key, value))
        else:
            self.updatetable(self.cache)


App().mainloop()
