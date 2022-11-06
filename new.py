from csv import writer
from functools import partial
from pandas import DataFrame, read_csv
from re import split
from tkinter import BOTH, END, TOP, X, Frame, Menu, Scrollbar, Tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring
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
        self.bind("<Control-s>", self.page.savefile)

        self.barmenu = Menu(self)
        filemenu = Menu(self.barmenu, tearoff=0)
        filemenu.add_command(label="Ouvrir", command=self.choosefile)
        filemenu.add_command(label="Ouvrir via une URL", command=self.chooseremotefile)
        filemenu.add_command(label="Sauvegarder", command=self.page.savefile)
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.quit)
        self.barmenu.add_cascade(label="Fichier", menu=filemenu)
        self.statsmenu = Menu(self.barmenu, tearoff=0)
        self.statsmenu.add_command(label="Stats générales", command=self.page.show_stats)
        self.statsmenu.add_separator()
        self.barmenu.add_cascade(label="Statistiques", menu=self.statsmenu)

        self.config(menu=self.barmenu)

        self.mainloop()

    def choosefile(self, file=None):
        self.page.file = file or askopenfilename(
            title="Ouvrir un fichier CSV",
            filetypes=[
                ("Fichier CSV", "*.csv"),
                ("Fichiers TXT", "*.txt"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        if not self.page.file:
            return
        self.page.datatable.set_datatable(
            read_csv(
                self.page.file, delimiter=";", encoding="utf-8", low_memory=False, nrows=100000
            )
        )

        self.statsmenu.delete(2, END)

        for column in self.page.datatable.stored_dataframe.columns:
            self.statsmenu.add_command(label=column, command=partial(self.page.show_stats, column))
    
    def chooseremotefile(self):
        url = askstring("Ouvrir un fichier CSV", "URL du fichier CSV")
        self.choosefile(url)


class Table(Treeview):
    def __init__(self, parent):
        super().__init__(parent)
        scroll_Y = Scrollbar(self, orient="vertical", command=self.yview)
        scroll_X = Scrollbar(self, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=scroll_Y.set, xscrollcommand=scroll_X.set)
        scroll_Y.pack(side="right", fill="y")
        scroll_X.pack(side="bottom", fill="x")
        self.stored_dataframe = DataFrame()  # type: ignore

        self.line_menu = Menu(self, tearoff=0)
        self.line_menu.add_command(label="Insérer une ligne en dessous", command=self.insert_line)
        self.line_menu.add_command(label="Supprimer", command=self.delete_selected)

        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Insérer une ligne", command=self.insert_line)
        self.bind("<Button-3>", self._popup)
        self.bind("<Double-Button-1>", self._edit_cell)

    def insert_line(self):
        self.insert("", "end", values=[""] * len(self.stored_dataframe.columns))

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

    def _popup(self, event):
        match self.identify_region(event.x, event.y):
            case "cell":
                self.line_menu.post(event.x_root, event.y_root)
            case "heading":
                self.context_menu.post(event.x_root, event.y_root)
            case _:
                self.context_menu.post(event.x_root, event.y_root)

    def _edit_cell(self, event):
        if self.identify_region(event.x, event.y) != "cell":
            return
        
        column = self.identify_column(event.x)
        column_index = int(column[1:]) -1
        selected_iid = self.focus()
        selected_values = self.item(selected_iid)
        if column == "#0":
            return
        selected_text  = selected_values.get("values")[column_index]
        column_box = self.bbox(selected_iid, column=column)

        entry_edit = Entry(self, width=column_box[2])  # type: ignore
        entry_edit.editing_column_index = column_index  # type: ignore
        entry_edit.editing_item_iid = selected_iid  # type: ignore
        entry_edit.insert(0, selected_text)
        entry_edit.select_range(0, END)
        entry_edit.focus()
        entry_edit.bind("<FocusOut>", self._edit_cell_focusout)
        entry_edit.bind("<Escape>", self._edit_cell_focusout)
        entry_edit.bind("<Return>", self._edit_cell_return)
        entry_edit.place(x=column_box[0], y=column_box[1], w= column_box[2], h=column_box[3])
    
    def _edit_cell_return(self, event):
        new_text = event.widget.get()
        selected_iid = event.widget.editing_item_iid
        column_index = event.widget.editing_column_index

        if column_index != -1:
            current_values = self.item(selected_iid).get("values")
            current_values[column_index] = new_text  # type: ignore
            self.item(selected_iid, values=current_values)
        
        event.widget.destroy()

    def _edit_cell_focusout(self, event):
        event.widget.destroy()

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
    file = ""
    def __init__(self, parent):
        super().__init__(parent)
        self.searchbox = Entry(parent)
        self.searchbox.pack(fill=X, side=TOP)
        self.searchbox.bind("<Return>", self.search_table)

        self.datatable = Table(parent)
        self.datatable.pack(fill=BOTH, expand=True, side=TOP)

    def savefile(self, *wargs):
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
            for pair in split(",|;|/", entry):  # type: ignore
                pair_split = pair.split("=")
                if len(pair_split) == 2:
                    col = pair_split[0]
                    if col in self.datatable.stored_dataframe.columns:
                        filter[col] = pair_split[1]
            self.datatable.find_value(pairs=filter)
    
    def show_stats(self, column="Global"):
        if column == "Global":
            stats = {
                "Nombre de lignes": len(self.datatable.stored_dataframe),
                "Nombre de colonnes": len(self.datatable.stored_dataframe.columns),
            }
        else:
            stats = dict(self.datatable.stored_dataframe[column].value_counts())
        message = ""
        for key, value in stats.items():
            message += f"{key}: {value}\n"
        showinfo(title=f"Colonne: {column}", message=message)


App()
