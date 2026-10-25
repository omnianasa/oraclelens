import getpass
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OracleLensConfig:
    user: str
    password: str
    dsn: str

    # @classmethod
    # def from_env(cls) -> "OracleLensConfig":
    #     return cls(
    #         user=os.getenv("ORACLE_USER", "").strip(),
    #         password=os.getenv("ORACLE_PASSWORD", ""),
    #         dsn=os.getenv("ORACLE_DSN", "").strip(),
    #     )

    @classmethod
    def from_prompt(cls) -> "OracleLensConfig":
        print("\nEnter your Oracle Database credentials.\n")

        user = input("Oracle username: ").strip()
        password = getpass.getpass("Oracle password: ")

        default_dsn = "localhost:8521/FREEPDB1"
        dsn = input(
            f"Oracle DSN [{default_dsn}]: "
        ).strip()

        if not dsn:
            dsn = default_dsn

        config = cls(
            user=user,
            password=password,
            dsn=dsn,
        )

        config.validate()
        return config

    def validate(self) -> None:
        missing = []

        if not self.user:
            missing.append("username")
        if not self.password:
            missing.append("password")
        if not self.dsn:
            missing.append("DSN")

        if missing:
            raise ValueError(
                "Missing required connection fields: "
                + ", ".join(missing)
            )