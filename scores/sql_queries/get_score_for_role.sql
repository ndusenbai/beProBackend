drop function if exists get_score_for_role;
create or replace function get_score_for_role(my_role_id bigint)
returns int
language plpgsql as $$
declare score int;
BEGIN
    select sum(sr.score) + 100 as score
    into score
    from companies_role cr
         inner join scores_score ss on ss.role_id =cr.id
         inner join scores_reason sr on ss.reason_id=sr.id
    where
        cr.id=my_role_id
        and
        extract (month from ss.created_at) = extract (month from current_date)
    group by cr.id;
    if score is null then
        score=100;
    end if;
    return score;
end $$;