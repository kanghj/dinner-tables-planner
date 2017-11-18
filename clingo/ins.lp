total_persons(7).
total_tables(2).
person(1..N) :- total_persons(N).

cliques(3).

in_clique(1..4, 1).
in_clique(5..6, 2).
in_clique(7, 3).

table_size(1, 4).
table_size(2, 3).

