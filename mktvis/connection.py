import ssl
import typing
import ipinfo
import routeros_api

from mktvis.config import MKTVISConfig


class IPInfoConnection:

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token
        self._handler = ipinfo.getHandler(access_token)

    @classmethod
    def from_config(cls, config: MKTVISConfig) -> 'IPInfoConnection':
        return cls(
            config.IP_INFO_ACCESS_TOKEN
        )

    @property
    def ipinfo_api(self) -> ipinfo.Handler:
        return self._handler


class RouterConnection:

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
