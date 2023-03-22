import tkinter as tk
from tkinter import ttk

from chessengine import Chess
from dbmanager import ChessDatabase


class ChessGUI:
    """Responsible for handling the Tkinter GUI."""
    def __init__(self):
        self.init_window = tk.Tk()
        self.init_window.geometry("220x250")

        # Handling white's widgets.
        white_label = tk.Label(self.init_window, text="White", font=("CAD:", 20))
        white_label.grid(row=0, column=0)

        white_frame = tk.Frame(self.init_window)
        white_frame.grid(row=1, column=0)
        white_name = tk.Label(white_frame, text="Name: ")
        white_name.grid(row=0, column=0)
        self.white_name_entry = tk.Entry(white_frame)
        self.white_name_entry.grid(row=0, column=1)
        white_elo = tk.Label(white_frame, text="ELO: ")
        white_elo.grid(row=1, column=0)
        self.white_elo_entry = tk.Entry(white_frame)
        self.white_elo_entry.grid(row=1, column=1)
        
        # Handling blacks widgets.
        black_label = tk.Label(self.init_window, text="Black", font=("CAD:", 20))
        black_label.grid(row=2, column=0)

        black_frame = tk.Frame(self.init_window)
        black_frame.grid(row=3, column=0)
        black_name = tk.Label(black_frame, text="Name: ")
        black_name.grid(row=0, column=0)
        self.black_name_entry = tk.Entry(black_frame)
        self.black_name_entry.grid(row=0, column=1)
        black_elo = tk.Label(black_frame, text="ELO: ")
        black_elo.grid(row=1, column=0)
        self.black_elo_entry = tk.Entry(black_frame)
        self.black_elo_entry.grid(row=1, column=1)

        err = "Names should be between 1 and 20\ncharacters long, and ELO ratings\nmust be " + \
              "be integers between 1 and 5000."
        self.invalid_data_label = tk.Label(self.init_window, foreground="#F0F0F0", text=err)
        self.invalid_data_label.grid(row=4, column=0)

        # Buttons.
        button_frame = tk.Frame(self.init_window)
        button_frame.grid(row = 5, column=0)

        start_game_button = tk.Button(button_frame, text="Start Game", command=self.start_chess_game)
        start_game_button.grid(row=0, column=0)

        view_database_button = tk.Button(button_frame, text="View Database", command=self.view_database)
        view_database_button.grid(row=0, column=1)

        quit_button = tk.Button(button_frame, text="Quit", command=self.init_window.destroy)
        quit_button.grid(row=0, column=2)

        self.init_window.mainloop()

    def start_chess_game(self):
        """Starts the chess game, if the details entered are valid."""
        w_name = self.white_name_entry.get().strip()
        w_elo = self.white_elo_entry.get().strip()
        b_name = self.black_name_entry.get().strip()
        b_elo = self.black_elo_entry.get().strip()

        if len(w_name) == 0 or len(w_name) > 20 or len(b_name) == 0 or len(b_name) > 20 or \
           not w_elo.isdigit() or not b_elo.isdigit():
            self.invalid_data_label.configure(fg="red")
            return

        if int(w_elo) < 1 or int(w_elo) > 5000 or int(b_elo) < 1 or int(b_elo) > 5000:
            self.invalid_data_label.configure(fg="red")
            return

        self.init_window.destroy()

        chess = Chess()
        chess.display_users(w_name, w_elo, b_name, b_elo)
        chess.start_game()

    def view_database(self):
        view_database_window = tk.Tk()
        view_database_window.geometry("700x300")

        table_frame = tk.Frame(view_database_window)
        table_frame.pack()

        scroll_bar = tk.Scrollbar(table_frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        table = ttk.Treeview(table_frame, yscrollcommand=scroll_bar.set)
        table.pack()

        scroll_bar.config(command=table.yview)

        table['columns'] = ('game_id', 'w_name', 'w_elo', 'b_name', 'b_elo', 'winner', 'moves')

        table.column("#0", width=0, stretch=tk.NO)
        table.column("game_id", anchor=tk.CENTER, width=30)
        table.column("w_name", anchor=tk.CENTER, width=120)
        table.column("w_elo", anchor=tk.CENTER, width=80)
        table.column("b_name", anchor=tk.CENTER, width=120)
        table.column("b_elo", anchor=tk.CENTER, width=80)
        table.column("winner", anchor=tk.CENTER, width=80)
        table.column("moves", anchor=tk.CENTER, width=170)

        table.heading("#0", text="", anchor=tk.CENTER)
        table.heading("game_id", text="ID", anchor=tk.CENTER)
        table.heading("w_name", text="White's name", anchor=tk.CENTER)
        table.heading("w_elo", text="While's ELO", anchor=tk.CENTER)
        table.heading("b_name", text="Black's Name", anchor=tk.CENTER)
        table.heading("b_elo", text="Black's ELO", anchor=tk.CENTER)
        table.heading("winner", text="Winner", anchor=tk.CENTER)
        table.heading("moves", text="Moves played", anchor=tk.CENTER)

        db = ChessDatabase()
        games = db.get_entries()
        db.close()
        for i, game in enumerate(games):
            moves = game[6].split("\n")[0] + ".."
            table.insert(parent='', index='end', iid=i, text='',
                         values=(game[0], game[1], game[2], game[3], game[4],
                                 game[5], moves))

        table.pack()

        enter_game_id_label = tk.Label(view_database_window, text='Enter game ID to view the full list of moves:')
        enter_game_id_label.pack()
        game_id_entry = tk.Entry(view_database_window)
        game_id_entry.pack()
        view_moves_button = tk.Button(view_database_window, text='View',
                                      command=lambda : self.view_moves_of_game(game_id_entry.get()))
        view_moves_button.pack()

        view_database_window.mainloop()

    def view_moves_of_game(self, game_id: str):
        if not game_id.isdigit():
            return

        db = ChessDatabase()
        games = db.get_entries()
        db.close()

        game_id = int(game_id)
        found = False
        for game in games:
            if game_id == game[0]:
                found = True
                break

        if not found:
            return

        text = game[6] + "\n" + "WINNER: " + game[5]

        view_moves_window = tk.Tk()
        view_moves_window.geometry("250x400")

        moves_label = tk.Label(view_moves_window, text=text)
        moves_label.pack()

        view_moves_window.mainloop()
