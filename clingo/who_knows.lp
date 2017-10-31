person(1..N) :- total_persons(N).
table(1..M) :- total_tables(M).
knows(A, B) :- knows(B, A).

count_knows(A, T) :- person(A), T = {knows(A, B) : person(B)}.
