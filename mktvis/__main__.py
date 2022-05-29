from mktvis.collector import COLLECTOR
from mktvis.config import MKTVISConfig
from mktvis.connection import IPInfoConnection, RouterConnection
from mktvis.server import ExportProcessor


def main():
    config = MKTVISConfig.load('default.yml')
    router_conn = RouterConnection.from_config(config)
    ipinfo_conn = IPInfoConnection.from_config(config)

    COLLECTOR.init(router_conn, ipinfo_conn)
    ExportProcessor.run(port=8080) #TODO

if __name__ == '__main__':
    main()