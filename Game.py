#programmes
import Player, GameManager
import Terrain
import Weapon
import random

#librairies
from math import pi, sin, cos 

#librairies panda3d
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core  import CollisionTraverser, CollisionHandlerQueue
from panda3d.core  import CollisionHandlerPusher, BitMask32
from pandac.PandaModules import ClockObject
FPS = 30
globalClock = ClockObject.getGlobalClock()
globalClock.setMode(ClockObject.MLimited)
globalClock.setFrameRate(FPS)

loadPrcFile('ressources/settings.prc') # charger les paramètres de configuration

def degToRad(deg):
    """Convertir des degrés en radiants.
    Args:
        deg (float): angle en degrés
    Returns:
        float: angle en radiants
    """
    return deg * (pi / 180)

class MyGame():
    """Classe représentant la partie."""
    def __init__(self, menu):
        """Initialisation de la partie.
        Args:
            None
        Returns:
            None
        """
        self.block = {} #dico des differents blocks du jeu
        self.menu = menu
        self.screen = self.menu
        self.gametime = 0
        
        self.worldMask = BitMask32.bit(1) #creation masque 1er etage
        self.cTrav = CollisionTraverser() # gestionnaire de collisions
        self.pusher = CollisionHandlerPusher() # gestionnaire de poussée
        self.floorQueue = CollisionHandlerQueue() # gestionnaire de collisions pour le sol

        self.loadModels() # appel methode loadModels
        self.setupLights() # appel methode setupLights
        
        self.terrain = Terrain.Terrain(self, self.block) # creation terrain
        self.GameManager = GameManager.GameManagement(self)
        self.player = Player.Player(self, [30,30,self.terrain.max_height * self.terrain.block_size]) # creation player
        self.weapon = Weapon.Weapon("Épée en bois", "Une épée basique en bois.", 100, 4, 1.0) # creation arme
        self.monsters = []
        
        self.player.weapon = self.weapon # assigner les degats de l'arme au joueur
        
        self.setupSkybox() # appel methode setupSkybox

        taskMgr.add(self.update, "update") # mise à jour


    def update(self, task):
        """update la partie.
        Args:
            task (Task): tâche en cours
        Returns:
            Task.cont: continuer la tâche
        """
        dt = globalClock.getDt() # temps entre chaque frame
        self.gametime += dt
        
        if hasattr(self, "cTrav"): # vérifier si cTrav est défini
            self.cTrav.traverse(render) 
        if self.gametime > 3:
            self.player.update(dt) #update le player
            self.GameManager.update(dt)
            for monster in self.monsters:
                monster.update(dt) #update le monstre
        
        return task.cont
        
    def setupSkybox(self):
        """création ciel en fond.
        Args:
            None
        Returns:
            None
        """
        skybox = loader.loadModel('skybox/skybox.egg')  # charger le modèle de la skybox
        skybox.setScale(500) # mettre la taille de la skybox a 500
        skybox.setBin('background', 1) # définir la skybox comme arrière-plan
        skybox.setDepthWrite(0) # désactiver l'écriture de la profondeur
        skybox.setLightOff() # désactiver l'éclairage pour la skybox
        skybox.reparentTo(render) # attacher la skybox au render

    def loadModels(self):
        """chargement des modèles 3D.
        Args:
            None
        Returns:
            None
        """
        self.block["grassBlock"] = loader.loadModel('model3d/grass-block.glb') # charger le model grass block
        self.block["dirtBlock"] = loader.loadModel('model3d/dirt-block.glb') # charger le model dirt block
        self.block["stoneBlock"] = loader.loadModel('model3d/stone-block.glb') # charger le model stone block
        self.block["sandBlock"] = loader.loadModel('model3d/sand-block.glb') # charger le model sand block

    def setupLights(self):
        """setup les lumieres.
        Args:
            None
        Returns:
            None
        """
        mainLight = DirectionalLight('mainLight') # creer une lumiere directionnelle
        mainLightNodePath = render.attachNewNode(mainLight) # attacher la lumiere au render
        mainLightNodePath.setHpr(30, -60, 0) # orienter la lumiere
        render.setLight(mainLightNodePath) # activer la lumiere dans le render

        ambientLight = AmbientLight('ambient light') # creer une lumiere ambiante
        ambientLight.setColor((0.3, 0.3, 0.3, 1)) # definir la couleur de la lumiere ambiante
        ambientLightNodePath = render.attachNewNode(ambientLight) # attacher la lumiere au render
        render.setLight(ambientLightNodePath) # activer la lumiere dans le render



    