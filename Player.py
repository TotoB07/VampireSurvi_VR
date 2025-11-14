#librairies
from math import pi, sin, cos

#librairies panda3d
from panda3d.core import CollisionNode, CollisionSphere, CollisionRay, BitMask32
from panda3d.core import TransparencyAttrib, WindowProperties, CardMaker
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

def degToRad(deg):
    """Convertir des degrés en radiants.
    Args:
        deg (float): angle en degrés
    Returns:
        float: angle en radiants
    """

    return deg * (pi / 180)

class Player():
    """Classe représentant le joueur."""

    def __init__(self, game, position):
        """Initialisation du joueur.
        Args:
            game (Game): reference vers la classe principale
            position (list): position initiale du joueur [x, y, z]
        Returns:
            None
        """
        
        self.game = game  # référence vers la classe principale
        self.screen = game.screen

        # Infos joueur
        self.health = 100 # santé actuelle du joueur
        self.maxhealth = 100 # santé maximale du joueur
        self.position = position # position du joueur [x,y,z]
        self.is_attacking = False
        self.weapon = None # arme du joueur
        
        # Physique
        self.zVel = 0.0 # vitesse verticale du joueur
        self.gravity = -20.0 # gravité du jeu
        self.jumpSpeed = 10.0 # vitesse du joueur sur le plan vertical
        self.onGround = False # savoir si le joueur est dans les airs
        self.moveSpeed = 10 #v itesse du joueur sur le plan horizontal
        self.initialSpeed = 10
        
        # Contrôles
        self.setupControls() # configuration des contrôles
        self.setupCamera(self.position) # configuration de la caméra
        
        # État de la souris
        self.cameraSwingActivated = False # savoir si la sourie est dans le jeu ou non
        self.cameraSwingFactor = 10 # facteur de la sourie

        #Barre de vie
        cm = CardMaker("fond")
        cm.setFrame(0, 1, 0, 0.05)
        self.fond = aspect2d.attachNewNode(cm.generate())
        self.fond.setPos(-0.5, 0, -0.9)
        self.fond.setColor(0.2, 0.2, 0.2, 1)

        # Barre rouge
        cm2 = CardMaker("barre")
        cm2.setFrame(0, 1, 0, 0.05)
        self.barre = aspect2d.attachNewNode(cm2.generate())
        self.barre.setPos(-0.5, 0, -0.9)
        self.barre.setColor(1, 0, 0, 1)

    def setupControls(self):
        """Initialisation des touches de controles.
        Args:
            None
        Returns:
            None
        """

        # dictionnaire pour savoir dans quels direction le joueur se deplace
        self.keyMap = {
            "forward": False, # devant
            "backward": False, # derriere
            "left": False, # à gauche
            "right": False, # à droite
            "up": False, # au dessus 
            "down": False, # en dessous
            "attaque": False, # attaque du joueur
            "Sprint": False
        }
        
        # Binding des touches
        self.screen.accept(self.game.menu.bindings["Sortir"], self.releaseMouse) # touche pour desactiver la sourie 
        self.screen.accept(self.game.menu.bindings["mouse1"], self.captureMouse) # touche pour activer la sourie 
        self.screen.accept(self.game.menu.bindings["Attaque"], self.updateKeyMap, ["attaque", True]) # touche pour attaquer
        self.screen.accept(self.game.menu.bindings["Avancer"], self.updateKeyMap, ["forward", True]) # touche pour avancer
        self.screen.accept(self.game.menu.bindings["Avancer"] + "-up", self.updateKeyMap, ["forward", False]) # touche pour arreter d'avancer
        self.screen.accept(self.game.menu.bindings["Reculer"], self.updateKeyMap, ["backward", True]) # touche pour reculer
        self.screen.accept(self.game.menu.bindings["Reculer"] + "-up", self.updateKeyMap, ["backward", False]) # touche pour arreter de reculer
        self.screen.accept(self.game.menu.bindings["Gauche"], self.updateKeyMap, ["left", True]) # touche pour aller à gauche
        self.screen.accept(self.game.menu.bindings["Gauche"] + "-up", self.updateKeyMap, ["left", False]) # touche pour arreter d'aller à gauche
        self.screen.accept(self.game.menu.bindings["Droite"], self.updateKeyMap, ["right", True]) # touche pour aller à droite
        self.screen.accept(self.game.menu.bindings["Droite"] + "-up", self.updateKeyMap, ["right", False]) # touche pour arreter d'aller à droite
        self.screen.accept(self.game.menu.bindings["Saut"], self.updateKeyMap, ["up", True]) # touche pour sauter
        self.screen.accept(self.game.menu.bindings["Saut"] + "-up", self.updateKeyMap, ["up", False]) # touche pour arreter de sauter
        self.screen.accept(self.game.menu.bindings["Accroupir"], self.updateKeyMap, ["down", True]) # touche pour se baisser
        self.screen.accept(self.game.menu.bindings["Accroupir"]+ "-up", self.updateKeyMap, ["down", False]) # touche pour arreter de se baisser
        self.screen.accept(self.game.menu.bindings["Sprint"], self.updateKeyMap, ["Sprint", True]) # touche pour se baisser
        self.screen.accept(self.game.menu.bindings["Sprint"]+ "-up", self.updateKeyMap, ["Sprint", False]) # touche pour arreter de se baisser

    def setupCamera(self, position):
        """Initialisation de la camera du joueur.
        Args:
            position (list): position du joueur
        Returns:
            None
        """
        self.screen.disableMouse() # desactivation de la sourie à l'ecran
        self.screen.camera.setPos(position[0], position[1], position[2]) # donner a la camera une position de base
        
        # Crosshair
        self.crosshairs = OnscreenImage(
            image='img/crosshairs.png', #image
            pos=(0, 0, 0), #position
            scale=0.05 #taille
        )
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha) #afficher le crosshairs

        # Collisions
        self.setupCollisions()

    def setupCollisions(self):
        """Initialisation des collitions du joueur.
        Args:
            None
        Returns:
            None
        """
        # Collider joueur
        playerNode = CollisionNode('player-collider') # creer un node de collision pour le joueur
        playerNode.addSolid(CollisionSphere(0, 0, 0, 0.5)) # ajouter une sphere de collision au node
        playerNode.setFromCollideMask(self.game.worldMask) # rendre ces nodes "from" pour la mask du monde
        playerNode.setIntoCollideMask(BitMask32.allOff()) # desactiver les collisions "into" pour le joueur
        self.playerCollider = self.screen.camera.attachNewNode(playerNode) # attacher le node de collision a la camera
        self.game.cTrav.addCollider(self.playerCollider, self.game.pusher) # ajouter le collider au systeme de collision
        self.game.pusher.addCollider(self.playerCollider, self.screen.camera) # ajouter le collider au systeme de poussée

        # Rayon sol
        floorRay = CollisionRay(0, 0, 0, 0, 0, -1)  # rayon pointant vers le bas
        floorNode = CollisionNode('floor-ray') # creer un node de collision pour le rayon du sol
        floorNode.addSolid(floorRay) # ajouter le rayon de collision au node
        floorNode.setFromCollideMask(self.game.worldMask) # rendre ces nodes "from" pour la mask du monde
        floorNode.setIntoCollideMask(BitMask32.allOff()) # desactiver les collisions "into" pour le rayon du sol
        self.floorRayNP = self.screen.camera.attachNewNode(floorNode) # attacher le node de collision a la camera
        self.floorQueue = self.game.floorQueue # utiliser le gestionnaire de collision du sol
        self.game.cTrav.addCollider(self.floorRayNP, self.floorQueue) # ajouter le collider au systeme de collision

    def update(self, dt):
        """update les actions du joueur.
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        
        if self.health > 0: # regarde si le joueur n'est pas mort
            if self.keyMap["Sprint"]:
                self.moveSpeed = self.initialSpeed*2
            else:
                self.moveSpeed = self.initialSpeed
            
            self.updateMovement(dt) # on modifie sa position dans l'espace
            self.updateMouseLook(dt) # on modifie sa vision

            # logique pour l'attaque ( a modifier quand y'aura pls monstre )
            if self.keyMap["attaque"] and not self.is_attacking: # si le joueur appuye sur la touche pour attaquer
                for monster in self.game.monsters:
                    distance = monster.getDistanceToPlayer() # on regarde la distance
                    # on regarde si le joueur est a la bonne distance
                    Is_attack_range = True
                    for elt in distance:
                        if self.weapon == None and abs(elt) > 3: # si le joueur n'a pas d'arme
                            Is_attack_range = False # le monstre est trop loin
                        elif self.weapon != None and abs(elt) > self.weapon.range: # si le joueur a une arme
                            Is_attack_range = False # le monstre est trop loin
                    if Is_attack_range:
                        self.attaque(monster) # on attaque
                        self.is_attacking = True # on indique su'il est en train d'attaquer
                    self.keyMap["attaque"] = False # On remet a 0 la touche pour pas attaquer

            # logique pour savoir s'il est tjs en train d'attaquer
            if self.is_attacking:
                if self.weapon.cooldown <= 0: # si plus de cooldown alors on peut reattaquer
                    self.is_attacking = False
                    self.weapon.cooldown = self.weapon.initialCooldown # on remet le cooldown a son etat de depart
                else:
                    self.weapon.cooldown -= dt # sinon, on enleve le temps qui c'est passé
        else:
            self.died()
        
    def updateMovement(self, dt):
        """faire deplacer le joueur.
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        # Mouvement horizontal
        x_movement = 0 # en x
        y_movement = 0 # en y

        if self.keyMap['forward']: # s'il se deplace vers l'avant
            x_movement -= dt * self.moveSpeed * sin(degToRad(self.screen.camera.getH()))
            y_movement += dt * self.moveSpeed * cos(degToRad(self.screen.camera.getH()))
        if self.keyMap['backward']: # s'il se deplace vers l'arriere
            x_movement += dt * self.moveSpeed * sin(degToRad(self.screen.camera.getH()))
            y_movement -= dt * self.moveSpeed * cos(degToRad(self.screen.camera.getH()))
        if self.keyMap['left']: # s'il se deplace vers la gauche
            x_movement -= dt * self.moveSpeed * cos(degToRad(self.screen.camera.getH()))
            y_movement -= dt * self.moveSpeed * sin(degToRad(self.screen.camera.getH()))
        if self.keyMap['right']: # s'il se deplace vers la droite
            x_movement += dt * self.moveSpeed * cos(degToRad(self.screen.camera.getH()))
            y_movement += dt * self.moveSpeed * sin(degToRad(self.screen.camera.getH()))

        # Saut et traversée
        if self.keyMap['up'] and self.onGround:
            self.zVel = self.jumpSpeed # ajout de la velocité vers le haut
            self.onGround = False # il n'est plus sur le sol
            
        if self.keyMap['down']:
            if hasattr(self, "playerCollider"): # regarder s"il n'y a pas des collision qui nous empêche de descendre
                self.playerCollider.node().setFromCollideMask(BitMask32.allOff()) #descandre
        else:
            if hasattr(self, "playerCollider"): # on regarde si on ne tombe pas
                self.playerCollider.node().setFromCollideMask(self.game.worldMask)

        # Application mouvement
        # sur la camera
        self.screen.camera.setPos( 
            self.screen.camera.getX() + x_movement, #axe X
            self.screen.camera.getY() + y_movement, #axe Y
            self.screen.camera.getZ() #axe Z
        )
        # sur le joueur
        self.position[0] += x_movement #axe X
        self.position[1] += y_movement #axe Y
        

        # Gravité
        newZ = self.screen.camera.getZ()
        self.zVel += self.gravity * dt # changer le velosité sur l'axe Z en fonction de la gravité
        newZ = self.screen.camera.getZ() + self.zVel * dt # nouvelle valeur position Z du joueur

        # Detection sol
        if self.floorQueue.getNumEntries() > 0:
            self.floorQueue.sortEntries() # trier les collisions du sol
            entry = self.floorQueue.getEntry(0) # prendre la premiere collision (la plus proche)
            surfaceZ = entry.getSurfacePoint(self.screen.render).getZ() #recuperer la hauteur du sol en dessous du joueur
            dist = self.screen.camera.getZ() - surfaceZ #distance entre la camera et le sol
            if dist <= 2 and self.zVel <= 0: # on est sur le sol
                self.onGround = True # le joueur est sur le sol
                self.zVel = 0.0 # remetre notre velocité d'axe Z a 0
                newZ = surfaceZ + 2.0 # remetre la position Z du joueur a 0
            else: # on n'est pas sur le sol
                self.onGround = False

        self.screen.camera.setZ(newZ) #changer la position Z de la camera
        self.position[2] = newZ #axe Z

    def updateMouseLook(self, dt):
        """update la vision du joueur
        Args:
            dt (float): temps qui c passer depuis la derniere update
        Returns:
            None
        """
        if self.cameraSwingActivated: 
            if not self.screen.win.getProperties().getForeground(): # verifier si la fenetre est en arriere plan
                self.releaseMouse() #liberation de la sourie
            else:
                wp = self.screen.win.getProperties() # obtenir les propriétés de la fenêtre
                cx = int(wp.getXSize() / 2) # calculer le centre X
                cy = int(wp.getYSize() / 2) # calculer le centre Y

                md = self.screen.win.getPointer(0) # obtenir la position actuelle de la souris
                mouseX = md.getX() # obtenir la coordonnée X de la souris
                mouseY = md.getY() # obtenir la coordonnée Y de la souris

                mouseChangeX = mouseX - cx # calculer le changement en X
                mouseChangeY = mouseY - cy # calculer le changement en Y

                currentH = self.screen.camera.getH() # obtenir l'angle de lacamera en H
                currentP = self.screen.camera.getP() # obtenir l'angle de la camera en P

                self.screen.camera.setHpr(
                    currentH - mouseChangeX * dt * self.cameraSwingFactor,
                    min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                    0
                ) # mettre a jour l'angle de la camera
                
                self.screen.win.movePointer(0, cx, cy) # repositionner la souris au centre

    def updateKeyMap(self, key, value):
        """charger les touches que le joueur utilise.
        Args:
            key (str): nom de l'action
            value (bool): valeur de la key
        Returns:
            None
        """
        self.keyMap[key] = value # mettre a jour l'état de la touche

    def captureMouse(self):
        """activer les mouvements de la camera.
        Args:
            None
        Returns:
            None
        """
        self.cameraSwingActivated = True # activer le mouvement de la camera
        properties = WindowProperties() # creer des proprietes de fenetre
        properties.setCursorHidden(True) # cacher le curseur
        properties.setMouseMode(WindowProperties.M_confined) # confiner la souris dans la fenêtre
        self.screen.win.requestProperties(properties) # appliquer les proprietes a la fenetre
        
        wp = self.screen.win.getProperties() # obtenir les propriétés de la fenêtre
        self.screen.win.movePointer(0, int(wp.getXSize() / 2), int(wp.getYSize() / 2)) # positionner la souris au centre

    def releaseMouse(self):
        """desactiver les mouvements de la camera.
        Args:
            None
        Returns:
            None
        """
        self.cameraSwingActivated = False # desactiver le mouvement de la camera
        properties = WindowProperties() # creer des proprietes de fenetre
        properties.setCursorHidden(False) # afficher le curseur
        properties.setMouseMode(WindowProperties.M_absolute) # liberer la souris
        self.screen.win.requestProperties(properties) # appliquer les proprietes a la fenetre

    def attaque(self, target):
        """attaque du joueur.
        Args:
            target (Target): cible
        Returns:
            None
        """
        if target in self.game.monsters:
            if self.weapon != None:
                target.changeHealth(self.weapon.degats)
            else:
                target.changeHealth(2)

    def died(self):
        self.crosshairs.destroy()
        self.fond.removeNode()
        self.barre.removeNode()

        self.message = OnscreenText(
            text="Vous etes mort",
            pos=(0, 0),
            scale=0.2,
            fg=(1, 0, 0, 1)
        )
        