total_persons(300).
total_tables(30).
cliques(10).
person(1..N) :- total_persons(N).
can_violate_isolation_rule(A) :- person(A).

clique_weight(C, 1) :- clique(C).

in_clique(1..40, 1).
in_clique(41..60, 2).
in_clique(61..70, 3).
in_clique(71..95, 4).
in_clique(96..130, 5).
in_clique(100..150, 6).
in_clique(120..195, 7).
in_clique(150..225, 8).
in_clique(180..265, 9).
in_clique(250..285, 9).
in_clique(257..300, 10).
person_size(P, 1) :- person(P).

#const table_size = 10.

table_size(0..30, 10).