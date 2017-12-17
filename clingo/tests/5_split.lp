total_persons(8).
total_tables(3).
cliques(4).
person(1..N) :- total_persons(N).

in_clique(1..2, 1).
in_clique(3..4, 2).
in_clique(5..6, 3).
in_clique(7..8, 4).
person_size(P, 1) :- person(P).

#const table_size = 3.