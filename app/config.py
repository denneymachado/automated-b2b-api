from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Carrega credenciais do .env
load_dotenv()

class Settings(BaseSettings):
    database_name: str = os.getenv("DATABASE_NAME")
    database_user: str = os.getenv("DATABASE_USER")
    database_password: str = os.getenv("DATABASE_PASSWORD")
    database_host: str = os.getenv("DATABASE_HOST")
    database_port: int = int(os.getenv("DATABASE_PORT"))

    ftp_b2c_host: str = os.getenv("FTP_B2C_HOST")
    ftp_b2c_user: str = os.getenv("FTP_B2C_USER")
    ftp_b2c_password: str = os.getenv("FTP_B2C_PASSWORD")

    ftp_b2b_host: str = os.getenv("FTP_B2B_HOST")
    ftp_b2b_user: str = os.getenv("FTP_B2B_USER")
    ftp_b2b_password: str = os.getenv("FTP_B2B_PASSWORD")

    ftp_directory: str = os.getenv("FTP_DIRECTORY")

    authcode: str = os.getenv("AUTHCODE")

settings = Settings()
