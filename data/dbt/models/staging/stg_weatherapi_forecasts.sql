with source as (
    select
        provider,
        city_name,
        country,
        latitude,
        longitude,
        ingested_at,
        payload
    from {{ source('raw', 'WEATHER_FORECAST_PAYLOADS') }}
    where provider = 'weatherapi'
),

daily_forecasts as (
    select
        provider,
        city_name,
        country,
        latitude,
        longitude,
        ingested_at,
        forecast_day.value:date::date as forecast_date,
        forecast_day.value:day:mintemp_c::float as temp_min_c,
        forecast_day.value:day:maxtemp_c::float as temp_max_c,
        forecast_day.value:day:daily_chance_of_rain::float / 100 as precip_probability,
        forecast_day.value:day:maxwind_kph::float as wind_kmh,
        forecast_day.value:day:uv::float as uv_index,
        forecast_day.value:day:condition:text::string as condition
    from source,
        lateral flatten(input => payload:forecast:forecastday) as forecast_day
)

select * from daily_forecasts
