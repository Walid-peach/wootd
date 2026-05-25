with source as (
    select
        provider,
        city_name,
        latitude,
        longitude,
        ingested_at,
        payload
    from {{ source('raw', 'OPEN_METEO_FORECASTS') }}
),

daily_forecasts as (
    select
        provider,
        city_name,
        latitude,
        longitude,
        ingested_at,
        forecast_day.value::date as forecast_date,
        get(payload:daily:temperature_2m_min, forecast_day.index)::float as temp_min_c,
        get(payload:daily:temperature_2m_max, forecast_day.index)::float as temp_max_c,
        get(payload:daily:precipitation_probability_max, forecast_day.index)::float / 100
            as precip_probability,
        get(payload:daily:wind_speed_10m_max, forecast_day.index)::float as wind_kmh,
        get(payload:daily:uv_index_max, forecast_day.index)::float as uv_index,
        null::string as condition
    from source,
        lateral flatten(input => payload:daily:time) as forecast_day
)

select * from daily_forecasts
