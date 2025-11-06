from direct.showbase.ShowBase import ShowBase

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        loader.loadModel('grass-block.glb')

if __name__ == "__main__":
    app = MyGame()
    app.run()

    