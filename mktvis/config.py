import pathlib
import typing
import yaml

_KEYS = (
    'maxmind_license_key',
    'routerboard_address',
    'routerboard_user',
    'routerboard_password',
    'routerboard_use_ssl',
    'routerboard_ssl_certificate_verify',
    'routerboard_ssl_certificate_path',
    'routerboard_port',
    'listen_port',
    'city_db_path',
    'asn_db_path',

)


class UnknownConfigurationKeyError(Exception):
    """Raised when the config loader encounters an unknown key"""

    def __init__(self, key: str) -> None:
        super().__init__(f'Unknown configuration key \'{key}\'')

        self.key = key


class MissingConfigurationKey(Exception):
    """Raised when the config has missing required keys"""

    def __init__(self, key: str) -> None:
        super().__init__(f'Missing configuration key \'{key}\'')

        self.key = key


class ConfigurationValueError(ValueError):
    """Raised when the configuration value is not atomic"""


def is_atomic(val: typing.Any) -> bool:
    if val is None:
        return True

    if isinstance(val, str):
        return True

    if isinstance(val, int):
        return True

    return False


class MKTVISConfig:

    LISTEN_PORT: int

    ROUTERBOARD_ADDRESS: str
    ROUTERBOARD_PORT: str
    ROUTERBOARD_USER: str
    ROUTERBOARD_PASSWORD: str
    ROUTERBOARD_USE_SSL: str
    ROUTERBOARD_SSL_CERTIFICATE_VERIFY: str
    ROUTERBOARD_SSL_CERTIFICATE_PATH: str

    CITY_DB_PATH: str
    ASN_DB_PATH: str

    def __init__(self, key_value_dict: typing.Dict[str, typing.Any]) -> None:
        self._key_value_dict = key_value_dict

        missing = self.missing_keys
        if missing:
            raise MissingConfigurationKey(missing.pop())

    @property
    def missing_keys(self) -> typing.Set[str]:
        return set(_KEYS).difference(set(self._key_value_dict.keys()))

    def __str__(self) -> str:
        return str(self._key_value_dict)

    def __getattr__(self, __name: str) -> typing.Any:
        key = __name.lower()
        return self._key_value_dict[key]

    @classmethod
    def from_dict(cls, dict_obj: typing.Dict[str, typing.Any]) -> 'MKTVISConfig':
        key_value_dict = {k: None for k in _KEYS}
        for key, val in dict_obj.items():
            if key not in _KEYS:
                raise UnknownConfigurationKeyError(key)

            if not is_atomic(val):
                raise ConfigurationValueError(val)

            key_value_dict[key] = val

        return cls(key_value_dict)

    @classmethod
    def load(cls, fpath: str) -> 'MKTVISConfig':
        path: pathlib.Path = pathlib.Path(fpath)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(
                f'{fpath} not found or not readable by application')

        with open(fpath, 'r') as fd:
            yaml_dict = yaml.safe_load(fd)
            return cls.from_dict(yaml_dict)
