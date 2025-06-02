import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def recommend_workout(df, tfidf, tfidf_matrix, goal, muscle, equipment, level, num_recommendations=5, min_rating=0.0, require_description=False):
    user_profile = f"{goal} {muscle} {equipment} {level}"
    user_tfidf = tfidf.transform([user_profile])
    user_sim_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
    top_indices = user_sim_scores.argsort()[::-1]
    recommendations = df.iloc[top_indices][['Title', 'Type', 'BodyPart', 'Equipment', 'Level', 'Rating', 'Desc']]
    recommendations = recommendations[recommendations['Level'].str.lower() == level.lower()]
    if min_rating > 0.0:
        recommendations = recommendations[recommendations['Rating'] >= min_rating]
    if require_description:
        recommendations = recommendations[recommendations['Desc'] != 'No description available']
    return recommendations.drop_duplicates().head(num_recommendations * 2), len(recommendations)

def suggest_sets_reps(ex_type, level):
    if ex_type.lower() == 'strength':
        return "4 sets x 6-8 reps"
    elif ex_type.lower() == 'cardio':
        return "20-30 mins"
    elif level.lower() == 'beginner':
        return "3 sets x 10-12 reps"
    return "3-4 sets x 8-12 reps"

def generate_routine(recommendations, days=3, split="Full Body"):
    routine = {}
    recommendations = recommendations.reset_index(drop=True)

    if split == "Full Body":
        per_day = max(1, len(recommendations) // days)
        for i in range(days):
            day_exercises = recommendations.iloc[i * per_day: (i + 1) * per_day]
            routine[f"Day {i+1} - Full Body"] = day_exercises

    elif split == "Upper/Lower":
        upper = recommendations[recommendations['BodyPart'].str.contains("Chest|Back|Shoulders|Arms", case=False, na=False)]
        lower = recommendations[recommendations['BodyPart'].str.contains("Legs|Glutes|Calves", case=False, na=False)]
        for i in range(days):
            routine[f"Day {i+1} - {'Upper' if i % 2 == 0 else 'Lower'} Body"] = upper if i % 2 == 0 else lower

    elif split == "Push/Pull/Legs":
        push = recommendations[recommendations['BodyPart'].str.contains("Chest|Shoulders|Triceps", case=False, na=False)]
        pull = recommendations[recommendations['BodyPart'].str.contains("Back|Biceps", case=False, na=False)]
        legs = recommendations[recommendations['BodyPart'].str.contains("Legs|Glutes|Calves", case=False, na=False)]
        split_cycle = [push, pull, legs]
        for i in range(days):
            part = ["Push", "Pull", "Legs"][i % 3]
            routine[f"Day {i+1} - {part}"] = split_cycle[i % 3]
    return routine