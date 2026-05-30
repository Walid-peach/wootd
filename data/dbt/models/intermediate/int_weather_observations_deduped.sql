with daily as (
    select * from {{ ref('int_daily_city_forecasts') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by lower(city_name), forecast_date
            order by
                case provider
                    when 'open_meteo' then 1
                    when 'weatherapi' then 2
                    else 99
                end,
                latest_ingested_at desc
        ) as provider_rank
    from daily
)

select
    provider,
    city_name,
    forecast_date,
    latitude,
    longitude,
    latest_ingested_at,
    temp_min_c,
    temp_max_c,
    precip_probability,
    wind_kmh,
    uv_index,
    condition
from ranked
where provider_rank = 1
