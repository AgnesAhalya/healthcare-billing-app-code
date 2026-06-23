from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
EXPIRY_TIME = int(os.environ.get("EXPIRY_TIME", "1800"))
JWT_ISSUER = "healthcare-benchmark"
JWT_AUDIENCE = "healthcare-users"
PRIVATE_KEY_PEM = Path(os.environ.get("JWT_PRIVATE_KEY_PATH", BASE_DIR.parent / "certs" / "localhost.key")).read_text()
PUBLIC_KEY_PEM = Path(os.environ.get("JWT_PUBLIC_KEY_PATH", BASE_DIR.parent / "certs" / "jwt_public.pem")).read_text() if Path(os.environ.get("JWT_PUBLIC_KEY_PATH", BASE_DIR.parent / "certs" / "jwt_public.pem")).exists() else PRIVATE_KEY_PEM



csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)

