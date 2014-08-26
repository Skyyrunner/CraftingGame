import json
from enum import Enum
import math
import random
#import rpdb2; rpdb2.start_embedded_debugger('1234')

strTypes = [str, unicode]
# -1 for 'any'
operators = {
    "+": -1,
    "-": 2,
    "/": 2,
    "*": -1,
    "sqrt": 1,
    "range": 2,
    "triangular": 3,
    "pow": 2
    }

class ErrorTypes(Enum):
    NoExpression = 1
    NestedExpression = 2
    ArgumentError = 3
    InvalidArgument = 4
    InvalidObject = 5

class ExpressionError(BaseException):
    def __init__(self, expr, type_):
        # type_s are defined in ErrorTypes.
        self.type_ = type_
        self.expr = expr

    def __str__(self):
        if self.type_ == ErrorTypes.NoExpression:
            return "An expression was not provided."
        elif self.type_ == ErrorTypes.NestedExpression:
            return "In expression\n\t" + repr(self.expr) + "\ndid not expect nested expressions."
        elif self.type_ == ErrorTypes.ArgumentError:
            expect = operators[self.expr[0]]
            actual = len(self.expr)-1
            return "In expression\n\t" + repr(self.expr) + "\nexpected " + str(expect) + " arguments but got " + str(actual) + " arguments."
        elif self.type_ == ErrorTypes.InvalidArgument:
            return "In expression\n\t" + repr(self.expr) + "\nfound invalid argument--check for $ sigil."
        elif self.type_ == ErrorTypes.InvalidObject:
            return "In expression\n\t" + repr(self.expr) + "\nfound object('{}')--objects are illegal."

class OperatorError(BaseException):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "Unknown operator: " + repr(self.expr[0])

class PrefixHolder:
    def __init__(self, expr = []):
        self.expr = expr
        # Validate some parts of expression
        self.validateExpr(expr)

        
    lambdas = {
    '+'  :  lambda args: sum(args),
    '-'  :  lambda args: args[0] - args[1],
    '/'  :  lambda args: args[0] / args[1],
    '*'  :  lambda args: reduce(lambda x,y: x * y, args),
    'sqrt': lambda args: math.sqrt(args[0]),
    'range': lambda args: random.uniform(args[0], args[1]),
    'triangular': lambda args: random.triangular(args[0], args[1], args[2]),
    'pow': lambda args: math.pow(args[0], args[1])
    }
        
    # Create lamba functions, that accept lists, to execute the simple expressions.
    def lambafactory(self, operator):
        return self.lambdas[operator]

    def validateExpr(self, expr):
        if type(expr) in [int, float]:
            return

        # Checks for errors in expressions, common to complex and simple expressions.
        if len(expr) == 0:
            raise ExpressionError(expr, ErrorTypes.NoExpression)
        # Does this operator exist?
        if not expr[0] in operators:
            raise OperatorError(expr)
        # Check # of args
        expectedArgs = operators[expr[0]]
        if expectedArgs != -1:
            numArgs = len(expr)-1
            if numArgs != expectedArgs:
                raise ExpressionError(expr, ErrorTypes.ArgumentError)
    
    def evalSimple(self, expr, variables = {}):
        # Evaluate a single expression consisting of one operator and its components.
        # Do basic checks first
        self.validateExpr(expr)
        # Check that expr is simple, ie not nested
        for x in xrange(len(expr)):
            if x == 0:
                continue # first element doesn't count, is operator
            argType = type(expr[x])
            if not argType in strTypes and argType != int and argType != float:
                if argType == list:
                    # No nested expressions allowed
                    raise ExpressionError(expr, ErrorTypes.NestedExpression)
                raise ExpressionError(expr, ErrorTypes.InvalidObject) # Objects ('{}') are illegal
            # Verify variables
            if type(expr[x]) in strTypes:
                if expr[x][0] != "$":
                    raise ExpressionError(expr, ErrorTypes.InvalidArgument)
                elif not expr[x][1:] in variables:
                    raise NameError("Did not find variable '" + expr[x][1:] + "' in variables.")        
        
        # Now do calculations
        args = expr[1:]
        for i in xrange(len(args)):
            if type(args[i]) in strTypes:
                args[i] = variables[args[i][1:]] # Strip sigil and retrieve value.
        return self.lambafactory(expr[0])(args)
    
    def recursiveEval(self, expr, variables):
        # recursive function to crawl expression tree. Called by evalute() 
        for x in xrange(len(expr)):
            if x == 0:
                continue
            if type(expr[x]) == dict:
                raise ExpressionError()
            if type(expr[x]) == list:
                expr[x] = self.recursiveEval(expr[x], variables)

        return self.evalSimple(expr, variables)

    # Variables to be referenced by the expression.
    def evaluate(self, variables = {}): 
        if type(self.expr) != list:
            return self.expr
        return self.recursiveEval(self.expr, variables)