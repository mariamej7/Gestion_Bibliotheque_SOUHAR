# exceptions.py

class LivreIndisponibleError(Exception):
    def __init__(self, message="Le livre est déjà emprunté."):
        super().__init__(message)


class QuotaEmpruntDepasseError(Exception):
    def __init__(self, message="Le membre a atteint le nombre maximum d'emprunts."):
        super().__init__(message)


class MembreInexistantError(Exception):
    def __init__(self, message="Membre introuvable."):
        super().__init__(message)


class LivreInexistantError(Exception):
    def __init__(self, message="Livre introuvable."):
        super().__init__(message)
