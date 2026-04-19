{{ config(materialized = 'table') }}
with grouped as (
    select
        res_9,
        amenity_score,
        count(*) as count
    from
        {{ ref('int_osm') }}
    where
        amenity_score > 0
    group by
        1, 2
)
select 
    res_9,
    max(case when amenity_score = 1 then count end) as `Health Care Systems`,
    max(case when amenity_score = 0.9 then count end) as `Food Access Systems`,
    max(case when amenity_score = 0.7 then count end) as `Emergency Systems`,
    max(case when amenity_score = 0.8 then count end) as `Education Systems`,
    max(case when amenity_score = 0.6 then count end) as `Financial Systems`,
    max(case when amenity_score = 0.75 then count end) as `Public Transport`,
    max(case when amenity_score = 0.78 then count end) as `Green Spaces Systems`,
    max(case when amenity_score = 0.2 then count end) as `Food and beverages`,
    max(case when amenity_score = 0.1 then count end) as `Other Systems`,
    sum(count * amenity_score) as gross_amenity_score
from 
    grouped
group by
    res_9