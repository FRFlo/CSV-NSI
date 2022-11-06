from csv import writer # Permet d'écrire dans un fichier csv
from functools import partial # Permet de créer une fonction partielle (voir plus bas)
from pandas import DataFrame, read_csv # Mode de gestion de données et lecture de fichiers csv
from re import split # Permet de découper une chaîne de caractères selon un motif
from tkinter import BOTH, END, TOP, X, Frame, Menu, Scrollbar, Tk # Permet de créer une interface graphique et de gérer les menus
from tkinter.filedialog import askopenfilename # Permet d'ouvrir une fenêtre de dialogue pour choisir un fichier
from tkinter.messagebox import showinfo # Permet d'afficher une fenêtre de dialogue avec un message
from tkinter.simpledialog import askstring # Permet d'afficher une fenêtre de dialogue avec une zone de saisie
from tkinter.ttk import Entry, Treeview # Permet de créer des widgets graphiques


class App(Tk): # Création de la classe App qui hérite de la classe Tk
    def __init__(self): # Constructeur de la classe App
        super().__init__() # Appel du constructeur de la classe mère
        self.title("CSV-NSI") # Définition du titre de la fenêtre
        self.geometry("1280x720") # Définition de la taille de la fenêtre
        self.minsize(1280, 720) # Définition de la taille minimale de la fenêtre
        self.maxsize(1920, 1080) # Définition de la taille maximale de la fenêtre
        self.iconbitmap("assets/icon.ico") # Définition de l'icône de la fenêtre
        self.protocol("WM_DELETE_WINDOW", self.quit) # Définition de la fonction à appeler lors de la fermeture de la fenêtre
        self.main_frame = Frame(self) # Création d'un widget Frame
        self.main_frame.pack(fill=BOTH, expand=True) # Placement du widget Frame
        self.main_frame.config(background="#36393F") # Définition de la couleur de fond du widget Frame

        self.page = Page(self.main_frame) # Création d'un widget Page
        self.bind("<Control-s>", self.page.savefile) # Définition de la fonction à appeler lors de l'appui sur Ctrl+S

        self.barmenu = Menu(self) # Création d'un widget Menu
        filemenu = Menu(self.barmenu, tearoff=0) # Création d'un sous-menu
        filemenu.add_command(label="Ouvrir", command=self.choosefile) # Ajout d'une commande au sous-menu
        filemenu.add_command(label="Ouvrir via une URL", command=self.chooseremotefile) # Ajout d'une commande au sous-menu
        filemenu.add_command(label="Sauvegarder", command=self.page.savefile) # Ajout d'une commande au sous-menu
        filemenu.add_separator() # Ajout d'un séparateur au sous-menu
        filemenu.add_command(label="Quitter", command=self.quit) # Ajout d'une commande au sous-menu
        self.barmenu.add_cascade(label="Fichier", menu=filemenu) # Ajout du sous-menu au menu principal
        self.statsmenu = Menu(self.barmenu, tearoff=0) # Création d'un sous-menu
        self.statsmenu.add_command(label="Stats générales", command=self.page.show_stats) # Ajout d'une commande au sous-menu
        self.statsmenu.add_separator() # Ajout d'un séparateur au sous-menu
        self.barmenu.add_cascade(label="Statistiques", menu=self.statsmenu) # Ajout du sous-menu au menu principal

        self.config(menu=self.barmenu) # Définition du menu de la fenêtre

        self.mainloop() # Boucle principale de la fenêtre

    def choosefile(self, file=None): # Fonction permettant d'ouvrir un fichier csv
        self.page.file = file or askopenfilename( # Définition du chemin du fichier
            title="Ouvrir un fichier CSV", # Titre de la fenêtre de dialogue
            filetypes=[ # Types de fichiers autorisés
                ("Fichier CSV", "*.csv"), # Fichier CSV
                ("Fichiers TXT", "*.txt"), # Fichier TXT
                ("Tous les fichiers", "*.*"), # Tous les fichiers
            ],
        ) # On ferme la fonction askopenfilename
        if not self.page.file: # Si le chemin du fichier est vide
            return # On arrête la fonction
        self.page.datatable.set_datatable( # On définit la DataTable du widget Page
            read_csv( # On lit le fichier csv
                self.page.file, delimiter=";", encoding="utf-8", low_memory=False, nrows=100000 # On définit les paramètres de lecture
            ) # On ferme la fonction read_csv
        ) # On ferme la fonction set_datatable

        self.statsmenu.delete(2, END) # On supprime les anciennes commandes du sous-menu

        for column in self.page.datatable.stored_dataframe.columns: # Pour chaque colonne du DataFrame
            self.statsmenu.add_command(label=column, command=partial(self.page.show_stats, column)) # On ajoute une commande au sous-menu
    
    def chooseremotefile(self): # Fonction permettant d'ouvrir un fichier csv à partir d'une URL
        url = askstring("Ouvrir un fichier CSV", "URL du fichier CSV") # On demande à l'utilisateur l'URL du fichier
        self.choosefile(url) # On appelle la fonction choosefile avec l'URL du fichier en paramètre


