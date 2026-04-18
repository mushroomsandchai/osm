with ids as (
    select
        {{ dbt_utils.generate_surrogate_key([
                                                "name", "amenity", "shop", "leisure", "latitude",
                                                "longitude", "amenity_score", "open_hours"
                                            ]) }} as unique_id,
        name,
        amenity,
        shop,
        leisure,
        latitude,
        longitude,
        amenity_score,
        cast(split(open_hours, '-')[safe_offset(0)] as numeric) as opening_hour,
        cast(split(open_hours, '-')[safe_offset(1)] as numeric) as closing_hour
    from
        {{ ref('stg_osm') }}
    where
        open_hours != 'closed'
)
select
    *
from
    ids
qualify row_number() over (partition by unique_id order by closing_hour desc, opening_hour) = 1
  