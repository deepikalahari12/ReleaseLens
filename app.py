
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from github_integration import fetch_workflow_runs, fetch_github_releases


from release_traceability import (
    save_workflow_runs,
    get_workflows_for_commit
)
from release_health import assess_release_health
from data_sources import (
    normalize_github_runs,
    normalize_sample_records,
)
# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_PATH = Path(__file__).with_name("releaselens.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS releases (
                id INTEGER PRIMARY KEY,
                version TEXT UNIQUE NOT NULL,
                commit_sha TEXT NOT NULL,
                build_status TEXT NOT NULL,
                test_status TEXT NOT NULL,
                deployment_status TEXT NOT NULL,
                environment TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM releases"
        ).fetchone()[0]

        if count == 0:
            sample_releases = [
                (
                    "v1.0.0",
                    "a1b2c3d",
                    "Passed",
                    "Passed",
                    "Deployed",
                    "Production",
                    "2026-11-12"
                ),
                (
                    "v1.1.0",
                    "e4f5a6b",
                    "Passed",
                    "Failed",
                    "Not Deployed",
                    "Staging",
                    "2026-11-15"
                ),
                (
                    "v1.2.0",
                    "c7d8e9f",
                    "Running",
                    "Pending",
                    "Not Deployed",
                    "Development",
                    "2026-11-18"
                )
            ]

            conn.executemany("""
                INSERT INTO releases (
                    version,
                    commit_sha,
                    build_status,
                    test_status,
                    deployment_status,
                    environment,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_releases)


# ==========================================
# LOAD RELEASE DATA
# ==========================================

def load_releases():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM releases ORDER BY id DESC",
            conn
        )


# ==========================================
# RELEASE READINESS LOGIC
# ==========================================

def calculate_readiness(release):
    if (
        release["build_status"] == "Failed"
        or release["test_status"] == "Failed"
    ):
        return "Blocked"

    if (
        release["build_status"] == "Passed"
        and release["test_status"] == "Passed"
    ):
        return "Ready"

    return "Pending"


# ==========================================
# STREAMLIT DASHBOARD
# ==========================================

def main():

    st.set_page_config(
        page_title="ReleaseLens",
        page_icon="📊",
        layout="wide"
    )

    initialize_database()

    df = load_releases()

    df["readiness"] = df.apply(
        calculate_readiness,
        axis=1
    )

    # ======================================
    # HEADER
    # ======================================

    st.title("📊 ReleaseLens")

    st.subheader(
        "Software Release Visibility Platform"
    )

        
    st.info(
        "ReleaseLens combines sample release records "
        "stored in SQLite with live GitHub Actions "
        "workflow data. Release readiness is currently "
        "calculated from the sample records."
    )

    

    # ======================================
    # REAL RELEASE HEALTH OVERVIEW
    # ======================================

    st.header("Real Release Health Overview")
    st.caption(
        "Live GitHub release and CI evidence. "
        "Deployment status is not independently verified."
    )

    try:
        real_releases = fetch_github_releases()
        live_runs = fetch_workflow_runs()

        if real_releases:
            release_names = [
                item["version"] for item in real_releases
            ]

            chosen_version = st.selectbox(
                "Select a published GitHub release",
                release_names,
                key="real_release_selector"
            )

            selected_real_release = next(
                item for item in real_releases
                if item["version"] == chosen_version
            )

            full_sha = selected_real_release.get(
                "commit_sha"
            ) or ""

            evidence = [
                run for run in live_runs
                if full_sha
                and run.get("full_commit_sha") == full_sha
            ]

            assessment = assess_release_health(evidence)

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Release",
                chosen_version
            )

            col2.metric(
                "CI Health",
                assessment["status"]
            )

            col3.metric(
                "Deployment",
                assessment["deployment"]
            )

            st.subheader("Analysis Outcome")

            if assessment["status"] == "CI Passed":
                st.success(assessment["reason"])
            elif assessment["status"] == "CI Failed":
                st.error(assessment["reason"])
            else:
                st.warning(assessment["reason"])

            st.info(
                "Assessment: CI evidence is evaluated "
                "for the selected release commit. "
                "Successful CI does not establish "
                "deployment readiness."
            )

            st.write(
                "**Release Commit:**",
                full_sha[:7] if full_sha else "Unavailable"
            )

            st.write(
                "**Matching CI Workflows:**",
                len(evidence)
            )

            if evidence:
                st.subheader("Supporting CI Evidence")
                st.dataframe(
                    pd.DataFrame(evidence),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "url": st.column_config.LinkColumn(
                            "Workflow Evidence"
                        )
                    }
                )
            else:
                st.warning(
                    "No matching CI evidence found "
                    "among the retrieved workflow runs."
                )

            if selected_real_release.get("url"):
                st.link_button(
                    "View Release on GitHub",
                    selected_real_release["url"]
                )

        else:
            st.info(
                "No published GitHub releases found."
            )

    except Exception as error:
        st.error(
            f"Unable to load real release evidence: {error}"
        )


    st.divider()

    # ======================================
    # RELEASE METRICS
    # ======================================

    total_releases = len(df)

    ready_releases = (
        df["readiness"] == "Ready"
    ).sum()

    blocked_releases = (
        df["readiness"] == "Blocked"
    ).sum()

    deployed_releases = (
        df["deployment_status"] == "Deployed"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Sample Releases",
        total_releases
    )

    col2.metric(
        "Sample Ready",
        ready_releases
    )

    col3.metric(
        "Sample Blocked",
        blocked_releases
    )

    col4.metric(
        "Sample Deployed",
        deployed_releases
    )

    st.divider()

    # ======================================
    # RELEASE OVERVIEW
    # ======================================

    st.header("Sample Release Overview")
    st.caption(
    "Demonstration records stored in SQLite. "
    "These are not verified production releases."
)

    st.dataframe(
        df[
            [
                "version",
                "commit_sha",
                "build_status",
                "test_status",
                "deployment_status",
                "readiness"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # READINESS CHART
    # ======================================

    st.header("Sample Release Readiness Distribution")

    readiness_counts = (
        df["readiness"].value_counts()
    )

    st.bar_chart(readiness_counts)

    st.divider()

    # ======================================
    # RELEASE TRACEABILITY
    # ======================================

    st.header("Release Traceability")

    st.subheader("Live Workflow Traceability")

    selected_commit = st.text_input(
        "Enter a GitHub commit SHA",
        value="be820ef"
    )

    if selected_commit:
        matching_runs = get_workflows_for_commit(
            selected_commit.strip()
        )

        if matching_runs:
            st.success(
                f"Found {len(matching_runs)} workflow run(s)"
            )

            st.dataframe(
                pd.DataFrame(matching_runs),
                width="stretch",
                hide_index=True
            )


            st.subheader("Evidence-Based Release Health")

            assessment = assess_release_health(matching_runs)

            st.write("**CI Health:**", assessment["status"])
            st.write("**Assessment Reason:**", assessment["reason"])
            st.write("**Deployment Status:**", assessment["deployment"])

        else:
            st.info(
                "No stored workflow evidence "
                "found for this commit."
            )

    st.divider()

    selected_version = st.selectbox(
        "Select a release",
        df["version"].tolist()
    )

    release = df[
        df["version"] == selected_version
    ].iloc[0]

    st.write(
        "**Release Version:**",
        release["version"]
    )

    st.write(
        "**Source Commit:**",
        release["commit_sha"]
    )

    st.write(
        "**Build Status:**",
        release["build_status"]
    )

    st.write(
        "**Test Status:**",
        release["test_status"]
    )

    st.write(
        "**Deployment Status:**",
        release["deployment_status"]
    )

    st.write(
        "**Environment:**",
        release["environment"]
    )

    st.write(
        "**Last Updated:**",
        release["updated_at"]
    )

    # ======================================
    # RELEASE HEALTH
    # ======================================

    readiness = release["readiness"]

    st.subheader("Release Health Assessment")

    if readiness == "Ready":
        st.success(
            "Release readiness: READY"
        )

    elif readiness == "Blocked":
        st.error(
            "Release readiness: BLOCKED"
        )

    else:
        st.warning(
            "Release readiness: PENDING"
        )

    st.caption(
        "Readiness is calculated from build "
        "and test status. This prototype "
        "does not independently verify "
        "production deployment safety."
    )

    st.divider()

    
    # ======================================
    # LIVE GITHUB ACTIONS MONITORING
    # ======================================

    st.header("Live GitHub Actions Monitoring")

    st.info(
        "Real workflow data retrieved from the "
        "public ReleaseLens GitHub repository."
    )

    if st.button("Refresh GitHub Workflows"):
        st.rerun()

    try:


    
        workflow_runs = fetch_workflow_runs()
        save_workflow_runs(workflow_runs)


        if workflow_runs:
            workflow_df = pd.DataFrame(workflow_runs)

            # Multi-source data demonstration
            st.subheader("Multi-Source Data Integration")

            sample_records = [
                {
                    "reference": "VER-001",
                    "status": "completed",
                    "result": "success",
                    "timestamp": "2026-11-18T09:00:00Z"
                },
                {
                    "reference": "VER-002",
                    "status": "completed",
                    "result": "failure",
                    "timestamp": "2026-11-18T10:00:00Z"
                },
                {
                    "reference": "VER-003",
                    "status": "in_progress",
                    "result": None,
                    "timestamp": "2026-11-18T11:00:00Z"
                }
            ]

            github_data = normalize_github_runs(
                workflow_runs
            )
            sample_data = normalize_sample_records(
                sample_records
            )

            combined_df = pd.DataFrame(
                github_data + sample_data
            )

            st.caption(
                "Demonstrates a common data format for "
                "real GitHub Actions runs and simulated "
                "verification-system records. "
                "Sample records are not Scania data."
            )

            st.dataframe(
                combined_df,
                use_container_width=True,
                hide_index=True
            )

            source_counts = (
                combined_df.groupby(
                    ["source", "result"],
                    dropna=False
                )
                .size()
                .reset_index(name="count")
            )

            st.subheader("Verification Outcomes by Source")

            st.bar_chart(
                source_counts,
                x="source",
                y="count",
                color="result"
            )

            st.subheader("Cross-Source Analysis")

            source_summary = (
                combined_df.assign(
                    outcome=combined_df["result"].fillna("pending")
                )
                .groupby(["source", "outcome"])
                .size()
                .unstack(fill_value=0)
            )

            st.dataframe(
                source_summary,
                use_container_width=True
            )

            for source, group in combined_df.groupby("source"):
                failures = (
                    group["result"] == "failure"
                ).sum()

                incomplete = (
                    group["status"] != "completed"
                ).sum()

                if failures > 0:
                    st.warning(
                        f"{source}: {failures} failed record(s). "
                        "Investigate the failed verification evidence."
                    )

                if incomplete > 0:
                    st.warning(
                        f"{source}: {incomplete} incomplete record(s). "
                        "Wait for verification to finish."
                    )

                if failures == 0 and incomplete == 0:
                    st.success(
                        f"{source}: no failed or incomplete "
                        "records in the retrieved dataset."
                    )

            st.caption(
                      "Analysis is performed separately for each "
                      "source. Simulated verification records are "
                      "used for demonstration purposes."
)



            # Visualize actual GitHub Actions results
            st.subheader("Live CI Workflow Results")

            ci_counts = (
                workflow_df["conclusion"]
                .fillna("Pending")
                .value_counts()
            )

            st.bar_chart(
                ci_counts,
                x_label="Workflow Outcome",
                y_label="Number of Workflow Runs"
            )

            successful = (
                workflow_df["conclusion"] == "success"
            ).sum()

            completed = (
                workflow_df["status"] == "completed"
            ).sum()

            if completed > 0:
                success_rate = successful / completed * 100
                st.metric(
                    "Completed Workflow Success Rate",
                    f"{success_rate:.1f}%"
                )


            st.metric(
                "Workflow Runs Retrieved",
                len(workflow_df)
            )

            st.subheader("CI Analysis and Recommendations")

            failed = (
                workflow_df["conclusion"] == "failure"
            ).sum()

            pending = (
                workflow_df["status"] != "completed"
            ).sum()

            if failed > 0:
                st.error(
                    f"{failed} failed workflow run(s) detected."
                )
                st.write(
                    "**Recommended action:** Investigate failed "
                    "workflows and review their logs."
                )

            elif pending > 0:
                st.warning(
                    f"{pending} workflow run(s) are incomplete."
                )
                st.write(
                    "**Recommended action:** Wait for CI "
                    "verification before making a decision."
                )

            elif successful == len(workflow_df):
                st.success(
                    "All retrieved CI workflow runs passed."
                )
                st.write(
                    "**Analysis outcome:** No CI failures were "
                    "detected in the retrieved workflow history."
                )
                st.write(
                    "**Recommended action:** Review additional "
                    "quality and deployment evidence before "
                    "approving release readiness."
                )

            else:
                st.info(
                    "Some workflow outcomes require further review."
                )

            st.caption(
                "Analysis covers only the recently retrieved "
                "GitHub Actions runs, not all historical "
                "verification evidence."
            )


            st.dataframe(
                workflow_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "url": st.column_config.LinkColumn(
                        "GitHub Workflow Link"
                    )
                }
            )

        else:
            st.warning(
                "No GitHub Actions workflow runs found."
            )

    except Exception as error:
        st.error(
            f"Unable to retrieve GitHub Actions data: {error}"
        )

    st.divider()


    st.caption(
        "ReleaseLens | Software Release "
        "Monitoring and Traceability Prototype"
    )


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
