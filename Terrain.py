#librairies panda3d
from panda3d.core  import CollisionNode, CollisionBox

class Terrain():
    """Classe représentant le terrain."""
    def __init__(self, game, block):
        """Initialisation du terrain.
        Args:
            game (Game): reference vers la classe principale
            block (dico): block du jeu
        Returns:
            None
        """
        self.game = game # instance de la partie
        self.block = block # dico avec les blocks du jeu

        self.generateTerrain() # generation du terrain
        


    def generateTerrain(self):
        """generation du terrain.
        Args:
            None
        Returns:
            None
        """
        for z in range(10):
            for y in range(20):
                for x in range(20):
                    newBlockNode = render.attachNewNode('new-block_placeholder') # creation d'un noeud
                    newBlockNode.setPos(x*2 -20, y*2 -20, -z *2) # position du noeud

                    if z == 0:
                        self.block["grassBlock"].instanceTo(newBlockNode)  # mettre le noeud comme un grassBlock
                    elif z < 4:
                        self.block["dirtBlock"].instanceTo(newBlockNode) # mettre le noeud comme un dirtBlock
                    else:
                        self.block["stoneBlock"].instanceTo(newBlockNode) # mettre le noeud comme un stoneBlock
                    
                    blockSolid = CollisionBox((-1,-1,-1), (1,1,1)) # creation de la boite de collision
                    blockNode = CollisionNode('block-collision-node') # creation du node de collision
                    blockNode.addSolid(blockSolid) # ajout de la boite de collision au node
                    blockNode.setIntoCollideMask(self.game.worldMask) # definir le masque de collision
                    collider = newBlockNode.attachNewNode(blockNode) # attacher le node de collision au noeud du block
                    collider.setPythonTag('owner', newBlockNode) # tag python pour référencer le block