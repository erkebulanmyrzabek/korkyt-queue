from passlib.context import CryptContext

# We use PBKDF2 here to avoid runtime incompatibilities between passlib and
# newer bcrypt releases inside containers. It is a solid default for the
# generated 6-digit instructor passwords used by this project scaffold.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
