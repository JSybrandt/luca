The Luca programming language is a replacement of the Lua language.

The goal is to be easy to implement AND easy to write.

Goals:

- Have fewer shoeguns than Lua.
- Be interpreted.
- Be reasonably fast.
- Be easy to extend.
- Have simple semantics.
- Be easy to learn for new developers.

Thinks I like about Lua:

- Pretty much anything you want to do is _technically_ possible.
- Functions work as you'd expect.
- "everything is tables" is pretty clever.

Things I don't like about Lua:

- One based
- edge cases don't work as exptect (closures, length)
- global scope only!!!


# Draft 1

- Everything is a fn?
- No difference between lambda and non-lambda
- Last line of fn is the return
- Pound is comment

```
square: x -> x*x
print(squre(10))  # 100
```

- closures are allowed

```
linear_fn: slope, offset ->
  (x){y}
}
```

# Draft 2

- Exery expression is an object
- functions are a type of object
- no such thing as classes
- As much as possible is in the std lib, not in the language def.
- lets ignore scope for now


```
() # This indicates a parameter list. If empty it may be omitted.
{} # This indicates an expression. It evaluates as something. It captures variables in scope.
# Whitespace doesn't matter.
# Sometimes, expressions can depend on parameter lists. We call that a fn.
sum = (x, y):{x + y}
# Now sum is an alias for the two parameters, and those parametrs are captured
by the expression.
sum(1, 2) # Here, we bind x and y to 1 and 2 to the parameter
```

# Data model

Function
  - (...):{...}
  - Contains a list of free variables
  - Contains a list of captured variables
  - Can be called by binding the free variables. Then the expression is
      evaluated.
  - This is an expression that returns the function object.

Expression
  - { ... }
  - A nesting structure.
  - Can be evalauted to produce a result.
  - The last expression to be evaluated in the nest is the result of that
      expession.
  - The "ret" keyword can return early.
  - The simplest expression is simply an object, which evalautes to itself.
  - The empty expression returns Null.

Assignment
  - <identifier> = <expression>
  - Creates an entry in the current scope under the given id. Evalutes the
      expression.

Calling
  - <identifer><parameterlist>
```
# Create a no-op function
a = ():{}
```


# Idea 3

- Everything is an "entity"


```
{} # This is an entity.

x = {} # Entities can be assigned names.

x = {y = {}}
x.y # Entities can contain named entities

There are also primitives:
number, boolean, string, null
a = 1
b = true
c = "hello"

Entities can be evaluated, which produces a new entity or primtiive. The thing
an entity evaluates to is determined by "return."

x = { return 5 }
x() # Evaluates to 5. The () here say "evaluate this entity."

Entities can be parameterized!
sum = (x, y){return x+y}  # Lets not talk about how + works just yet.
sum(1,2) # Evaluates to 3. Here we "bind" the parameters of the "sum" entity and
         # evaluate it.
add_five = sum(5) # Here, we only bind the first parmater. The result is a new
                  # parameterized entity with only one free parameter.

Entities can also contain parameterized entities.
foo = {
  bar = (x, y){return x+y}
}
foo() # This evaluates the foo entity. It doesn't have a return, so it returns
      # itself.
foo.bar(1, 3) # This looks up the bar name in the foo entity. Then it binds the
              # parameters to the bar entity and evaluates it to return 4.
baz = (a){
  bax = (b){return a + b}
}
bay = baz(1) # This returns itself, with the a parameter bound to 1.
bay.bax(2) # This looks up the bax name in bay, and binds the b parameter to 2.
           # It evaluates the entity, which has a return.

parameterized entities cannot be evaluated unless all paramers are bound!

You can also set entires in entities after they are made.
foo = {}
foo.x = 5 # foo.x doesn't exist at first, so its initially set to null. Then its
          # overwritten to 5.

You can also list entries under primitive values. Use [] to do that.
foo[1] = 5
foo[2] = 6
foo[true] = 7
foo["x"] = 8  # we'll make ["bar"] be equivalent to foo.bar

If an entity is listed inside [], then its evaluated until it results into a
primitive type.

a = {
  return {
    return 5
  }
}
foo[a] == 5


We can implement a number of useful things with these building blocks!

Namesapces : 
namespace_a = {...}
namespace_b = {...}

Classes:

my_class = (a,b){
  get_a = {return a}
  get_b = {return b}
}
my_instance = my_class(1, 2)

Maps
my_map = {}
my_map[1] = 2
my_map["foo"] = "bar"
my_map["baz"] == null

Sets
my_set = {}
my_set["a"] = true
my_set["b"] = true
my_set["c"] = true

cast to bool
bool = (value){
  return value == true
}

if statements
ifelse = (condition, if_true, if_false){
  _ = {}
  _[true] = if_true
  _[false] = if_false
  return _[condition]
}
if = (condition, if_true){
  return ifelse(condition, if_true, null)
}
This also means that ifelse is also a ternary op!

while loop
while = (condition, loop_body){
  return if(
    condition,{
      loop_body
      for(condition, loop_body)
    })
}

x = 5
while({return x > 5}, {x -= 2})

i = 0
while({x < 10}, {x+=1 do_work})


```

