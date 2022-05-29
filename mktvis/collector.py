from mktvis.connection import RouterConnection


class GeoIPExporter:

    def __init__(self, conn) -> None:
        self._ip_info_conn = conn

    def get_batch_data(self, ips):
        return self._ip_info_conn.ipinfo_api.getBatchDetails(ips)


class ConnectionExporter:

    def __init__(self, conn) -> None:
        self._router_connection = conn

    def get_connections(self):
        return self._router_connection.router_api.get_resource('/ip/firewall/connection').get()

    def get_destinations(self):
        return [conn['dst-address'].split(':')[0] for conn in self.get_connections()]


class ConnectionsCollector:

    def __init__(self) -> None:
        self.cache = {}
        self.conn_exp = None

    def init(self, router_conn, ip_info_conn):
        self.conn_exp = ConnectionExporter(router_conn)
        self.ip_exp = GeoIPExporter(ip_info_conn)

    def collect(self):
        destination_ips = self.conn_exp.get_destinations()
        geo_data = self.ip_exp.get_batch_data(destination_ips)
        result = []

        for ip, geo_details in geo_data.items():
            result.append(
                {'ip': ip, 'lat': geo_details['latitude'],
                    'lon': geo_details['longitude']}
            )

        return result


COLLECTOR = ConnectionsCollector()
