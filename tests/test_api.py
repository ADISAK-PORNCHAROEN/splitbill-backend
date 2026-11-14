import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import psycopg
import pytest


def headers(user="alice", key=None):
    result = {"X-User": user}
    if key is not None:
        result["Idempotency-Key"] = key
    return result


def equal(amount="100.00", members=None, paid_by="alice"):
    return {
        "description": "Dinner",
        "paid_by": paid_by,
        "amount": amount,
        "split": {
            "type": "equal",
            "members": ["alice", "bob", "carol"] if members is None else members,
        },
    }


def create(client, body=None, key="one", user="alice", group=1):
    return client.post(
        f"/groups/{group}/expenses", headers=headers(user, key), json=body or equal()
    )


def balances(client):
    response = client.get("/groups/1/balances", headers=headers())
    assert response.status_code == 200
    return {entry["member"]: entry["balance"] for entry in response.json()}


def assert_error(response, status):
    assert response.status_code == status, response.text
    error = response.json()["error"]
    assert isinstance(error["code"], str) and error["code"]
    assert isinstance(error["message"], str) and error["message"]


def test_groups_identity_and_access(client):
    assert client.get("/groups", headers=headers()).json() == [{"id": 1, "name": "Chiang Mai trip"}]
    detail = client.get("/groups/1", headers=headers()).json()
    assert detail["id"] == 1 and detail["name"] == "Chiang Mai trip"
    assert set(detail["members"]) == {"alice", "bob", "carol"}
    for identity in ({}, {"X-User": ""}, {"X-User": "unknown"}):
        assert_error(client.get("/groups", headers=identity), 400)
    for path in ("/groups/2", "/groups/2/expenses", "/groups/2/balances"):
        assert_error(client.get(path, headers=headers()), 404)
    assert_error(create(client, group=2), 404)
    assert_error(client.delete("/groups/2/expenses/1", headers=headers()), 404)


