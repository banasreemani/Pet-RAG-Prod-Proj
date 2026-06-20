from collections import defaultdict

from evaluation.eval import evaluate_all_retrieval, evaluate_all_answers


def run_retrieval_summary():
    total_mrr = 0.0
    total_ndcg = 0.0
    total_coverage = 0.0
    category_mrr = defaultdict(list)
    count = 0

    for test, result, prog_value in evaluate_all_retrieval():
        count += 1
        total_mrr += result.mrr
        total_ndcg += result.ndcg
        total_coverage += result.keyword_coverage
        category_mrr[test.category].append(result.mrr)

    if count == 0:
        return {
            "count": 0,
            "avg_mrr": 0.0,
            "avg_ndcg": 0.0,
            "avg_coverage": 0.0,
            "category_data": []
        }

    category_data = []
    for category, scores in category_mrr.items():
        category_data.append({
            "Category": category,
            "Average MRR": sum(scores) / len(scores)
        })

    return {
        "count": count,
        "avg_mrr": total_mrr / count,
        "avg_ndcg": total_ndcg / count,
        "avg_coverage": total_coverage / count,
        "category_data": category_data
    }


def run_answer_summary():
    total_accuracy = 0.0
    total_completeness = 0.0
    total_relevance = 0.0
    category_accuracy = defaultdict(list)
    count = 0

    for test, result, prog_value in evaluate_all_answers():
        print(f"Answer eval completed for: {test.question}")
        count += 1
        total_accuracy += result.accuracy
        total_completeness += result.completeness
        total_relevance += result.relevance
        category_accuracy[test.category].append(result.accuracy)

    if count == 0:
        return {
            "count": 0,
            "avg_accuracy": 0.0,
            "avg_completeness": 0.0,
            "avg_relevance": 0.0,
            "category_data": []
        }

    category_data = []
    for category, scores in category_accuracy.items():
        category_data.append({
            "Category": category,
            "Average Accuracy": sum(scores) / len(scores)
        })

    return {
        "count": count,
        "avg_accuracy": total_accuracy / count,
        "avg_completeness": total_completeness / count,
        "avg_relevance": total_relevance / count,
        "category_data": category_data
    }