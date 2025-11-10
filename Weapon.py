
class Weapon():
    def __init__(self, name, description, degats, range, cooldown):
        """Initialisation de l'arme.
        Args:
            name (str): nom de l'arme
            description (str): description de l'arme
            degats (int): degats infligés par l'arme
            range (float): portée de l'arme
            cooldown (float): temps de recharge entre les attaques
        Returns:
            None
        """
        self.name = name  # nom de l'arme
        self.description = description  # description de l'arme
        self.degats = degats  # degats infligés par l'arme
        self.range = range  # portée de l'arme
        self.initialCooldown = cooldown # temps de recharge initial entre les attaques
        self.cooldown = cooldown  # temps de recharge entre les attaques
