ok(1..2).
haha(M) :- M = #sum {1 * 2,1, 1: ok(1); 1,1,2: ok(2)}.

numbers(1..50).
{ pick(X) : numbers(X)} = 5.
:- #sum { X: pick(X)} <     30.


:- X < 5, pick(X).
