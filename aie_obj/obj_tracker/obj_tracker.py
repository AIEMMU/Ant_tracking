class obj_tracker():
    def __init__(self, layers):
        self.layers = layers

    def __call__(self, x):
        for l in self.layers: x = l(x)
        return x

