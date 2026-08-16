from bson import DBRef
from flask import g, has_request_context


def request_memo(key, compute):
    if not has_request_context():
        return compute()

    memo = getattr(g, "noppakao_request_memo", None)
    if memo is None:
        memo = {}
        g.noppakao_request_memo = memo

    if key not in memo:
        memo[key] = compute()

    return memo[key]


def reference_id(value):
    if value is None:
        return None

    if isinstance(value, DBRef):
        return value.id

    return getattr(value, "pk", value)
