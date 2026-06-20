import gradio as gr
import pandas as pd
from collections import defaultdict, Counter
from dotenv import load_dotenv
from pathlib import Path
import json

#from evaluation.eval import evaluate_all_retrieval, evaluate_all_answers
from app.evaluation_service import run_retrieval_summary, run_answer_summary

#from evaluation.eval import evaluate_all_retrieval, evaluate_all_answers

load_dotenv(override=True)

# Color coding thresholds - Retrieval
MRR_GREEN = 0.9
MRR_AMBER = 0.75
NDCG_GREEN = 0.9
NDCG_AMBER = 0.75
COVERAGE_GREEN = 90.0
COVERAGE_AMBER = 75.0

# Color coding thresholds - Answer (1-5 scale)
ANSWER_GREEN = 4.5
ANSWER_AMBER = 4.0


def get_color(value: float, metric_type: str) -> str:
    """Get color based on metric value and type."""
    if metric_type == "mrr":
        if value >= MRR_GREEN:
            return "green"
        elif value >= MRR_AMBER:
            return "orange"
        else:
            return "red"
    elif metric_type == "ndcg":
        if value >= NDCG_GREEN:
            return "green"
        elif value >= NDCG_AMBER:
            return "orange"
        else:
            return "red"
    elif metric_type == "coverage":
        if value >= COVERAGE_GREEN:
            return "green"
        elif value >= COVERAGE_AMBER:
            return "orange"
        else:
            return "red"
    elif metric_type in ["accuracy", "completeness", "relevance"]:
        if value >= ANSWER_GREEN:
            return "green"
        elif value >= ANSWER_AMBER:
            return "orange"
        else:
            return "red"
    return "black"


def format_metric_html(
    label: str,
    value: float,
    metric_type: str,
    is_percentage: bool = False,
    score_format: bool = False,
) -> str:
    """Format a metric with color coding."""
    color = get_color(value, metric_type)
    if is_percentage:
        value_str = f"{value:.1f}%"
    elif score_format:
        value_str = f"{value:.2f}/5"
    else:
        value_str = f"{value:.4f}"
    return f"""
    <div style="margin: 10px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px; border-left: 5px solid {color};">
        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">{label}</div>
        <div style="font-size: 28px; font-weight: bold; color: {color};">{value_str}</div>
    </div>
    """


# def run_retrieval_evaluation(progress=gr.Progress()):
#     """Run retrieval evaluation and yield updates."""
#     total_mrr = 0.0
#     total_ndcg = 0.0
#     total_coverage = 0.0
#     category_mrr = defaultdict(list)
#     count = 0

#     for test, result, prog_value in evaluate_all_retrieval():
#         count += 1
#         total_mrr += result.mrr
#         total_ndcg += result.ndcg
#         total_coverage += result.keyword_coverage

#         category_mrr[test.category].append(result.mrr)

#         # Update progress bar only
#         progress(prog_value, desc=f"Evaluating test {count}...")

#     # Calculate final averages
#     avg_mrr = total_mrr / count
#     avg_ndcg = total_ndcg / count
#     avg_coverage = total_coverage / count

#     # Create final summary metrics HTML
#     final_html = f"""
#     <div style="padding: 0;">
#         {format_metric_html("Mean Reciprocal Rank (MRR)", avg_mrr, "mrr")}
#         {format_metric_html("Normalized DCG (nDCG)", avg_ndcg, "ndcg")}
#         {format_metric_html("Keyword Coverage", avg_coverage, "coverage", is_percentage=True)}
#         <div style="margin-top: 20px; padding: 10px; background-color: #d4edda; border-radius: 5px; text-align: center; border: 1px solid #c3e6cb;">
#             <span style="font-size: 14px; color: #155724; font-weight: bold;">✓ Evaluation Complete: {count} tests</span>
#         </div>
#     </div>
#     """

#     # Create final bar chart data
#     category_data = []
#     for category, mrr_scores in category_mrr.items():
#         avg_cat_mrr = sum(mrr_scores) / len(mrr_scores)
#         category_data.append({"Category": category, "Average MRR": avg_cat_mrr})

#     df = pd.DataFrame(category_data)

