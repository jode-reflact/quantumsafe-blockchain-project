from sqlalchemy import exc

from node.database import db
from node.transaction.transaction_model import PendingTransaction


class TransactionService:
    @staticmethod
    def get_pending_transactions():
        return db.session.query(PendingTransaction).all()

    @staticmethod
    def add_transaction(sender, receiver, amount, timestamp, signature):
        transaction = PendingTransaction(timestamp=timestamp,
                                         sender=sender,
                                         receiver=receiver,
                                         amount=amount,
                                         signature=signature
                                         )
        transaction.verify()

        # TODO: distribute transaction across the network

        # Insert transaction in db
        try:
            db.session.add(transaction)
            db.session.commit()
        except exc.IntegrityError:
            # transaction already known
            db.session.rollback()
