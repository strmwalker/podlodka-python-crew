from pydantic import BaseSettings, PostgresDsn, SecretStr


class Settings(BaseSettings):
    db_protocol: str = 'postgresql+asyncpg'
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int

    def db_dsn(self, protocol=None) -> PostgresDsn:
        protocol = protocol or self.db_protocol
        return PostgresDsn.build(
            scheme=protocol,
            user=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=str(self.db_port),
            path=f'/{self.db_name}',
        )