#     return final_html, df

def run_retrieval_evaluation(progress=gr.Progress()):
    progress(0.1, desc="Running retrieval evaluation...")

    summary = run_retrieval_summary()

    progress(1.0, desc="Evaluation complete")

    final_html = f"""
    <div style="padding: 0;">
        {format_metric_html("Mean Reciprocal Rank (MRR)", summary["avg_mrr"], "mrr")}
        {format_metric_html("Normalized DCG (nDCG)", summary["avg_ndcg"], "ndcg")}
        {format_metric_html("Keyword Coverage", summary["avg_coverage"], "coverage", is_percentage=True)}
        <div style="margin-top: 20px; padding: 10px; background-color: #d4edda; border-radius: 5px; text-align: center; border: 1px solid #c3e6cb;">
            <span style="font-size: 14px; color: #155724; font-weight: bold;">✓ Evaluation Complete: {summary["count"]} tests</span>
        </div>
    </div>
    """

    df = pd.DataFrame(summary["category_data"])

    return final_html, df


# def run_answer_evaluation(progress=gr.Progress()):
#     """Run answer evaluation and yield updates (async)."""
#     total_accuracy = 0.0
#     total_completeness = 0.0
#     total_relevance = 0.0
#     category_accuracy = defaultdict(list)
#     count = 0

#     for test, result, prog_value in evaluate_all_answers():
#         count += 1
#         total_accuracy += result.accuracy
#         total_completeness += result.completeness
#         total_relevance += result.relevance

#         category_accuracy[test.category].append(result.accuracy)

#         # Update progress bar only
#         progress(prog_value, desc=f"Evaluating test {count}...")

#     # Calculate final averages
#     avg_accuracy = total_accuracy / count
#     avg_completeness = total_completeness / count
#     avg_relevance = total_relevance / count

#     # Create final summary metrics HTML
#     final_html = f"""
#     <div style="padding: 0;">
#         {format_metric_html("Accuracy", avg_accuracy, "accuracy", score_format=True)}
#         {format_metric_html("Completeness", avg_completeness, "completeness", score_format=True)}
#         {format_metric_html("Relevance", avg_relevance, "relevance", score_format=True)}
#         <div style="margin-top: 20px; padding: 10px; background-color: #d4edda; border-radius: 5px; text-align: center; border: 1px solid #c3e6cb;">
#             <span style="font-size: 14px; color: #155724; font-weight: bold;">✓ Evaluation Complete: {count} tests</span>
#         </div>
#     </div>
#     """

#     # Create final bar chart data
#     category_data = []
#     for category, accuracy_scores in category_accuracy.items():
#         avg_cat_accuracy = sum(accuracy_scores) / len(accuracy_scores)
#         category_data.append({"Category": category, "Average Accuracy": avg_cat_accuracy})

#     df = pd.DataFrame(category_data)

#     return final_html, df

def run_answer_evaluation(progress=gr.Progress()):
    progress(0.1, desc="Running answer evaluation...")

    summary = run_answer_summary()

    progress(1.0, desc="Evaluation complete")

    final_html = f"""
    <div style="padding: 0;">
        {format_metric_html("Accuracy", summary["avg_accuracy"], "accuracy", score_format=True)}
        {format_metric_html("Completeness", summary["avg_completeness"], "completeness", score_format=True)}
        {format_metric_html("Relevance", summary["avg_relevance"], "relevance", score_format=True)}
        <div style="margin-top: 20px; padding: 10px; background-color: #d4edda; border-radius: 5px; text-align: center; border: 1px solid #c3e6cb;">
            <span style="font-size: 14px; color: #155724; font-weight: bold;">✓ Evaluation Complete: {summary["count"]} tests</span>
        </div>
    </div>
    """

    df = pd.DataFrame(summary["category_data"])

    return final_html, df

def load_feedback_records():
    feedback_file = Path("feedback/feedback.jsonl")

    if not feedback_file.exists():
        return []

    records = []

    with feedback_file.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    return records


# def run_feedback_analytics():
#     records = load_feedback_records()

#     if not records:
#         html = """
#         <div style="padding: 20px; text-align: center; color: #999;">
#             No feedback records found.
#         </div>
#         """

