select
    provider,
    city_name,
    latitude,
    longitude,
    ingested_at,
    forecast_date,
    temp_min_c,
    temp_max_c,
    precip_probability,
    wind_kmh,
    uv_index,
    condition
from {{ ref('stg_open_meteo_forecasts') }}

union all

select
    provider,
    city_name,
    latitude,
    longitude,
    ingested_at,
    forecast_date,
    temp_min_c,
    temp_max_c,
    precip_probability,
    wind_kmh,
    uv_index,
    condition
from {{ ref('stg_weatherapi_forecasts') }}
