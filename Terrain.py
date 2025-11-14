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
        self.game = game
        self.blocks = blocks
        self.screen = game.screen
        
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
        """Génère le terrain avec hauteurs aléatoires (bruit Perlin)."""
        # Créer un dossier pour le terrain
        terrain_node = self.screen.render.attachNewNode('terrain')
        
        for y in range(self.terrain_length):
            for x in range(self.terrain_width):
                # Calculer la hauteur avec le bruit Perlin
                noise_value = self.noise([x * 0.1, y * 0.1])
                
                # Convertir en hauteur entière (0 à max_height)
                height = int((noise_value + 1) / 2 * self.max_height)
                height = max(0, min(height, self.max_height))
                
                # Générer les blocs de la surface jusqu'à la bedrock
                block_pos_x = x * self.block_size - (self.terrain_width * self.block_size / 2)
                block_pos_y = y * self.block_size - (self.terrain_length * self.block_size / 2)
                block_pos_z = (height * self.block_size) - self.max_height
                
                # Créer le noeud du bloc
                block_node = terrain_node.attachNewNode(f'block_{x}_{y}_{height}')
                block_node.setPos(block_pos_x, block_pos_y, block_pos_z)
                
                # Déterminer le type de bloc
                block_type = self.getBlockType(height, height)
                
                # Attacher le modèle du bloc
                self.blocks[block_type].instanceTo(block_node)
                
                # Ajouter la collision
                self.addBlockCollision(block_node)
                
                # Garder une référence
                self.terrain_blocks.append({
                    'node': block_node,
                    'pos': (x, y, height),
                    'type': block_type
                })

    def getBlockType(self, z, surface_height):
        """Détermine le type de bloc selon sa profondeur."""
        if z == surface_height:
            return 'grassBlock'
        elif z < surface_height and z > surface_height - 3 :
            return 'dirtBlock'
        else:
            return 'stoneBlock'

    def addBlockCollision(self, block_node):
        """Ajoute une collision à un bloc."""
        blockSolid = CollisionBox((-1, -1, -1), (1, 1, 1))
        blockNode = CollisionNode('block-collision')
        blockNode.addSolid(blockSolid)
        blockNode.setIntoCollideMask(self.game.worldMask)
        collider = block_node.attachNewNode(blockNode)
        collider.setPythonTag('owner', block_node)

    def unloadTerrain(self):
        """Décharge le terrain de la mémoire."""
        for block in self.terrain_blocks:
            block['node'].removeNode()
        self.terrain_blocks.clear()