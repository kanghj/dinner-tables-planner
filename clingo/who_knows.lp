person(1..N) :- total_persons(N).
table(1..M) :- total_tables(M).
knows(A, B) :- knows(B, A).
clique(1..C) :- cliques(C).

count_knows(A, T) :- person(A), T = {in_clique(B, C) : person(B), clique(C), in_clique(A, C)}.

#show count_knows/2.