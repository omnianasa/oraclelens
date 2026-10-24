import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OracleLensConfig:
    user: str
    password: str
    dsn: str

    @classmethod
    def from_env(cls) -> "OracleLensConfig":
        return cls(
            user=os.getenv("ORACLE_USER", "").strip(),
            password=os.getenv("ORACLE_PASSWORD", ""),
            dsn=os.getenv("ORACLE_DSN", "").strip(),
        )

    def validate(self) -> None:
        missing = []

        if not self.user:
            missing.append("ORACLE_USER")
        if not self.password:
            missing.append("ORACLE_PASSWORD")
        if not self.dsn:
            missing.append("ORACLE_DSN")

        if missing:
            raise ValueError(
                "Missing environment variables: "
                + ", ".join(missing)
            )