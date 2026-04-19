{{ config(materialized = 'table') }}
with grouped as (
    select
        res_7,
        count(shop) as num_shops
    from
        {{ ref('int_osm') }}
    group by
        1
)
select 
    * 
from 
    grouped