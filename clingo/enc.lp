%% persons and tables
person(1..N) :- total_persons(N).
table(1..M) :- total_tables(M).
clique(1..C) :- cliques(C).

%% total_cliques(A, N) :- person(A), N = #count { in_clique(A, C) : clique(C) }.



%% each person belongs to 1 table
{ in_table(I, J) : table(J) } = 1 :- person(I).

%% table_size - 1 <= { in_table(I, J) : table(J), person(I) } <= table_size + 1.

%% table has a maximum size
table_size - 2 <= { in_table(I, J) : person(I) } <= table_size :- table(J).

%% 'cuts' counts relationships of people who are not sitting together
cut(C, N) :- clique(C), N = { in_clique(B, C) : person(B), person(A), in_clique(A, C), table(T), in_table(A, T), not in_table(B, T) }.
total_cut(C) :- C = #sum { N,C : cut(C, N), clique(C) }.

%% #minimize {(in_table(A,T), in_table(B,Q))@0 : table(T), table(Q), person(A), person(B), in_clique(A, C), in_clique(B, C), total_cliques(A, 1), total_cliques(B, 1) }.

#minimize {C@1 : total_cut(C)}.


