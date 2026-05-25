with source as (
    select
        provider,
        city_name,
        ingested_at,
        payload
    from {{ source('raw', 'NOAA_FORECASTS') }}
),

periods as (
    select
        provider,
        city_name,
        ingested_at,
        period.value:startTime::timestamp_tz as forecast_start_at,
        period.value:endTime::timestamp_tz as forecast_end_at,
        period.value:temperature::float as temperature_value,
        period.value:temperatureUnit::string as temperature_unit,
        period.value:probabilityOfPrecipitation:value::float as precipitation_percent,
        period.value:windSpeed::string as wind_speed_text,
        period.value:shortForecast::string as condition,
        period.value:isDaytime::boolean as is_daytime
    from source,
        lateral flatten(input => payload:properties:periods) as period
),

normalized as (
    select
        provider,
        city_name,
        null::float as latitude,
        null::float as longitude,
        ingested_at,
        forecast_start_at::date as forecast_date,
        case
            when temperature_unit = 'F' then (temperature_value - 32) * 5 / 9
            else temperature_value
        end as temp_c,
        coalesce(precipitation_percent, 0) / 100 as precip_probability,
        coalesce(regexp_substr(wind_speed_text, '\\d+')::float, 0) * 1.60934 as wind_kmh,
        null::float as uv_index,
        condition,
        is_daytime
    from periods
)

select
    provider,
    city_name,
    latitude,
    longitude,
    ingested_at,
    forecast_date,
    temp_c as temp_min_c,
    temp_c as temp_max_c,
    precip_probability,
    wind_kmh,
    uv_index,
    condition
from normalized
