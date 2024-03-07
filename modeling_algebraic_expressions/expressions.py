# Guided by Paul Orlean's "Math for Programmers" book.
from abc import ABC, abstractmethod
import math

class Expression(ABC):
  @abstractmethod
  def __str__(self):
    pass

  @abstractmethod
  def evaluate(self, **bindings):
    pass

  @abstractmethod
  def expand(self):
    pass

  @abstractmethod
  def derivative(self, variable):
    pass

  @abstractmethod
  def get_distinct_variables(self):
    pass

  @abstractmethod
  def get_distinct_numbers(self):
    pass

  @abstractmethod
  def get_distinct_functions(self):
    pass

  def contains(self, variable):
    return variable in self.get_distinct_variables()


_SPECIAL_FUNCTIONS_BINDING = {
  "sin": math.sin,
  "cos": math.cos,
  "tan": math.tan,
  "asin": math.asin,
  "acos": math.acos,
  "atan": math.atan,
  "atan2": math.atan2,
  "sinh": math.sinh,
  "cosh": math.cosh,
  "tanh": math.tanh,
  "asinh": math.asinh,
  "acosh": math.acosh,
  "atanh": math.atanh,
  "exp": math.exp,
  "ln": math.log,
  "log": math.log10,
  "sqrt": math.sqrt,
  "abs": abs,
  "ceil": math.ceil,
  "floor": math.floor,
}


class Power(Expression):
  def __init__(self, base, exponent):
    self.base = base
    self.exponent = exponent

  def evaluate(self, **bindings):
    return self.base.evaluate(**bindings) ** self.exponent.evaluate(**bindings)
  
  def expand(self):
    expaded_base = self.base.expand()
    expanded_exponent = self.exponent.expand()

    if isinstance(expaded_base, Sum):
      return Sum(*[Power(term, self.exponent).expand() for term in expaded_base.terms])
    
    if isinstance(expanded_exponent, Sum):
      return Product(*[Power(self.base, term).expand() for term in expanded_exponent.terms])
    
    return Power(expaded_base, expanded_exponent)
  
  def derivative(self, variable):
    return Product(self.exponent, Power(self.base, Difference(self.exponent, Number(1))), self.base.derivative(variable))
  
  def get_distinct_functions(self):
    return self.base.get_distinct_functions().union(self.exponent.get_distinct_functions())
  
  def get_distinct_numbers(self):
    return self.base.get_distinct_numbers().union(self.exponent.get_distinct_numbers())
  
  def get_distinct_variables(self):
    return self.base.get_distinct_variables().union(self.exponent.get_distinct_variables())
  

class Number(Expression):
  def __init__(self, value):
    self.value = value

  def evaluate(self, **bindings):
    return self.value
  
  def expand(self):
    return self
  
  def derivative(self, variable):
    return Number(0)
  
  def get_distinct_functions(self):
    return set()
  
  def get_distinct_numbers(self):
    return {self.value}
  
  def get_distinct_variables(self):
    return set()

class Variable(Expression):
  def __init__(self, name):
    self.name = name

  def evaluate(self, **bindings):
    try:
      return bindings[self.name]
    except KeyError:
      raise ValueError(f"Variable {self.name} is not bound to a value")
    
  def expand(self):
    return self
  
  def derivative(self, variable):
    if self.name == variable:
      return Number(1)
    else:
      return Number(0)
    
  def get_distinct_functions(self):
    return set()
  
  def get_distinct_numbers(self):
    return set()
  
  def get_distinct_variables(self):
    return {self.name}
  

class Product(Expression):
  def __init__(self, factor1, factor2):
    self.factor1 = factor1
    self.factor2 = factor2

  def evaluate(self, **bindings):
    return self.factor1.evaluate(**bindings) * self.factor2.evaluate(**bindings)
  
  def expand(self):
    expanded_factor1 = self.factor1.expand()
    expanded_factor2 = self.factor2.expand()

    if isinstance(expanded_factor1, Sum):
      return Sum(*[Product(term, self.factor2).expand() for term in expanded_factor1.terms])
    
    if isinstance(expanded_factor2, Sum):
      return Sum(*[Product(self.factor1, term).expand() for term in expanded_factor2.terms])
    
    return Product(expanded_factor1, expanded_factor2)
  
  def derivative(self, variable):
    return Sum(Product(self.factor1, self.factor2.derivative(variable)), Product(self.factor1.derivative(variable), self.factor2))
  
  def get_distinct_functions(self):
    return self.factor1.get_distinct_functions().union(self.factor2.get_distinct_functions())
  
  def get_distinct_numbers(self):
    return self.factor1.get_distinct_numbers().union(self.factor2.get_distinct_numbers())
  
  def get_distinct_variables(self):
    return self.factor1.get_distinct_variables().union(self.factor2.get_distinct_variables())


class Quotient(Expression):
  def __init__(self, numerator, denominator):
    self.numerator = numerator
    self.denominator = denominator

  def evaluate(self, **bindings):
    return self.numerator.evaluate(**bindings) / self.denominator.evaluate(**bindings)
  
  def expand(self):
    expanded_numerator = self.numerator.expand()
    expanded_denominator = self.denominator.expand()

    if isinstance(expanded_numerator, Sum):
      return Sum(*[Quotient(term, self.denominator).expand() for term in expanded_numerator.terms])
    
    if isinstance(expanded_denominator, Sum):
      return Sum(*[Quotient(self.numerator, term).expand() for term in expanded_denominator.terms])
    
    return Quotient(expanded_numerator, expanded_denominator)
  
  def derivative(self, variable):
    return Quotient(Difference(Product(self.numerator.derivative(variable), self.denominator), Product(self.numerator, self.denominator.derivative(variable))), Power(self.denominator, Number(2)))
  
  def get_distinct_functions(self):
    return self.numerator.get_distinct_functions().union(self.denominator.get_distinct_functions())
  
  def get_distinct_numbers(self):
    return self.numerator.get_distinct_numbers().union(self.denominator.get_distinct_numbers())
  
  def get_distinct_variables(self):
    return self.numerator.get_distinct_variables().union(self.denominator.get_distinct_variables())


