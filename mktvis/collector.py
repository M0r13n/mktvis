

import ipaddress
import typing
import geoip2.errors
import geoip2.models

from mktvis.connection import MaxMindDatabaseConnection, RouterConnection


def is_private(ip: str) -> bool:
    """True if an IP is private else False"""
    return ipaddress.ip_address(ip).is_private


class GeoIPExporter:
    """
    Utilize the IPInfoConnection in order to collect relevant GeoIP data.
    """

    def __init__(self, conn: MaxMindDatabaseConnection) -> None:
        self.datasource = conn

    def get_city(self, ip: str) -> typing.Optional[geoip2.models.City]:
        try:
            city = self.datasource.city_reader.city(ip)
            return city
        except geoip2.errors.AddressNotFoundError:
            pass
        return None

    def get_asn(self, ip: str) -> typing.Optional[geoip2.models.ASN]:
        try:
            asn = self.datasource.asn_reader.asn(ip)
            return asn
        except geoip2.errors.AddressNotFoundError:
            pass
        return None

    def get_batch_data(self, ips: typing.Generator[str, None, None]) -> typing.Dict[str, typing.Any]:
        """
        Takes a generator of IPs (str) and gets the GeoIP data for every IP.
        This method executes a batch request to IPInfo -> single HTTP request.
        Also the IPInfoConnection implements caching by itself (LRU in memory).
        """

        results = {}

        for ip in ips:
            city = self.get_city(ip)
            asn = self.get_asn(ip)

            if city:
                results[ip] = {
                    'ip': ip,
                    'latitude': city.location.latitude,
                    'longitude': city.location.longitude,
                    'city': city.city.names['en'] if 'en' in city.city.names else 'n.a.',
                    'org': asn.autonomous_system_organization if asn else None
                }

        return results


class ConnectionExporter:
    """
    Utilize the RouterConnection in order to export all currently
    open connections.
    """

    def __init__(self, conn: RouterConnection) -> None:
        self._router_connection = conn

    def get_connections(self) -> typing.List[typing.Dict[str, typing.Any]]:
        """Get all open connection from Mikrotik Routerboard"""
        return typing.cast(
            typing.List[typing.Dict[str, typing.Any]],
            self._router_connection.router_api.get_resource('/ip/firewall/connection').get()

        )

    def get_remote_connections(self) -> typing.Generator[str, None, None]:
        """Get all open connections that are not limited to the local subnet"""
        for conn in self.get_connections():
            # Remove ports from addresses (NAT)
            src = conn['src-address'].split(':')[0]
            dst = conn['dst-address'].split(':')[0]

            # Ignore network local connection between clients in the same subnet
            if is_private(src) and is_private(dst):
                continue

            # Local host --> remote host
            if is_private(src):
                yield dst
            else:
                # Remote host --> local host
                # Due to firewall rules this might be impossible
                yield src


class ConnectionsCollector:
    """
    Merges connection data and GeoIP data
    """

    def __init__(self) -> None:
        # Initially the exporters are None
        self._conn_exp: typing.Optional[ConnectionExporter] = None
        self._ip_exp: typing.Optional[GeoIPExporter] = None

    def init(self, router_conn: RouterConnection, ip_info_conn: MaxMindDatabaseConnection) -> None:
        """Inject Exporter connections"""
        self._conn_exp = ConnectionExporter(router_conn)
        self._ip_exp = GeoIPExporter(ip_info_conn)

    @property
    def conn_exp(self) -> ConnectionExporter:
        if self._conn_exp is None:
            raise ValueError('ConnectionExporter not set. Call .init(...) first')
        return self._conn_exp

    @property
    def ip_exp(self) -> GeoIPExporter:
        if self._ip_exp is None:
            raise ValueError('GeoIPExporter not set. Call .init(...) first')
        return self._ip_exp

    def collect(self) -> typing.List[typing.Dict[str, typing.Any]]:
        """Collect connection data incl. GeoIP data"""
        destination_ips = self.conn_exp.get_remote_connections()
        geo_data = self.ip_exp.get_batch_data(destination_ips)

        result = []
        for ip, geo_details in geo_data.items():
            # While lat/lon keys are always present in the geo details dict,
            # org and city might raise a KeyError. Therefore, .get() is used
            result.append(
                {
                    'ip': ip,
                    'lat': geo_details['latitude'],
                    'lon': geo_details['longitude'],
                    'org': geo_details.get('org'),
                    'city': geo_details.get('city'),
                }
            )

        return result


COLLECTOR = ConnectionsCollector()
