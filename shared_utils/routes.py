import os

from fastapi.routing import APIRouter
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
import aiosmtplib
from email.message import EmailMessage
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from typing import Annotated, Dict, Optional, Union
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from starlette.requests import Request
import base64
from pathlib import Path
import mailtrap as mt
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from shared_utils.token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token

router = APIRouter()

emailRouter = APIRouter()

security = HTTPBearer()


# # 定义 SMTP 服务器的配置
# SMTP_HOST = "smtp-mail.outlook.com"
# SMTP_PORT = 465
# SMTP_USERNAME = 'noreply@tzpro.xyz'
# SMTP_PASSWORD = "Aa112211."
# FROM_EMAIL = 'noreply'


def load_template(template_name, context):
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")))
    template = env.get_template(template_name)
    return template.render(context)


def sendMail(receiver, subject, body):
    mail = mt.Mail(
        sender=mt.Address(email="noreply@email.tzpro.uk", name="noreply"),
        to=[mt.Address(email=receiver, name="")],
        subject=subject,
        text="Welcome to tzpro!",
        html=body,
        category="Test",
        headers={"X-MT-Header": "Custom header"},
        custom_variables={"year": 2023},
    )

    client = mt.MailtrapClient(token="f1a5f8020f9fc16405cb0c6ce6711aba")
    client.send(mail)


# 一个能作为 depends 的解析器 把 token 解析成 email
def verify_token(token: str = Depends(security)):
    return decode_access_token(token)


@router.route("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        response = RedirectResponse(url="/")
        response.delete_cookie("token")
        return response
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.route("/login")
async def login(request: Request):
    response = HTMLResponse(load_template("main.html", {}))
    return response


@emailRouter.post("/send")
async def sendCaptcha(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    email = data["email"]
    if email == "":
        raise HTTPException(status_code=400, detail="Invalid email")
    token = create_access_token(str(email))
    base_url = request.base_url
    timestamp = datetime.now().timestamp()
    link = f"{base_url.scheme}://{base_url.netloc}/login/verify/{token.access_token}?security={timestamp}&email={email}"
    context = {
        "login_link": link
    }
    html_content = load_template("email.html", context)
    subject = "Login to tzpro"
    try:
        # sendMail(email, subject, html_content)
        print("Email sent")
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "Email not sent"}, status_code=400)
    # background_tasks.add_task(send_email, message)
    return JSONResponse(content={"message": "Email sent"})
    # return JSONResponse(content={"message": link})


@router.route("/login/verify/{token}")
async def verifyEmail(request: Request):
    try:
        token = request.path_params["token"]
        email = decode_access_token(token)
        print(email)
        if email != request.query_params["email"]:
            response = RedirectResponse(url="/")
            response.delete_cookie("token")
            return response
        if datetime.now().timestamp() - float(request.query_params["security"]) > 600:
            response = RedirectResponse(url="/")
            response.delete_cookie("token")
            print("time out")
            return response
        response = RedirectResponse(url="/zh-cn")
        # response.set_cookie("token", token, secure=True, domain="tzpro.xyz", samesite="strict",
        #                 expires=ACCESS_TOKEN_EXPIRE_MINUTES)  # 1h
        response.set_cookie("token", token, expires=ACCESS_TOKEN_EXPIRE_MINUTES)
        print("success")
        return response
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@emailRouter.route("/verify")
async def verifyEmail(token: str, request: Request):
    try:
        email = decode_access_token(token)
        if email != request.query_params["email"]:
            response = RedirectResponse(url="/")
            response.delete_cookie("token")
            return response
        if datetime.now().timestamp() - float(request.query_params["security"]) > 600:
            response = RedirectResponse(url="/")
            response.delete_cookie("token")
            return response
        response = RedirectResponse(url="/zh-cn")
        response.set_cookie("token", token, secure=True, domain="tzpro.xyz", samesite="strict",
                            expires=ACCESS_TOKEN_EXPIRE_MINUTES)  # 1h
        return response
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@emailRouter.route("/resend")
async def sendCaptcha(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    email = data["email"]
    if email == "":
        raise HTTPException(status_code=400, detail="Invalid email")
    token = create_access_token(str(email))
    base_url = request.base_url
    timestamp = datetime.now().timestamp()
    link = f"{base_url.scheme}://{base_url.netloc}/login/verify/{token.access_token}?security={timestamp}&email={email}"
    context = {
        "login_link": link
    }
    html_content = load_template("email.html", context)
    subject = "Login to tzpro"
    sendMail(email, subject, html_content)
    # background_tasks.add_task(send_email, message)
    return JSONResponse(content={"message": "Email sent"}, status_code=200)
