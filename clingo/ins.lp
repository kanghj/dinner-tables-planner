total_persons(10).
total_tables(4).
person(1..N) :- total_persons(N).
person_size(P, 1) :- person(P).

cliques(3).

clique_weight(C, 1) :- clique(C).

in_clique(0, 1;5, 1;10, 1).
in_clique(1, 2;2, 2;3, 2;4, 2;6, 2;7, 2).
in_clique(8, 3;9, 3).

table_size(0, 3).
table_size(1, 3).
table_size(2, 3).
table_size(3, 3).
