from node.block.block_model import Block
from node.block.block_service import BlockService
from node.chain.chain_model import Chain
from node.database import db


class ChainService:
    @staticmethod
    def get_chain():
        return db.session.query(Chain).first()

    @staticmethod
    def resolve_conflicts(other_chain):
        own_chain = ChainService.get_chain()

        # save computational cost and create instance after this check
        if own_chain is not None and len(own_chain.blocks) >= len(other_chain["blocks"]):
            return

        # create instances of class Chain
        other_chain = Chain.from_json(other_chain)

        # TODO: validate other_chain
        # try:
        #     other_chain.validate()
        # except Exception:
        #     return

        # replace chain
        if own_chain is not None:
            db.session.delete(own_chain)
        db.session.add(other_chain)
        db.session.commit()
