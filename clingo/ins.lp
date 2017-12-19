total_persons(7).
total_tables(4).
person(1..N) :- total_persons(N).
person_size(P, 1) :- person(P).

cliques(3).

clique_weight(C, 1) :- clique(C).

in_clique(1..4, 1).
in_clique(5..6, 2).
in_clique(7, 3).

table_size(0, 1).
table_size(1, 2).
table_size(2, 3).
table_size(3, 3).
