# API

FastAPI service for outfit recommendations and user feedback.

The API reads recommendation-ready weather data from Snowflake:

```text
Snowflake MARTS.FCT_DAILY_FORECAST -> FastAPI /recommend
FastAPI /feedback -> Snowflake RAW.USER_FEEDBACK
```

Run locally:

```bash
make api-dev
```
