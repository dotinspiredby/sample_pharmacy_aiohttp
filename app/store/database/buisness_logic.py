def price_markup_(trade_price: float, online: bool = False) -> float:
    """ 20% for offline purchase, 15% for online purchase """
    if online:
        return float('{:.2f}'.format(trade_price * 1.15))
    return float('{:.2f}'.format(trade_price * 1.2))


def edit_rating(rating: int, sum_: float) -> int:
    """ change rating """
    if sum_ <= 50:
        return rating + 2
    elif sum_ <= 100:
        return rating + 4
    else:
        return rating + 8

