from fastapi import FastAPI, Request, HTTPException
import jwt

app = FastAPI()

SECRET = "admsisplus"


@app.get("/home")
def home(request: Request):
    token = request.query_params.get("token")

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token não informado")

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return {
        "mensagem": f"Bem-vindo {payload['full_name']}",
        "usuario": payload["user"],
        "roles": payload["roles"]
    }