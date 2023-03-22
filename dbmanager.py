import sqlite3 as sql


class ChessDatabase:
    def __init__(self):
        self.con = sql.connect('games.db')
        self.cur = self.con.cursor()

        create_table = """
                        CREATE TABLE IF NOT EXISTS games (
                            id integer PRIMARY KEY,
                            w_name text NOT NULL,
                            w_elo text NOT NULL,
                            b_name text NOT NULL,
                            b_elo text NOT NULL,
                            winner text NOT NULL,
                            moves text NOT NULL);
                       """

        self.query(create_table)

    def get_entries(self):
        return self.query("SELECT * FROM games;")

    def add_entry(self, w_name, w_elo, b_name, b_elo, winner, moves):
        if not self.get_entries():
            game_id = 1
        else:
            game_id = self.query("SELECT max(id) FROM games;")[0][0] + 1
        command = f"""
                    INSERT INTO games
                    (id, w_name, w_elo, b_name, b_elo, winner, moves) 
                    VALUES 
                    ({game_id}, '{w_name}', '{w_elo}', '{b_name}', '{b_elo}', '{winner}', '{moves}');
                  """

        self.query(command)

    def del_entry(self, game_id):
        self.query(f"DELETE FROM games WHERE id={game_id}")

    def query(self, command):
        self.cur.execute(command)
        return self.cur.fetchall()

    def save(self):
        self.con.commit()

    def close(self):
        self.con.close()


if __name__ == "__main__":
    db = ChessDatabase()
    print(db.get_entries())
