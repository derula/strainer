from lark import Token


class SemanticError(Exception):
    def __init__(self, token: Token, message: str):
        self.line = token.line
        self.column = token.column
        super().__init__(f'Semantic error in line {token.line}, column {token.column}: {message}')
