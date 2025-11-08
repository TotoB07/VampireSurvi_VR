#programme
import Player
import Monster

#librairie
from math import pi, sin, cos 

#librairie panda3d
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
        
        self.worldMask = BitMask32.bit(1)
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.floorQueue = CollisionHandlerQueue()

        self.loadModels()
        self.setupLights()
        self.generateTerrain()
        
        # Créer le joueur après avoir initialisé les systèmes nécessaires
        self.player = Player.Player(self)
        self.monster = Monster.Monster(self, (10,10,2), 100, 2, 10, 5, 50)
        
        self.setupSkybox()

        taskMgr.add(self.update, "update")

    def update(self, task):
        dt = globalClock.getDt()
        
        if hasattr(self, "cTrav"):
            self.cTrav.traverse(render)
            
        self.player.update(dt)
        
        return task.cont
        
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
        self.grassBlock = loader.loadModel('model3d/grass-block.glb')
        self.dirtBlock = loader.loadModel('model3d/dirt-block.glb')
        self.stoneBlock = loader.loadModel('model3d/stone-block.glb')
        self.sandBlock = loader.loadModel('model3d/sand-block.glb')

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

    