class Sum(Expression):
  def __init__(self, *terms):
    self.terms = terms

  def evaluate(self, **bindings):
    return sum(term.evaluate(**bindings) for term in self.terms)
  
  def expand(self):
    return Sum(*[term.expand() for term in self.terms])
  
  def derivative(self, variable):
    return Sum(*[term.derivative(variable) for term in self.terms])
  
  def get_distinct_functions(self):
    return set().union(*(term.get_distinct_functions() for term in self.terms))
  
  def get_distinct_numbers(self):
    return set().union(*(term.get_distinct_numbers() for term in self.terms))
  
  def get_distinct_variables(self):
    return set().union(*(term.get_distinct_variables() for term in self.terms))

class Difference(Expression):
  def __init__(self, minuend, subtrahend):
    self.minuend = minuend
    self.subtrahend = subtrahend

  def evaluate(self, **bindings):
    return self.minuend.evaluate(**bindings) - self.subtrahend.evaluate(**bindings)
  
  def expand(self):
    return Difference(self.minuend.expand(), self.subtrahend.expand())
  
  def derivative(self, variable):
    return Difference(self.minuend.derivative(variable), self.subtrahend.derivative(variable))
  
  def get_distinct_functions(self):
    return self.minuend.get_distinct_functions().union(self.subtrahend.get_distinct_functions())
  
  def get_distinct_numbers(self):
    return self.minuend.get_distinct_numbers().union(self.subtrahend.get_distinct_numbers())
  
  def get_distinct_variables(self):
    return self.minuend.get_distinct_variables().union(self.subtrahend.get_distinct_variables())


class Negative(Expression):
  def __init__(self, expression):
    self.expression = expression

  def evaluate(self, **bindings):
    return -self.expression.evaluate(**bindings)
  
  def expand(self):
    return Negative(self.expression.expand())
  
  def derivative(self, variable):
    return Negative(self.expression.derivative(variable))
  
  def get_distinct_functions(self):
    return self.expression.get_distinct_functions()
  
  def get_distinct_numbers(self):
    return self.expression.get_distinct_numbers()
  
  def get_distinct_variables(self):
    return self.expression.get_distinct_variables()
  

class AbsoluteValue(Expression):
  def __init__(self, expression):
    self.expression = expression

  def evaluate(self, **bindings):
    return abs(self.expression.evaluate(**bindings))
  
  def expand(self):
    return AbsoluteValue(self.expression.expand())
  
  def derivative(self, variable):
    return AbsoluteValue(self.expression.derivative(variable))
  
  def get_distinct_functions(self):
    return self.expression.get_distinct_functions()
  
  def get_distinct_numbers(self):
    return self.expression.get_distinct_numbers()
  
  def get_distinct_variables(self):
    return self.expression.get_distinct_variables()
  

class SquareRoot(Expression):
  def __init__(self, expression):
    self.expression = expression

  def evaluate(self, **bindings):
    return self.expression.evaluate(**bindings) ** 0.5
  
  def expand(self):
    return SquareRoot(self.expression.expand())
  
  def get_distinct_functions(self):
    return self.expression.get_distinct_functions()
  
  def get_distinct_numbers(self):
    return self.expression.get_distinct_numbers()
  
  def get_distinct_variables(self):
    return self.expression.get_distinct_variables()
  

class Modulo(Expression):
  def __init__(self, dividend, divisor):
    self.dividend = dividend
    self.divisor = divisor

  def evaluate(self, **bindings):
    return self.dividend.evaluate(**bindings) % self.divisor.evaluate(**bindings)
  
  def get_distinct_functions(self):
    return self.dividend.get_distinct_functions().union(self.divisor.get_distinct_functions())
  
  def get_distinct_numbers(self):
    return self.dividend.get_distinct_numbers().union(self.divisor.get_distinct_numbers())
  
  def get_distinct_variables(self):
    return self.dividend.get_distinct_variables().union(self.divisor.get_distinct_variables())


class Function():
  def __init__(self, name):
    self.name = name

  def get_distinct_functions(self):
    return {self.name}
  
  def get_distinct_numbers(self):
    return set()
  
  def get_distinct_variables(self):
    return set()
  

class Apply(Expression):
  def __init__(self, function, argument):
    self.function = function
    self.argument = argument

  def evaluate(self, **bindings):
    return _SPECIAL_FUNCTIONS_BINDING[self.function.name](self.argument.evaluate(**bindings))
  
  def expand(self):
    return Apply(self.function, self.argument.expand())
  
  def get_distinct_functions(self):
    return {self.function.name}.union(self.argument.get_distinct_functions())
  
  def get_distinct_numbers(self):
    return self.argument.get_distinct_numbers()
  
  def get_distinct_variables(self):
    return self.argument.get_distinct_variables()
  



def distinct_functions(expression):
  return expression.get_distinct_functions()

def expression_contain_combinator(expression, combinator):
  if isinstance(expression, combinator):
    return True
  elif isinstance(expression, Expression):
    return any(expression_contain_combinator(sub_expression, combinator) for sub_expression in expression.__dict__.values())
  else:
    raise TypeError("expression must be an instance of Expression")
  