#         return html, pd.DataFrame(columns=["timestamp", "rating", "question", "comment"])

#     total = len(records)
#     thumbs_up = sum(1 for r in records if r.get("rating") == "thumbs_up")
#     thumbs_down = sum(1 for r in records if r.get("rating") == "thumbs_down")
#     positive_rate = (thumbs_up / total * 100) if total else 0

#     html = f"""
#     <div style="padding: 0;">
#         {format_metric_html("Total Feedback", total, "coverage")}
#         {format_metric_html("Helpful 👍", thumbs_up, "coverage")}
#         {format_metric_html("Not Helpful 👎", thumbs_down, "coverage")}
#         {format_metric_html("Positive Rate", positive_rate, "coverage", is_percentage=True)}
#     </div>
#     """

#     recent_records = records[-20:]
#     rows = []

#     for r in reversed(recent_records):
#         rows.append({
#             "timestamp": r.get("timestamp", ""),
#             "rating": r.get("rating", ""),
#             "question": r.get("question", ""),
#             "trace_id": r.get("trace_id", ""),
#             "comment": r.get("comment", "")
#         })

#     df = pd.DataFrame(rows)

#     return html, df    

def run_feedback_analytics():
    records = load_feedback_records()

    if not records:
        html = """
        <div style="padding: 20px; text-align: center; color: #999;">
            No feedback records found.
        </div>
        """
        empty_df = pd.DataFrame(columns=["timestamp", "rating", "question", "comment"])
        empty_neg = pd.DataFrame(columns=["question", "downvotes"])
        return html, empty_df, empty_neg

    total = len(records)
    thumbs_up = sum(1 for r in records if r.get("rating") == "thumbs_up")
    thumbs_down = sum(1 for r in records if r.get("rating") == "thumbs_down")
    positive_rate = (thumbs_up / total * 100) if total else 0

    html = f"""
    <div style="padding: 0;">
        {format_metric_html("Total Feedback", total, "coverage")}
        {format_metric_html("Helpful 👍", thumbs_up, "coverage")}
        {format_metric_html("Not Helpful 👎", thumbs_down, "coverage")}
        {format_metric_html("Positive Rate", positive_rate, "coverage", is_percentage=True)}
    </div>
    """

    recent_rows = []
    for r in reversed(records[-20:]):
        recent_rows.append({
            "timestamp": r.get("timestamp", ""),
            "rating": r.get("rating", ""),
            "question": r.get("question", ""),
            "comment": r.get("comment", "")
        })

    recent_df = pd.DataFrame(recent_rows)

    negative_questions = [
        r.get("question", "")
        for r in records
        if r.get("rating") == "thumbs_down"
    ]

    negative_counter = Counter(negative_questions)

    negative_rows = [
        {"question": question, "downvotes": count}
        for question, count in negative_counter.most_common(10)
    ]

    negative_df = pd.DataFrame(negative_rows)

    return html, recent_df, negative_df

def get_recent_negative_feedback():
    records = load_feedback_records()

    rows = []

    for r in reversed(records):
        if r.get("rating") == "thumbs_down":

            answer = r.get("answer", "")

            if len(answer) > 150:
                answer = answer[:150] + "..."

            rows.append({
                "timestamp": r.get("timestamp", ""),
                "question": r.get("question", ""),
                "answer": answer,
                "comment": r.get("comment") or "No comment provided",
                "trace_id": r.get("trace_id", "")
            })

    return pd.DataFrame(rows)

def refresh_feedback_dashboard():

    metrics_html, recent_df, negative_df = run_feedback_analytics()

    negative_details_df = get_recent_negative_feedback()

    return (
        metrics_html,
        recent_df,
        negative_df,
        negative_details_df
    )    

