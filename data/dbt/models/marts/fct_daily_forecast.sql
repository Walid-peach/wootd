with forecasts as (
    select * from {{ ref('int_weather_observations_deduped') }}
),

cities as (
    select * from {{ ref('dim_city') }}
)

select
    md5(lower(forecasts.city_name) || '|' || forecasts.forecast_date::string) as daily_forecast_id,
    cities.city_id,
    forecasts.city_name,
    forecasts.forecast_date,
    forecasts.provider as selected_provider,
    coalesce(forecasts.latitude, cities.latitude) as latitude,
    coalesce(forecasts.longitude, cities.longitude) as longitude,
    forecasts.latest_ingested_at,
    round(forecasts.temp_min_c, 2) as temp_min_c,
    round(forecasts.temp_max_c, 2) as temp_max_c,
    round((forecasts.temp_min_c + forecasts.temp_max_c) / 2, 2) as temp_avg_c,
    round(forecasts.precip_probability, 3) as precip_probability,
    round(forecasts.wind_kmh, 2) as wind_kmh,
    round(coalesce(forecasts.uv_index, 0), 2) as uv_index,
    forecasts.condition
from forecasts
left join cities
    on lower(forecasts.city_name) = lower(cities.city_name)
