from dataclasses import dataclass, field


@dataclass
class WeatherSnapshot:
    temp_min_c: float
    temp_max_c: float
    precip_probability: float  # 0–1
    wind_kmh: float
    uv_index: float


@dataclass
class Outfit:
    top: str
    bottom: str
    outer: str | None
    accessories: list[str] = field(default_factory=list)
    explanation: str = ""


def recommend(weather: WeatherSnapshot) -> Outfit:
    feels = (weather.temp_min_c + weather.temp_max_c) / 2

    if feels < 0:
        top, bottom, outer = "thermal base layer", "insulated trousers", "heavy winter coat"
        explanation = "Freezing temperatures — layer up fully."
    elif feels < 10:
        top, bottom, outer = "heavy sweater", "jeans", "coat"
        explanation = "Cold day — a coat is essential."
    elif feels < 15:
        top, bottom, outer = "long-sleeve shirt", "chinos", "light jacket"
        explanation = "Cool day — a light jacket will do."
    elif feels < 20:
        top, bottom, outer = "long-sleeve shirt", "chinos", None
        explanation = "Mild day — no outer layer needed."
    elif feels < 25:
        top, bottom, outer = "t-shirt", "chinos", None
        explanation = "Warm day — dress light."
    else:
        top, bottom, outer = "t-shirt", "shorts", None
        explanation = "Hot day — go minimal."

    accessories: list[str] = []
    if weather.precip_probability >= 0.7:
        accessories.append("umbrella")
        explanation += " Rain very likely — bring an umbrella."
    elif weather.precip_probability >= 0.4:
        accessories.append("compact umbrella")
        explanation += " Some rain possible."

    if weather.wind_kmh >= 30 and outer is None:
        outer = "windbreaker"
        explanation += " Windy — a windbreaker helps."

    if weather.uv_index >= 6:
        accessories.extend(["sunglasses", "sunscreen"])
        explanation += " High UV — protect your skin."

    return Outfit(
        top=top,
        bottom=bottom,
        outer=outer,
        accessories=accessories,
        explanation=explanation.strip(),
    )
