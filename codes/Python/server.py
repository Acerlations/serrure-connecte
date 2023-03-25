import socket, threading, mysql.connector, pickle, random


class ThreadForClient(threading.Thread):
    """Thread qui se lance pour chaque client"""
    def __init__(self, conn, Network):
        threading.Thread.__init__(self)
        self.conn = conn
        self.Network = Network

    def run(self):
        while True:
            try:
                data = self.conn.recv(1024)
            except ConnectionResetError:  # Permet de fermer correctement le thread lors qu'un client se déconnecte
                break

            if not data: break  # Ou cas ou une donnée de donne rien on casse la boucle, dans ce cas ça peut être le client qui se déconnecte
	    
            data = pickle.loads(data) # On décode les données 
	    
            
            
            
            # A FAIRE






        self.conn.close()


class Network:
    """Class NetWork qui gere la pacerelle client/serveur"""
    def __init__(self, ip, port):
        self.ip = ip  # '' = localhost
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))

        self.database = DataBase("", "", "", "")


def start(self):
    """Boucle principale qui alloue un thread lors d'une connection au client"""

    while True:
        self.socket.listen()  # Le serveur est en "ecoute"
        conn, address = self.socket.accept()

        print("Un client se connecte")

        thread = ThreadForClient(conn, self)
        thread.start()


def sendData(self, data, conn):
    """Envoie des données au client donné"""
    data = pickle.dumps(data)
    conn.send(data)

def createCookie(self, conn, userid):
    """Creer un cookie et le met en lien avec l'utilisateur donné dans la base de donnée"""
    cookie = "".join([chr(random.randint(33, 126)) for _ in range(255)])

    request = "UPDATE users SET cookie = %s WHERE id = %s;"
    adr = (cookie, userid)
    self.database.execute(request, adr, commit=True)

    data = ["cookie", cookie]
    self.sendData(data, conn)

def login(self, conn, data):
    """Permet de s'identifier selon les données entré par l'utilisateur """
    username, password = data[2].lower(), data[3].lower()

    request = "SELECT password, id FROM users WHERE username = %s;"
    adr = (username, )
    result = self.database.execute(request, adr, "one")

    if result is None:
        data = ["error", "[ERREUR] Pseudo non existant"]
        self.sendData(data, conn)
        return

    if password == result[0]:  # Le mot de passe corresponds à celui de l'utilisateur donnée
        userid = result[1]
        self.createCookie(conn, userid)
    else:
        data = ["error", "[ERREUR] Mot de passe incorrect"]
        self.sendData(data, conn)
        return

def register(self, conn, data):
    """Permet a l'utilisateur de s'enregistrer"""
    username, password = data[2].lower(), data[3].lower()

    request = "SELECT count(username) FROM users WHERE username = %s;"
    adr = (username, )
    result = self.database.execute(request, adr, fetch="one")

    if int(result[0]) > 0: 
        data = ["error", "[ERREUR] Pseudo deja utilise"]
        self.sendData(data, conn)
        return

    request = "INSERT INTO users(username, password) VALUES (%s, %s);"
    adr = (username, password)
    userid = self.database.execute(request, adr, commit=True, getRowId=True)

    self.createCookie(conn, userid)


class DataBase:
    def __init__(self, host, user, password, database):
        """Objet Base donnée permet de se connecter à une base de donnée entré"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.DB = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password=  self.password,
            database = self.database)

    def execute(self, request, adr, fetch=None, commit=False, getRowId=False):
        """Permet d'executer une requete sql
            request (string) = requete sql
            adr (tuple) = les variables
            fetch (str) = one (on recupre la 1er ligne), all (tout les lignes)
            commit (bool) = sauvegarde les modifications avec un INSERT INTO ou UPDATE etc...
            getRowID (bool) = permet d'avoir la l'id de la ligne apres une modification ou un ajout
        """
        mycursor = self.DB.cursor()
        mycursor.execute(request, adr)

        if commit: self.DB.commit()

        if getRowId: return mycursor.lastrowid

        if fetch == "one": 
            return mycursor.fetchone()
        if fetch == "all": 
            return mycursor.fetchall()


Network = Network('', 59500)
Network.start()

