from node.chain.chain_model import Chain
from node.database import db
from node.transaction.pending_transaction_model import PendingTransaction


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

        try:
            other_chain.validate()
        except Exception:
            print("Other Chain is not valid")
            return

        # replace chain
        if own_chain is not None:
            db.session.delete(own_chain)
        db.session.add(other_chain)

        ChainService.__update_pending_transactions(new_chain=other_chain)

        db.session.commit()

    # PROBLEM: - comparison of pending tx and confirmed tx is not possible with a set difference
    #            (only by implementing __hash() method)
    #          - transactions must be deleted from one table and inserted in other table (inefficient)
    # SOLUTION: use just one table for transactions in general use a column that indicates block affiliation
    @staticmethod
    def __update_pending_transactions(new_chain):
        confirmed_transactions = set()
        for block in new_chain.blocks:
            confirmed_transactions.update(block.transactions)

        current_pending_transactions = set(db.session.query(PendingTransaction).all())

        # TODO: build difference set

        pass