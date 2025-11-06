from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile 
from panda3d.core import DirectionalLight, AmbientLight

loadPrcFile('settings.prc')

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.loadModels()
        self.setupLights()

    def loadModels(self):
        self.grassBlock = loader.loadModel('grass-block.glb')
        self.grassBlock.reparentTo(render)

        self.dirtBlock = loader.loadModel('dirt-block.glb')
        self.dirtBlock.setPos(0, 2, 0)
        self.dirtBlock.reparentTo(render)

        self.stoneBlock = loader.loadModel('stone-block.glb')
        self.stoneBlock.setPos(0, 4, 0)
        self.stoneBlock.reparentTo(render)

        self.sandBlock = loader.loadModel('sand-block.glb')
        self.sandBlock.setPos(0, 6, 0)
        self.sandBlock.reparentTo(render)

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

    