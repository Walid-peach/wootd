select
    md5(lower(city_name)) as city_id,
    city_name,
    country,
    latitude,
    longitude,
    is_active
from {{ ref('cities') }}
