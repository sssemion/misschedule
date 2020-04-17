banned = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm', 'йцукенгшщзхъ', "фывапролджэё", "ячсмитьбю"]
big, small = 'QWERTYUIOPLKJHGFDSAZXCVBNMЁЙЦУКЕНГШЩЗХЪЭЖДЛОРПАВЫФЯЧСМИТЬБЮ', \
             'qwertyuioplkjhgfdsazxcvbnmюбьтимсчяфывапролджэъхзщшгнекуцйё'
nums = '1234567890'


class PasswordError(Exception):
    pass


class LengthError(PasswordError):
    pass


class LetterError(PasswordError):
    pass


class DigitError(PasswordError):
    pass


class SequenceError(PasswordError):
    pass


error_description = {'LengthError': 'Длина пароля меньше 9 символов',
                     'LetterError': 'Все символы в пароле одного регистра',
                     'DigitError': 'В пароле нет ни одной цифры',
                     'SequenceError': 'Комбинация из 3 символов, стоящих рядом на клавиатуре', }


def length_check(password):
    if len(password) > 8:
        return True
    raise LengthError


def big_small_check(password):
    big_flag, small_flag = False, False
    for symbol in password:
        if symbol in big:
            big_flag = True
        elif symbol in small:
            small_flag = True
    if big_flag and small_flag:
        return True
    raise LetterError


def nums_check(password):
    num_flag = False
    for symbol in password:
        if symbol in nums:
            num_flag = True
            break
    if num_flag:
        return True
    raise DigitError


def three_row_check(password):
    for i in range(0, len(password) - 2):
        for row in banned:
            if password[i: i + 3].lower() in row:
                raise SequenceError
    return True


def check_password(password):
    try:
        length_check(password)
        big_small_check(password)
        nums_check(password)
        three_row_check(password)
        return 'ok'
    except PasswordError as e:
        raise PasswordError(error_description[type(e).__name__])
