total_persons(30).
total_tables(3).
cliques(3).
person(1..N) :- total_persons(N).

clique_weight(C, 1) :- clique(C).

in_clique(1..10, 1).
in_clique(11..21, 2).
in_clique(22..30, 3).
person_size(P, 1) :- person(P).

#const table_size = 10.
table_size(0..30, 10).