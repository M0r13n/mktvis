from mktvis.collector import COLLECTOR
from mktvis.config import MKTVISConfig
from mktvis.connection import MaxMindDatabaseConnection, RouterConnection
from mktvis.server import ExportProcessor


def main() -> None:
    # Create and init all instances that need to access the config
    # The actual instances are decoupled from the config object
    # Therefore, these need to be instantiated individually
    config = MKTVISConfig.load('/etc/mktvis/config.yml')

    with RouterConnection.from_config(config) as router_conn, MaxMindDatabaseConnection.from_config(config) as maxmind_conn:
        COLLECTOR.init(router_conn, maxmind_conn)  # type:ignore

        # This start the server which collects connection data on demand
        ExportProcessor.run(port=config.LISTEN_PORT)


if __name__ == '__main__':
    main()
