from flask import Blueprint, jsonify, request
from http import HTTPStatus
from sqlalchemy import select
from ..extensions import db
from ..models import Assignment

bp = Blueprint("assignments", __name__)


@bp.get("/<customer_id>")
def get_assignment(customer_id: str):
    tenant_id = request.args.get("tenant_id")
    if not tenant_id:
        return jsonify({"error": "tenant_id is required"}), HTTPStatus.BAD_REQUEST

    # Prefer lookup by business UID to avoid FK dependency
    stmt = select(Assignment).where(
        Assignment.customer_uid == customer_id,
        Assignment.tenant_id == tenant_id,
    )
    assignment = db.session.execute(stmt).scalars().first()
    if assignment is None:
        return jsonify({"customer_id": customer_id, "tenant_id": tenant_id, "assigned": False}), HTTPStatus.OK

    payload = assignment.to_dict()
    payload["assigned"] = True
    return jsonify(payload), HTTPStatus.OK
