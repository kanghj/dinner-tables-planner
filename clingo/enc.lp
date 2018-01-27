%% persons and tables

{ total_tables(L..U) } = 1 :- total_tables_min(L), total_tables_max(U).

table(0..M-1) :- total_tables(M).
clique(1..C) :- cliques(C).

%% total_cliques(A, N) :- person(A), N = #count { in_clique(A, C) : clique(C) }.


%% each person belongs to 1 table
{ in_table(I, J) : table(J) } = 1 :- person(I).

%% table has a maximum size
%% table_occupied(J, T) :- table(J), T = #sum { F,I : person(I), in_table(I, J), person_size(I, F) }.
:- #sum { F,I : person(I), in_table(I, J), person_size(I, F) } > S, table(J), table_size(J, S).

%% 'cuts' counts relationships of people who are not sitting together
cut(C, V) :- clique(C), V = #sum {AS, A : person_size(A, AS), in_clique(B, C), in_clique(A, C), in_table(A, T), not in_table(B, T), table(T)}.

%% total_cut(M) :- M = #sum { (AS + BS) * W, A, B : clique(C), person_size(A, AS), person_size(B, BS), clique_weight(C, W), in_clique(B, C), person(B), in_clique(A, C), person(A), table(T), in_table(A, T), not in_table(B, T)}.
%% weighted_cuts(C, N * W) :- cut(C, N), clique_weight(C, W).
total_cut(M) :- M = #sum { N, C : cut(C, N), clique(C), clique_weight(C, W)}.

%% #minimize {(in_table(A,T), in_table(B,Q))@0 : table(T), table(Q), person(A), person(B), in_clique(A, C), in_clique(B, C), total_cliques(A, 1), total_cliques(B, 1) }.

#minimize {C@1 : total_cut(C)}.
#minimize {M@2 : total_tables(M)}.

%% prevent people from sitting alone without anyone they know
minimum_isolation_size(1).


%% counter(C, A, P) :- clique(C), in_clique(A, C), P = {person(B) :in_clique(B, C) , in_table(A, T), in_table(B, T), table(T)}.

violates_isolation_rule(A) :- can_violate_isolation_rule(A), #sum {PS, B : person_size(B, PS), in_clique(B, C), in_table(A, T), in_table(B, T), table(T), clique(C), in_clique(A, C)} <= S, minimum_isolation_size(S).

clique_size(C, N) :- clique(C), N = #sum { W, A: person_size(A, W), in_clique(A, C)}.

has_violation(C) :- violates_isolation_rule(A), in_clique(A, C), N > S, clique_size(C, N), minimum_isolation_size(S).
:- has_violation(_).

#show in_table/2.

#show total_tables/1.

%% #show clique_weight/2.
%% #show cut/2.
#show violates_isolation_rule/1.
#show has_violation/1.

#show person_size/2.
%%#show in_clique/2.
#show clique_size/2.
