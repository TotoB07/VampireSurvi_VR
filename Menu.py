from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectOptionMenu
from panda3d.core import Vec4, loadPrcFileData, TextNode, WindowProperties
from direct.gui.OnscreenText import OnscreenText
import Game

loadPrcFileData("", "win-size 1280 720")

class Menu(ShowBase):
    def __init__(self):
        ShowBase.__init__(self) # initialisation classe parent
        self.create_menu()

        self.bindings = {
            "Sortir": "escape",
            "Avancer": "z",
            "Reculer": "s",
            "Gauche": "q",
            "Droite": "d",
            "Saut": "space",
            "Accroupir": "lshift",
            "Attaque": "mouse3",
            "mouse1": "mouse1"
        }
        
    
    def create_menu(self):
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

    def supprimer_boutons(self):
        self.message.destroy()
        if hasattr(self, 'bouton_jouer'):
            self.bouton_jouer.destroy()
        if hasattr(self, 'bouton_credit'):
            self.bouton_credit.destroy()
        if hasattr(self, 'bouton_quitter'):
            self.bouton_quitter.destroy()
        if hasattr(self, 'bouton_settings'):
            self.bouton_settings.destroy()
        if hasattr(self, 'retour_bouton'):
            self.retour_bouton.destroy()
        if hasattr(self, 'option_resolution'):
            self.option_resolution.destroy()
        if hasattr(self, 'message'):
            self.message.destroy()
        if hasattr(self, 'message_touch'):
            for msg in self.message_touch:
                msg.destroy()
        if hasattr(self, 'bouton_touche'):
            for btn in self.bouton_touche:
                btn.destroy()
        

    def lancer_partie(self):
        self.supprimer_boutons()
        game = Game.MyGame(self)

    def credit(self):
        self.supprimer_boutons()
        self.message = OnscreenText(
            text="Crédits:\nDéveloppeur: Thomas\nGraphismes: Thomas\nMusique: Thomas\n mention speciale a Monokirb qui corrige les erreurs ",
            pos=(0, 0),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )
        self.retour_bouton = DirectButton(
            text="Retour",
            scale=0.07,
            pos=(-1.6,0, 0.9),
            command=self.fermer_settings,
            frameColor=(0.2, 0.4, 0.8, 1),
            text_fg=(1, 1, 1, 1)
        )


    def quitter(self):
        self.userExit()

    def ouvrir_settings(self):
        self.supprimer_boutons()

        self.retour_bouton = DirectButton(
            text="Retour",
            scale=0.07,
            pos=(-1.6, 0, 0.9),
            command=self.fermer_settings,
            frameColor=(0.2, 0.4, 0.8, 1),
            text_fg=(1, 1, 1, 1)
        )

        self.message = OnscreenText(
            text="Resolution :",
            pos=(-1.55, 0.35),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )

        self.option_resolution = DirectOptionMenu(
            text="Résolution",
            scale=0.08,
            items=["800x600", "1280x720", "1920x1080"],
            initialitem=1,
            pos=(-1.3, 0, 0.35),
            command=self.changer_resolution
        )

        #modifier les touches 
        self.message_touch = []
        self.bouton_touche = []
        for elt in self.bindings:
            message = OnscreenText(
                text=f"{elt} : {self.bindings[elt]}",
                pos=(-1.73, 0.2 - list(self.bindings.keys()).index(elt) * 0.1),
                scale=0.07,
                fg=(1, 1, 1, 1),
                align=TextNode.ALeft
            )
            self.message_touch.append(message)
            bouton = DirectButton(
                text="Changer",
                scale=0.07,
                pos=(-1, 0, 0.2 - list(self.bindings.keys()).index(elt) * 0.1),
                command=self.changer_touche,
                extraArgs=[elt]
            )
            self.bouton_touche.append(bouton)

    def fermer_settings(self):
        self.supprimer_boutons()
        self.create_menu()

            
    def changer_touche(self, action):
        def on_key_pressed(key):
            self.bindings[action] = key
            self.supprimer_boutons()
            self.ouvrir_settings()

        # Liste des touches à écouter
        all_keys = [
            "a","b","c","d","e","f","g","h","i","j","k","l","m","n",
            "o","p","q","r","s","t","u","v","w","x","y","z",
            "space","escape","lshift","control","alt","arrow_up",
            "arrow_down","arrow_left","arrow_right","mouse1","mouse2","mouse3"
        ]

        # Écouter chaque touche une seule fois
        for k in all_keys:
            self.acceptOnce(k, lambda key=k: on_key_pressed(key))



    def changer_resolution(self, choix):
        largeur, hauteur = map(int, choix.split('x'))

        # Créer un nouvel objet WindowProperties
        props = WindowProperties()
        props.setSize(largeur, hauteur)   # définir la nouvelle taille
        base.win.requestProperties(props)  # appliquer les nouvelles propriétés



