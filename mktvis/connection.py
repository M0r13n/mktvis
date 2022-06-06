import abc
import ssl
import typing
import geoip2.database
import routeros_api

from mktvis.config import MKTVISConfig

BC = typing.TypeVar('BC', bound='BaseConnection')


class BaseConnection(metaclass=abc.ABCMeta):

    def __enter__(self) -> 'BaseConnection':
        return self

    def __exit__(self, *args: typing.Any) -> None:
        self.close()

    @abc.abstractmethod
    def close(self) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def from_config(cls: typing.Type[BC], config: MKTVISConfig) -> BC:
        pass


class MaxMindDatabaseConnection(BaseConnection):

    def __init__(self, city_db_path: str, asn_db_path: str) -> None:
        self.city_reader = geoip2.database.Reader(city_db_path)
        self.asn_reader = geoip2.database.Reader(asn_db_path)

    @classmethod
    def from_config(cls, config: MKTVISConfig) -> 'MaxMindDatabaseConnection':
        return cls(config.CITY_DB_PATH, config.ASN_DB_PATH)

    def close(self) -> None:
        self.city_reader.close()
        self.asn_reader.close()


class RouterConnection(BaseConnection):

    def __init__(self, host: str, username: str, password: str, port: typing.Union[str, int] = 8728,
                 use_ssl: bool = False, ssl_verify: bool = True,
                 ssl_verify_hostname: bool = True, ssl_cert_path: typing.Optional[str] = None) -> None:

        ssl_context = None
        if use_ssl:
            ssl_context = ssl.create_default_context(cafile=ssl_cert_path)

        if port and isinstance(port, str):
            port = int(port)

        self._connection = routeros_api.RouterOsApiPool(
            host,
            username=username,
            password=password,
            port=port,
            use_ssl=use_ssl,
            ssl_verify=ssl_verify,
            ssl_verify_hostname=ssl_verify_hostname,
            ssl_context=ssl_context,
            plaintext_login=True
        )

        self._api = self._connection.get_api()

    @classmethod
    def from_config(cls, config: MKTVISConfig) -> 'RouterConnection':
        return cls(
            config.ROUTERBOARD_ADDRESS,
            username=config.ROUTERBOARD_USER,
            password=config.ROUTERBOARD_PASSWORD,
            port=config.ROUTERBOARD_PORT,
            use_ssl=config.ROUTERBOARD_USE_SSL,  # type: ignore
            ssl_verify=config.ROUTERBOARD_SSL_CERTIFICATE_VERIFY,  # type: ignore
            ssl_cert_path=config.ROUTERBOARD_SSL_CERTIFICATE_PATH
        )

    @property
    def router_api(self) -> routeros_api.RouterOsApiPool:
        return self._api

    def close(self) -> None:
        del self._api
