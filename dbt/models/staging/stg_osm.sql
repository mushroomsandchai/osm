{{ config(materialized = 'view') }}
with renamed as (
    select
        cast(name as string) as name,
        cast(amenity as string) as amenity,
        cast(shop as string) as shop,
        cast(leisure as string) as leisure,
        cast(lat as numeric) as latitude,
        cast(lon as numeric) as longitude,
        cast(h3_res_9 as string) as res_9,
        cast(h3_res_8 as string) as res_8,
        cast(h3_res_7 as string) as res_7,
        cast(amenity_score as numeric) as amenity_score,
        cast(typical_intervals as string) as open_hours
    from
        {{ source('raw', 'raw_osm') }}
)
select
    *
from
    renamed