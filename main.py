from function import *
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename


class App(Tk):
    file = ""

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
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.quit)
        menu_bar.add_cascade(label="Fichier", menu=filemenu)

        self.config(menu=menu_bar)

    def choosefile(self):
        file = askopenfilename(title="Ouvrir un fichier CSV", filetypes=[(
            "Fichier CSV", "*.csv"), ("Fichiers TXT", "*.txt"), ("Tous les fichiers", "*.*")])
        self.makeentry(file)

    def makeentry(self, file=None):
        if not file:
            nodata = Label(self, text="Aucunes données",
                           width=20, fg="white", bg="#3B3B3B")
            nodata.grid(column=0, row=0, padx=10, pady=10)
            nodata.place(anchor="center", relx=0.5, rely=0.5)
        else:
            for widget in self.winfo_children():
                widget.destroy()
            self.menubar()

            self.columns, self.cache = cache(file)
            for y, elt in enumerate(self.cache):
                for i, value in enumerate(elt):
                    item = Label(self, text=value,
                                 width=20, fg="white", bg="#3B3B3B")
                    item.grid(column=i, row=y, padx=10, pady=10)


App().mainloop()