def test_local_frontend_preflight_allows_required_headers(client):
    response = client.options(
        "/groups/1/expenses",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-user,idempotency-key",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    denied = client.options(
        "/groups/1/expenses",
        headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in denied.headers


def test_openapi_documents_expense_creation_contract(client):
    operation = client.get("/openapi.json").json()["paths"]["/groups/{group_id}/expenses"]["post"]
    assert operation["requestBody"]["required"] is True
    schema = operation["requestBody"]["content"]["application/json"]["schema"]
    assert set(schema["required"]) == {"description", "paid_by", "amount", "split"}
    assert schema["properties"]["amount"]["type"] == "string"
    assert {"200", "201", "400"} <= operation["responses"].keys()
    assert "422" not in operation["responses"]


def test_equal_split_and_balances(client):
    response = create(client)
    assert response.status_code == 201, response.text
    expense = response.json()
    assert expense["amount"] == "100.00"
    assert expense["shares"] == {"alice": "33.34", "bob": "33.33", "carol": "33.33"}
    values = balances(client)
    assert values == {"alice": "66.66", "bob": "-33.33", "carol": "-33.33"}
    assert sum(map(Decimal, values.values())) == Decimal("0.00")
    assert client.get("/groups/1/expenses", headers=headers()).json() == [expense]


def test_equal_split_order_zero_shares_and_payer_outside_split(client):
    response = create(client, equal("0.01", ["carol", "bob"], "alice"))
    assert response.status_code == 201, response.text
    assert response.json()["shares"] == {"carol": "0.01", "bob": "0.00"}
    assert balances(client) == {"alice": "0.01", "bob": "0.00", "carol": "-0.01"}


def test_exact_split(client):
    body = equal()
    body["split"] = {"type": "exact", "shares": {"bob": "60.00", "carol": "40.00"}}
    response = create(client, body)
    assert response.status_code == 201, response.text
    assert response.json()["shares"] == {"bob": "60.00", "carol": "40.00"}
    assert balances(client) == {"alice": "100.00", "bob": "-60.00", "carol": "-40.00"}


@pytest.mark.parametrize("amount", ["0", "-1", "1.001", "10000000000.00", "NaN", "Infinity", 1.5])
def test_invalid_amounts(client, amount):
    assert_error(create(client, equal(amount)), 400)
    assert client.get("/groups/1/expenses", headers=headers()).json() == []


@pytest.mark.parametrize(
    "split",
    [
        {"type": "equal", "members": []},
        {"type": "equal", "members": ["alice", "alice"]},
        {"type": "equal", "members": ["alice", "dan"]},
        {"type": "exact", "shares": {"alice": "99.99"}},
        {"type": "exact", "shares": {"alice": "100.00", "bob": "0.00"}},
        {"type": "exact", "shares": {"alice": "100.00", "dan": "0.01"}},
    ],
)
def test_invalid_splits(client, split):
    body = equal()
    body["split"] = split
    assert_error(create(client, body), 400)
    assert client.get("/groups/1/expenses", headers=headers()).json() == []


def test_nonmember_payer_and_missing_key(client):
    assert_error(create(client, equal(paid_by="dan")), 400)
    assert_error(client.post("/groups/1/expenses", headers=headers(), json=equal()), 400)
    assert_error(create(client, key=""), 400)


@pytest.mark.parametrize("description", ["bad\x00description", "bad\ud800description"])
def test_description_rejects_invalid_database_text(client, description):
    body = equal()
    body["description"] = description
    response = client.post(
        "/groups/1/expenses",
        headers=headers(key="invalid-text"),
        content=json.dumps(body),
    )
    assert_error(response, 400)
    assert client.get("/groups/1/expenses", headers=headers()).json() == []


def test_duplicate_json_keys_and_invalid_body_do_not_disclose_group(client):
    body = (
        '{"description":"Dinner","paid_by":"alice","amount":"100.00",'
        '"split":{"type":"exact","shares":{"alice":"50.00","alice":"50.00"}}}'
    )
    assert_error(client.post("/groups/1/expenses", headers=headers(key="dup"), content=body), 400)
    assert_error(client.post("/groups/2/expenses", headers=headers(key="dup"), content=body), 404)
    assert_error(client.post("/groups/2/expenses", headers=headers(key="bad"), content="{"), 404)


def test_body_size_limit_and_http_error_headers(client):
    body = b"x" * (1024 * 1024 + 1)
    assert_error(client.post("/groups/1/expenses", headers=headers(key="large"), content=body), 400)
    assert_error(client.post("/groups/2/expenses", headers=headers(key="large"), content=body), 404)
    response = client.put("/groups", headers=headers())
    assert_error(response, 405)
    assert "GET" in response.headers["allow"]


def test_replay_scope_validation_and_deletion(client):
    original = create(client).json()
    changed = equal("4.00", ["bob"], "bob")
    replay = create(client, changed, user="bob")
    assert replay.status_code == 200 and replay.json() == original
    assert_error(create(client, equal("1.001")), 400)
    assert_error(create(client, user="dan"), 404)
    other_group = create(client, equal("1.00", ["bob", "dan"], "bob"), user="bob", group=2)
    assert other_group.status_code == 201
    assert_error(client.delete(f"/groups/1/expenses/{original['id']}", headers=headers("bob")), 403)
    deleted = client.delete(f"/groups/1/expenses/{original['id']}", headers=headers())
    assert deleted.status_code == 204 and deleted.content == b""
    assert_error(client.delete(f"/groups/1/expenses/{original['id']}", headers=headers()), 404)
    assert client.get("/groups/1/expenses", headers=headers()).json() == []
    assert balances(client) == {"alice": "0.00", "bob": "0.00", "carol": "0.00"}
    replay_deleted = create(client)
    assert replay_deleted.status_code == 200 and replay_deleted.json() == original
    assert client.get("/groups/1/expenses", headers=headers()).json() == []


def test_concurrent_replays_create_one_expense(client):
    barrier = Barrier(8)

    def send(_):
        barrier.wait(timeout=10)
        return create(client, key="concurrent")

    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(send, range(8)))
    assert sorted(response.status_code for response in responses) == [200] * 7 + [201]
    payloads = [response.json() for response in responses]
    assert all(payload == payloads[0] for payload in payloads)
    assert client.get("/groups/1/expenses", headers=headers()).json() == [payloads[0]]


def test_concurrent_deletes_have_one_success(client):
    expense_id = create(client).json()["id"]
    barrier = Barrier(2)

    def delete(_):
        barrier.wait(timeout=10)
        return client.delete(f"/groups/1/expenses/{expense_id}", headers=headers())

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(delete, range(2)))
    assert sorted(response.status_code for response in responses) == [204, 404]
    assert balances(client) == {"alice": "0.00", "bob": "0.00", "carol": "0.00"}


def test_seed_is_repeatable_without_duplicate_data(client, test_database):
    database_url, env = test_database
    subprocess.run([sys.executable, "-m", "app.seed"], env=env, check=True)
    conninfo = database_url.set(drivername="postgresql").render_as_string(hide_password=False)
    with psycopg.connect(conninfo) as connection:
        counts = connection.execute(
            "SELECT (SELECT count(*) FROM users), (SELECT count(*) FROM groups), "
            "(SELECT count(*) FROM memberships)"
        ).fetchone()
    assert counts == (4, 2, 5)


def test_expense_order_by_timestamp_then_id(client, test_database):
    first = create(client, key="first").json()
    second = create(client, key="second").json()
    third = create(client, key="third").json()
    database_url, _ = test_database
    conninfo = database_url.set(drivername="postgresql").render_as_string(hide_password=False)
    with psycopg.connect(conninfo) as connection:
        connection.execute(
            "UPDATE expenses SET created_at = CASE WHEN id = %s "
            "THEN '2025-01-02T00:00:00Z'::timestamptz ELSE '2025-01-01T00:00:00Z'::timestamptz END",
            (first["id"],),
        )
    response = client.get("/groups/1/expenses", headers=headers())
    assert response.status_code == 200
    assert [expense["id"] for expense in response.json()] == [
        first["id"],
        third["id"],
        second["id"],
    ]
