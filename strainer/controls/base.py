class MyActionWidget:
    _text = ''

    def __init__(self, parent):
        super().__init__(self._text, parent)
        self._actions = []
        for action in self.__class__._actions:
            if action:
                action = parent.action(action)
                self.addAction(action)
            else:
                self.addSeparator()
