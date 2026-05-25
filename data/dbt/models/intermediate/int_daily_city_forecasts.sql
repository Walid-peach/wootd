with observations as (
    select * from {{ ref('int_weather_observations_unioned') }}
),

daily as (
    select
        provider,
        city_name,
        forecast_date,
        max(latitude) as latitude,
        max(longitude) as longitude,
        max(ingested_at) as latest_ingested_at,
        min(temp_min_c) as temp_min_c,
        max(temp_max_c) as temp_max_c,
        max(precip_probability) as precip_probability,
        max(wind_kmh) as wind_kmh,
        max(uv_index) as uv_index,
        any_value(condition) as condition
    from observations
    group by provider, city_name, forecast_date
)

select * from daily
