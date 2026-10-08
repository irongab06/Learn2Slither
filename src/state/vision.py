def encode_symbol(symbol):
    if symbol == "S":
        return [1, 0, 0, 0, 0]
    if symbol == "G":
        return [0, 1, 0, 0, 0]
    if symbol == "R":
        return [0, 0, 1, 0, 0]
    if symbol == "0":
        return [0, 0, 0, 1, 0]
    if symbol == "W":
        return [0, 0, 0, 0, 1]
    raise ValueError(f"Symbole inconnu : {symbol}")


def encode_vision(vision):
    encoded_vision = []
    for direction in ["up", "down", "left", "right"]:
        for symbol in vision[direction]:
            encoded_vision.extend(encode_symbol(symbol))
        missing_cells = 25 - len(vision[direction])
        for _ in range(missing_cells):
            encoded_vision.extend([0, 0, 0, 0, 0])
    return encoded_vision
