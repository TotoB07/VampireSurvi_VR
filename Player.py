from math import pi, sin, cos
from panda3d.core import CollisionNode, CollisionSphere, CollisionRay, BitMask32
from panda3d.core import TransparencyAttrib, WindowProperties
from direct.gui.OnscreenImage import OnscreenImage

def degToRad(deg):
    return deg * (pi / 180)

class Player():
    def __init__(self, game, position):
        self.game = game  # référence vers la classe principale
        self.health = 100
        self.maxhealth = 100
        self.position = position
        
        # Physique
        self.zVel = 0.0
        self.gravity = -20.0
        self.jumpSpeed = 10.0
        self.onGround = False
        self.moveSpeed = 10
        
        # Contrôles
        self.setupControls()
        self.setupCamera()
        
        # État de la souris
        self.cameraSwingActivated = False
        self.cameraSwingFactor = 10

    def setupControls(self):
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        
        # Binding des touches
        self.game.accept("escape", self.releaseMouse)
        self.game.accept("mouse1", self.captureMouse)
        self.game.accept("z", self.updateKeyMap, ["forward", True])
        self.game.accept("z-up", self.updateKeyMap, ["forward", False])
        self.game.accept("s", self.updateKeyMap, ["backward", True])
        self.game.accept("s-up", self.updateKeyMap, ["backward", False])
        self.game.accept("q", self.updateKeyMap, ["left", True])
        self.game.accept("q-up", self.updateKeyMap, ["left", False])
        self.game.accept("d", self.updateKeyMap, ["right", True])
        self.game.accept("d-up", self.updateKeyMap, ["right", False])
        self.game.accept("space", self.updateKeyMap, ["up", True])
        self.game.accept("space-up", self.updateKeyMap, ["up", False])
        self.game.accept("lshift", self.updateKeyMap, ["down", True])
        self.game.accept("lshift-up", self.updateKeyMap, ["down", False])

    def setupCamera(self):
        self.game.disableMouse()
        self.game.camera.setPos(0, 0, 6)
        
        # Crosshair
        self.crosshairs = OnscreenImage(
            image='img/crosshairs.png', 
            pos=(0, 0, 0), 
            scale=0.05
        )
        self.crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        # Collisions
        self.setupCollisions()

    def setupCollisions(self):
        # Collider joueur
        playerNode = CollisionNode('player-collider')
        playerNode.addSolid(CollisionSphere(0, 0, 0, 0.5))
        playerNode.setFromCollideMask(self.game.worldMask)
        playerNode.setIntoCollideMask(BitMask32.allOff())
        self.playerCollider = self.game.camera.attachNewNode(playerNode)
        self.game.cTrav.addCollider(self.playerCollider, self.game.pusher)
        self.game.pusher.addCollider(self.playerCollider, self.game.camera)

        # Rayon sol
        floorRay = CollisionRay(0, 0, 0, 0, 0, -1)
        floorNode = CollisionNode('floor-ray')
        floorNode.addSolid(floorRay)
        floorNode.setFromCollideMask(self.game.worldMask)
        floorNode.setIntoCollideMask(BitMask32.allOff())
        self.floorRayNP = self.game.camera.attachNewNode(floorNode)
        self.floorQueue = self.game.floorQueue
        self.game.cTrav.addCollider(self.floorRayNP, self.floorQueue)

    def update(self, dt):

        if self.health > 0:
            self.updateMovement(dt)
            self.updateMouseLook(dt)
        else:
            print("Player is dead")  # Gérer la mort du joueur ici
        
    def updateMovement(self, dt):
        # Mouvement horizontal
        x_movement = 0
        y_movement = 0

        if self.keyMap['forward']:
            x_movement -= dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))
            y_movement += dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
        if self.keyMap['backward']:
            x_movement += dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))
            y_movement -= dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
        if self.keyMap['left']:
            x_movement -= dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
            y_movement -= dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))
        if self.keyMap['right']:
            x_movement += dt * self.moveSpeed * cos(degToRad(self.game.camera.getH()))
            y_movement += dt * self.moveSpeed * sin(degToRad(self.game.camera.getH()))

        # Saut et traversée
        if self.keyMap['up'] and self.onGround:
            self.zVel = self.jumpSpeed
            self.onGround = False
            
        if self.keyMap['down']:
            if hasattr(self, "playerCollider"):
                self.playerCollider.node().setFromCollideMask(BitMask32.allOff())
        else:
            if hasattr(self, "playerCollider"):
                self.playerCollider.node().setFromCollideMask(self.game.worldMask)

        # Application mouvement
        self.game.camera.setPos(
            self.game.camera.getX() + x_movement,
            self.game.camera.getY() + y_movement,
            self.game.camera.getZ()
        )
        self.position[0] += x_movement
        self.position[1] += y_movement
        

        # Gravité
        self.zVel += self.gravity * dt
        newZ = self.game.camera.getZ() + self.zVel * dt

        # Detection sol
        if self.floorQueue.getNumEntries() > 0:
            self.floorQueue.sortEntries()
            entry = self.floorQueue.getEntry(0)
            surfaceZ = entry.getSurfacePoint(self.game.render).getZ()
            dist = self.game.camera.getZ() - surfaceZ
            if dist <= 2 and self.zVel <= 0:
                self.onGround = True
                self.zVel = 0.0
                newZ = surfaceZ + 2.0
            else:
                self.onGround = False

        self.game.camera.setZ(newZ)
        self.position[2] = newZ

    def updateMouseLook(self, dt):
        if self.cameraSwingActivated:
            if not self.game.win.getProperties().getForeground():
                self.releaseMouse()
            else:
                wp = self.game.win.getProperties()
                cx = int(wp.getXSize() / 2)
                cy = int(wp.getYSize() / 2)

                md = self.game.win.getPointer(0)
                mouseX = md.getX()
                mouseY = md.getY()

                mouseChangeX = mouseX - cx
                mouseChangeY = mouseY - cy

                currentH = self.game.camera.getH()
                currentP = self.game.camera.getP()

                self.game.camera.setHpr(
                    currentH - mouseChangeX * dt * self.cameraSwingFactor,
                    min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                    0
                )
                
                self.game.win.movePointer(0, cx, cy)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def captureMouse(self):
        self.cameraSwingActivated = True
        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_confined)
        self.game.win.requestProperties(properties)
        
        wp = self.game.win.getProperties()
        self.game.win.movePointer(0, int(wp.getXSize() / 2), int(wp.getYSize() / 2))

    def releaseMouse(self):
        self.cameraSwingActivated = False
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.game.win.requestProperties(properties)
