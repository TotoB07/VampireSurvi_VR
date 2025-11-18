#librairies
import random
from perlin_noise import PerlinNoise

#librairies panda3d
from panda3d.core import CollisionNode, CollisionBox, BitMask32

class Terrain():
    """Classe représentant le terrain."""
    def __init__(self, game, blocks):
        """Initialisation du terrain.
        Args:
            game (Game): reference vers la classe principale
            blocks (dict): dictionnaire avec les blocks du jeu
        Returns:
            None
        """
        self.game = game # reference vers la classe principale
        self.blocks = blocks # dictionnaire avec les blocks du jeu
        self.screen = game.screen # reference vers l'écran du jeu
        
        # Paramètres du terrain
        self.terrain_width = 75
        self.terrain_length = 75
        self.max_height = 10
        self.block_size = 2
        
        # Seed pour la génération aléatoire reproductible
        self.seed = random.randint(0, 10000)
        self.noise = PerlinNoise(octaves=0.6, seed=self.seed)
        
        self.terrain_blocks = []  # Liste pour garder track des blocks
        self.generateTerrain()

    def generateTerrain(self):
        """Génère le terrain avec hauteurs aléatoires (bruit Perlin).
        Args:
            None
        Returns:
            None
        """
        # Créer un dossier pour le terrain
        terrain_node = self.screen.render.attachNewNode('terrain')
        
        for y in range(self.terrain_length):
            for x in range(self.terrain_width):
                # Calculer la hauteur avec le bruit Perlin
                noise_value = self.noise([x * 0.1, y * 0.1])
                
                # Convertir en hauteur entière (0 à max_height)
                height = int((noise_value + 1) / 2 * self.max_height)
                height = max(0, min(height, self.max_height))
                
                # Créer le noeud du bloc
                block_node = terrain_node.attachNewNode(f'block_{x}_{y}_{height}')
                block_node.setPos(x * self.block_size, y * self.block_size, height * self.block_size)
                
                # Attacher le modèle du bloc
                self.blocks['grassBlock'].instanceTo(block_node)
                
                # Ajouter la collision
                self.addBlockCollision(block_node)
                
                # Garder une référence
                self.terrain_blocks.append({
                    'node': block_node,
                    'pos': (x * self.block_size, y * self.block_size, height * self.block_size),
                    'type': 'grassBlock'
                })


    def addBlockCollision(self, block_node):
        """Ajoute une collision à un bloc.
        args:
            block_node (NodePath): le noeud du bloc auquel ajouter la collision
        Returns:
            None
        """
        blockSolid = CollisionBox((-1, -1, -1), (1, 1, 1)) # Créer une boîte de collision
        blockNode = CollisionNode('block-collision') # Créer un noeud de collision
        blockNode.addSolid(blockSolid) # Ajouter la boîte solide au noeud de collision
        blockNode.setIntoCollideMask(self.game.worldMask) # Définir le masque de collision
        collider = block_node.attachNewNode(blockNode) # Attacher le noeud de collision au bloc
        collider.setPythonTag('owner', block_node) # Tag pour référence future

    def unloadTerrain(self):
        """Décharge le terrain de la mémoire.
        Args:
            None
        Returns:
            None
        """
        for block in self.terrain_blocks:
            block['node'].removeNode() # Supprimer le noeud du bloc
        self.terrain_blocks.clear() # Vider la liste des blocks

    def getSurfaceLevel(self, x, y):
        """Obtient le niveau de surface (hauteur) à une position donnée.
        Args:
            x (float): position x
            y (float): position y
        Returns:
            float: niveau de surface (hauteur) à la position donnée
        """
        liste = [] # liste des hauteurs des blocks à la position (x, y)
        for elt in self.terrain_blocks:
            if elt['pos'][0] >= x and elt['pos'][0] < x + self.block_size and elt['pos'][1] >= y and elt['pos'][1] < y + self.block_size: 
                liste.append(elt['pos'][2]) # ajouter la hauteur du block à la liste
        if liste != []:
            return max(liste) # retourner la hauteur maximale trouvée
        return 0 # si aucun block trouvé, retourner 0