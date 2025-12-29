CORE_NUMBER = 88  # random.randint(1, 100)

print(f"Core number is: {CORE_NUMBER}")


def guess_number(guess_number: int) -> str:
    """
    A number guessing game tool.

    The tool picks an core number in range 1-100 and compares it with the guessed number.

    Args:
        guess_number: The number guessed by the user (0-100)

    Returns:
        A string indicating whether the guess is bigger, smaller, or equal to the core number
    """

    if guess_number > CORE_NUMBER:
        return "your guessed number is bigger than core number"
    elif guess_number < CORE_NUMBER:
        return "your guessed number is smaller than the core number"
    else:
        return "correct! the core number is"