class Table(Treeview): # Création de la classe Table qui hérite de la classe Treeview
    def __init__(self, parent): # Constructeur de la classe Table
        super().__init__(parent) # Appel du constructeur de la classe mère
        scroll_Y = Scrollbar(self, orient="vertical", command=self.yview) # Création d'un widget Scrollbar
        scroll_X = Scrollbar(self, orient="horizontal", command=self.xview) # Création d'un widget Scrollbar
        self.configure(yscrollcommand=scroll_Y.set, xscrollcommand=scroll_X.set) # Définition des Scrollbar de la Table
        scroll_Y.pack(side="right", fill="y") # Placement du widget Scrollbar
        scroll_X.pack(side="bottom", fill="x") # Placement du widget Scrollbar
        self.stored_dataframe = DataFrame() # Définition du DataFrame

        self.line_menu = Menu(self, tearoff=0) # Création d'un widget Menu
        self.line_menu.add_command(label="Insérer une ligne en dessous", command=self.insert_line) # Ajout d'une commande au menu
        self.line_menu.add_command(label="Supprimer", command=self.delete_selected) # Ajout d'une commande au menu

        self.context_menu = Menu(self, tearoff=0) # Création d'un widget Menu
        self.context_menu.add_command(label="Insérer une ligne", command=self.insert_line) # Ajout d'une commande au menu
        self.bind("<Button-3>", self._popup) # Définition de la fonction à appeler lors du clic droit
        self.bind("<Double-Button-1>", self._edit_cell) # Définition de la fonction à appeler lors du double clic gauche

    def insert_line(self): # Fonction permettant d'insérer une ligne dans la Table
        self.insert("", "end", values=[""] * len(self.stored_dataframe.columns)) # On insère une ligne vide à la fin de la Table

    def delete_selected(self): # Fonction permettant de supprimer une ligne de la Table
        selected = self.selection() # On récupère la ligne sélectionnée
        for item in selected: # Pour chaque ligne sélectionnée
            self.delete(item) # On supprime la ligne

    def set_datatable(self, dataframe): # Fonction permettant de définir la DataTable de la Table
        self.stored_dataframe = dataframe # On définit le DataFrame
        self._draw_table(dataframe) # On appelle la fonction _draw_table

    def _draw_table(self, dataframe): # Fonction permettant de dessiner la Table
        self.delete(*self.get_children()) # On supprime les anciennes lignes de la Table
        columns = list(dataframe.columns) # On récupère les noms des colonnes du DataFrame
        self.__setitem__("column", columns) # On définit les colonnes de la Table
        self.__setitem__("show", "headings") # On définit l'affichage de la Table

        for col in columns: # Pour chaque colonne du DataFrame
            self.heading(col, text=col) # On définit le nom de la colonne

        df_rows = dataframe.to_numpy().tolist() # On récupère les lignes du DataFrame
        for row in df_rows: # Pour chaque ligne du DataFrame
            self.insert("", "end", values=row) # On insère la ligne dans la Table
        return None # On retourne None

    def _popup(self, event): # Fonction permettant d'afficher le menu contextuel
        match self.identify_region(event.x, event.y): # On vérifie la zone cliquée
            case "cell": # Si la zone cliquée est une cellule
                self.line_menu.post(event.x_root, event.y_root) # On affiche le menu contextuel
            case "heading": # Si la zone cliquée est une colonne
                self.context_menu.post(event.x_root, event.y_root) # On affiche le menu contextuel
            case _: # Si la zone cliquée est autre chose
                self.context_menu.post(event.x_root, event.y_root) # On affiche le menu contextuel

    def _edit_cell(self, event): # Fonction permettant d'éditer une cellule
        if self.identify_region(event.x, event.y) != "cell": # Si la zone cliquée n'est pas une cellule
            return # On arrête la fonction
        
        column = self.identify_column(event.x) # On récupère la colonne de la cellule
        column_index = int(column[1:]) -1 # On récupère l'index de la colonne
        selected_iid = self.focus() # On récupère l'identifiant de la ligne sélectionnée
        selected_values = self.item(selected_iid) # On récupère les valeurs de la ligne sélectionnée
        if column == "#0": # Si la colonne est la colonne des identifiants
            return # On arrête la fonction
        selected_text  = selected_values.get("values")[column_index] # On récupère le texte de la cellule
        column_box = self.bbox(selected_iid, column=column) # On récupère la position de la cellule

        entry_edit = Entry(self, width=column_box[2]) # On crée un widget Entry
        entry_edit.editing_column_index = column_index # On définit l'index de la colonne de l'Entry
        entry_edit.editing_item_iid = selected_iid # On définit l'identifiant de la ligne de l'Entry
        entry_edit.insert(0, selected_text) # On insère le texte de la cellule dans l'Entry
        entry_edit.select_range(0, END) # On sélectionne tout le texte de l'Entry
        entry_edit.focus() # On donne le focus à l'Entry pour pouvoir éditer le texte
        entry_edit.bind("<FocusOut>", self._edit_cell_focusout) # On définit la fonction à appeler lors de la perte du focus
        entry_edit.bind("<Escape>", self._edit_cell_focusout) # On définit la fonction à appeler lors de l'appui sur la touche Echap
        entry_edit.bind("<Return>", self._edit_cell_return) # On définit la fonction à appeler lors de l'appui sur la touche Entrée
        entry_edit.place(x=column_box[0], y=column_box[1], w= column_box[2], h=column_box[3]) # On place l'Entry dans la Table
    
    def _edit_cell_return(self, event): # Fonction permettant de valider l'édition d'une cellule
        new_text = event.widget.get() # On récupère le texte de l'Entry
        selected_iid = event.widget.editing_item_iid # On récupère l'identifiant de la ligne de l'Entry
        column_index = event.widget.editing_column_index # On récupère l'index de la colonne de l'Entry

        if column_index != -1: # Si l'index de la colonne est différent de -1
            current_values = self.item(selected_iid).get("values") # On récupère les valeurs de la ligne sélectionnée
            current_values[column_index] = new_text # On modifie la valeur de la cellule
            self.item(selected_iid, values=current_values) # On modifie les valeurs de la ligne sélectionnée
        
        event.widget.destroy() # On détruit l'Entry

    def _edit_cell_focusout(self, event): # Fonction permettant de valider l'édition d'une cellule
        event.widget.destroy() # On détruit l'Entry

    def find_value(self, pairs): # Fonction permettant de trouver une valeur dans la Table
        new_df = self.stored_dataframe # On récupère le DataFrame de la Table
        for col, value in pairs.items(): # Pour chaque couple colonne/valeur
            query_string = f"{col}.str.contains('{value}')" # On crée la chaîne de caractères de la requête
            new_df = new_df.query(query_string, engine="python") # On effectue la requête
        self._draw_table(new_df) # On dessine la Table avec le DataFrame filtré

    def reset_table(self): # Fonction permettant de réinitialiser la Table
        self._draw_table(self.stored_dataframe) # On dessine la Table avec le DataFrame initial

    def add_element(self, row): # Fonction permettant d'ajouter une ligne à la Table
        self.insert("", "end", values=row) # On insère la ligne dans la Table


