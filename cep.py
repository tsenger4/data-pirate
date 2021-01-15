import re

class Cep:
    def __init__(self):
        return

    def validate(self, cep):
        return re.match(r'[0-9]{5}-[\d]{3}', cep)
