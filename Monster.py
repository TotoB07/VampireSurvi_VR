from math import sin, cos, pi
from panda3d.core import Vec3, NodePath
from panda3d.core  import CollisionNode, CollisionBox


def degToRad(deg):
    return deg * (pi / 180)

class Monster:
    def __init__(self, game, position, health, speed, attack_power, attack_range, xp_value, monster_type="normal"):
        self.game = game  # référence vers la partie
        self.position = position
        self.type = monster_type
        self.health = health
        self.speed = speed
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.xp_value = xp_value

        # État
        self.is_alive = True
        self.is_attacking = False

        self.loadMonster()
        
        # - Chargement du modèle 3D
        # - Configuration des collisions
        # - Animation du monstre
        # - Sons du monstre

    def loadMonster(self):
        self.monster = loader.loadModel('model3d/grass-block.glb')
        self.monster.reparentTo(self.game.render)  # Attacher au render
        self.monster.setPos(self.position[0], self.position[1], self.position[2])
        
        blockSolid = CollisionBox((-1,-1,-1), (1,1,1))
        blockNode = CollisionNode('block-collision-node')
        blockNode.addSolid(blockSolid)
        # rendre ces nodes "into" pour la mask du monde
        blockNode.setIntoCollideMask(self.game.worldMask)
        collider = self.monster.attachNewNode(blockNode)
        collider.setPythonTag('owner', self.monster)
        

    def Movement(self, dt, orientation):
        if orientation == "devant":
            self.position[0] -= dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))
            self.position[1] += dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
        elif orientation == "derrière":
            self.position[0] += dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))
            self.position[1] -= dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
        elif orientation == "gauche":
            self.position[0] -= dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
            self.position[1] -= dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))
        elif orientation == "droite":
            self.position[0] += dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
            self.position[1] += dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))

    def attack(self, target):
        if isinstance(self.game.player, target):
            target.health -= self.attack_power
            self.is_attacking = True

    def changeHealth(self, value):
        self.health += value