class Page(Frame): # Classe permettant de créer une page
    file = "" # Variable permettant de stocker le chemin du fichier
    def __init__(self, parent): # Fonction permettant d'initialiser la classe
        super().__init__(parent) # On appelle le constructeur de la classe parente
        self.searchbox = Entry(parent) # On crée un widget Entry
        self.searchbox.pack(fill=X, side=TOP) # On place le widget Entry dans la page
        self.searchbox.bind("<Return>", self.search_table) # On définit la fonction à appeler lors de l'appui sur la touche Entrée

        self.datatable = Table(parent) # On crée un widget Table
        self.datatable.pack(fill=BOTH, expand=True, side=TOP) # On place le widget Table dans la page

    def savefile(self, *wargs): # Fonction permettant de sauvegarder le fichier
        with open(self.file, "w", newline="") as file: # On ouvre le fichier en mode écriture
            csvwriter = writer(file, delimiter=";") # On crée un objet csvwriter permettant d'écrire dans le fichier
            csvwriter.writerow(self.datatable.stored_dataframe.columns) # On écrit les noms des colonnes dans le fichier
            for row_id in self.datatable.get_children(): # Pour chaque identifiant de ligne
                row = self.datatable.item(row_id)["values"] # On récupère les valeurs de la ligne
                csvwriter.writerow(row) # On écrit les valeurs de la ligne dans le fichier

    def search_table(self, event): # Fonction permettant de rechercher une valeur dans la Table
        entry = self.searchbox.get() # On récupère le texte de l'Entry
        if entry == "": # Si le texte de l'Entry est vide
            self.datatable.reset_table() # On réinitialise la Table
        else: # Sinon
            filter = {} # On crée un dictionnaire vide
            for pair in split(",|;|/", entry): # Pour chaque couple colonne/valeur
                pair_split = pair.split("=") # On sépare la colonne de la valeur
                if len(pair_split) == 2: # Si la séparation a bien fonctionné
                    col = pair_split[0] # On récupère la colonne
                    if col in self.datatable.stored_dataframe.columns: # Si la colonne existe dans le DataFrame
                        filter[col] = pair_split[1] # On ajoute le couple colonne/valeur au dictionnaire
            self.datatable.find_value(pairs=filter) # On filtre la Table avec le dictionnaire
    
    def show_stats(self, column="Global"): # Fonction permettant d'afficher les statistiques
        if column == "Global": # Si la colonne est "Global"
            stats = { # On crée un dictionnaire contenant les statistiques
                "Nombre de lignes": len(self.datatable.stored_dataframe), # Nombre de lignes
                "Nombre de colonnes": len(self.datatable.stored_dataframe.columns), # Nombre de colonnes
            }
        else: # Sinon
            stats = dict(self.datatable.stored_dataframe[column].value_counts()) # On récupère les statistiques de la colonne
        message = "" # On crée une chaîne de caractères vide
        for key, value in stats.items(): # Pour chaque couple clé/valeur
            message += f"{key}: {value}\n" # On ajoute le couple clé/valeur à la chaîne de caractères
        showinfo(title=f"Colonne: {column}", message=message) # On affiche les statistiques


App() # On lance l'application
