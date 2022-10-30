from werkzeug.security import generate_password_hash, check_password_hash
from sql_connector import User, db_session
import argparse as ap
import re

REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def _email_check(email):
    email_match = True if REGEX.match(email) else False
    return email_match


def parser_opt():
    parser = ap.ArgumentParser()
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        help="your TBG email address",
        required=True,
    )
    parser.add_argument(
        "-p", "--password", type=str, help="your password", required=True
    )
    parser.add_argument(
        "-m",
        "--method",
        default="insert",
        choices=["insert", "update", "delete"],
        help="insert, update or delete a user (default as insert)",
    )
    parser.add_argument("-a", "--admin", action=ap.BooleanOptionalAction)

    args = parser.parse_args()
    return args


def add_user(email, password, admin=False, method="insert"):

    if not _email_check(email):
        print("wrong email format")
        return

    admin = 1 if admin else 0
    users = db_session.query(User).all()
    users_dict = {}
    for u in users:
        users_dict[u.user_name] = {
            "password": u.password,
            "admin": u.admin,
        }

    if method == "insert":
        new_user = User(
            user_name=email,
            password=generate_password_hash(password),
            admin=admin,
        )
        db_session.add(new_user)
        db_session.commit()

    elif method == "update":
        if email not in users_dict:
            print("user not found")
            return

        db_session.query(User).filter(User.user_name == email).update(
            {"password": generate_password_hash(password), "admin": admin}
        )
        db_session.commit()

    elif method == "delete":
        if email not in users_dict or check_password_hash(
            users_dict[email]["password"], password
        ):
            print("user not found or wrong password")
            return

        db_session.query(User).filter(User.user_name == email).delete()
        db_session.commit()

    method = method + "ed" if method[-1] != "e" else method + "d"
    print("new user has been %s:\n%s" % (method, email))


if __name__ == "__main__":
    args = parser_opt()
    add_user(args.email, args.password, admin=args.admin, method=args.method)
