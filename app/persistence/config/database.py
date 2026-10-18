import json
import logging
import os
from pathlib import Path
from typing import Optional

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, Session

logger = logging.getLogger("cassandra")


class CassandraDatabase:
    """
    Connection manager for Apache Cassandra and DataStax Astra DB.
    Enables environment-driven configuration with automatic fallback to local Docker.
    """

    def __init__(self):
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None
        self.keyspace = os.getenv("CASSANDRA_KEYSPACE", "museo_auditoria")
        self.host = os.getenv("CASSANDRA_HOST", "127.0.0.1")
        self.port = int(os.getenv("CASSANDRA_PORT", "9042"))
        self.username = os.getenv("CASSANDRA_USERNAME", None)
        self.password = os.getenv("CASSANDRA_PASSWORD", None)

        # Settings for DataStax Astra DB (Cloud)
        self.astra_token_path = os.getenv("ASTRA_DB_TOKEN_PATH", "cluster_museo_uneg-token.json")
        self.astra_bundle_path = os.getenv("ASTRA_DB_BUNDLE_PATH", "secure-connect-cluster-museo-uneg.zip")

    def _should_use_astra(self) -> bool:
        """Determines whether Astra DB credentials should be used based on file existence."""
        token_file = Path(self.astra_token_path)
        bundle_file = Path(self.astra_bundle_path)
        return token_file.is_file() and bundle_file.is_file()

    def conectar(self) -> Session:
        """Initializes connection to local Cassandra or DataStax Astra DB."""
        if self.session and not self.session.is_shutdown:
            return self.session

        try:
            if self._should_use_astra():
                logger.info("[Cassandra] Astra DB credentials detected. Connecting to cloud cluster...")
                with open(self.astra_token_path, "r", encoding="utf-8") as f:
                    secrets = json.load(f)

                client_id = secrets.get("clientId")
                client_secret = secrets.get("secret")
                auth_provider = PlainTextAuthProvider(client_id, client_secret)

                cloud_config = {"secure_connect_bundle": str(self.astra_bundle_path)}
                self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
                self.session = self.cluster.connect()
                self.session.set_keyspace(self.keyspace)
                logger.info("[Cassandra] Connected to DataStax Astra DB keyspace: '%s'", self.keyspace)
            else:
                logger.info("[Cassandra] Connecting to local/on-premise node at %s:%s...", self.host, self.port)
                auth_provider = None
                if self.username and self.password:
                    auth_provider = PlainTextAuthProvider(self.username, self.password)

                self.cluster = Cluster([self.host], port=self.port, auth_provider=auth_provider)
                self.session = self.cluster.connect()
                self.session.set_keyspace(self.keyspace)
                logger.info("[Cassandra] Connected to local node keyspace: '%s'", self.keyspace)

            return self.session

        except Exception as e:
            logger.error("[Cassandra] Critical connection error: %s", e)
            raise e

    def is_healthy(self) -> bool:
        """Checks if the active session can execute a simple health query."""
        if not self.session or self.session.is_shutdown:
            return False
        try:
            row = self.session.execute("SELECT release_version FROM system.local").one()
            return row is not None
        except Exception:
            return False

    def cerrar(self) -> None:
        """Safely shuts down the active Cassandra session and cluster."""
        if self.session and not self.session.is_shutdown:
            self.session.shutdown()
        if self.cluster and not self.cluster.is_shutdown:
            self.cluster.shutdown()
        logger.info("[Cassandra] Connection safely closed.")


# Singleton instance for application lifecycle
db_cassandra = CassandraDatabase()
