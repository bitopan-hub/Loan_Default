FEATURE_LABELS = {
    "debt_ratio_cleaned": "Debt Ratio",
    "late_payment_score": "Payment History",
    "util_ratio": "Credit Utilization",
    "age": "Age",
    "realEstate_lines": "Real Estate Ownership"
}

def describe_feature(feature, value, impact):
    if feature == "debt_ratio_cleaned":
        return "High debt compared to income" if impact == "increase" else "Low debt burden"

    if feature == "late_payment_score":
        return "History of late payments" if impact == "increase" else "No late payments"

    if feature == "util_ratio":
        return "High credit usage" if impact == "increase" else "Low credit usage"

    if feature == "age":
        return "Lower age increases risk" if impact == "increase" else "Stable age profile"

    if feature == "realEstate_lines":
        return "No property ownership" if impact == "increase" else "Owns property"

    return feature

def build_explanations(shap_values, X_row, feature_names):
    explanations = []

    for i, feature in enumerate(feature_names):
        shap_val = shap_values[i]
        value = X_row[i]

        impact = "increase" if shap_val > 0 else "decrease"

        explanations.append({
            "feature": feature,
            "name": FEATURE_LABELS.get(feature, feature),
            "impact": impact,
            "strength": abs(float(shap_val)),
            "description": describe_feature(feature, value, impact)
        })

    # Sort by importance
    explanations = sorted(explanations, key=lambda x: x["strength"], reverse=True)

    return explanations

def build_xai_response(explanations, top_n=5):
    return explanations[:top_n]

