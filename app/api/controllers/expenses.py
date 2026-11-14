import json
from decimal import Decimal, InvalidOperation
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.database import SessionLocal, get_session
from app.domain.types import bad_request
from app.services import expenses
from app.services.groups import authorize, identify

router = APIRouter(prefix="/groups/{group_id}/expenses")
MAX_BODY_BYTES = 1024 * 1024


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def process_expense(
    group_id: int, x_user: str | None, key: str | None, raw_body: bytearray, too_large: bool
) -> tuple[dict, bool]:
    with SessionLocal() as session:
        actor = identify(session, x_user)
        authorize(session, actor.id, group_id)
        if too_large:
            raise bad_request("Request body is too large")
        try:
            body = json.loads(
                raw_body,
                object_pairs_hook=unique_object,
                parse_float=Decimal,
                parse_constant=reject_constant,
            )
        except (ValueError, UnicodeDecodeError, RecursionError, InvalidOperation):
            raise bad_request("Invalid JSON body") from None
        return expenses.create(session, actor.id, group_id, key, body)


@router.post(
    "",
    status_code=201,
    responses={200: {"description": "Original expense returned for a valid replay"}},
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["description", "paid_by", "amount", "split"],
                        "properties": {
                            "description": {"type": "string"},
                            "paid_by": {"type": "string"},
                            "amount": {"type": "string", "example": "100.00"},
                            "split": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "required": ["type", "members"],
                                        "properties": {
                                            "type": {"const": "equal"},
                                            "members": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        },
                                    },
                                    {
                                        "type": "object",
                                        "required": ["type", "shares"],
                                        "properties": {
                                            "type": {"const": "exact"},
                                            "shares": {
                                                "type": "object",
                                                "additionalProperties": {"type": "string"},
                                            },
                                        },
                                    },
                                ]
                            },
                        },
                    }
                }
            },
        }
    },
)
async def create_expense(
    group_id: int,
    request: Request,
    response: Response,
    x_user: Annotated[str | None, Header()] = None,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    raw_body = bytearray()
    too_large = False
    async for chunk in request.stream():
        if len(raw_body) + len(chunk) > MAX_BODY_BYTES:
            too_large = True
            break
        raw_body.extend(chunk)
    result, created = await run_in_threadpool(
        process_expense, group_id, x_user, idempotency_key, raw_body, too_large
    )
    response.status_code = 201 if created else 200
    return result


@router.get("")
def list_expenses(
    group_id: int,
    session: Annotated[Session, Depends(get_session)],
    x_user: Annotated[str | None, Header()] = None,
):
    actor = identify(session, x_user)
    return expenses.list_active(session, actor.id, group_id)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    group_id: int,
    expense_id: int,
    session: Annotated[Session, Depends(get_session)],
    x_user: Annotated[str | None, Header()] = None,
):
    actor = identify(session, x_user)
    expenses.delete(session, actor.id, group_id, expense_id)
    return Response(status_code=204)
