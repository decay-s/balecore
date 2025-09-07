from dataclasses import dataclass

@dataclass
class Transaction:
    id: str
    status: str
    userID: int
    amount: int
    createdAt: int

    def __str__(self):
        return (
            f"Transaction(\n"
            f"    id={self.id},\n"
            f"    status={self.status},\n"
            f"    userID={self.userID},\n"
            f"    amount={self.amount},\n"
            f"    createdAt={self.createdAt}\n"
            f")"
        )