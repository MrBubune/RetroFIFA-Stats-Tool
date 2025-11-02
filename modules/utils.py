import pandas as pd
import numpy as np

def load_sample_df(n_matches=500, random_state=1):
    """
    Generate a synthetic season match-level dataset.
    Columns: Player, Team, Opponent, Date, Minutes, Goals, Assists, Shots, KeyPasses, Tackles, Interceptions, PassesCompleted, DistanceKm
    """
    rng = np.random.default_rng(random_state)
    players = [f"Player {i}" for i in range(1, 101)]
    teams = [f"Team {i}" for i in range(1, 21)]
    opponents = teams.copy()

    rows = []
    for _ in range(n_matches):
        player = rng.choice(players)
        team = rng.choice(teams)
        opponent = rng.choice([t for t in opponents if t != team])
        minutes = int(rng.integers(0, 91))
        goals = int(rng.binomial(3, 0.02) if minutes>0 else 0)
        assists = int(rng.binomial(2, 0.03) if minutes>0 else 0)
        shots = int(rng.poisson(1.2) if minutes>0 else 0)
        keypasses = float(rng.poisson(0.8))
        tackles = int(rng.poisson(1.0))
        interceptions = int(rng.poisson(0.6))
        passes_completed = int(rng.integers(10, 80) if minutes>0 else 0)
        distance = round(rng.normal(9.0, 2.0) if minutes>0 else 0.0, 2)
        date = pd.Timestamp("2024-08-01") + pd.to_timedelta(int(rng.integers(0, 280)), unit='D')
        rows.append({
            "Player": player, "Team": team, "Opponent": opponent, "Date": date,
            "Minutes": minutes, "Goals": goals, "Assists": assists, "Shots": shots,
            "KeyPasses": keypasses, "Tackles": tackles, "Interceptions": interceptions,
            "PassesCompleted": passes_completed, "DistanceKm": distance
        })
    df = pd.DataFrame(rows)
    return df

def preprocess_uploaded_df(df):
    # try to parse dates
    for c in df.columns:
        if "date" in c.lower():
            try:
                df[c] = pd.to_datetime(df[c], errors='coerce')
            except Exception:
                pass
    # fill missing numeric with zeros (safe default for match stats)
    num = df.select_dtypes(include='number').columns
    df[num] = df[num].fillna(0)
    return df
