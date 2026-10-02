"""Uniform public error envelope; dependency details stay out of responses."""

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import DependencyTimeout, DependencyUnavailable
from app.modules.answering.service import InvalidModelResponse
from app.modules.conversations.service import ConversationNotFound


def _response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {
        "code": code, "message": message, "request_id": request.state.request_id}})


def register_error_handlers(application: FastAPI) -> None:
    @application.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc: RequestValidationError):
        return _response(request, 422, "invalid_input", "请求参数无效")

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        if exc.status_code == 404:
            return _response(request, 404, "not_found", "资源不存在")
        return _response(request, exc.status_code, "http_error", str(exc.detail))

    @application.exception_handler(ConversationNotFound)
    async def missing_conversation(request: Request, exc: ConversationNotFound):
        return _response(request, 404, "not_found", "资源不存在")

    async def dependency_error(request: Request, exc: Exception):
        return _response(request, 503, "dependency_unavailable", "依赖暂不可用，请稍后重试")

    for error_type in (DependencyTimeout, DependencyUnavailable, InvalidModelResponse,
                       SQLAlchemyError, httpx.HTTPError):
        application.add_exception_handler(error_type, dependency_error)

    @application.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception):
        return _response(request, 500, "internal_error", "请求暂时无法完成")
