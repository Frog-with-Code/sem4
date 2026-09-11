% Лабораторная работа №2 по дисциплине ЛОИС
% Выполнена студентом группы 421702 БГУИР Шумилов Артем Андреевич
% Основной файл, в котором реализуется вся логика программы
% 08.05.2026;

% SWI-Prolog Official Documentation [Электронный ресурс]. - Режим доступа: https://www.swi-prolog.org/pldoc/index.html [дата обращения: 27.04.2026].

initial_state(state(e, s, s, s, e, s, e, s, e, s, e, e)).

target_state(state(e, s, e, e, s, s, e, s, s, s, e, e)).

% По часовой стрелке
move(state(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12),
     state(N4, N1, N3, N8, N5, N2, N7, N9, N6, N10,  N11, N12), c1_cw).
% Против часовой стрелки
move(state(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12),
     state(N2, N6, N3, N1, N5, N9, N7, N4, N8, N10,  N11, N12), c1_ccw).

% По часовой стрелке
move(state(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12),
     state(N1, N5, N2, N4, N9, N6, N3, N8, N10, N7,  N11, N12), c2_cw).
% Против часовой стрелки
move(state(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12),
     state(N1, N3, N7, N4, N2, N6, N10, N8, N5, N9,  N11, N12), c2_ccw).

% По часовой стрелке
move(state(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12),
     state(N1, N2, N3, N4, N8, N5, N7, N11, N9, N6,  N12, N10), c3_cw).
% Против часовой стрелки
move(state(N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12),
     state(N1, N2, N3, N4, N6, N10, N7, N5, N9, N12,  N8, N11), c3_ccw).

solve(Moves) :-
    initial_state(Init),
    target_state(Target),
    length(Moves, _), % Итеративное увеличение глубины поиска
    solve_path(Init, Target, Moves, [Init]).

solve_path(State, State, [], _).
solve_path(Current, Target, [Move|Moves], Visited) :-
    move(Current, Next, Move),
    \+ member(Next, Visited),
    solve_path(Next, Target, Moves, [Next|Visited]).

run :-
    solve(Moves),
    writeln('Решение найдено! Последовательность ходов:'),
    writeln(Moves),
    !.