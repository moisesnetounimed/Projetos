# SISPLUS

Base refatorada do portal institucional SISPLUS com FastAPI, Jinja2 e módulos preparados para evolução.

## Estrutura
- `app/core`: configuração, contexto, sessão e segurança
- `app/routers`: autenticação e home
- `app/modules`: módulos funcionais (`financeiro`, `contabil`, `operacoes`)
- `app/templates`: templates Jinja2
- `app/static`: CSS, JS, imagens e ícones

## Como executar
## Poweshell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install itsdangerous
pip install fastapi uvicorn jinja2 python-dotenv itsdangerous
pip freeze > requirements.txt
python.exe -m pip install --upgrade pip
uvicorn app.main:app --reload
```

## Observações
- Não suba `.env` nem `.venv` para versionamento.
- O timeout de inatividade padrão é de 30 minutos.
- A autenticação continua consultando as functions Oracle existentes do pacote `CUSTOM.PKG_SISPLUS`.
