from csv import writer
from pandas import DataFrame, read_csv
from re import split
from tkinter import BOTH, TOP, X, Frame, Menu, Scrollbar, Tk
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Entry, Treeview


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV-NSI")
        self.geometry("1280x720")
        self.minsize(1280, 720)
        self.maxsize(1920, 1080)
        self.iconbitmap("assets/icon.ico")
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.main_frame = Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True)
        self.main_frame.config(background="#36393F")

        self.page = Page(self.main_frame)

        self.barmenu = Menu(self)
        filemenu = Menu(self.barmenu, tearoff=0)
        filemenu.add_command(label="Ouvrir", command=self.page.choosefile)
        filemenu.add_command(label="Sauvegarder", command=self.page.savefile)
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.quit)
        self.barmenu.add_cascade(label="Fichier", menu=filemenu)

        self.config(menu=self.barmenu)

        self.mainloop()


class Table(Treeview):
    def __init__(self, parent):
        super().__init__(parent)
        scroll_Y = Scrollbar(self, orient="vertical", command=self.yview)
        scroll_X = Scrollbar(self, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=scroll_Y.set, xscrollcommand=scroll_X.set)
        scroll_Y.pack(side="right", fill="y")
        scroll_X.pack(side="bottom", fill="x")
        self.stored_dataframe = DataFrame()

        self.line_menu = Menu(self, tearoff=0)
        self.line_menu.add_command(label="Insérer une ligne en dessous", command=self.insert_line)
        self.line_menu.add_command(label="Supprimer", command=self.delete_selected)

        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Insérer une ligne", command=self.insert_line)
        self.bind("<Button-3>", self._popup)
        self.bind("<Double-Button-1>", self._edit_cell)

    def insert_line(self):
        values = []
        for k in self.stored_dataframe.columns:
            elt = askstring("Nouvelle ligne", f"Valeur de la colonne {k}")
        self.insert("", "end", values=values)

    def delete_selected(self):
        selected = self.selection()
        for item in selected:
            self.delete(item)

    def set_datatable(self, dataframe):
        self.stored_dataframe = dataframe
        self._draw_table(dataframe)

    def _draw_table(self, dataframe):
        self.delete(*self.get_children())
        columns = list(dataframe.columns)
        self.__setitem__("column", columns)
        self.__setitem__("show", "headings")

        for col in columns:
            self.heading(col, text=col)

        df_rows = dataframe.to_numpy().tolist()
        for row in df_rows:
            self.insert("", "end", values=row)
        return None

    def find_value(self, pairs):
        # pairs is a dictionary
        new_df = self.stored_dataframe
        for col, value in pairs.items():
            query_string = f"{col}.str.contains('{value}')"
            new_df = new_df.query(query_string, engine="python")
        self._draw_table(new_df)

    def reset_table(self):
        self._draw_table(self.stored_dataframe)
    
    def add_element(self, row):
        self.insert("", "end", values=row)


class Page(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.searchbox = Entry(parent)
        self.searchbox.pack(fill=X, side=TOP)
        self.searchbox.bind("<Return>", self.search_table)

        self.datatable = Table(parent)
        self.datatable.pack(fill=BOTH, expand=True, side=TOP)

    def choosefile(self):
        self.file = askopenfilename(
            title="Ouvrir un fichier CSV",
            filetypes=[
                ("Fichier CSV", "*.csv"),
                ("Fichiers TXT", "*.txt"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        self.datatable.set_datatable(
            read_csv(
                self.file, delimiter=";", encoding="utf-8", low_memory=False, nrows=100000
            )
        )

    def savefile(self):
        with open(self.file, "w", newline="") as file:
            csvwriter = writer(file, delimiter=";")
            csvwriter.writerow(self.datatable.stored_dataframe.columns)
            for row_id in self.datatable.get_children():
                row = self.datatable.item(row_id)["values"]
                csvwriter.writerow(row)

    def search_table(self, event):
        entry = self.searchbox.get()
        if entry == "":
            self.datatable.reset_table()
        else:
            filter = {}
            for pair in split(",|;|/", entry):
                pair_split = pair.split("=")
                if len(pair_split) == 2:
                    col = pair_split[0]
                    if col in self.datatable.stored_dataframe.columns:
                        filter[col] = pair_split[1]
            self.datatable.find_value(pairs=filter)


App()
