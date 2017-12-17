total_persons(50).
total_tables(5).
cliques(3).
person(1..N) :- total_persons(N).

in_clique(1..40, 1).
in_clique(41..45, 2).
in_clique(46..50, 3).
person_size(P, 1) :- person(P).

#const table_size = 10.
table_size(0..30, 10).