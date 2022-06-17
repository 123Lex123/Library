class WrongPasswordError(Exception):
    pass


class WrongLoginError(Exception):
    pass


class PasswordDigitError(WrongPasswordError):
    pass


class LoginLengthError(WrongLoginError):
    pass


class PasswordLetterError(WrongPasswordError):
    pass


class PasswordLengthError(WrongPasswordError):
    pass
