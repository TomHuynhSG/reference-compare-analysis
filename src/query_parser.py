"""
Query Parser for Boolean Search Queries

Parses complex Boolean search queries with AND/OR operators, parentheses,
quoted phrases, and wildcard support.

Example queries:
- Simple: "LLM"
- OR: "LLM OR GPT"
- AND: "LLM AND Risk"
- Complex: ("Large Language Model*" OR "LLM") AND "Risk of bias"
"""

import re
from typing import List, Union, Dict, Any


class QuerySyntaxError(Exception):
    """Raised when query syntax is invalid"""
    pass


class ASTNode:
    """Base class for Abstract Syntax Tree nodes"""
    pass


class TermNode(ASTNode):
    """Leaf node representing a search term or phrase"""
    def __init__(self, term: str, is_phrase: bool = False):
        self.term = term
        self.is_phrase = is_phrase
        
    def __repr__(self):
        if self.is_phrase:
            return f'Term("{self.term}")'
        return f'Term({self.term})'


class OperatorNode(ASTNode):
    """Node representing AND or OR operator"""
    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.operator = operator.upper()
        self.left = left
        self.right = right
        
    def __repr__(self):
        return f'({self.left} {self.operator} {self.right})'


def tokenize(query: str) -> List[str]:
    """
    Tokenize query string into terms, operators, and parentheses.
    
    Handles:
    - Quoted phrases: "Large Language Model"
    - Parentheses: ( )
    - Operators: AND, OR
    - Terms with wildcards: GPT*, *model
    
    Args:
        query: Raw query string
        
    Returns:
        List of tokens
    """
    tokens = []
    i = 0
    query = query.strip()
    
    while i < len(query):
        # Skip whitespace
        if query[i].isspace():
            i += 1
            continue
        
        # Quoted phrase - capture everything inside quotes
        if query[i] == '"':
            j = i + 1
            while j < len(query) and query[j] != '"':
                j += 1
            if j >= len(query):
                raise QuerySyntaxError(f"Unclosed quote at position {i}")
            tokens.append(query[i:j+1])  # Include quotes
            i = j + 1
            continue
        
        # Parentheses
        if query[i] in '()':
            tokens.append(query[i])
            i += 1
            continue
        
        # Word or operator
        j = i
        while j < len(query) and not query[j].isspace() and query[j] not in '()':
            j += 1
        word = query[i:j]
        if word:
            tokens.append(word)
        i = j
    
    return tokens


def parse_query(query: str) -> ASTNode:
    """
    Parse query string into Abstract Syntax Tree.
    
    Grammar:
        expression := term | expression AND expression | expression OR expression | (expression)
        term := word | "phrase" | word* | *word
    
    Args:
        query: Boolean search query string
        
    Returns:
        Root node of AST
        
    Raises:
        QuerySyntaxError: If query syntax is invalid
    """
    if not query or not query.strip():
        raise QuerySyntaxError("Query cannot be empty")
    
    tokens = tokenize(query)
    
    if not tokens:
        raise QuerySyntaxError("No valid tokens found in query")
    
    # Validate parentheses balance
    paren_count = 0
    for token in tokens:
        if token == '(':
            paren_count += 1
        elif token == ')':
            paren_count -= 1
        if paren_count < 0:
            raise QuerySyntaxError("Unbalanced parentheses: too many closing parentheses")
    if paren_count != 0:
        raise QuerySyntaxError("Unbalanced parentheses: unclosed opening parentheses")
    
    result, pos = parse_expression(tokens, 0)
    
    if pos < len(tokens):
        raise QuerySyntaxError(f"Unexpected token at position {pos}: {tokens[pos]}")
    
    return result


def parse_expression(tokens: List[str], pos: int) -> tuple[ASTNode, int]:
    """
    Parse expression with operator precedence.
    
    Precedence (lowest to highest):
    1. OR
    2. AND
    3. Terms and parentheses
    
    Args:
        tokens: List of tokens
        pos: Current position in token list
        
    Returns:
        (AST node, new position)
    """
    # Parse first term/group
    left, pos = parse_and_expression(tokens, pos)
    
    # Check for OR operator
    while pos < len(tokens) and tokens[pos].upper() == 'OR':
        pos += 1  # Skip OR
        right, pos = parse_and_expression(tokens, pos)
        left = OperatorNode('OR', left, right)
    
    return left, pos


def parse_and_expression(tokens: List[str], pos: int) -> tuple[ASTNode, int]:
    """
    Parse AND expressions (higher precedence than OR).
    
    Args:
        tokens: List of tokens
        pos: Current position in token list
        
    Returns:
        (AST node, new position)
    """
    left, pos = parse_primary(tokens, pos)
    
    # Check for AND operator
    while pos < len(tokens) and tokens[pos].upper() == 'AND':
        pos += 1  # Skip AND
        right, pos = parse_primary(tokens, pos)
        left = OperatorNode('AND', left, right)
    
    return left, pos


def parse_primary(tokens: List[str], pos: int) -> tuple[ASTNode, int]:
    """
    Parse primary expression (term, phrase, or parenthesized expression).
    
    Args:
        tokens: List of tokens
        pos: Current position in token list
        
    Returns:
        (AST node, new position)
    """
    if pos >= len(tokens):
        raise QuerySyntaxError("Unexpected end of query")
    
    token = tokens[pos]
    
    # Parenthesized expression
    if token == '(':
        pos += 1  # Skip (
        node, pos = parse_expression(tokens, pos)
        if pos >= len(tokens) or tokens[pos] != ')':
            raise QuerySyntaxError("Missing closing parenthesis")
        pos += 1  # Skip )
        return node, pos
    
    # Closing parenthesis without opening
    if token == ')':
        raise QuerySyntaxError("Unexpected closing parenthesis")
    
    # Quoted phrase
    if token.startswith('"') and token.endswith('"'):
        phrase = token[1:-1]  # Remove quotes
        return TermNode(phrase, is_phrase=True), pos + 1
    
    # Regular term (may contain wildcards)
    if token.upper() not in ('AND', 'OR'):
        return TermNode(token, is_phrase=False), pos + 1
    
    raise QuerySyntaxError(f"Unexpected token: {token}")


def validate_query(query: str) -> tuple[bool, str]:
    """
    Validate query syntax without parsing.
    
    Args:
        query: Query string to validate
        
    Returns:
        (is_valid, error_message)
    """
    try:
        parse_query(query)
        return True, ""
    except QuerySyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    test_queries = [
        'LLM',
        '"Large Language Model"',
        'LLM OR GPT',
        'LLM AND GPT',
        '("Large Language Model*" OR "LLM") AND "Risk of bias"',
        '(A OR B) AND (C OR D)',
        'GPT* AND assessment*',
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            ast = parse_query(query)
            print(f"AST: {ast}")
        except QuerySyntaxError as e:
            print(f"Error: {e}")