def main():
    """Launch the Gradio evaluation app."""
    theme = gr.themes.Soft(font=["Inter", "system-ui", "sans-serif"])

    with gr.Blocks(title="RAG Evaluation Dashboard", theme=theme) as app:
        gr.Markdown("# 📊 RAG Evaluation Dashboard")
        gr.Markdown("Evaluate retrieval and answer quality for the Insurellm RAG system")

        # RETRIEVAL SECTION
        gr.Markdown("## 🔍 Retrieval Evaluation")

        retrieval_button = gr.Button("Run Evaluation", variant="primary", size="lg")

        with gr.Row():
            with gr.Column(scale=1):
                retrieval_metrics = gr.HTML(
                    "<div style='padding: 20px; text-align: center; color: #999;'>Click 'Run Evaluation' to start</div>"
                )

            with gr.Column(scale=1):
                retrieval_chart = gr.BarPlot(
                    x="Category",
                    y="Average MRR",
                    title="Average MRR by Category",
                    y_lim=[0, 1],
                    height=400,
                )

        # ANSWERING SECTION
        gr.Markdown("## 💬 Answer Evaluation")

        answer_button = gr.Button("Run Evaluation", variant="primary", size="lg")

        with gr.Row():
            with gr.Column(scale=1):
                answer_metrics = gr.HTML(
                    "<div style='padding: 20px; text-align: center; color: #999;'>Click 'Run Evaluation' to start</div>"
                )

            with gr.Column(scale=1):
                answer_chart = gr.BarPlot(
                    x="Category",
                    y="Average Accuracy",
                    title="Average Accuracy by Category",
                    y_lim=[1, 5],
                    height=400,
                )

        # # FEEDBACK SECTION
        # gr.Markdown("## 📣 Feedback Analytics")

        # feedback_button = gr.Button("Refresh Feedback Analytics", variant="primary", size="lg")

        # with gr.Row():
        #     with gr.Column(scale=1):
        #         feedback_metrics = gr.HTML(
        #             "<div style='padding: 20px; text-align: center; color: #999;'>Click 'Refresh Feedback Analytics' to load feedback</div>"
        #         )

        #     with gr.Column(scale=2):
        #         feedback_table = gr.Dataframe(
        #             headers=["timestamp", "rating", "question","trace_id", "comment"],
        #             label="Recent Feedback"
        #             # height=400,
        #             # wrap=True
        #         )    

                # FEEDBACK SECTION
        gr.Markdown("## 📣 Feedback Analytics")

        feedback_button = gr.Button(
            "Refresh Feedback Analytics",
            variant="primary",
            size="lg"
        )

        with gr.Row():
            with gr.Column(scale=1):
                feedback_metrics = gr.HTML(
                    "<div style='padding: 20px; text-align: center; color: #999;'>Click refresh to load feedback</div>"
                )

            with gr.Column(scale=2):
                recent_feedback_table = gr.Dataframe(
                    headers=["timestamp", "rating", "question", "comment"],
                    label="Recent Feedback"
                )

        gr.Markdown("### 👎 Top Negative Feedback Questions")

        negative_feedback_table = gr.Dataframe(
            headers=["question", "downvotes"],
            label="Questions with Most Negative Feedback"
        )

        gr.Markdown("### 🔍 Recent Negative Feedback")

        negative_details_table = gr.Dataframe(
            headers=[
                "timestamp",
                "question",
                "answer",
                "comment",
                "trace_id"
            ],
            label="Recent Negative Feedback"
        )

        # Wire up the evaluations
        retrieval_button.click(
            fn=run_retrieval_evaluation,
            outputs=[retrieval_metrics, retrieval_chart],
        )

        answer_button.click(
            fn=run_answer_evaluation,
            outputs=[answer_metrics, answer_chart],
        )

        # feedback_button.click(
        #     fn=run_feedback_analytics,
        #     outputs=[feedback_metrics, feedback_table],
        # )

        # feedback_button.click(
        #     fn=run_feedback_analytics,
        #     outputs=[
        #         feedback_metrics,
        #         recent_feedback_table,
        #         negative_feedback_table
        #     ],
        # )

        feedback_button.click(
        fn=refresh_feedback_dashboard,
        outputs=[
            feedback_metrics,
            recent_feedback_table,
            negative_feedback_table,
            negative_details_table
        ],
)

    #app.launch(inbrowser=True)
    app.launch(
    server_name="0.0.0.0",
    server_port=7861
    )


if __name__ == "__main__":
    main()
