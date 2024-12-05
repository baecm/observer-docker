import numpy as np


class Terrain:
    def __init__(self, loader):
        for key, value in loader.data.items():
            setattr(self, key, value['terrain'])

        self.terrain = np.concatenate([np.asarray(t.strip().split(
            ','), dtype=int) for t in terrain]).reshape(int(meta['height']), int(meta['width']))
        
    def decode(self, ):
        
        pass
