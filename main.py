from function import *
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
from functools import partial


class App(Tk):
    file = ""
    columns = ()

    def __init__(self):
        Tk.__init__(self)
        self.menubar()
        self.makeentry()

        # Propriétés de la fenêtre

        self.title("CSV-NSI")
        self.geometry("1280x720")
        self["bg"] = "#121212"

    def menubar(self):
        menu_bar = Menu(self)

        filemenu = Menu(menu_bar, tearoff=0)
        filemenu.add_command(label="Ouvrir", command=self.choosefile)
        filemenu.add_command(label="Fermer", command=self.makeentry)
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.quit)
        menu_bar.add_cascade(label="Fichier", menu=filemenu)

        filtermenu = Menu(menu_bar, tearoff=0)
        filtermenu.add_command(
            label="Supprimer le filtre", command=self.filter)
        filtermenu.add_separator()
        for key in self.columns:
            filtermenu.add_command(
                label=key, command=partial(self.filter, key))
        menu_bar.add_cascade(label="Filtrer", menu=filtermenu)

        self.config(menu=menu_bar)

    def makeentry(self, data=None):
        for widget in self.winfo_children():
            widget.destroy()

        self.menubar()

        if not data:
            nodata = Label(self, text="Aucunes données",
                           width=20, fg="white", bg="#3B3B3B")
            nodata.grid(column=0, row=0, padx=1, pady=1)
            nodata.place(anchor="center", relx=0.5, rely=0.5)
        else:
            for y, elt in enumerate(data):
                for i, value in enumerate(elt):
                    item = Label(self, text=value,
                                 width=20, fg="white", bg="#3B3B3B")
                    item.grid(column=i, row=y, padx=1, pady=1)

    def scrollbar(self):
        Scrollbar()

    def choosefile(self):
        file = askopenfilename(title="Ouvrir un fichier CSV", filetypes=[(
            "Fichier CSV", "*.csv"), ("Fichiers TXT", "*.txt"), ("Tous les fichiers", "*.*")])

        self.columns, self.cache = cache(file)
        self.icolumns = {k: v for v, k in enumerate(self.columns)}
        self.makeentry(self.cache)

    def filter(self, key=None):
        if key:
            value = askstring("Filtrer", "Valeur à filtrer")
            self.makeentry(listfilter(
                self.cache, self.icolumns, key, value))
        else:
            self.makeentry(self.cache)


App().mainloop()
