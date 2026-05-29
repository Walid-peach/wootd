select *
from {{ ref('fct_daily_forecast') }}
where temp_min_c < -60
   or temp_max_c > 70
   or temp_min_c > temp_max_c
