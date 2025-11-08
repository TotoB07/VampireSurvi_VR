from math import pi, sin, cos 

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile 
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core import TransparencyAttrib
from panda3d.core import WindowProperties
from panda3d.core  import CollisionTraverser, CollisionNode, CollisionBox, CollisionRay, CollisionHandlerQueue
from panda3d.core  import CollisionHandlerPusher, CollisionSphere, BitMask32
from direct.gui.OnscreenImage import OnscreenImage


loadPrcFile('settings.prc')

def degToRad(deg):
    return deg * (pi / 180)

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # physique du joueur
        self.zVel = 0.0
        self.gravity = -20.0
        self.jumpSpeed = 7.0
        self.onGround = False
        # mask utilisé pour les collisions "sol / blocs"
        self.worldMask = BitMask32.bit(1)

        self.loadModels()
        self.setupLights()
        self.generateTerrain()
        self.setupCamera()
        self.setupSkybox()
        self.captureMouse()
        self.setupControls()

        taskMgr.add(self.update, "update")

    def update(self, task):
        dt = globalClock.getDt()

        playerMoveSpeed = 10

        x_movement = 0
        y_movement = 0

        if self.keyMap['forward']:
            x_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
        if self.keyMap['backward']:
            x_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
        if self.keyMap['left']:
            x_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        if self.keyMap['right']:
            x_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        # gestion saut / tomber
        if self.keyMap['up'] and self.onGround:
            # on ne peut sauter que si on est au sol
            self.zVel = self.jumpSpeed
            self.onGround = False
        # si on maintient LShift, on veut passer à travers les blocs vers le bas :
        if self.keyMap['down']:
            # désactiver temporairement le collider "from" du joueur pour traverser
            if hasattr(self, "playerCollider"):
                self.playerCollider.node().setFromCollideMask(BitMask32.allOff())
        else:
            # réactiver
            if hasattr(self, "playerCollider"):
                self.playerCollider.node().setFromCollideMask(self.worldMask)

        camera.setPos(
            camera.getX() + x_movement,
            camera.getY() + y_movement,
            camera.getZ()
        )

        # lancer la traversée de collision pour mettre à jour self.rayQueue
        if hasattr(self, "cTrav"):
            self.cTrav.traverse(render)
            # ici tu peux lire self.rayQueue pour voir les collisions si besoin

        # appliquer gravité et mouvement vertical
        self.zVel += self.gravity * dt
        newZ = self.camera.getZ() + self.zVel * dt

        # lire la queue du rayon vers le bas pour détecter le sol
        if hasattr(self, "floorQueue"):
            if self.floorQueue.getNumEntries() > 0:
                self.floorQueue.sortEntries()
                entry = self.floorQueue.getEntry(0)
                surfacePt = entry.getSurfacePoint(render)
                surfaceZ = surfacePt.getZ()
                # distance entre la caméra et la surface juste en dessous
                dist = self.camera.getZ() - surfaceZ
                # ajuster seuil en fonction de la "hauteur" du joueur (ici ~1.0)
                groundThreshold = 1.1
                if dist <= groundThreshold and self.zVel <= 0:
                    # on est au sol : bloquer la chute et remettre la caméra sur le sol
                    self.onGround = True
                    self.zVel = 0.0
                    newZ = surfaceZ + 1.0
                else:
                    self.onGround = False

        # appliquer la nouvelle position Z
        self.camera.setZ(newZ)


        if self.cameraSwingActivated:
            # si on perd le focus, relâcher la souris pour éviter blocage
            if not self.win.getProperties().getForeground():
                self.releaseMouse()
            else:
                wp = self.win.getProperties()
                cx = int(wp.getXSize() / 2)
                cy = int(wp.getYSize() / 2)

                md = self.win.getPointer(0)
                mouseX = md.getX()
                mouseY = md.getY()

                # Calculer le changement par rapport au centre
                mouseChangeX = mouseX - cx
                mouseChangeY = mouseY - cy

                
                self.cameraSwingFactor = 10

                currentH = self.camera.getH()
                currentP = self.camera.getP()

                self.camera.setHpr(
                    currentH - mouseChangeX * dt * self.cameraSwingFactor,
                    min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                    0
                )
                # recentrer la souris
                self.win.movePointer(0, cx, cy)

        return task.cont

    def setupControls(self):
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.accept("escape", self.releaseMouse)
        self.accept("mouse1", self.captureMouse)

        self.accept("z", self.updateKeyMap, ["forward", True])
        self.accept("z-up", self.updateKeyMap, ["forward", False])
        self.accept("s", self.updateKeyMap, ["backward", True])
        self.accept("s-up", self.updateKeyMap, ["backward", False])
        self.accept("q", self.updateKeyMap, ["left", True])
        self.accept("q-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("space", self.updateKeyMap, ["up", True])
        self.accept("space-up", self.updateKeyMap, ["up", False])
        self.accept("lshift", self.updateKeyMap, ["down", True])
        self.accept("lshift-up", self.updateKeyMap, ["down", False])

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def captureMouse(self):
        self.cameraSwingActivated = True
        # mettre la souris cachée et en mode relatif, puis recentrer immédiatement
        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_confined)  # ou M_confined pour garder le curseur dans la fenêtre
        self.win.requestProperties(properties)

        # recentrer la souris
        wp = self.win.getProperties()
        cx = int(wp.getXSize() / 2)
        cy = int(wp.getYSize() / 2)
        self.win.movePointer(0, cx, cy)

        
    def releaseMouse(self):
        self.cameraSwingActivated = False
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def setupCamera(self):
        self.disableMouse()
        self.camera.setPos(0, 0, 3)
        crosshairs = OnscreenImage(
            image='crosshairs.png', 
            pos=(0, 0, 0), 
            scale=0.05
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        self.cTrav = CollisionTraverser()
        # collider "player" (utilisé par le Pusher)
        self.pusher = CollisionHandlerPusher()
        playerNode = CollisionNode('player-collider')
        playerNode.addSolid(CollisionSphere(0, 0, 0, 0.5))
        playerNode.setFromCollideMask(self.worldMask)
        playerNode.setIntoCollideMask(BitMask32.allOff())
        self.playerCollider = self.camera.attachNewNode(playerNode)
        self.cTrav.addCollider(self.playerCollider, self.pusher)
        self.pusher.addCollider(self.playerCollider, self.camera)

        # rayon vers le bas pour détecter le sol
        floorRay = CollisionRay(0, 0, 0, 0, 0, -1)
        floorNode = CollisionNode('floor-ray')
        floorNode.addSolid(floorRay)
        floorNode.setFromCollideMask(self.worldMask)
        floorNode.setIntoCollideMask(BitMask32.allOff())
        self.floorRayNP = self.camera.attachNewNode(floorNode)
        self.floorQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.floorRayNP, self.floorQueue)
 
        

        
    def setupSkybox(self):
        skybox = loader.loadModel('skybox/skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)



    def generateTerrain(self):
        for z in range(10):
            for y in range(20):
                for x in range(20):
                    newBlockNode = render.attachNewNode('new-block_placeholder')
                    newBlockNode.setPos(x*2 -20, y*2 -20, -z *2)

                    if z == 0:
                        self.grassBlock.instanceTo(newBlockNode)
                    elif z < 4:
                        self.dirtBlock.instanceTo(newBlockNode)
                    else:
                        self.stoneBlock.instanceTo(newBlockNode)
                    
                    blockSolid = CollisionBox((-1,-1,-1), (1,1,1))
                    blockNode = CollisionNode('block-collision-node')
                    blockNode.addSolid(blockSolid)
                    # rendre ces nodes "into" pour la mask du monde
                    blockNode.setIntoCollideMask(self.worldMask)
                    collider = newBlockNode.attachNewNode(blockNode)
                    collider.setPythonTag('owner', newBlockNode)

    def loadModels(self):
        self.grassBlock = loader.loadModel('grass-block.glb')
        self.dirtBlock = loader.loadModel('dirt-block.glb')
        self.stoneBlock = loader.loadModel('stone-block.glb')
        self.sandBlock = loader.loadModel('sand-block.glb')

    def setupLights(self):
        mainLight = DirectionalLight('mainLight')
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(30, -60, 0)
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)

if __name__ == "__main__":
    app = MyGame()
    app.run()

    