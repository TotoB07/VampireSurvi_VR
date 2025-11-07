from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile 
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core import TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage

loadPrcFile('settings.prc')

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.loadModels()
        self.setupLights()
        self.generateTerrain()
        self.setupCamera()

    def setupCamera(self):
        self.disableMouse()
        self.camera.setPos(0, 0, 3)
        crosshairs = OnscreenImage(
            image='crosshairs.png', 
            pos=(0, 0, 0), 
            scale=0.05
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)
         

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

    