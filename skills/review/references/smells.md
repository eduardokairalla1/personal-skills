# Smell baseline

Code smells from Fowler's _Refactoring_ (ch. 3). Each is a labelled
heuristic, never a hard violation: report it as "possible X", quote the
hunk, and suppress it when a documented repo standard endorses the shape.

- **Mysterious Name**: a function, variable or type whose name does not say
  what it does or holds. → rename; if no honest name comes, the design is
  murky.
- **Duplicated Code**: the same logic shape in more than one hunk or file of
  the change. → extract the shared shape, call it from both.
- **Long Function**: a body you have to scroll to hold in your head. →
  split by intent; name each piece by what it does.
- **Long Parameter List**: so many arguments that call sites are hard to
  read. → bundle into an object, or let the callee ask for what it needs.
- **Feature Envy**: a method that reaches into another object's data more
  than its own. → move it onto the data it envies.
- **Data Clumps**: the same few fields or params always travelling
  together. → bundle them into one type.
- **Primitive Obsession**: a primitive or string standing in for a domain
  concept. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if` cascade on the same type in
  several places. → polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forcing scattered edits across
  many files. → gather what changes together into one module.
- **Divergent Change**: one module edited for several unrelated reasons. →
  split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters or hooks for needs
  the spec does not have. → delete; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` walks the caller should not
  depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly delegates onward. → cut
  it, call the real target.
- **Refused Bequest**: a subclass that ignores or overrides most of what it
  inherits. → drop the inheritance, use composition.
- **Comments as deodorant**: a comment explaining code that could be made
  clear instead. → rename, extract, then delete the comment.
