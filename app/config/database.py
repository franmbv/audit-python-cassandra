from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging

logger = logging.getLogger("cassandra")

class CassandraConfig:
    def __init__(self):
        self.cluster = None
        self.session = None
        self.keyspace = "museo_auditoria"

    def conectar(self):
        """Inicializa los cables de conexión hacia el contenedor de Docker"""
        try:
            # 1. Apuntamos al localhost y al puerto estándar que configuraste en Docker
            self.cluster = Cluster(['127.0.0.1'], port=9042)
            
            # 2. Abrimos la sesión de comunicación global
            self.session = self.cluster.connect()
            
            # 3. Creamos el Keyspace (la base de datos) de forma automatizada si no existe
            self.session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
                WITH replication = {{
                    'class': 'SimpleStrategy',
                    'replication_factor': 1
                }}
            """)
            
            # 4. Le decimos a la sesión que use este Keyspace por defecto para todas las consultas futuras
            self.session.set_keyspace(self.keyspace)
            print(f"[Cassandra] Conexión establecida con éxito en el keyspace: '{self.keyspace}'")
            
        except Exception as e:
            logger.error(f"Error crítico al conectar con Apache Cassandra en Docker: {e}")
            raise e

    def cerrar(self):
        """Cierra los sockets de red de forma limpia al apagar el servidor"""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        print("[Cassandra] Conexiones cerradas de forma segura.")

conexion_cassandra = CassandraConfig()