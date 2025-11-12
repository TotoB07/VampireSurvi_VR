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
            text="Nom du jeu",
            pos=(0, 0.35),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )

        self.bouton_jouer = DirectButton(
            text="Jouer",
            scale=0.1,
            pos=(0, 0, -0.15),
            command=self.lancer_partie
        )

        self.bouton_credit = DirectButton(
            text="Crédits",
            scale=0.1,
            pos=(0, 0, -0.3),
            command=self.credit
        )

        self.bouton_quitter = DirectButton(
            text="Quitter",
            scale=0.1,
            pos=(0, 0, -0.45),
            command=self.quitter,
            frameColor=(0.6, 0.1, 0.1, 1),
            text_fg=(1, 1, 1, 1)  
        )

        self.bouton_settings = DirectButton(
            text="settings",
            scale=0.07,
            pos=(-1.6, 0, 0.9),        # 🔹 haut gauche
            command=self.ouvrir_settings,
            frameColor=(0.2, 0.4, 0.8, 1),  # bleu
            text_fg=(1, 1, 1, 1)
        )

    def lancer_partie(self):
        self.message.destroy()
        self.bouton_jouer.destroy()
        self.bouton_quitter.destroy()
        self.bouton_credit.destroy()
        game = Game.MyGame(self)

    def credit(self):
        return

    def quitter(self):
        self.userExit()

    def ouvrir_settings(self):
        return



