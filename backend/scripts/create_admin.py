"""
Cria ou promove um usuário admin no banco de dados.
Uso: python scripts/create_admin.py
"""
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from getpass import getpass
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.user import User
from app.routers.auth import hash_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def main():
    create_db_and_tables()

    print("=== Criar / Promover Admin ===")
    name = input("Nome completo: ").strip()
    email = input("Email: ").strip()

    if not EMAIL_RE.match(email):
        print("Formato de email inválido.")
        sys.exit(1)

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()

        if existing:
            if existing.role == "admin":
                print("já é admin.")
                sys.exit(0)

            # role == "member" — oferecer promoção
            answer = input(
                "Usuário já existe como member. Promover para admin? (s/N): "
            ).strip().lower()
            if answer != "s":
                print("Encerrado sem alteração.")
                sys.exit(0)

            existing.role = "admin"
            session.add(existing)
            session.commit()
            print(f"Usuário {existing.name} promovido para admin com sucesso.")
            sys.exit(0)

        # Novo usuário — coletar senha
        while True:
            password = getpass("Senha (mín. 8 caracteres): ")
            if len(password) < 8:
                print("A senha deve ter pelo menos 8 caracteres.")
                continue
            confirm = getpass("Confirme a senha: ")
            if password != confirm:
                print("senhas não conferem.")
                continue
            break

        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )
        session.add(user)
        session.commit()

    print(f"Admin {name} <{email}> criado com sucesso.")


if __name__ == "__main__":
    main()
