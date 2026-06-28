FEATURE_LABELS = {
    "debt_ratio_cleaned": "Debt Ratio",
    "late_payment_score": "Payment History",
    "util_ratio": "Credit Utilization",
    "age": "Age",
    "realEstate_lines": "Real Estate Ownership"
}

def describe_feature(feature, value, impact, feature_ranges=None):
    base_desc = feature
    if feature == "debt_ratio_cleaned":
        base_desc = "High debt compared to income" if impact == "increase" else "Low debt burden"
    elif feature == "late_payment_score":
        base_desc = "History of late payments" if impact == "increase" else "No late payments"
    elif feature == "util_ratio":
        base_desc = "High credit usage" if impact == "increase" else "Low credit usage"
    elif feature == "age":
        base_desc = "Lower age increases risk" if impact == "increase" else "Stable age profile"
    elif feature == "realEstate_lines":
        base_desc = "No property ownership" if impact == "increase" else "Owns property"

    if feature_ranges and feature in feature_ranges:
        f_min = feature_ranges[feature]['min']
        f_max = feature_ranges[feature]['max']
        return f"{base_desc} (Present: {value:.2f}, Range: {f_min:.2f} to {f_max:.2f})"
    
    return base_desc

def build_explanations(shap_values, X_row, feature_names, feature_ranges=None):
    explanations = []

    for i, feature in enumerate(feature_names):
        shap_val = shap_values[i]
        value = X_row[i]

        impact = "increase" if shap_val > 0 else "decrease"
        
        details = {
            "feature": feature,
            "name": FEATURE_LABELS.get(feature, feature),
            "impact": impact,
            "strength": abs(float(shap_val)),
            "description": describe_feature(feature, value, impact, feature_ranges),
            "present_value": float(value)
        }
        
        if feature_ranges and feature in feature_ranges:
            details["min_val"] = feature_ranges[feature]['min']
            details["max_val"] = feature_ranges[feature]['max']
            details["mean_val"] = feature_ranges[feature]['mean']

        explanations.append(details)

    # Sort by importance
    explanations = sorted(explanations, key=lambda x: x["strength"], reverse=True)

    return explanations

def build_xai_response(explanations, top_n=5):
    return explanations[:top_n]

