select
    daily_forecast_id,
    city_id,
    city_name,
    forecast_date,
    temp_min_c,
    temp_max_c,
    temp_avg_c,
    precip_probability,
    wind_kmh,
    uv_index,
    case
        when temp_avg_c < 10 then 'cold'
        when temp_avg_c < 20 then 'mild'
        when temp_avg_c < 25 then 'warm'
        else 'hot'
    end as temperature_band,
    precip_probability >= 0.4 as rain_possible,
    precip_probability >= 0.7 as rain_likely,
    wind_kmh >= 30 as windy,
    uv_index >= 6 as high_uv
from {{ ref('fct_daily_forecast') }}
