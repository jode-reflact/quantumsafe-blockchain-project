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
        ChainService.__remove_confirmed_transactions_from_pending_transactions(new_chain=other_chain)
        db.session.commit()

    @staticmethod
    def __remove_confirmed_transactions_from_pending_transactions(new_chain):
        confirmed_transactions = set()
        for block in new_chain.blocks:
            confirmed_transactions.update(block.transactions)

        # remove confirmed tx from pending tx
        confirmed_transactions_timestamps = set(
            map(lambda t: t.timestamp, confirmed_transactions)
        )
        db.session\
            .query(PendingTransaction)\
            .filter(PendingTransaction.timestamp.in_(confirmed_transactions_timestamps))\
            .delete(synchronize_session=False)
