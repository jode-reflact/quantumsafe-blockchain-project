from flask.blueprints import Blueprint
from flask import request, jsonify

from node.chain.chain_model import Chain
from node.chain.chain_service import ChainService

chain = Blueprint("chain", __name__)


@chain.route('/', methods=["GET"])
def get_chain():
    chain = ChainService.get_chain()
    if chain is None:
        chain = Chain(blocks=[])
    response = {"chain": chain.to_dict()}

    return jsonify(response), 200

@chain.route('/validate', methods=["GET"])
def validate_own_chain():
    chain = ChainService.get_chain()
    if chain is None:
        chain = Chain(blocks=[])
    try:
        chain.validate()
        return jsonify({"valid": True}), 200
    except ValueError:
        return jsonify({"valid": False, "reason": "Transaction not valid"}), 200
    except Exception as e:
        return jsonify({"valid": False, "reason": "Chain not valide", "message": str(e)}), 200

    response = {"chain": chain.to_dict()}

    return jsonify(response), 200


@chain.route('/', methods=["POST"])
def resolve_conflicts():
    other_chain = request.get_json()["chain"]
    ChainService.resolve_conflicts(other_chain)

    return '', 204

@chain.route('/', methods=["PUT"])
def distribute_chain():
    ChainService.distribute_chain()
    return '', 200
