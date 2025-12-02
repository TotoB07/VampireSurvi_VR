#librairies
from math import sin, cos, pi, atan2, degrees

#librairies panda3d
from panda3d.core import Vec3
from panda3d.core  import CollisionNode, CollisionBox
from direct.actor.Actor import Actor


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
        self.screen = game.screen # référence vers l'écran de jeu
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
        self.size = 3.5
        

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
                self.timeToReload -= dt # diminuer le temps avant la prochaine attaque
            if self.timeToReload <= 0: 
                self.timeToReload = self.initialTimeToReload # reinitialiser le temps avant la prochaine attaque
                self.is_attacking = False # le monstre n'attaque plus
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
        if self.position[2] > terrain_level + self.size: # si le monstre est au-dessus du sol
            if self.position[2] + self.gravity * dt < terrain_level + self.size: # si le monstre va toucher le sol
                self.position[2] = terrain_level + self.size # placer le monstre au niveau du sol
            else:
                self.position[2] += self.gravity * dt # appliquer la gravité
        #ajouter le fait de sauter un block de hauteur maximum
        if self.position[2] <= terrain_level + self.size: # si le monstre est au niveau du sol
            self.position[2] = terrain_level + self.size # placer le monstre au niveau du sol
        self.monster.setZ(self.position[2]) # mettre à jour la position en Z du monstre
        
            
    def isDead(self):
        """verifier si le monstre est mort.
        Args:
            None
        Returns:
            (bool) : etat du monstre
        """
        return self.health <= 0

    def loadMonster(self):
        """Charger le modèle du monstre et initialiser collision/animations."""
        model_path = 'model3d/monsterCarton.glb'
        # essayer Actor (pour animations) puis fallback sur NodePath
        try:
            self.monster = Actor(model_path)
        except Exception:
            self.monster = loader.loadModel(model_path)

        # attacher et positionner
        self.monster.reparentTo(self.screen.render)
        self.monster.setPos(self.position[0], self.position[1], self.position[2])

        # détecter animations si Actor
        self.walk_anim = 'marche1'
        self.is_walking = False

        # collider simple en sphere centré sur le modèle
        blockSolid = CollisionBox((-1,-1,-1), (1,1,1))
        blockNode = CollisionNode('monster-collision')
        blockNode.addSolid(blockSolid)
        blockNode.setIntoCollideMask(self.game.worldMask)
        collider = self.monster.attachNewNode(blockNode)
        collider.setPythonTag('owner', self.monster)

    def unloadMonster(self):
        """dechargement monstre.
        Args:
            None
        Returns:
            None
        """
        self.game.GameManager.score += 100
        self.game.monsters.remove(self)
        self.monster.removeNode() # supprimer monstre

    def nextAction(self, dt):
        """prochaine action du monstre.
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        distance = self.getDistanceToPlayer() # obtenir la distance entre le joueur et le monstre
        self.monster.setH(self.getAngleToPlayer(distance)) # Faire tourner le monstre vers le joueur
 

        good_distance = True # savoir s'i le joueur est dans la range du monstre
        for elt in distance:
            if abs(elt) > self.attack_range * self.size//2: # savoir si le joueur est trop loin
                good_distance = False 
        if good_distance: 
            self.attack(self.game.player) # le monstre attaque s'il est dans la range
            if self.is_walking:
                self.stopWalkAnimation()
        
        else: # sinon le monstre se deplace 
            # Se déplacer devant soi (direction de heading)
            self.Movement(dt, "devant")
            if not self.is_attacking:
                self.playWalkAnimation()

    def getAngleToPlayer(self, distance):
        angle_to_player = atan2(distance[1], distance[0]) # Calculer l'angle vers le joueur
        angle_to_player_degrees = degrees(angle_to_player)
        return angle_to_player_degrees

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
        if orientation == "devant": # s'il se deplace vers la droite
            if not self.isWallCollision(self.position[0], self.position[1]): # verifier s'il y a une collision avec un mur
                self.position[0] += dt * self.speed * cos(degToRad(self.monster.getH()))
                self.position[1] += dt * self.speed * sin(degToRad(self.monster.getH()))
                self.gravityEffect(dt, self.position[0] - 0.5 * self.size, self.position[1])
            else:
                self.bypassWallCollision() #contourne le mur s'il y a une collision
        self.monster.setPos(self.position[0], self.position[1], self.position[2]) # modifier les positions du mosntre  

    def bypassWallCollision(self):
        """contourner la collision avec un mur.
        Args:
            None
        Returns:
            None
        """
        # Logique pour contourner la collision avec les murs
        pass


    def isWallCollision(self, new_x, new_y):
        """verifier si le monstre entre en collision avec un mur.
        Args:
            new_x (float): nouvelle position en x
            new_y (float): nouvelle position en y
        Returns:
            (bool): True si collision, False sinon
        """
        if self.game.terrain.getSurfaceLevel(new_x, new_y) > self.position[2] + self.size:
            return True
        return False
    

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

    def playWalkAnimation(self):
        """Lancer l'animation de marche si disponible."""
        if not self.is_walking and isinstance(self.monster, Actor) and self.walk_anim:
            try:
                self.monster.loop(self.walk_anim)
                self.is_walking = True
            except Exception:
                pass


    def stopWalkAnimation(self):
        """Stopper l'animation de marche si elle tourne."""
        if isinstance(self.monster, Actor) and self.walk_anim:
            try:
                self.monster.stop(self.walk_anim)
            except Exception:
                pass
        else:
            try:
                self.monster.stop()
            except Exception:
                pass
        self.is_walking = False

