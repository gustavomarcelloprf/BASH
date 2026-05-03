"""
Cria um usuário no banco de dados via linha de comando.
Uso: python scripts/create_user.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from getpass import getpass
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.user import User
from app.routers.auth import hash_password


def main():
    create_db_and_tables()

    print("=== Criar novo usuário ===")
    name = input("Nome: ").strip()
    email = input("Email: ").strip()
    password = getpass("Senha: ")

    if not name or not email or not password:
        print("Todos os campos são obrigatórios.")
        sys.exit(1)

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            print(f"Erro: já existe um usuário com o email '{email}'.")
            sys.exit(1)

        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="member",
        )
        session.add(user)
        session.commit()

    print(f"Usuário {name} criado com sucesso.")


if __name__ == "__main__":
    main()
