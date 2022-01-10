import typer

from db.deps import get_session
from schemas.user import UserCreateRequest
from services.user import user_service

user_cli = typer.Typer()


@user_cli.command("create_admin")
def create_admin_user(
    email: str = typer.Option("admin@mail.com", help="Default admin@mail.com."),
    full_name: str = typer.Option("admin", help="Default admin."),
    password: str = typer.Option("123456@abc", help="Default 123456@abcA"),
):
    session = next(get_session())
    flt = {
        "email": email,
        "full_name": full_name,
    }
    if user_service.is_exist(session, flt=flt):
        typer.secho(f"User Existed ", fg=typer.colors.RED)
        session.close()
        exit()
    user_obj = UserCreateRequest(email=email, password=password, full_name=full_name, is_superuser=True)
    user_service.create(session=next(get_session()), obj_in=user_obj)
    typer.secho(f"User create succeeded", fg=typer.colors.GREEN)
    session.close()
    exit()


if __name__ == "__main__":
    user_cli()
