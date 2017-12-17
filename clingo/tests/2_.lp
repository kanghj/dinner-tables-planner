total_persons(70).
total_tables(10).
cliques(3).
person(1..N) :- total_persons(N).

in_clique(1..40, 1).
in_clique(41..60, 2).
in_clique(61..70, 3).
person_size(P, 1) :- person(P).

#const table_size = 10.
table_size(0..30, 10).