%% persons and tables
person(1..N) :- total_persons(N).
table(1..M) :- total_tables(M).

%% assume relationships between people are symmetric
knows(A, B) :- knows(B, A).

%% each person belongs to 1 table
{ in_table(I, J) : table(J) } = 1 :- person(I).

%% table_size - 1 <= { in_table(I, J) : table(J), person(I) } <= table_size + 1.

%% table has a maximum size
{ in_table(I, J) : person(I) } <= table_size :- table(J).

%% 'cuts' counts relationships of people who are not sitting together
cut(I, N) :- person(I), N = { knows(I, P) : person(P), in_table(I, J), not in_table(P, J) }.
total_cut(C) :- C = #sum { N : cut(I, N) }.

#minimize {C@0 : total_cut(C)}.
