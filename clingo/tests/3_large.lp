total_persons(180).
total_tables(18).
cliques(5).
person(1..N) :- total_persons(N).

in_clique(1..40, 1).
in_clique(41..60, 2).
in_clique(61..70, 3).
in_clique(71..95, 4).
in_clique(96..130, 5).
person_size(P, 1) :- person(P).

#const table_size = 10.
table_size(0..30, 10).