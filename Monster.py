#librairies
from math import sin, cos, pi

#librairies panda3d
from panda3d.core import Vec3
from panda3d.core  import CollisionNode, CollisionBox


def degToRad(deg):
    """Convertir des degrés en radiants.
    Args:
        deg (float): angle en degrés
    Returns:
        float: angle en radiants
    """
    return deg * (pi / 180)

class Monster:
    """Classe représentant un monstre."""
    def __init__(self, game, position, health, speed, attack_power, attack_range, xp_value, monster_type="normal"):
        """Initialisation du monstre.
        Args:
            game (Game): reference vers la classe principale
            position (list): position initiale du monstre [x, y, z]
            health (int): points de vie du monstre
            speed (float): vitesse de déplacement du monstre
            attack_power (int): puissance d'attaque du monstre
            attack_range (float): portée d'attaque du monstre
            xp_value (int): points d'expérience donnés à la mort du monstre
            monster_type (str): type de monstre
        Returns:
            None
        """
        self.screen = game.screen
        self.game = game  # référence vers la partie
        self.position = position # position du monstre
        self.type = monster_type # type du monstre
        self.health = health # santé du monstre
        self.speed = speed # vitesse du monstre
        self.attack_power = attack_power # nombre de degats
        self.attack_range = attack_range # range de l'attaque
        self.xp_value = xp_value # gain d'xp

        # État
        self.is_alive = True # etat du moponstre
        self.is_attacking = False # etat de son attaque
        self.initialTimeToReload = 3 # temps initial pour que le monstre reattaque
        self.timeToReload = self.initialTimeToReload # temps avant que le monstre reattaque
        self.gravity = -20  # accélération due à la gravité
        

        self.loadMonster() # chargement du monstre

        
        # - Configuration des collisions
        # - Animation du monstre
        # - Sons du monstre

    def update(self, dt):
        """update les actions du monstre.
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        self.is_alive = not self.isDead() # on regarde s'il est toujours en vie
        if self.is_alive: 
            self.nextAction(dt) # effectuer la prochaine action
            if self.is_attacking:
                self.timeToReload -= dt
            if self.timeToReload <= 0:
                self.timeToReload = self.initialTimeToReload
                self.is_attacking = False
        else:
            self.unloadMonster() # supprimer le monstre

    def gravityEffect(self, dt, x, y):
        """appliquer la gravité au monstre.
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        terrain_level = self.game.terrain.getSurfaceLevel(x ,y) # obtenir le niveau du terrain aux coordonnées (x, y)
        if self.position[2] > terrain_level + self.game.terrain.block_size:
            if self.position[2] + self.gravity * dt < terrain_level + self.game.terrain.block_size:
                self.position[2] = terrain_level + self.game.terrain.block_size
            else:
                self.position[2] += self.gravity * dt
        if self.position[2] <= terrain_level + self.game.terrain.block_size:
            self.position[2] = terrain_level + self.game.terrain.block_size
        self.monster.setZ(self.position[2])
        
            
    def isDead(self):
        """verifier si le monstre est mort.
        Args:
            None
        Returns:
            (bool) : etat du monstre
        """
        return self.health <= 0

    def loadMonster(self):
        """chargement monstre.
        Args:
            None
        Returns:
            None
        """
        self.monster = loader.loadModel('model3d/stone-block.glb') # chargement model du monstre
        self.monster.reparentTo(self.screen.render)  # Attacher au render
        self.monster.setPos(self.position[0], self.position[1], self.position[2]) # placer le monstre au position
        
        blockSolid = CollisionBox((-1,-1,-1), (1,1,1)) # creation boxe de collision
        blockNode = CollisionNode('block-collision-node') # creer un node de collision pour le monstre
        blockNode.addSolid(blockSolid) # ajouter le rayon de collision au node
        # rendre ces nodes "into" pour la mask du monde
        blockNode.setIntoCollideMask(self.game.worldMask) # definir le masque de collision
        collider = self.monster.attachNewNode(blockNode) # attacher le node de collision au noeud du monstre
        collider.setPythonTag('owner', self.monster) # tag python pour référencer le monstre

    def unloadMonster(self):
        """dechargement monstre.
        Args:
            None
        Returns:
            None
        """
        self.monster.removeNode() # supprimer monstre

    def nextAction(self, dt):
        """prochaine action du monstre.
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        distance = self.getDistanceToPlayer() # obtenir la distance entre le joueur et le monstre
        good_distance = True # savoir s'i le joueur est dans la range du monstre
        
        for elt in distance:
            if abs(elt) > self.attack_range//10: # savoir si le joueur est trop loin
                good_distance = False
        
        if good_distance: 
            self.attack(self.game.player) # le monstre attaque s'il est dans la range
        
        else: # sinon le monstre se deplace 
            # on regarde quel axe est le plus grand
            if max(abs(distance[0]), abs(distance[1])) == abs(distance[0]): # axe x est le plus grand
                if distance[0] > 0: 
                    self.Movement(dt, "droite") # on se deplace a droite
                else:
                    self.Movement(dt, "gauche") # on se deplace a gauche
            else: # axe y est le plus grand
                if distance[1] > 0:
                    self.Movement(dt, "devant") # on se deplace devant
                else:
                    self.Movement(dt, "derrière") # on se deplace derriere

    def getDistanceToPlayer(self):
        """optenir la distance entre le joueur est le monstre.
        Args:
            dt (float): temps qui c passer depuis la derniere update
            orientation (str): dirrection du deplacement
        Returns:
            distance (Vec3): distance en x,y,z entre le joueur et le monstre
        """
        player_pos = self.game.player.position # recuperation position du joueur
        distance = Vec3(player_pos[0] - self.position[0], # distance en X
                         player_pos[1] - self.position[1], # distance en Y
                         player_pos[2] - self.position[2] # distance en Z
                        ) # distance en x,y,z entre le joueur et le monstre
        return distance
        
    def Movement(self, dt, orientation):
        """faire deplacer le monstre.
        Args:
            dt (float): temps qui c passer depuis la derniere update
            orientation (str): dirrection du deplacement
        Returns:
            None
        """
        if orientation == "devant": # s'il se deplace vers l'avant
            self.position[0] -= dt * self.speed * sin(degToRad(self.monster.getH()))
            self.position[1] += dt * self.speed * cos(degToRad(self.monster.getH()))
            self.gravityEffect(dt, self.position[0], self.position[1] - 0.5 * self.game.terrain.block_size)
            print("devant")
        elif orientation == "derrière": # s'il se deplace vers l'arriere
            self.position[0] += dt * self.speed * sin(degToRad(self.monster.getH()))
            self.position[1] -= dt * self.speed * cos(degToRad(self.monster.getH()))
            self.gravityEffect(dt, self.position[0] , self.position[1]- 0.5 * self.game.terrain.block_size)
            print("derrière")
        elif orientation == "gauche": # s'il se deplace vers la gauche
            self.position[0] -= dt * self.speed * cos(degToRad(self.monster.getH()))
            self.position[1] -= dt * self.speed * sin(degToRad(self.monster.getH()))
            self.gravityEffect(dt, self.position[0] - 0.5 * self.game.terrain.block_size, self.position[1])
            print("gauche")
        elif orientation == "droite": # s'il se deplace vers la droite
            self.position[0] += dt * self.speed * cos(degToRad(self.monster.getH()))
            self.position[1] += dt * self.speed * sin(degToRad(self.monster.getH()))
            self.gravityEffect(dt, self.position[0] - 0.5 * self.game.terrain.block_size, self.position[1])

            print("droite")
        self.monster.setPos(self.position[0], self.position[1], self.position[2]) # modifier les positions du mosntre  

    def attack(self, target):
        """attaque du monstre.
        Args:
            target (Target): cible de l'attaque
        Returns:
            None
        """
        if self.game.player == target and not self.is_attacking: # si c le joueur
            target.health -= self.attack_power # on lui enleve de la vie 
            self.is_attacking = True # le monstre est en train d'attaquer
            target.barre.setScale(target.health/100, 1, 1)

    def changeHealth(self, degats):
        """modifier la vie du monstre.
        Args:
            degat(int): degats que se prend le monstre
        Returns:
            None
        """
        self.health -= degats

