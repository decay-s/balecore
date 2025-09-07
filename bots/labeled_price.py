from typing import Callable, Union

def LabeledPrice(
    label: str, 
    amount: Union[int, str]
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            prices = [{"label": label, "amount": amount}]
            return func(*args, prices=prices, **kwargs)
        return wrapper
    return decorator