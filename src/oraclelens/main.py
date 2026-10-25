from oraclelens.app import OracleLensApplication

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def main() -> None:
    app = OracleLensApplication()
    app.run()


if __name__ == "__main__":
    main()