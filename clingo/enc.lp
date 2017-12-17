%% persons and tables


table(0..M-1) :- total_tables(M).
clique(1..C) :- cliques(C).

%% total_cliques(A, N) :- person(A), N = #count { in_clique(A, C) : clique(C) }.


%% each person belongs to 1 table
{ in_table(I, J) : table(J) } = 1 :- person(I).

%% table has a maximum size
%% table_occupied(J, T) :- table(J), T = #sum { F,I : person(I), in_table(I, J), person_size(I, F) }.
:- #sum { F,I : person(I), in_table(I, J), person_size(I, F) } > S, table(J), table_size(J, S).

%% 'cuts' counts relationships of people who are not sitting together
cut(C, N) :- clique(C), N = { in_clique(B, C) : person(B), in_clique(A, C), person(A), table(T), in_table(A, T), not in_table(B, T) }.
total_cut(M) :- M = #sum { N,C : cut(C, N), clique(C) }.

%% #minimize {(in_table(A,T), in_table(B,Q))@0 : table(T), table(Q), person(A), person(B), in_clique(A, C), in_clique(B, C), total_cliques(A, 1), total_cliques(B, 1) }.

#minimize {C@1 : total_cut(C)}.

#show in_table/2.
