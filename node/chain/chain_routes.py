from flask.blueprints import Blueprint
from flask import request, jsonify

from node.chain.chain_service import ChainService

chain = Blueprint("chain", __name__)


@chain.route('/', methods=["GET"])
def get_chain():
    chain = ChainService.get_chain()
    response = {"chain": chain.to_dict()}

    return jsonify(response), 200


@chain.route('/', methods=["POST"])
def resolve_conflicts():
    other_chain = request.get_json()["chain"]
    ChainService.resolve_conflicts(other_chain)

    return '', 204
