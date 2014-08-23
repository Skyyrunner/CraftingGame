import unittest
import prefix
from prefix import PrefixHolder
from prefix import ExpressionError, OperatorError
from prefix import ErrorTypes

#import rpdb2; rpdb2.start_embedded_debugger('1234')

class TestPrefixReader(unittest.TestCase):
    def setUp(self):
        "Normally setup goes here."

    def test_add(self):
        expr = PrefixHolder(["+", 1, 2])
        # Test for simple addition
        self.assertEqual(expr.evaluate(), 3)

    def test_sqrt(self):
        expr = PrefixHolder(["sqrt", 9])
        self.assertEqual(expr.evaluate(), 3)
        # Test that invalid number of arguments throws exception TypeError
        with self.assertRaises(ExpressionError):
            expr = PrefixHolder(["sqrt", 9, 3])

    def test_variables(self):
        # Test that values can be referenced in an addition
        expr = PrefixHolder(["+", "$var1", 1])
        self.assertEqual(expr.evaluate({"var1":2}), 3)
        expr = PrefixHolder(["+", 1, "$var"])
        self.assertEqual(expr.evaluate({"var":2}), 3)
        # Test that variables that don't exist throw NameError
        # var1 is referenced in the expression but isn't provided.
        with self.assertRaises(NameError):
            expr.evaluate({"$var2":1})

    def test_recursion(self):
        # Test that nested expressions work
        expr = PrefixHolder(["+", ["+", 1, 2], 3])
        self.assertEqual(expr.evaluate(), 6)
        expr = PrefixHolder(["+", 3, ["+", 1, 2]])
        self.assertEqual(expr.evaluate(), 6)
        # Test that double-nested expressions also work
        expr = PrefixHolder(["+", ["+", ["+", 1, 2], 3], 4])
        self.assertEqual(expr.evaluate(), 10)
        # Test that nested expressions of various arg lengths work
        expr = PrefixHolder(["+", ["sqrt", 9], 3])
        self.assertEqual(expr.evaluate(), 6)
    
    def test_EvalSimple(self):
        expr = PrefixHolder(["+", 1, 1])
        
        # First check that the function validates expressions correctly
        with self.assertRaises(prefix.ExpressionError) as cm:
            expr.evalSimple([])
        expected = ExpressionError([], ErrorTypes.NoExpression).args
        self.assertEqual(cm.exception.args, expected)
        
        with self.assertRaises(prefix.OperatorError):
            expr.evalSimple(["!?!?!"]) # test that non-existing operators are identified
        
        with self.assertRaises(prefix.ExpressionError) as cm:
            expr.evalSimple(['/', 1, 2, 3])
        expected = ExpressionError(['/', 1, 2, 3], ErrorTypes.ArgumentError).args
        self.assertEqual(cm.exception.args, expected) # Check for number of arguments
        
        
        with self.assertRaises(prefix.ExpressionError) as cm:
            expr.evalSimple(['+', ['+', 1, 2], 3])
        expected = ExpressionError(['+', ['+', 1, 2], 3], ErrorTypes.NestedExpression).args
        self.assertEqual(cm.exception.args, expected) # check that there are no nested expressions
        
        with self.assertRaises(prefix.ExpressionError) as cm:
            expr.evalSimple(['+', "variable", 2])
        expected = ExpressionError(['+', "variable", 2], ErrorTypes.InvalidArgument).args
        self.assertEqual(cm.exception.args, expected) # check that all string arguments have a sigil

        with self.assertRaises(prefix.ExpressionError) as cm:
            expr.evalSimple(['+', 3, {}])
        expected = ExpressionError(['+', 3, {}], ErrorTypes.InvalidObject).args
        self.assertEqual(cm.exception.args, expected) # check that there are no nested expressions
        
        # Check for whether the variable exists
        with self.assertRaises(NameError) as cm:
            expr.evalSimple(['+', "$var1", "$var2"], {"var1": 1, "var3": 3})
        exception = cm.exception.args[0]
        self.assertEqual(exception, "Did not find variable 'var2' in variables.")
        
        # Check some expressions
        self.assertEqual(3, expr.evalSimple(['+', 1, "$c"], {"c": 2}))
        self.assertEqual(4, expr.evalSimple(['sqrt', 16]))
        self.assertEqual(1, expr.evalSimple(['/', "$a", "$b"], {"a": 1, "b": 1}))
            

if __name__=="__main__":
    unittest.main()
