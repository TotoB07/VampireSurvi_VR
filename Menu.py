from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton
from panda3d.core import Vec4, loadPrcFileData, TextNode
from direct.gui.OnscreenText import OnscreenText
import Game

loadPrcFileData("", "win-size 1280 720")

class Menu(ShowBase):
    def __init__(self):
        ShowBase.__init__(self) # initialisation classe parent
        
        self.setBackgroundColor(Vec4(0, 0, 0, 1))
        self.message = OnscreenText(
            text="Appuyez sur Entrée pour commencer",
            pos=(0, 0),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )

        self.bouton_jouer = DirectButton(
            text="Jouer",
            scale=0.1,
            pos=(0, 0, -0.1),
            command=self.lancer_partie
        )

    def lancer_partie(self):
        self.message.destroy()
        self.bouton_jouer.destroy()
        game = Game.MyGame(self)



