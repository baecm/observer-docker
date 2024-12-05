class Meta:
    def __init__(self, loader):
        for key, value in loader.data.items():
            setattr(self, key, value['meta'])
