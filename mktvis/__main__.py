from mktvis.collector import COLLECTOR
from mktvis.config import MKTVISConfig
from mktvis.connection import IPInfoConnection, RouterConnection
from mktvis.server import ExportProcessor


def main() -> None:
    # Create and init all instances that need to access the config
    # The actual instances are decoupled from the config object
    # Therefore, these need to be instantiated individually
    config = MKTVISConfig.load('/etc/mktvis/config.yml')
    router_conn = RouterConnection.from_config(config)
    ipinfo_conn = IPInfoConnection.from_config(config)

    COLLECTOR.init(router_conn, ipinfo_conn)

    # This start the server which collects connection data on demand
    ExportProcessor.run(port=config.LISTEN_PORT)


if __name__ == '__main__':
    main()
