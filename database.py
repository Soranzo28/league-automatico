import sqlite3

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise RuntimeError('Use Database.get_instance() instead of Database()')
        return super().__new__(cls)

    def __init__(self, path): 
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    @classmethod
    def get_instance(cls, path='lol.db'):
        if cls._instance is None:
            cls._instance = cls(path)
        return cls._instance

    def _create_tables(self):
        with self.conn:
            self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS champions(id INTEGER PRIMARY KEY, nome TEXT, nome_id TEXT, png_url TEXT);
            CREATE TABLE IF NOT EXISTS picks(id INTEGER PRIMARY KEY AUTOINCREMENT, champion_id INTEGER, prioridade INTEGER UNIQUE NOT NULL, lane TEXT, FOREIGN KEY (champion_id) REFERENCES champions(id));
            CREATE TABLE IF NOT EXISTS bans(id INTEGER PRIMARY KEY AUTOINCREMENT, champion_id INTEGER, prioridade INTEGER UNIQUE NOT NULL, FOREIGN KEY (champion_id) REFERENCES champions(id));
            CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY AUTOINCREMENT, version TEXT);
            CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL, value TEXT)
            """
            )
    def insert_version(self, version):
        with self.conn:
            self.conn.execute('INSERT INTO versions (version) VALUES (?)', (version,))

    def get_latest_version(self):
        cursor = self.conn.execute('SELECT version FROM versions ORDER BY versions.id DESC LIMIT 1')
        row = cursor.fetchone()
        return row['version'] if row else None 

    def insert_champion(self, id, nome, nome_id, png_url): 
        with self.conn:
            self.conn.execute('INSERT INTO champions VALUES (?, ?, ?, ?)', (id, nome, nome_id, png_url))

    def get_champion_by_name(self, nome): 
        cursor = self.conn.execute('SELECT * FROM champions WHERE nome LIKE ?', (nome,))
        return cursor.fetchone()

    def get_champion_by_id(self, id): 
        cursor = self.conn.execute('SELECT * FROM champions WHERE id = ?', (id, ))
        return cursor.fetchone()

    # picks

    def insert_pick(self, champion_id, prioridade, lane): 
        with self.conn:
            self.conn.execute('INSERT INTO picks (champion_id, prioridade, lane) VALUES (?, ?, ?)', (champion_id, prioridade, lane))

    def get_picks(self): 
        return self.conn.execute('SELECT * FROM picks ORDER BY picks.prioridade').fetchall()

    def get_picks_by_lane(self, lane):
        return self.conn.execute('SELECT * FROM picks WHERE picks.lane = ? ORDER BY picks.prioridade', (lane,)).fetchall()

    def update_pick_priority(self, champion_id, prioridade):
        prio_atual = self.conn.execute('SELECT prioridade FROM picks WHERE champion_id = ?', (champion_id,)).fetchone()[0]
        prio_trocar = self.conn.execute('SELECT champion_id FROM picks WHERE prioridade = ?', (prioridade,)).fetchone()[0]

        with self.conn:
            self.conn.execute('UPDATE picks SET prioridade = ? WHERE champion_id = ?', (prioridade, champion_id))
            self.conn.execute('UPDATE picks SET prioridade = ? WHERE champion_id = ?', (prio_atual, prio_trocar))

    def delete_pick(self, champion_id): 
        with self.conn:
            cursor = self.conn.execute('DELETE FROM picks WHERE champion_id = ?', (champion_id, ))
        return cursor.rowcount > 0

    # bans
    def insert_ban(self, champion_id, prioridade): 
        with self.conn:
            self.conn.execute('INSERT INTO bans (champion_id, prioridade) VALUES (?, ?)', (champion_id, prioridade))

    def get_bans(self):
        return self.conn.execute('SELECT * FROM bans ORDER BY bans.prioridade').fetchall()
        

    def update_ban_priority(self, champion_id, prioridade):
        prio_atual = self.conn.execute('SELECT prioridade FROM bans WHERE champion_id = ?', (champion_id,)).fetchone()[0]
        prio_trocar = self.conn.execute('SELECT champion_id FROM bans WHERE prioridade = ?', (prioridade,)).fetchone()[0]

        with self.conn:
            self.conn.execute('UPDATE bans SET prioridade = ? WHERE champion_id = ?', (prioridade, champion_id))
            self.conn.execute('UPDATE bans SET prioridade = ? WHERE champion_id = ?', (prio_atual, prio_trocar))
            
    def delete_ban(self, champion_id): 
        with self.conn:
            cursor = self.conn.execute('DELETE FROM bans WHERE champion_id = ?', (champion_id, ))
        return cursor.rowcount > 0


    # Utils
    def get_random_champion_id(self):
        return self.conn.execute('SELECT id FROM champions ORDER BY RANDOM() LIMIT 1').fetchone()['id']

    def get_all_champions(self):
        return self.conn.execute('SELECT * FROM champions ORDER BY nome_id').fetchall()

    # Settings
    def get_setting(self, key: str, default: str = '0') -> str:
        row = self.conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        with self.conn:
            self.conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))