select *
from {{ ref('fct_daily_forecast') }}
where precip_probability < 0
   or precip_probability > 1
